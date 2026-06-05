import json
import os
from utils import calculate_hash

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "blocks")

def ensure_dirs() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

def readFile() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "pending": [], "blocks": []}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return {"users": {}, "pending": [], "blocks": []}

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Ошибка файл blockchain.txt поврежден: {e}")
        return {"users": {}, "pending": [], "blocks": []}

def write_file(state: dict) -> None:
    ensure_dirs()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def save_state(users: dict, pending: list, blocks: list) -> None:
    state = {
        "users": users,
        "pending": pending,
        "blocks": blocks,
    }
    write_file(state)

def load_state() -> tuple:
    state = readFile()
    users = state.get("users", {})
    pending = state.get("pending", [])
    blocks = state.get("blocks", [])

    for block in blocks:
        block.setdefault("is_closed", False)
        block.setdefault("block_hash", "")
        block.setdefault("miner", "")
        block.setdefault("nonce", 0)
        block.setdefault("parent_index", -1)
        block.setdefault("transactions", [])

    return users, pending, blocks
