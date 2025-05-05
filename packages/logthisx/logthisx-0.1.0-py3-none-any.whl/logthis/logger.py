import datetime
import os

_log_file_path = None

def _timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def enable_file_logging(filepath: str):
    global _log_file_path
    _log_file_path = filepath

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(_log_file_path, "a", encoding="utf-8") as f:
        f.write(f"\n--- New log session at {_timestamp()} ---\n")

def _write_to_file(formatted: str):
    if _log_file_path:
        with open(_log_file_path, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")

def log_info(message: str):
    formatted = f"[{_timestamp()}] [INFO] {message}"
    print(f"\033[92m{formatted}\033[0m")
    _write_to_file(formatted)

def log_warn(message: str):
    formatted = f"[{_timestamp()}] [WARN] {message}"
    print(f"\033[93m{formatted}\033[0m")
    _write_to_file(formatted)

def log_error(message: str):
    formatted = f"[{_timestamp()}] [ERROR] {message}"
    print(f"\033[91m{formatted}\033[0m")
    _write_to_file(formatted)