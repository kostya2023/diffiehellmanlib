import json
import os
import datetime
import traceback
import threading
import time
import platform
import ctypes
import random
from diffiehellmanlib import wrapper
from diffiehellmanlib.exchange import exchange
from tqdm import tqdm
import tracemalloc

# Путь к папке логов
LOG_DIR = "test_logs"

# Путь к журналу тестирования
TEST_JOURNAL = "test_journal.log"


def create_log_dir():
    """Создаем папку для логов, если ее нет."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)


def log(message, log_file):
    """Записываем сообщение в лог-файл."""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_file.write(f"[{timestamp}] {message}\n")
    log_file.flush()


def log_error(message, log_file):
    """Записываем сообщение об ошибке в лог-файл."""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_file.write(f"[{timestamp}] ERROR: {message}\n")
    log_file.flush()


def log_traceback(log_file):
    """Записываем traceback в лог-файл."""
    log_file.write(f"{traceback.format_exc()}\n")
    log_file.flush()


def get_current_date():
    """Получаем текущую дату в формате DD.MM.YYYY."""
    return datetime.datetime.now().strftime("%d.%m.%Y")


def get_full_date():
    """Получаем текущую дату в формате DD.MM.YYYY HH:MM."""
    return datetime.datetime.now().strftime("%d.%m.%Y %H:%M")


def get_platform_info():
    """Получаем информацию о платформе."""
    return f"{platform.system()} {platform.release()} {platform.machine()} и python {platform.python_version()} {platform.architecture()[0]}"


def test_exchange(config, test_log, session_id):
    """Тест exchange_server и exchange_client."""
    log("Старт теста exchange_server и exchange_client", test_log)
    bugs_list = []
    exchange_config = config.get('tests', {}).get('exchange_test', {})
    if not all(key in exchange_config for key in ['server_ip', 'client_ip', 'port']):
        log_error("Недостаточно параметров для теста exchange_test в config.json", test_log)
        bugs_list.append({"Bug": 1, "Traceback": "Недостаточно параметров в config.json"})
        return bugs_list

    server_ip = exchange_config['server_ip']
    client_ip = exchange_config['client_ip']
    port = exchange_config['port']

    try:
        server_thread = threading.Thread(target=run_exchange_server, args=(server_ip, port, client_ip, test_log))
        client_thread = threading.Thread(target=run_exchange_client, args=(client_ip, port, test_log))

        server_thread.start()
        time.sleep(0.5)  # Пауза чтобы сервер точно начал работать
        client_thread.start()

        server_thread.join()
        client_thread.join()

        log("Тест обмена ключами выполнен успешно", test_log)
    except Exception as e:
        log_error(f"Ошибка в тесте обмена ключами: {e}", test_log)
        log_traceback(test_log)
        bugs_list.append({
            "Bug": 1,
            "Traceback": f"{traceback.format_exc()}"
        })
    finally:
        log("Тест exchange_server и exchange_client завершён.", test_log)

    if not bugs_list:
        bugs_list.append("Не обнаружено.")

    return bugs_list


def run_exchange_server(server_ip, port, client_ip, test_log):
    """Запускает сервер для обмена ключами."""
    try:
        log("Запуск exchange_server", test_log)
        shared_key = exchange.exchange_server(server_ip, port, client_ip)
        log(f"Server shared key: {shared_key}", test_log)
    except Exception as e:
        log_error(f"Ошибка в exchange_server: {e}", test_log)
        log_traceback(test_log)
    finally:
        log("exchange_server завершён.", test_log)


def run_exchange_client(client_ip, port, test_log):
    """Запускает клиент для обмена ключами."""
    try:
        log("Запуск exchange_client", test_log)
        shared_key = exchange.exchange_client(client_ip, port)
        log(f"Client shared key: {shared_key}", test_log)
    except Exception as e:
        log_error(f"Ошибка в exchange_client: {e}", test_log)
        log_traceback(test_log)
    finally:
        log("exchange_client завершён.", test_log)


def speed_test(config, test_log, session_id):
    """Тест скорости генерации ключа."""
    log("Старт теста скорости генерации ключа", test_log)
    bugs_list = []
    speed_test_config = config.get('tests', {}).get('speed_test', {})
    if not all(key in speed_test_config for key in ['p_bits_start', 'p_bits_end']):
        log_error("Недостаточно параметров для теста speed_test в config.json", test_log)
        bugs_list.append({"Bug": 1, "Traceback": "Недостаточно параметров в config.json"})
        return bugs_list

    p_bits_start = speed_test_config['p_bits_start']
    p_bits_end = speed_test_config['p_bits_end']

    try:
        log(f"Тестирование скорости генерации секретного ключа (K) с размером p от {p_bits_start} до {p_bits_end} бит.", test_log)
        for bits in range(p_bits_start, p_bits_end + 1, 100):
            start_time = time.time()
            p, g = wrapper.generate_p_g(bits)
            a = wrapper.generate_a_or_b(p, g)
            A = wrapper.generate_A_or_B(p, g, a)
            b = wrapper.generate_a_or_b(p, g)
            B = wrapper.generate_A_or_B(p, g, b)
            shared_key_server = wrapper.generate_shared_key(B, p, g, a)
            shared_key_client = wrapper.generate_shared_key(A, p, g, b)
            end_time = time.time()
            execution_time = end_time - start_time
            log(f"Для p размера {bits} бит - Время выполнения: {execution_time:.6f} секунд", test_log)
            assert shared_key_server == shared_key_client
        log("Тест скорости генерации ключа выполнен успешно", test_log)

    except Exception as e:
        log_error(f"Ошибка в тесте скорости генерации ключа: {e}", test_log)
        log_traceback(test_log)
        bugs_list.append({
            "Bug": 1,
            "Traceback": f"{traceback.format_exc()}"
        })

    finally:
        log("Тест скорости генерации ключа завершён.", test_log)

    if not bugs_list:
        bugs_list.append("Не обнаружено.")
    return bugs_list


def test_primality(config, test_log, session_id):
    """Тест проверки простоты генерируемых p."""
    log("Старт теста проверки простоты p", test_log)
    bugs_list = []
    primality_config = config.get('tests', {}).get('primality_test', {})
    if not all(key in primality_config for key in ['p_bits_start', 'p_bits_end', 'iterations']):
        log_error("Недостаточно параметров для теста primality_test в config.json", test_log)
        bugs_list.append({"Bug": 1, "Traceback": "Недостаточно параметров в config.json"})
        return bugs_list

    p_bits_start = primality_config['p_bits_start']
    p_bits_end = primality_config['p_bits_end']
    iterations = primality_config['iterations']
    try:
        for bits in range(p_bits_start, p_bits_end + 1, 100):
            for _ in range(iterations):
                p, g = wrapper.generate_p_g(bits)
                if not is_prime(p):
                    log_error(f"Число {p} не является простым!", test_log)
                    bugs_list.append({
                        "Bug": 1,
                        "Traceback": f"Число {p} не является простым!"
                    })
        log("Тест проверки простоты p завершен", test_log)
    except Exception as e:
        log_error(f"Ошибка в тесте проверки простоты p: {e}", test_log)
        log_traceback(test_log)
        bugs_list.append({
            "Bug": 1,
            "Traceback": f"{traceback.format_exc()}"
        })
    finally:
        log("Тест проверки простоты p завершён.", test_log)

    if not bugs_list:
        bugs_list.append("Не обнаружено.")
    return bugs_list


def is_prime(n, k=5):  # Тест Миллера-Рабина
    """Проверка простоты числа."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    s = 0
    d = n - 1
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def test_stress(config, test_log, session_id):
    """Тест на стрессовую нагрузку."""
    log("Старт теста на стрессовую нагрузку", test_log)
    bugs_list = []
    stress_config = config.get('tests', {}).get('stress_test', {})
    if not all(key in stress_config for key in ['threads_count', 'key_size']):
        log_error("Недостаточно параметров для теста stress_test в config.json", test_log)
        bugs_list.append({"Bug": 1, "Traceback": "Недостаточно параметров в config.json"})
        return bugs_list

    threads_count = stress_config['threads_count']
    key_size = stress_config['key_size']
    threads = []
    results = []

    try:
        for i in range(threads_count):
            thread = threading.Thread(target=generate_keys, args=(key_size, results))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        log(f"Результаты генерации ключей: {results}", test_log)  # Вывод результатов

    except Exception as e:
        log_error(f"Ошибка в тесте на стрессовую нагрузку: {e}", test_log)
        log_traceback(test_log)
        bugs_list.append({
            "Bug": 1,
            "Traceback": f"{traceback.format_exc()}"
        })

    finally:
        log("Тест на стрессовую нагрузку завершён.", test_log)

    if not bugs_list:
        bugs_list.append("Не обнаружено.")
    return bugs_list


