from utils import calculate_hash,print_error,print_success

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


def delete_user(users: dict, target_login: str, requester_login: str, requested_password: str,) -> bool:
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

    if not is_admin(requester) and requester_login != target_login:
        print_error("Недостаточно прав. Только администратор может удалять других.")
        return False

    del users[target_login]
    print_success(f"Пользователь '{target_login}' удалён.")
    return True

def authenticate(users: dict, login: str, password: str) -> bool:
    user = users.get(login)
    if user is None:
        return False
    return check_password(user, password)


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

