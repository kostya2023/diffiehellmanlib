# DiffieHellmanLib

Библиотека для генерации параметров протокола Диффи-Хеллмана (Diffie-Hellman).

## Возможности

*   Генерация криптографически безопасных параметров `p` и `g`.
*   Генерация приватных ключей `a` и `b`.
*   Генерация публичных ключей `A` и `B`.
*   Вычисление общего секрета на основе публичных и приватных ключей.

## Как оно работает

Основные функции библиотеки реализованы на языке Rust для повышения производительности. Для ускорения генерации простых чисел `p` используется кэш, хранящий сгенерированные значения с меткой времени. Если срок хранения (1 час) истек, генерируется новое значение `p`, а старое удаляется.

Принцип работы Diffie-Hellman:

1.  Обе стороны договариваются о согласовании общих публичных параметров: большого простого числа `p` и примитивного корня по модулю `p` - `g`. Размер простого числа `p` напрямую влияет на безопасность алгоритма: чем больше `p`, тем сложнее его взломать. В библиотеке установлено ограничение на размер `p`: от 512 до 8192 бит. Рекомендуемый размер `p` - 2048 бит. На моей системе (Intel Core i3-7gen, 6 ГБ ОЗУ) генерация `p` занимает около 6-8 секунд, но благодаря кэшированию удается достичь прироста скорости до 21 раза (результаты могут отличаться на других системах).
2.  Каждая сторона генерирует свой приватный ключ (`a` или `b`) – случайное число в диапазоне от 1 до `p - 1`, используя криптографически безопасный генератор случайных чисел.
3.  Каждая сторона вычисляет свой публичный ключ:
    *   Алиса: `A = g^a mod p`
    *   Боб: `B = g^b mod p`
4.  Стороны обмениваются публичными ключами.
5.  Каждая сторона вычисляет общий секрет `K`:
    *   Алиса: `K = B^a mod p`
    *   Боб: `K = A^b mod p`

В результате обе стороны получают одинаковый общий секрет `K`, который далее может быть использован для генерации ключей шифрования и векторов инициализации. Для повышения безопасности, `K` проходит хеширование SHA-256 и HKDF с использованием встроенной соли.

## Безопасность

*   **Важно!** При передаче сгенерированных параметров (`p` и `g`) по сети используйте надежные механизмы аутентификации и проверки целостности данных (например, цифровые подписи, HMAC и т.п.).
*   Размер `p` в 512 бит следует использовать **только для тестирования**. Для реальных задач рекомендуется использовать 1024 или 2048 бит.
*   При использовании кэширования учитывайте, что скомпрометированное значение `p` в кэше может снизить безопасность.

## Установка

1.  Убедитесь, что у вас установлены Rust и Cargo. Вы можете установить их с помощью [rustup](https://rustup.rs/).
2.  Убедитесь, что у вас установлен Python 3.7 или выше.

3.  Установите библиотеку с помощью pip:

    ```bash
    pip install diffiehellmanlib
    ```

    (Для Linux x64-x86 доступны готовые wheel-пакеты).

4.  Если установка через pip не удалась, можно установить из исходников:

    ```bash
    git clone https://github.com/kostya2023/diffiehellmanlib.git
    cd diffiehellmanlib
    python -m venv venv       # Создание виртуального окружения
    source venv/bin/activate   # Активация виртуального окружения (Linux/macOS)
    .\venv\Scripts\activate    # Активация виртуального окружения (Windows)
    pip install maturin       # Установка maturin - инструмента для сборки Python-расширений на Rust
    maturin build --release   # Сборка расширения в режиме release
    pip install ./target/wheels/diffiehellmanlib*.whl  # Установка собранного wheel-файла
    ```

## Использование

```python
import diffiehellmanlib as dh

# Генерация криптографических параметров
p, g = dh.generate_p_g(1024)
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
shared_key_alice = dh.generate_shared_key(B, p, a)
shared_key_bob = dh.generate_shared_key(A, p, b)

print(f"\nРезультат:\nКлюч Алисы: {shared_key_alice}\nКлюч Боба:   {shared_key_bob}")
```

## Лицензия
 - “Буду рад, если вы укажете меня как автора при использовании этого софта.” =)
 - [MIT](https://choosealicense.com/licenses/mit/)



## Авторы

- [kostya2023](https://github.com/kostya2023)

