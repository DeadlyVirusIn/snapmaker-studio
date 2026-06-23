// Snapmaker Studio desktop shell.
//
// On startup it spawns the local Python engine sidecar, reads its handshake line
// ({"port", "token"}) from stdout, and exposes that to the frontend via the
// `get_api_info` command. The frontend then calls the sidecar over loopback.
//
// DEV (debug): runs `python -m snapstudio_api` from <repo>/backend (the live engine).
// PROD (release): runs the PyInstaller-frozen sidecar bundled via Tauri externalBin,
//                 which lands next to the app exe as `snapstudio-api.exe`.
//
// The sidecar child is tracked in app state and killed on exit — no orphan process.

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::io::{BufRead, BufReader};
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;

use serde::{Deserialize, Serialize};
use tauri::{Manager, RunEvent, State, Url, WebviewUrl, WebviewWindowBuilder};

// Model Browser allowlist — the ONLY domains the in-app browser may navigate to.
// Enforced in Rust at open time and on every navigation; off-allowlist top-level
// navigations are blocked. The browser window gets no capabilities (no IPC).
const ALLOWED_MODEL_DOMAINS: &[&str] = &[
    "printables.com",
    "thingiverse.com",
    "myminifactory.com",
    "cults3d.com",
    "thangs.com",
    "makerworld.com",
];

fn model_host_allowed(url: &Url) -> bool {
    match url.host_str() {
        Some(h) => {
            let h = h.to_ascii_lowercase();
            ALLOWED_MODEL_DOMAINS
                .iter()
                .any(|d| h == *d || h.ends_with(&format!(".{d}")))
        }
        None => false,
    }
}

/// Open (or reuse) the locked in-app Model Browser at an approved-site URL.
/// The frontend builds the (encoded) URL; Rust is the security boundary: it
/// refuses anything not https + on the approved-domain allowlist, and blocks any
/// later navigation that leaves the allowlist.
#[tauri::command]
fn open_model_browser(app: tauri::AppHandle, url: String) -> Result<(), String> {
    let parsed = Url::parse(&url).map_err(|_| "invalid url".to_string())?;
    if parsed.scheme() != "https" || !model_host_allowed(&parsed) {
        return Err("url is not on the approved model-site allowlist".into());
    }
    let label = "model-browser";
    if let Some(w) = app.get_webview_window(label) {
        w.navigate(parsed).map_err(|e| e.to_string())?;
        let _ = w.set_focus();
        return Ok(());
    }
    WebviewWindowBuilder::new(&app, label, WebviewUrl::External(parsed))
        .title("Snapmaker Studio — Model Browser (approved sites only)")
        .inner_size(1180.0, 820.0)
        .on_navigation(|u| model_host_allowed(u))
        .build()
        .map_err(|e| e.to_string())?;
    Ok(())
}

// ---- Snapmaker Orca handoff (one-way: Studio prepares, Orca slices) ----------
//
// Studio never slices and never controls Orca. These commands only (a) detect an
// installed Snapmaker Orca at a verified location and (b) launch that exact
// executable with the user's prepared 3MF as a single argument. No shell, no
// extra flags, no slicing commands. A path is only ever reported/used if it
// actually exists on disk — no guessed path is treated as truth.

/// Known Snapmaker Orca install locations on Windows, most-trusted first.
#[cfg(windows)]
fn orca_candidates() -> Vec<PathBuf> {
    let exe = "snapmaker-orca.exe";
    let mut v = Vec::new();
    // Verified default install (per-machine).
    match std::env::var("ProgramFiles") {
        Ok(pf) => v.push(Path::new(&pf).join("Snapmaker_Orca").join(exe)),
        Err(_) => v.push(PathBuf::from(r"C:\Program Files").join("Snapmaker_Orca").join(exe)),
    }
    if let Ok(pf86) = std::env::var("ProgramFiles(x86)") {
        v.push(Path::new(&pf86).join("Snapmaker_Orca").join(exe));
    }
    // Per-user install location.
    if let Ok(la) = std::env::var("LOCALAPPDATA") {
        v.push(Path::new(&la).join("Programs").join("Snapmaker_Orca").join(exe));
    }
    v
}

#[cfg(not(windows))]
fn orca_candidates() -> Vec<PathBuf> {
    Vec::new()
}

/// First candidate that is a real file on disk (never a guessed path).
fn first_existing(candidates: &[PathBuf]) -> Option<PathBuf> {
    candidates.iter().find(|p| p.is_file()).cloned()
}

/// Return the path to an installed Snapmaker Orca, or null if none is found.
#[tauri::command]
fn detect_orca() -> Option<String> {
    first_existing(&orca_candidates()).map(|p| p.to_string_lossy().into_owned())
}

/// Hand the prepared 3MF to Snapmaker Orca: launch the verified Orca exe with the
/// file as a single argument. The user drives slicing from there.
#[tauri::command]
fn open_in_orca(path: String) -> Result<(), String> {
    let file = Path::new(path.trim());
    if path.trim().is_empty() || !file.is_file() {
        return Err("prepared-file-missing".into());
    }
    let orca = first_existing(&orca_candidates()).ok_or_else(|| "orca-not-found".to_string())?;
    Command::new(&orca)
        .arg(file)
        .spawn()
        .map_err(|e| format!("launch-failed: {e}"))?;
    Ok(())
}

#[derive(Default, Clone, Serialize, Deserialize)]
struct ApiInfo {
    port: u16,
    token: String,
}

struct ApiState(Mutex<ApiInfo>);
struct SidecarProc(Mutex<Option<Child>>);

#[tauri::command]
fn get_api_info(state: State<ApiState>) -> ApiInfo {
    state.0.lock().unwrap().clone()
}