def generate_keys(key_size, results):
    """Генерирует ключи и добавляет время генерации в результаты."""
    start_time = time.time()
    p, g = wrapper.generate_p_g(key_size)
    a = wrapper.generate_a_or_b(p, g)
    A = wrapper.generate_A_or_B(p, g, a)
    b = wrapper.generate_a_or_b(p, g)
    B = wrapper.generate_A_or_B(p, g, b)
    shared_key_server = wrapper.generate_shared_key(B, p, g, a)
    shared_key_client = wrapper.generate_shared_key(A, p, g, b)
    end_time = time.time()
    execution_time = end_time - start_time
    results.append(execution_time)


def test_invalid_input(config, test_log, session_id):
    """Тест на неверные входные данные."""
    log("Старт теста на неверные входные данные", test_log)
    bugs_list = []
    invalid_input_config = config.get('tests', {}).get('invalid_input_test', {})
    if not all(key in invalid_input_config for key in ['p_invalid', 'g_invalid', 'bits_invalid']):
        log_error("Недостаточно параметров для теста invalid_input_test в config.json", test_log)
        bugs_list.append({"Bug": 1, "Traceback": "Недостаточно параметров в config.json"})
        return bugs_list

    p_invalid = invalid_input_config['p_invalid']
    g_invalid = invalid_input_config['g_invalid']
    bits_invalid = invalid_input_config['bits_invalid']

    try:
        p, g = wrapper.generate_p_g(2048)
        try:
            a = wrapper.generate_a_or_b(int(p_invalid), g)
            bugs_list.append({"Bug": 1, "Traceback": "Не сработал контроль на неверный тип p"})
        except Exception as e:
            log(f"Тест на неверный p ({p_invalid}) пройден: {e}", test_log)

        try:
            a = wrapper.generate_a_or_b(p, int(g_invalid))
            bugs_list.append({"Bug": 2, "Traceback": "Не сработал контроль на неверный тип g"})
        except Exception as e:
            log(f"Тест на неверный g ({g_invalid}) пройден: {e}", test_log)

        try:
            p, g = wrapper.generate_p_g(int(bits_invalid))
            bugs_list.append({"Bug": 3, "Traceback": "Не сработал контроль на неверный тип bits"})
        except Exception as e:
            log(f"Тест на неверные bits ({bits_invalid}) пройден: {e}", test_log)

        log("Тест на неверные входные данные завершен", test_log)
    except Exception as e:
        log_error(f"Ошибка в тесте на неверные входные данные: {e}", test_log)
        log_traceback(test_log)
        bugs_list.append({
            "Bug": 1,
            "Traceback": f"{traceback.format_exc()}"
        })
    finally:
        log("Тест на неверные входные данные завершён.", test_log)

    if not bugs_list:
        bugs_list.append("Не обнаружено.")
    return bugs_list


