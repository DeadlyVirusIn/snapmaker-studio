// Snapmaker Studio desktop shell.
//
// On startup it spawns the local Python engine sidecar (`python -m snapstudio_api`),
// reads its handshake line ({"port", "token"}), and exposes that to the frontend via
// the `get_api_info` command. The frontend then calls the sidecar over loopback.
//
// DEV: runs `python -m snapstudio_api` from ../backend (the repo engine).
// PROD (future): bundle a PyInstaller-frozen sidecar as a Tauri externalBin and spawn that.

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::io::{BufRead, BufReader};
use std::process::{Command, Stdio};
use std::sync::Mutex;

use serde::{Deserialize, Serialize};
use tauri::{Manager, State};

#[derive(Default, Clone, Serialize, Deserialize)]
struct ApiInfo {
    port: u16,
    token: String,
}

struct ApiState(Mutex<ApiInfo>);

#[tauri::command]
fn get_api_info(state: State<ApiState>) -> ApiInfo {
    state.0.lock().unwrap().clone()
}

fn spawn_sidecar() -> ApiInfo {
    // DEV: run the engine sidecar from <repo>/backend. CARGO_MANIFEST_DIR is
    // <repo>/desktop/src-tauri at build time, so ../../backend points at the engine.
    // PROD (future): spawn the PyInstaller-frozen sidecar bundled via externalBin instead.
    let backend = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("..")
        .join("backend");

    let mut child = Command::new("python")
        .args(["-m", "snapstudio_api"])
        .current_dir(&backend)
        .stdout(Stdio::piped())
        .spawn()
        .expect("failed to start snapstudio_api sidecar");

    let stdout = child.stdout.take().expect("sidecar stdout");
    let mut line = String::new();
    BufReader::new(stdout)
        .read_line(&mut line)
        .expect("failed to read sidecar handshake");
    let info: ApiInfo = serde_json::from_str(line.trim()).expect("invalid sidecar handshake");

    // Keep the sidecar alive for the app's lifetime (Phase 1: leak the handle).
    std::mem::forget(child);
    info
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .manage(ApiState(Mutex::new(ApiInfo::default())))
        .setup(|app| {
            let info = spawn_sidecar();
            *app.state::<ApiState>().0.lock().unwrap() = info;
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![get_api_info])
        .run(tauri::generate_context!())
        .expect("error while running Snapmaker Studio");
}
