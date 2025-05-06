use std::fs;
use std::io::{BufRead, BufReader};
use std::path::Path;
use std::process::{Command, Stdio};

fn find_entry_files() -> Vec<String> {
    let current_dir = Path::new(".");
    let mut entry_files = Vec::new();

    if let Ok(entries) = fs::read_dir(current_dir) {
        for entry in entries {
            if let Ok(entry) = entry {
                let path = entry.path();
                if path.is_file() && path.extension().and_then(|e| e.to_str()) == Some("int") {
                    entry_files.push(path.to_string_lossy().into_owned());
                }
            }
        }
    }
    entry_files
}

fn run_python_script(script_path: &str) {
    let python_path = Path::new("runtime/python.exe");

    let mut child = Command::new(python_path) // 或指定绝对路径如 "runtime/python.exe"
        .arg(script_path)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("启动Python失败");

    // 异步读取输出流
    let stdout = BufReader::new(child.stdout.take().unwrap());
    let stderr = BufReader::new(child.stderr.take().unwrap());

    // 输出处理线程
    let handle = std::thread::spawn(move || {
        for line in stdout.lines() {
            println!("输出: {}", line.unwrap());
        }
        for line in stderr.lines() {
            eprintln!("错误: {}", line.unwrap());
        }
    });

    let _status = child.wait().expect("进程未正常退出");
    handle.join().unwrap();
}

fn main() {
    let entry_files = find_entry_files();
    if 0 == entry_files.len() {
        println!("未找到入口脚本文件");
        return;
    }

    for file in entry_files {
        println!("正在执行脚本: {}", file);
        run_python_script(&file);
    }
}
