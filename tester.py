import os

# Функция для вывода структуры папок и файлов
def print_directory_structure(path, prefix=""):
    # Игнорируем папку .git
    if os.path.basename(path) == ".git":
        return

    if os.path.isfile(path):
        print(prefix + "└── " + os.path.basename(path))
        return

    print(prefix + "├── " + os.path.basename(path) + "/")
    items = os.listdir(path)
    # Фильтруем элементы, исключая папку .git
    items = [item for item in items if item != ".git"]
    for i, item in enumerate(items):
        item_path = os.path.join(path, item)
        if i == len(items) - 1:
            print_directory_structure(item_path, prefix + "    ")
        else:
            print_directory_structure(item_path, prefix + "│   ")

# Функция для вывода содержимого файлов
def print_file_contents(path):
    # Игнорируем папку .git
    if os.path.basename(path) == ".git":
        return

    if os.path.isfile(path):
        print(f"\nСодержимое файла {path}:")
        with open(path, "r", encoding="utf-8") as file:
            print(file.read())
    elif os.path.isdir(path):
        for item in os.listdir(path):
            # Фильтруем элементы, исключая папку .git
            if item == ".git":
                continue
            item_path = os.path.join(path, item)
            print_file_contents(item_path)

# Основная логика
if __name__ == "__main__":
    current_directory = "."
    
    # Выводим структуру
    print("Структура папок и файлов:")
    print_directory_structure(current_directory)
    
    # Выводим содержимое файлов
    print("\nСодержимое файлов:")
    print_file_contents(current_directory)