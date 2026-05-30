import storage
from utils import calculate_hash, print_success, print_error
import storage
import blocks as blk_module
from transactions import make_reward_transaction, TX_LIMIT
from utils import print_error, print_info, print_success

INITIAL_BALANCE = 100.0


def hash_password(password: str) -> str:
    return calculate_hash(password)


def make_user(login: str, password: str, role: str = "user") -> dict:
    return {
        "login": login,
        "password_hash": hash_password(password),
        "role": role,
        "balance": INITIAL_BALANCE,
    }


def check_password(user: dict, password: str) -> bool:
    return user["password_hash"] == hash_password(password)


def is_admin(user: dict) -> bool:
    return user["role"] == "admin"

def register_user(users: dict, login:str, password:str, role:str = "user") -> bool:
    if login in users:
        print_error(f"Пользователь {login} уже существует.")
        return False
    if len(login) < 3:
        print_error("Логин должен содержать минимум 3 символа.")
        return False
    if len(password) < 4:
        print_error("Пароль должен содержать минимум 4 символа.")
        return False

    users[login] = make_user(login, password, role)

    storage.save_users(users)

    print_success(
        f"Пользователь {login} зарегистрирован."
        f"Роль {role}. Баланс {INITIAL_BALANCE:.2f}"
    )
    return True

def show_users(users: dict, requester_login: str, requester_password: str) -> bool:
    requester = users[requester_login]

    if requester is None or not check_password(requester, requester_password):
        print_error("Неверный логин или пароль.")
        return False

    print(f"\n{'=' * 60}")

    if is_admin(requester):
        print(f" СПИСОК ПОЛЬЗОВАТЕЛЕЙ (всего: {len(users)})")
        print(f"{'=' * 60}")

        for user in users.values():
            role_label = "[ADMIN]" if user["role"] == "admin" else "[USER] "
            print(f" {role_label} {user['login']:<20} Баланс: {user['balance']:.2f}")

    else:
        print(" ВАШ ПРОФИЛЬ")
        print(f"{'=' * 60}")

        user = users[requester_login]
        print(f" Логин:  {user['login']}")
        print(f" Роль:   {user['role']}")
        print(f" Баланс: {user['balance']:.2f}")

    return True


def delete_user(users: dict,
                target_login: str,
                requester_login: str,
                requested_password: str,) -> bool:
    if target_login not in users:
        print_error(f"Пользователь '{target_login}' не найден." )
        return False

    requester = users.get(requester_login)
    if requester is None:
        print_error("Ваш логин не найден.")
        return False

    if not check_password(requester, requested_password):
        print_error("Неверный пароль")
        return False

    del users[target_login]

    storage.save_users(users)

    print_success(f"Пользователь '{target_login}' удалён.")
    return True

def authenticate(users: dict, login: str, password: str) -> bool:
    user = users.get(login)
    if user is None:
        return False
    return check_password(user, password)


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


def do_mining(
    users: dict,
    blocks: list,
    pending: list,
    miner_login: str,
    password: str,
) -> bool:



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
        storage.save_pending(pending)

    open_block["miner"] = miner_login

    mine_block(open_block)

    reward_tx = make_reward_transaction(miner_login, blk_module.MINING_REWARD)
    open_block["transactions"].append(reward_tx)


    users[miner_login]["balance"] += blk_module.MINING_REWARD


    storage.save_block(open_block)
    storage.save_users(users)

    print_success(
        f"Награда {blk_module.MINING_REWARD:.2f} монет "
        f"зачислена пользователю '{miner_login}'."
    )
    return True

def check_balance(users: dict, login: str, password: str) -> None:
    user = users.get(login)
    if user is None:
        print_error(f"Пользователь '{login}' не найден.")
        return
    if not check_password(user, password):
        print_error("Неверный пароль")
        return
    print(f"\n Пользователь : {login}")
    print(f" Баланс   : {user['balance']:.2f}")

