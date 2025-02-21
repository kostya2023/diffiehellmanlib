import diffiehellmanlib as dh
import time

def test():
    # Генерация криптографических параметров
    p, g = dh.generate_p_g(2048)
    print(f"p (первые 20 символов): {p[:20]}...")
    print(f"g: {g}")

    # Генерация ключей Алисы
    a = dh.generate_a_or_b(p)
    A = dh.generate_A_or_B(p, g, a)
    print(f"\nАлиса:\nСекретный ключ (начало): {a[:10]}...\nПубличный ключ (начало): {A[:20]}...")

    # Генерация ключей Боба
    b = dh.generate_a_or_b(p)
    B = dh.generate_A_or_B(p, g, b)
    print(f"\nБоб:\nСекретный ключ (начало): {b[:10]}...\nПубличный ключ (начало): {B[:20]}...")

    # Вычисление общего секрета
    start_time = time.perf_counter()
    shared_key_alice = dh.generate_shared_key(B, p, a)
    shared_key_bob = dh.generate_shared_key(A, p, b)
    keygen_time = (time.perf_counter() - start_time) * 1000  # Конвертация в миллисекунды

    print(f"\nРезультат:\nКлюч Алисы: {shared_key_alice}\nКлюч Боба:   {shared_key_bob}")
    print(f"Секреты совпадают: {shared_key_alice == shared_key_bob}")
    
    return keygen_time

def main():
    total_start = time.perf_counter()
    keygen_time = test()
    total_time = (time.perf_counter() - total_start) * 1000  # Конвертация в миллисекунды
    
    print(f"\nВремя генерации ключей: {keygen_time:.2f} ms")
    print(f"Общее время выполнения: {total_time:.2f} ms")

if __name__ == "__main__":
    main()


# import os

# IGNORED_DIRS = {"target", "venv", ".git"}

# def print_tree(directory, prefix=""):
#     entries = [e for e in os.listdir(directory) if e not in IGNORED_DIRS]
#     entries.sort()
    
#     for i, entry in enumerate(entries):
#         path = os.path.join(directory, entry)
#         is_last = (i == len(entries) - 1)
#         connector = "└── " if is_last else "├── "
        
#         if os.path.isdir(path):
#             print(prefix + connector + entry + "/")
#             new_prefix = prefix + ("    " if is_last else "│   ")
#             print_tree(path, new_prefix)
#         else:
#             print(prefix + connector + entry)

# def print_file_contents(directory):
#     for root, _, files in os.walk(directory):
#         if any(ignored in root.split(os.sep) for ignored in IGNORED_DIRS):
#             continue
        
#         for file in files:
#             file_path = os.path.join(root, file)
#             print(f"\n=== {file_path} ===\n")
#             try:
#                 with open(file_path, "r", encoding="utf-8") as f:
#                     print(f.read())
#             except Exception as e:
#                 print(f"[Ошибка чтения файла: {e}]")

# if __name__ == "__main__":
#     start_dir = os.getcwd()
#     print("Файловая структура:\n")
#     print_tree(start_dir)
#     print("\nСодержимое файлов:\n")
#     print_file_contents(start_dir)
