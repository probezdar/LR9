import blocks as blk_module
from transactions import make_reward_transaction, TX_LIMIT
from utils import print_error, print_info, print_success
from users import check_password

def mine_block(block: dict) -> str:
    target = "0" * blk_module.DIFFICULTY
    nonce  = 0

    print_info(f"Майним блок #{block['index']}...")
    print_info(f"Сложность: {blk_module.DIFFICULTY} ведущих нулей")

    while True:
        block["nonce"] = nonce
        current_hash   = blk_module.compute_block_hash(block)

        if nonce % 10_000 == 0 and nonce > 0:
            print_info(f"  Перебрано nonce: {nonce}...")

        if current_hash.startswith(target):
            block["block_hash"] = current_hash
            block["is_closed"]  = True
            print_success(
                f"Блок #{block['index']} закрыт! "
                f"Nonce={nonce}, Hash={current_hash[:20]}..."
            )
            return current_hash

        nonce += 1


def do_mining(users: dict,blocks: list,pending: list,miner_login: str,password: str,) -> bool:
    if miner_login not in users:
        print_error(f"Пользователь '{miner_login}' не найден.")
        return False
    if not check_password(users[miner_login], password):
        print_error("Неверный пароль.")
        return False

    open_block = blk_module.get_open_block(blocks)

    if open_block is None:
        if not pending:
            print_error("Нет блоков и транзакций для майнинга.")
            return False
        print_info("Нет открытых блоков. Упаковываем ожидающие транзакции...")
        open_block = blk_module.pack_pending_into_block(blocks, pending)
        del pending[:TX_LIMIT]

    open_block["miner"] = miner_login

    reward_tx = make_reward_transaction(miner_login, blk_module.MINING_REWARD)
    open_block["transactions"].append(reward_tx)
    mine_block(open_block)
    users[miner_login]["balance"] += blk_module.MINING_REWARD

    print_success(
        f"Награда {blk_module.MINING_REWARD:.2f} монет "
        f"зачислена пользователю '{miner_login}'."
    )
    return True