/// Build the command that launches the engine sidecar, choosing dev vs bundled.
fn sidecar_command() -> Command {
    #[cfg(debug_assertions)]
    {
        // DEV: live engine from <repo>/backend. CARGO_MANIFEST_DIR is
        // <repo>/desktop/src-tauri, so ../../backend points at the engine.
        let backend = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("..")
            .join("..")
            .join("backend");
        let mut cmd = Command::new("python");
        cmd.args(["-m", "snapstudio_api"]).current_dir(backend);
        cmd
    }
    #[cfg(not(debug_assertions))]
    {
        // PROD: frozen sidecar sits beside the app exe (Tauri strips the target
        // triple from the externalBin name when bundling).
        let exe_dir = std::env::current_exe()
            .expect("current_exe")
            .parent()
            .expect("exe parent")
            .to_path_buf();
        let mut cmd = Command::new(exe_dir.join("snapstudio-api.exe"));
        #[cfg(windows)]
        {
            // CREATE_NO_WINDOW: keep the console sidecar invisible while still
            // giving it a real stdout pipe for the handshake.
            use std::os::windows::process::CommandExt;
            cmd.creation_flags(0x0800_0000);
        }
        cmd
    }
}

/// Tie the sidecar (and any children it spawns — e.g. the PyInstaller onefile
/// bootloader + its Python child) to a Windows job object that is killed when
/// its last handle closes. Since this process holds the only handle, the whole
/// sidecar tree dies when the app exits for ANY reason: graceful close, crash,
/// or force-kill. This is the authoritative no-orphan guarantee.
#[cfg(windows)]
fn bind_to_kill_on_close_job(child: &Child) {
    use std::os::windows::io::AsRawHandle;
    use windows_sys::Win32::System::JobObjects::{
        AssignProcessToJobObject, CreateJobObjectW, SetInformationJobObject,
        JobObjectExtendedLimitInformation, JOBOBJECT_EXTENDED_LIMIT_INFORMATION,
        JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE,
    };
    unsafe {
        let job = CreateJobObjectW(std::ptr::null(), std::ptr::null());
        if job.is_null() {
            return;
        }
        let mut info: JOBOBJECT_EXTENDED_LIMIT_INFORMATION = std::mem::zeroed();
        info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
        SetInformationJobObject(
            job,
            JobObjectExtendedLimitInformation,
            &info as *const _ as *const core::ffi::c_void,
            std::mem::size_of::<JOBOBJECT_EXTENDED_LIMIT_INFORMATION>() as u32,
        );
        AssignProcessToJobObject(job, child.as_raw_handle() as _);
        // Keep the job handle open for the app's whole lifetime: the OS closes it
        // when this process dies, which kills the sidecar tree. The handle is a raw
        // pointer (Copy), so there is nothing to drop — binding to `_` is enough.
        let _ = job;
    }
}

/// Spawn the sidecar and block until its handshake line is read.
fn spawn_sidecar() -> (ApiInfo, Child) {
    let mut child = sidecar_command()
        // The sidecar watches this PID and self-exits if the app dies for any
        // reason (close, crash, force-kill) — belt to the exit-handler braces.
        .env("SNAPSTUDIO_PARENT_PID", std::process::id().to_string())
        .stdout(Stdio::piped())
        .spawn()
        .expect("failed to start snapstudio_api sidecar");

    #[cfg(windows)]
    bind_to_kill_on_close_job(&child);

    let stdout = child.stdout.take().expect("sidecar stdout");
    let mut line = String::new();
    BufReader::new(stdout)
        .read_line(&mut line)
        .expect("failed to read sidecar handshake");
    let info: ApiInfo = serde_json::from_str(line.trim()).expect("invalid sidecar handshake");

    (info, child)
}

fn main() {
    let app = tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .manage(ApiState(Mutex::new(ApiInfo::default())))
        .manage(SidecarProc(Mutex::new(None)))
        .invoke_handler(tauri::generate_handler![
            get_api_info,
            open_model_browser,
            detect_orca,
            open_in_orca
        ])
        .setup(|app| {
            let (info, child) = spawn_sidecar();
            *app.state::<ApiState>().0.lock().unwrap() = info;
            *app.state::<SidecarProc>().0.lock().unwrap() = Some(child);
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building Snapmaker Studio");

    app.run(|app_handle, event| {
        // Kill the sidecar when the app exits so no orphan process survives.
        if let RunEvent::Exit = event {
            if let Some(mut child) = app_handle.state::<SidecarProc>().0.lock().unwrap().take() {
                let _ = child.kill();
                let _ = child.wait();
            }
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn first_existing_returns_none_when_no_candidate_exists() {
        let candidates = vec![
            PathBuf::from(r"C:\does\not\exist\snapmaker-orca.exe"),
            PathBuf::from("/does/not/exist/snapmaker-orca"),
        ];
        assert!(first_existing(&candidates).is_none());
    }

    #[test]
    fn first_existing_picks_the_first_real_file() {
        // The test binary itself is guaranteed to exist on disk.
        let real = std::env::current_exe().expect("current exe");
        let candidates = vec![
            PathBuf::from(r"C:\nope\snapmaker-orca.exe"),
            real.clone(),
        ];
        assert_eq!(first_existing(&candidates), Some(real));
    }

    #[cfg(windows)]
    #[test]
    fn windows_candidates_include_verified_program_files_path() {
        let c = orca_candidates();
        assert!(!c.is_empty());
        let tail = Path::new("Snapmaker_Orca").join("snapmaker-orca.exe");
        assert!(c.iter().any(|p| p.ends_with(&tail)));
    }

    #[cfg(not(windows))]
    #[test]
    fn non_windows_has_no_candidates() {
        assert!(orca_candidates().is_empty());
    }
}
