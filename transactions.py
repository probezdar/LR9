from utils import calculate_hash, get_timestamp, print_success, print_error, print_info

TX_LIMIT = 2

def make_transaction(sender: str, receiver: str, amount: float) -> dict:
    ts = get_timestamp()
    raw = f"{sender}:{receiver}:{amount}{ts}"
    return {
        "sender": sender,
        "receiver": receiver,
        "amount": amount,
        "timestamp": ts,
        "tx_hash": calculate_hash(raw)
    }

def make_reward_transaction(miner_login, reward: float) -> dict:
    return make_transaction("SYSTEM", miner_login, reward )

def add_transaction(users: dict, pending: list, sender_login: str, receiver_login: str,amount: float,) -> bool:
    if sender_login not in users:
        print_error(f"Отправитель '{sender_login}' не найден.")
        return False
    if receiver_login not in users:
        print_error(f"Получатель '{receiver_login}' не найден")
        return False
    if sender_login == receiver_login:
        print_error("Нельзя переводить деньги самому себе")
        return False
    if amount <= 0:
        print_error(f"Недостаточно средств. ")
        return False

    sender = users[sender_login]
    if sender["balance"] < amount:
        print_error(
            f"Недостаточно средств. "
            f"Баланс: {sender['balance']:.2f}, нужно: {amount:.2f}"
        )
        return False

    users[sender_login]["balance"] -= amount
    users[receiver_login]["balance"] += amount

    tx = make_transaction(sender_login, receiver_login, amount)
    pending.append(tx)

    print_success(
        f"Транзакция {sender_login} -> {receiver_login},"
        f"сумма: {amount:.2f}"
    )
    print_info(f"В пуле транзакций: {len(pending)}/{TX_LIMIT}")
    return True

def format_tx(tx: dict) -> str:
    return(
        f"  TX | {tx['sender']} -> {tx['receiver']} | "
        f"Сумма: {tx['amount']:.2f} | {tx['timestamp']}"
    )