def test_hash_shared_key(config, test_log, session_id):
    """Тест функции hash_shared_key."""
    log("Старт теста функции hash_shared_key", test_log)
    bugs_list = []

    try:
        p, g = wrapper.generate_p_g(2048)
        a = wrapper.generate_a_or_b(p, g)
        A = wrapper.generate_A_or_B(p, g, a)
        b = wrapper.generate_a_or_b(p, g)
        B = wrapper.generate_A_or_B(p, g, b)
        shared_key1 = wrapper.generate_shared_key(B, p, g, a)
        shared_key2 = wrapper.generate_shared_key(A, p, g, b)

        assert shared_key1 == shared_key2
        log("Тест функции hash_shared_key завершен", test_log)
    except AssertionError:
        log_error("Хешированные ключи не совпадают!", test_log)
        bugs_list.append({"Bug": 1, "Traceback": "Хешированные ключи не совпадают!"})
    except Exception as e:
        log_error(f"Ошибка в тесте функции hash_shared_key: {e}", test_log)
        log_traceback(test_log)
        bugs_list.append({
            "Bug": 1,
            "Traceback": f"{traceback.format_exc()}"
        })
    finally:
        log("Тест функции hash_shared_key завершён.", test_log)

    if not bugs_list:
        bugs_list.append("Не обнаружено.")
    return bugs_list


