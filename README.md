# Diffie - Hellman Python/C++ Library

## Описание
Эта библиотека реализует криптографический протокол **Diffie-Hellman** для безопасного обмена ключами через незащищённый канал. 
Она использует C++ для высокой скорости генерации больших простых чисел и Python-обёртку (`wrapper`) для упрощённой интеграции.

## Основные возможности
- **Генерация параметров**: простое число \( p \), основание \( g \), приватные ключи \( a, b \), публичные ключи \( A, B \).
- **Обмен ключами**: функции для организации серверной и клиентской части через сокеты.
- **Поддержка хэширования**: автоматическое хэширование общего ключа для безопасности.
- **Кроссплатформенность**: поддержка Windows, Linux, и архитектур x86, x64, ARMv7, ARM64.

---

## Установка
Для установки библиотеки используйте:

```bash
pip install diffiehellmanlib
```

---

## Использование
### Импорт библиотеки
```python
from diffiehellmanlib import wrapper
```

### Пример 1: Генерация параметров
Генерация \( p \) и \( g \):
```python
p, g = wrapper.generate_p_g(2048)
print(f"Generated p: {p}, g: {g}")
```

### Пример 2: Генерация публичного и приватного ключей
```python
a = wrapper.generate_a_or_b(p, g)
A = wrapper.generate_A_or_B(p, g, a)
print(f"Private key (a): {a}, Public key (A): {A}")
```

### Пример 3: Генерация общего ключа
После обмена \( A \) и \( B \):
```python
shared_key = wrapper.generate_shared_key(B, p, g, a)
print(f"Shared key: {shared_key}")
```

---

## **Обмен ключами через сокеты**

*Функциональность доступна с версии 2.0*

Библиотека предоставляет функции `exchange_server` и `exchange_client` для безопасного обмена ключами через сеть.

### **Пример использования**
#### **Сервер**
```python
from diffiehellmanlib.exchange import exchange

shared_key = exchange.exchange_server("0.0.0.0", 5000, "127.0.0.1")
print(f"Shared key: {shared_key}")
```
- **IP**: `"0.0.0.0"` позволяет принимать соединения на всех интерфейсах.
- **Порт**: `5000` — порт для ожидания соединений.
- **Таргет IP**: `"127.0.0.1"` — IP-адрес клиента, с которым разрешено соединение.

#### **Клиент**
```python
from diffiehellmanlib.exchange import exchange

shared_key = exchange.exchange_client("127.0.0.1", 5000)
print(f"Shared key: {shared_key}")
```
- **Таргет IP сервера**: `"127.0.0.1"`.
- **Порт сервера**: `5000`.

### Алгоритм работы
1. **Сервер**
   - Генерирует \( p, g \), приватный ключ \( a \), и публичный ключ \( A \).
   - Отправляет их клиенту в формате JSON вместе с хэшами.
2. **Клиент**
   - Проверяет корректность данных и генерирует \( b \), \( B \).
   - Отправляет публичный ключ \( B \) серверу.
3. **Общий ключ**
   - Сервер и клиент рассчитывают общий ключ \( K \) с использованием своих приватных и чужих публичных ключей.

#### Формат сообщений
Сообщения передаются в формате JSON:
- От сервера:
  ```json
  {
      "error": false,
      "numbers": {"p": p, "g": g, "A": A},
      "hash": {"p": "hash_p", "g": "hash_g", "A": "hash_A"},
      "timeset": timeset
  }
  ```
- От клиента:
  ```json
  {
      "error": false,
      "numbers": {"B": B},
      "hashes": {"B": "hash_b"},
      "timeset": timeset
  }
  ```

---

## Примеры полного использования (Ручной режим)

### Alice (Серверная часть)
```python
from diffiehellmanlib import wrapper

p, g = wrapper.generate_p_g(2048)
a = wrapper.generate_a_or_b(p, g)
A = wrapper.generate_A_or_B(p, g, a)

# Отправляем p, g, A Bob-у и получаем B
shared_key = wrapper.generate_shared_key(B, p, g, a)
print(f"Shared key: {shared_key}")
```

### Bob (Клиентская часть)
```python
from diffiehellmanlib import wrapper

# Получаем p, g, A от Alice
b = wrapper.generate_a_or_b(p, g)
B = wrapper.generate_A_or_B(p, g, b)

# Отправляем B Alice и рассчитываем общий ключ
shared_key = wrapper.generate_shared_key(A, p, g, b)
print(f"Shared key: {shared_key}")
```
---
## Пример полного использования (Автоматический режим)

### Alice (Серверная часть)
```python
from diffiehellmanlib.exchange import exchange

shared_key = exchange.exchange_server(IP_alice, port, IP_bob)

print(f"Shared key: {shared_key}")
```

### Bob (Клиентская часть)
```python
from diffiehellmanlib.exchange import exchange

shared_key = exchange.exchange_client(IP_alice, port)

print(f"Shared key: {shared_key}")
```
---

## Лицензия

[MIT License](https://choosealicense.com/licenses/mit/)

---

## Авторы
- [kostya2023](https://github.com/kostya2023)
