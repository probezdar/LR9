import hashlib
import datetime

def calculate_hash(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def get_timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def print_success(msg):
    print(f" [OK] {msg}")

def print_header(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")

def print_error(msg):
    print(f" [ОШИБКА] {msg}")

def print_info(msg):
    print(f" [INFO] {msg}")