def test_memory_leak(config, test_log, session_id):
    """Тест на утечку памяти."""
    log("Старт теста на утечку памяти", test_log)
    bugs_list = []
    memory_leak_config = config.get('tests', {}).get('memory_leak_test', {})
    if not all(key in memory_leak_config for key in ['iterations', 'key_size', 'memory_threshold']):
         log_error("Недостаточно параметров для теста memory_leak_test в config.json", test_log)
         bugs_list.append({"Bug": 1, "Traceback": "Недостаточно параметров в config.json"})
         return bugs_list

    iterations = memory_leak_config['iterations']
    key_size = memory_leak_config['key_size']
    memory_threshold = memory_leak_config['memory_threshold']
    tracemalloc.start()
    try:
      
        snapshots = []
        for i in range(iterations):
            p, g = wrapper.generate_p_g(key_size)
            a = wrapper.generate_a_or_b(p, g)
            A = wrapper.generate_A_or_B(p, g, a)
            b = wrapper.generate_a_or_b(p, g)
            B = wrapper.generate_A_or_B(p, g, b)
            shared_key_server = wrapper.generate_shared_key(B, p, g, a)
            shared_key_client = wrapper.generate_shared_key(A, p, g, b)

            snapshots.append(tracemalloc.take_snapshot())
            if i > 0:
              top_stats = snapshots[i].compare_to(snapshots[i-1], 'lineno')
              total_diff = sum(stat.size_diff for stat in top_stats)
              if total_diff > memory_threshold:
                  log_error(f"Обнаружена утечка памяти на итерации {i}. Общий рост: {total_diff / 1024:.2f} КБ", test_log)
                  bugs_list.append({
                    "Bug": 1,
                    "Traceback": f"Обнаружена утечка памяти на итерации {i}. Общий рост: {total_diff / 1024:.2f} КБ"
                    })

        log("Тест на утечку памяти завершён.", test_log)
    except Exception as e:
      log_error(f"Ошибка в тесте на утечку памяти: {e}", test_log)
      log_traceback(test_log)
      bugs_list.append({
        "Bug": 1,
        "Traceback": f"{traceback.format_exc()}"
      })
    finally:
        tracemalloc.stop()
        log("Тест на утечку памяти завершён.", test_log)

    if not bugs_list:
        bugs_list.append("Не обнаружено.")
    return bugs_list

def run_test(test_name, config, session_id, test_log):
    """Запускает конкретный тест."""
    test_functions = {
        "exchange_test": test_exchange,
        "speed_test": speed_test,
        "primality_test": test_primality,
        "stress_test": test_stress,
        "invalid_input_test": test_invalid_input,
        "hash_shared_key_test": test_hash_shared_key,
        "memory_leak_test": test_memory_leak
    }

    test_function = test_functions.get(test_name)
    if test_function:
        return test_function(config, test_log, session_id)
    else:
        log_error(f"Неизвестный тест: {test_name}", test_log)
        return ["Неизвестный тест"]


