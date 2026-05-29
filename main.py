import storage
import users   as usr_module
import blocks  as blk_module
import mining  as mng_module
from transactions import add_transaction, TX_LIMIT
from utils import print_header, print_success, print_error, print_info


def init_state() -> tuple:

    storage.ensure_dirs()

    users   = storage.load_users()
    blocks  = storage.load_all_blocks()
    pending = storage.load_pending()

    if not blocks:
        print_info("Создаём первый-блок...")
        genesis = blk_module.make_genesis_block()
        blocks.append(genesis)
        storage.save_block(genesis)
        print_success("Первый-блок создан.")

    return users, blocks, pending



def menu_register(users: dict) -> None:

    print_header("РЕГИСТРАЦИЯ")
    login    = input("  Логин        : ").strip()
    password = input("  Пароль       : ").strip()
    role_raw = input("  Роль (user/admin) [Enter = user]: ").strip().lower()
    role     = "admin" if role_raw == "admin" else "user"
    usr_module.register_user(users, login, password, role)


def menu_transaction(users: dict, pending: list, blocks: list) -> None:

    print_header("ТРАНЗАКЦИЯ")

    if len(users) < 2:
        print_error("Нужно минимум 2 пользователя для транзакции.")
        return

    sender   = input("  Отправитель (логин)  : ").strip()
    password = input("  Пароль отправителя   : ").strip()

    if not usr_module.authenticate(users, sender, password):
        print_error("Неверный логин или пароль.")
        return

    receiver = input("  Получатель (логин)   : ").strip()

    try:
        amount = float(input("  Сумма                : ").strip())
    except ValueError:
        print_error("Сумма должна быть числом.")
        return

    success = add_transaction(users, pending, sender, receiver, amount)

    if success and len(pending) >= TX_LIMIT:
        print_info(
            f"Лимит {TX_LIMIT} транзакций достигнут! "
            "Автоматически создаётся блок..."
        )
        blk_module.pack_pending_into_block(blocks, pending)

        del pending[:TX_LIMIT]
        storage.save_pending(pending)


def menu_delete_user(users: dict) -> None:

    print_header("УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ")
    print_info("Администратор может удалить любого.")
    print_info("Пользователь может удалить только себя.")

    requester = input("  Ваш логин            : ").strip()
    password  = input("  Ваш пароль           : ").strip()
    target    = input("  Логин для удаления   : ").strip()

    usr_module.delete_user(users, target, requester, password)


def menu_show_blockchain(blocks: list, pending: list) -> None:

    print_header("БЛОКЧЕЙН")
    blk_module.show_blockchain(blocks, pending)


def menu_check_balance(users: dict) -> None:

    print_header("ПРОВЕРКА БАЛАНСА")
    login    = input("  Логин  : ").strip()
    password = input("  Пароль : ").strip()
    usr_module.check_balance(users, login, password)


def menu_show_users(users: dict) -> None:

    print_header("ПОЛЬЗОВАТЕЛИ")
    login    = input("  Ваш логин  : ").strip()
    password = input("  Ваш пароль : ").strip()
    usr_module.show_users(users, login, password)


def menu_mining(users: dict, blocks: list, pending: list) -> None:

    print_header("МАЙНИНГ")

    open_block = blk_module.get_open_block(blocks)
    if open_block:
        print_info(
            f"Найден незакрытый блок #{open_block['index']} "
            f"({len(open_block['transactions'])} транзакций)."
        )
    elif pending:
        print_info(f"В пуле {len(pending)} транзакций — будет создан новый блок.")
    else:
        print_error("Нет блоков и транзакций для майнинга.")
        return

    print_info(f"Награда за блок: {blk_module.MINING_REWARD:.2f} монет")
    print_info(f"Сложность: {blk_module.DIFFICULTY} ведущих нулей\n")

    login    = input("  Ваш логин (майнер) : ").strip()
    password = input("  Ваш пароль         : ").strip()
    confirm  = input("  Начать майнинг? (да/нет): ").strip().lower()

    if confirm not in ("да", "д", "yes", "y"):
        print_info("Майнинг отменён.")
        return

    mng_module.do_mining(users, blocks, pending, login, password)

def show_menu() -> None:
    print(f"""
{'=' * 60}
  1  —  Регистрация пользователя
  2  —  Совершить транзакцию
  3  —  Удалить пользователя
  4  —  Показать блокчейн
  5  —  Проверить баланс
  6  —  Посмотреть пользователей
  7  —  Майнинг блока
  0  —  Выход
{'=' * 60}""")


def main() -> None:

    print_header("Инициализация блокчейна")
    users, blocks, pending = init_state()
    print_success(
        f"Загружено: пользователей={len(users)}, "
        f"блоков={len(blocks)}, "
        f"транзакций в пуле={len(pending)}"
    )


    handlers = {
        "1": lambda: menu_register(users),
        "2": lambda: menu_transaction(users, pending, blocks),
        "3": lambda: menu_delete_user(users),
        "4": lambda: menu_show_blockchain(blocks, pending),
        "5": lambda: menu_check_balance(users),
        "6": lambda: menu_show_users(users),
        "7": lambda: menu_mining(users, blocks, pending),
    }

    while True:
        show_menu()
        choice = input("  Выберите пункт: ").strip()

        if choice == "0":
            print_success("До свидания! Все данные сохранены автоматически.")
            break
        elif choice in handlers:
            try:
                handlers[choice]()
            except KeyboardInterrupt:
                print_info("\nОперация прервана.")
            except Exception as ex:
                print_error(f"Непредвиденная ошибка: {ex}")
        else:
            print_error("Неверный выбор. Введите число от 0 до 7.")

        input("\n  [Enter — продолжить...]")


if __name__ == "__main__":
    main()


