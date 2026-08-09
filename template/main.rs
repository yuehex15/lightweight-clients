// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    #[cfg(target_os = "windows")]
    {
        if let Ok(exe_path) = std::env::current_exe() {
            if let Some(parent) = exe_path.parent() {
                let data_dir = parent.join("{NAME}_data");
                std::fs::create_dir_all(&data_dir).ok();
                std::env::set_var("WEBVIEW2_USER_DATA_FOLDER", &data_dir);
                // 设置 WebView2 固定运行时路径（便携，不装系统）
                let runtime_dir = parent.join("webview2-runtime");
                if runtime_dir.exists() {
                    std::env::set_var("WEBVIEW2_BROWSER_EXECUTABLE_FOLDER", &runtime_dir);
                }
            }
        }
    }
    app_lib::run();
}