def create_test_log(session_id, test_name):
    """Создает лог-файл для теста."""
    date_str = get_current_date()
    log_file_name = f"{test_name}_{date_str}.log"
    log_file_path = os.path.join(LOG_DIR, log_file_name)
    return open(log_file_path, "w", encoding="utf-8")


def write_test_journal(session_id, config, test_results):
    """Записывает результаты тестирования в журнал."""
    with open(TEST_JOURNAL, "a", encoding="utf-8") as journal:

        start_date = get_full_date()

        journal.write(f"\nТестирование {start_date}\n")
        journal.write(f"Версия {config['version']}\n")
        journal.write(f"Тестирование производится на {get_platform_info()}\n")

        for test_name, result in test_results.items():
            journal.write(f"Тестирование функций {test_name} из diffiehellmanlib\n")
            journal.write(f"Bugs list:\n")
            for bug in result:
                if bug == "Не обнаружено.":
                    journal.write(f"\t- {bug}\n")
                else:
                    journal.write(f"\t- Bug {bug['Bug']}:\n")
                    journal.write(f"\t\t- Traceback (most recent call last):\n")
                    journal.write(f"\t\t\t{bug['Traceback']}\n")
                    journal.flush()
            log_file_name = f"{test_name}_{get_current_date()}.log"
            journal.write(f"Логи теста - {os.path.join(LOG_DIR, log_file_name)}\n")

        journal.write("\nРезультат сессии теста.\n")
        if any(result != ["Не обнаружено."] for result in test_results.values()):
            journal.write("Что нужно поменять:\n")
            for test_name, result in test_results.items():
                for bug in result:
                    if bug != "Не обнаружено.":
                        journal.write(f"   -  {bug['Bug']} {test_name} \n")

        else:
            journal.write("Баги не обнаружены.\n")

        journal.write("Конец записи тестирования.\n")


def load_config():
    """Загружает конфигурацию из config.json."""
    try:
        with open("config.json", "r") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        print("Ошибка: Файл config.json не найден.")
        exit(1)
    except json.JSONDecodeError:
        print("Ошибка: Неверный формат файла config.json.")
        exit(1)


def main():
    """Главная функция для запуска тестов."""
    create_log_dir()
    config = load_config()
    session_id = config.get("session_id", "default_session")
    tests_to_run = [test for test in config['tests'] if config['tests'][test]['enabled']]
    test_results = {}

    with open(TEST_JOURNAL, "a", encoding="utf-8") as journal:
        journal.write(f"\nЖурнал тестов старт {get_full_date()}\n")

    if config['multithreading']:
      with tqdm(total=len(tests_to_run), desc="Выполнение тестов", dynamic_ncols=True) as pbar:
          threads = []
          for test_name in tests_to_run:
            test_log = create_test_log(session_id, test_name)
            log(f"Запуск теста: {test_name}", test_log)

            thread = threading.Thread(target=run_test_wrapper, args=(test_name, config, session_id, test_log, test_results, pbar))
            threads.append(thread)
            thread.start()

          for thread in threads:
            thread.join()
    else:
        for test_name in tqdm(tests_to_run, desc="Выполнение тестов", dynamic_ncols=True):
          test_log = create_test_log(session_id, test_name)
          log(f"Запуск теста: {test_name}", test_log)
          test_results[test_name] = run_test(test_name, config, session_id, test_log)


    write_test_journal(session_id, config, test_results)
    print("Тестирование завершено. Результаты в test_journal.log")


def run_test_wrapper(test_name, config, session_id, test_log, test_results, pbar):
    """Обертка для запуска тестов в потоках."""
    test_results[test_name] = run_test(test_name, config, session_id, test_log)
    pbar.update(1)


if __name__ == "__main__":
    main()