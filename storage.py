import json
import os

import blocks

DATA_DIR = "data"
BLOCKS_DIR = os.path.join(DATA_DIR, "blocks")
USERS_FILE = os.path.join(DATA_DIR, "users")
PENDING_FILE = os.path.join(DATA_DIR, "pending_transactions.txt")


def ensure_dirs() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(BLOCKS_DIR, exist_ok=True)

def read_file(filepath: str, default):
    if not os.path.exists(filepath):
        return default
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return default
        return json.loads(content)

def write_file(filepath: str, data) -> None:
    ensure_dirs()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_users(users: dict) -> None:
    write_file(USERS_FILE, users)

def load_users() -> dict:
    return read_file(USERS_FILE, {})

def save_pending(pending: list) -> None:
    write_file(PENDING_FILE, pending)

def load_pending() -> list:
    return read_file(PENDING_FILE, [])

def save_block(block: dict) -> None:
    filepath = os.path.join(BLOCKS_DIR, f"block_{block['index']}.txt")
    write_file(filepath, block)

def get_last_block() -> int:
    indexes = get_all_block_indexes()
    return indexes[-1]

def get_all_block_indexes() -> list[int]:
    indexes = []
    for fname in os.listdir(BLOCKS_DIR):
        if fname.startswith("block_") and fname.endswith(".txt"):
            number_str = fname[6:-4]
            if number_str.isdigit():
                indexes.append(int(number_str))
    indexes.sort()
    return indexes

def load_block(index: int) -> dict | None:
    filepath = os.path.join(BLOCKS_DIR, f"block_{index}.txt")
    data = read_file(filepath, None)
    if data is None:
        return None
    data.setdefault("is_closed", False)
    data.setdefault("block_hash", "")
    data.setdefault("miner", "")
    data.setdefault("nonce", 0)
    data.setdefault("parent_index", -1)
    data.setdefault("transactions", [])
    return data

def load_all_blocks() -> list:
    indexes = get_all_block_indexes()
    all_blocks = []
    for index in sorted(indexes):
        b = load_block(index)
        if b is not None:
            all_blocks.append(b)
    return all_blocks