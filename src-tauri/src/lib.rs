use tauri::Manager;
use tauri_plugin_shell::ShellExt;
use std::sync::Mutex;
use std::net::TcpListener;

struct SidecarState {
    child_id: Option<u32>,
    port: u16,
}

fn find_free_port(start: u16) -> u16 {
    for port in start..start + 100 {
        if TcpListener::bind(("127.0.0.1", port)).is_ok() {
            return port;
        }
    }
    start
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_notification::init())
        .manage(Mutex::new(SidecarState { child_id: None, port: 8008 }))
        .setup(|app| {
            let shell = app.shell();
            let port = find_free_port(8008);
            
            // Update state with the port
            let state = app.state::<Mutex<SidecarState>>();
            if let Ok(mut s) = state.lock() {
                s.port = port;
            }
            
            // Spawn the sidecar
            let (mut _rx, child) = shell
                .sidecar("api")
                .expect("failed to find sidecar binary")
                .args(["--port", &port.to_string()])
                .spawn()
                .expect("failed to spawn sidecar");
            
            // Store the child process ID
            if let Ok(mut s) = state.lock() {
                s.child_id = Some(child.pid());
            }
            
            log::info!("Sidecar started on port {}", port);
            
            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                let state = window.state::<Mutex<SidecarState>>();
                if let Ok(s) = state.lock() {
                    if let Some(pid) = s.child_id {
                        #[cfg(target_os = "windows")]
                        {
                            let _ = std::process::Command::new("taskkill")
                                .args(["/PID", &pid.to_string(), "/F"])
                                .output();
                        }
                        #[cfg(not(target_os = "windows"))]
                        {
                            unsafe { libc::kill(pid as i32, libc::SIGTERM); }
                        }
                    }
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
