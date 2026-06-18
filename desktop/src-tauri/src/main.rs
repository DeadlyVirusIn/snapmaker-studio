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
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;

use serde::{Deserialize, Serialize};
use tauri::{Manager, RunEvent, State};

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
        // Leak the job handle on purpose: it must stay open for the app's whole
        // lifetime. When this process dies the OS closes it -> kills the tree.
        std::mem::forget(job);
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
        .invoke_handler(tauri::generate_handler![get_api_info])
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
