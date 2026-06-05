from utils import calculate_hash, get_timestamp, print_info
from transactions import TX_LIMIT, format_tx
MINING_REWARD = 50.0
DIFFICULTY = 4

def make_block(index: int,transactions: list,previous_hash: str,parent_index: int = -1) -> dict:
    return {
        "index": index,
        "previous_hash": previous_hash,
        "miner" : "",
        "nonce" : 0,
        "timestamp" : get_timestamp(),
        "block_hash": "",
        "is_closed": False,
        "parent_index": parent_index,
        "transactions": list(transactions),
    }

def make_genesis_block() -> dict:
    genesis_tx = {
        "sender":    "SYSTEM",
        "receiver":  "SYSTEM",
        "amount":    0.0,
        "timestamp": get_timestamp(),
        "tx_hash":   "GENESIS",
    }
    block = make_block(
        index=0,
        transactions=[genesis_tx],
        previous_hash="0" * 64,
    )

    block["is_closed"] = True
    block["miner"] = "SYSTEM"
    block["block_hash"] = compute_block_hash(block)
    return block


def compute_block_hash(block: dict) -> str:

    tx_data = "".join(
        f"{tx['sender']}{tx['receiver']}{tx['amount']}{tx['timestamp']}"
        for tx in block["transactions"]
    )
    raw = (
        f"{block['index']}"
        f"{block['previous_hash']}"
        f"{tx_data}"
        f"{block['nonce']}"
        f"{block['timestamp']}"
    )
    return calculate_hash(raw)


def get_last_closed_block(blocks: list) -> dict:
    for block in reversed(blocks):
        if block.get("is_closed", False):
            return block
    return blocks[0]


def get_open_block(blocks: list) -> dict:
    for block in reversed(blocks):
        if not block.get("is_closed", False):
            return block
    return None


def get_next_index(blocks: list) -> int:
    if not blocks:
        return 0
    return max(b["index"] for b in blocks) + 1


def pack_pending_into_block(blocks: list, pending: list) -> dict:
    open_block = get_open_block(blocks)

    if open_block:
        previous_hash = (
                open_block.get("block_hash") or "0" * 64
        )
        parent_index  = open_block["index"]
        print_info(
            f"Обнаружен незакрытый блок #{open_block['index']}. "
            f"Создаём ответвление (форк)."
        )
    else:
        last = get_last_closed_block(blocks)
        previous_hash = last["block_hash"]
        parent_index  = -1

    txs = pending[:TX_LIMIT]
    new_block = make_block(
        index=get_next_index(blocks),
        transactions=txs,
        previous_hash=previous_hash,
        parent_index=parent_index,
    )

    blocks.append(new_block)

    print_info(f"Блок #{new_block['index']} создан и ожидает майнинга.")
    return new_block


def show_blockchain(blocks: list, pending: list) -> None:
    print(f"\n{'=' * 60}")
    print(f"  БЛОКЧЕЙН  |  Блоков: {len(blocks)}  |  Лимит: {TX_LIMIT} тх/блок")
    print(f"{'=' * 60}")

    for block in blocks:
        is_closed    = block.get("is_closed", False)
        status       = "ЗАКРЫТ" if is_closed else "ОТКРЫТ"
        parent_index = block.get("parent_index", -1)
        block_hash   = block.get("block_hash") or ""
        parent_str   = (
            f"  Родитель : блок #{parent_index}\n"
            if parent_index >= 0
            else ""
        )
        hash_preview = block_hash[:20] if block_hash else "(нет)"
        prev_preview = block.get("previous_hash", "")[:20]

        print(f"\n  Блок #{block.get('index')}  [{status}]")
        print(f"  Время    : {block.get('timestamp', '—')}")
        print(f"{parent_str}", end="")
        print(f"  Prev     : {prev_preview}...")
        print(f"  Hash     : {hash_preview}{'...' if block_hash else ''}")
        print(f"  Nonce    : {block.get('nonce', 0)}")
        print(f"  Майнер   : {block.get('miner') or '—'}")
        print(f"  Транзакции:")
        txs = block.get("transactions", [])
        if txs:
            for tx in txs:
                print(format_tx(tx))
        else:
            print("    (нет транзакций)")
        print(f"  {'-' * 55}")

    if pending:
        print(f"\n  Пул ожидающих транзакций ({len(pending)}):")
        for tx in pending:
            print(format_tx(tx))
    else:
        print("\n  Пул ожидающих транзакций: пуст")