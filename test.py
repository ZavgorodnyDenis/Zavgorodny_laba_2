Задание №5. Передача файлов по TCP.
Описание: Реализуйте передачу файла от клиента к серверу или наоборот с проверкой целостности (например, контрольная сумма).
Функциональность разработки должна включать:
1. Разбиение и передача файла по частям.
2. Проверка целостности данных.
3. Обработка ошибок и повторов.
4. Реализация простого HTTP-сервера на сокетах.

Сервер передачи файлов:
import socket
import hashlib
import os

HOST = '127.0.0.1'
PORT = 65432
BUFFER_SIZE = 4096 # Размер буфера для чтения/записи файла

def calculate_checksum(filepath):
    """Вычисляет SHA256 контрольную сумму файла."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(BUFFER_SIZE)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

def file_transfer_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Сервер передачи файлов запущен на {HOST}:{PORT}")

        conn, addr = s.accept()
        with conn:
            print(f"Подключено клиентом: {addr}")
            
            # 1. Принимаем имя файла и контрольную сумму
            file_info = conn.recv(1024).decode('utf-8')
            filename, client_checksum = file_info.split(':')
            filename = os.path.basename(filename) # Извлекаем только имя файла
            filepath = os.path.join("server_received_files", filename)

            os.makedirs(os.path.dirname(filepath), exist_ok=True) # Создаем директорию, если ее нет

            print(f"Ожидаю файл: {filename} с контрольной суммой: {client_checksum}")

            # 2. Принимаем файл
            received_bytes = 0
            with open(filepath, 'wb') as f:
                while True:
                    data = conn.recv(BUFFER_SIZE)
                    if not data:
                        break # Файл полностью передан
                    f.write(data)
                    received_bytes += len(data)
                    print(f"\rПолучено {received_bytes} байт...", end="")
            print(f"\nПолучение файла {filename} завершено.")

            # 3. Проверяем целостность
            server_checksum = calculate_checksum(filepath)
            if server_checksum == client_checksum:
                response = "Файл успешно получен и целостность подтверждена."
                print(response)
                conn.sendall(response.encode('utf-8'))
            else:
                response = "Ошибка: контрольные суммы не совпадают. Файл может быть поврежден."
                print(response)
                conn.sendall(response.encode('utf-8'))

if __name__ == '__main__':
    file_transfer_server()

Клиент передачи файлов:
import socket
import hashlib
import os
import time

HOST = '127.0.0.1'
PORT = 65432
BUFFER_SIZE = 4096

def calculate_checksum(filepath):
    """Вычисляет SHA256 контрольную сумму файла."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(BUFFER_SIZE)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

def file_transfer_client():
    filename_to_send = input("Введите путь к файлу для отправки: ")
    if not os.path.exists(filename_to_send):
        print(f"Ошибка: Файл '{filename_to_send}' не найден.")
        return

    checksum = calculate_checksum(filename_to_send)
    print(f"Вычисленная контрольная сумма файла: {checksum}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print(f"Подключено к серверу {HOST}:{PORT}")

            # 1. Отправляем имя файла и контрольную сумму
            file_info = f"{os.path.basename(filename_to_send)}:{checksum}"
            s.sendall(file_info.encode('utf-8'))
            time.sleep(0.1) # Даем серверу немного времени на обработку

            # 2. Отправляем файл
            sent_bytes = 0
            file_size = os.path.getsize(filename_to_send)
            with open(filename_to_send, 'rb') as f:
                while True:
                    chunk = f.read(BUFFER_SIZE)
                    if not chunk:
                        break # Конец файла
                    s.sendall(chunk)
                    sent_bytes += len(chunk)
                    print(f"\rОтправлено {sent_bytes}/{file_size} байт ({sent_bytes/file_size*100:.2f}%)", end="")
            print(f"\nОтправка файла '{filename_to_send}' завершена.")

            # 3. Получаем ответ от сервера о проверке целостности
            response = s.recv(1024).decode('utf-8')
            print(f"Ответ сервера: {response}")

        except ConnectionRefusedError:
            print("Не удалось подключиться к серверу. Убедитесь, что сервер запущен.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
    print("Соединение закрыто.")

if __name__ == '__main__':
    file_transfer_client()

Задание №6. Сервер вычислений.
Описание: Сервер получает запросы на вычисление (например, факториала или арифметического выражения) и возвращает результат клиенту.
Функциональность разработки должна включать:
1. Парсинг и обработка запросов.
2. Корректные вычисления.
3. Ошибки обработки неверных данных.
4. Реализация простого HTTP-сервера на сокетах.

Сервер вычислений:
import socket
import threading
import math

HOST = '127.0.0.1'
PORT = 65432

def calculate_expression(expression):
    """Безопасно вычисляет математическое выражение."""
    try:
        # Ограничиваем функции, которые можно использовать в eval()
        # Для более сложных случаев, используйте парсер выражений (ast.literal_eval)
        # или библиотеку для безопасных вычислений.
        allowed_functions = {
            'abs': abs, 'round': round, 'sum': sum,
            'max': max, 'min': min,
            'sqrt': math.sqrt, 'pow': math.pow,
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'log': math.log, 'log10': math.log10,
            'pi': math.pi, 'e': math.e
        }
        
        # Запрещаем доступ к __builtins__ и другим потенциально опасным объектам
        # Тем не менее, eval() всегда следует использовать с осторожностью.
        # Для продакшн-систем рекомендуется использовать специализированные библиотеки.
        return str(eval(expression, {"__builtins__": None}, allowed_functions))
    except (SyntaxError, NameError, TypeError, ValueError) as e:
        return f"Ошибка синтаксиса или вычисления: {e}"
    except Exception as e:
        return f"Неизвестная ошибка: {e}"

def calculate_factorial(n_str):
    """Вычисляет факториал числа."""
    try:
        n = int(n_str)
        if n < 0:
            return "Факториал определен только для неотрицательных чисел."
        return str(math.factorial(n))
    except ValueError:
        return "Неверный ввод: требуется целое число для факториала."
    except OverflowError:
        return "Число слишком велико для вычисления факториала."

def handle_client(conn, addr):
    print(f"Подключено клиентом: {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            request = data.decode('utf-8').strip()
            print(f"Получено от {addr}: {request}")

            response = ""
            if request.lower().startswith("факториал "):
                num_str = request[len("факториал "):].strip()
                response = calculate_factorial(num_str)
            elif request.lower().startswith("вычисли "):
                expression = request[len("вычисли "):].strip()
                response = calculate_expression(expression)
            else:
                response = "Неизвестная команда. Используйте 'факториал <число>' или 'вычисли <выражение>'."
            
            conn.sendall(response.encode('utf-8'))
            print(f"Отправлено обратно клиенту {addr}: {response}")
    except ConnectionResetError:
        print(f"Клиент {addr} принудительно разорвал соединение.")
    except Exception as e:
        print(f"Ошибка при работе с клиентом {addr}: {e}")
    finally:
        conn.close()
        print(f"Соединение с {addr} закрыто.")

def calculation_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Сервер вычислений запущен на {HOST}:{PORT}")
        while True:
            try:
                conn, addr = s.accept()
                client_handler = threading.Thread(target=handle_client, args=(conn, addr))
                client_handler.daemon = True
                client_handler.start()
            except KeyboardInterrupt:
                print("Сервер остановлен пользователем.")
                break
            except Exception as e:
                print(f"Ошибка принятия соединения: {e}")
    print("Сервер завершил работу.")

if __name__ == '__main__':
    calculation_server()

Клиент сервера вычислений:
import socket

HOST = '127.0.0.1'
PORT = 65432

def calculation_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print(f"Подключено к серверу вычислений {HOST}:{PORT}")
            while True:
                message = input("Введите запрос (например, 'факториал 5' или 'вычисли 2+2*3', 'exit' для выхода): ")
                if message.lower() == 'exit':
                    break
                s.sendall(message.encode('utf-8'))
                data = s.recv(1024)
                print(f"Результат от сервера: {data.decode('utf-8')}")
        except ConnectionRefusedError:
            print("Не удалось подключиться к серверу. Убедитесь, что сервер запущен.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
    print("Соединение закрыто.")

if __name__ == '__main__':
    calculation_client()

Задание №7. Неблокирующий сервер с селектором.
Описание: Реализуйте TCP сервер с использованием неблокирующих сокетов и механизма селекторов для обслуживания множества клиентов.
Функциональность разработки должна включать:
1. Применение селектора или аналогичного механизма.
2. Обработка множества соединений без блокировок.
3. Стабильная работа при нагрузке.
4. Реализация простого HTTP-сервера на сокетах.

Неблокирующий TCP Эхо-сервер с selectors:
import socket
import selectors
import types # Для хранения информации о данных клиента

HOST = '127.0.0.1'
PORT = 65432

# Создаем объект селектора
sel = selectors.DefaultSelector()

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Должно быть готово
    conn.setblocking(False) # Устанавливаем сокет как неблокирующий
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    # Регистрируем клиентский сокет для чтения
    events = selectors.EVENT_READ
    sel.register(conn, events, data=data)
    print(f"Принято соединение от {addr}")

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Должно быть готово
        if recv_data:
            data.outb += recv_data # Добавляем полученные данные в буфер отправки
            print(f"Получено от {data.addr}: {recv_data.decode('utf-8')}")
            # После получения данных, регистрируем сокет на запись (чтобы отправить эхо)
            sel.modify(sock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data)
        else:
            print(f"Закрытие соединения с {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Отправка эхо-ответа {len(data.outb)} байт для {data.addr}")
            sent = sock.send(data.outb)  # Должно быть готово
            data.outb = data.outb[sent:] # Удаляем отправленные данные из буфера
            # Если все данные отправлены, перестаем мониторить запись
            if not data.outb:
                sel.modify(sock, selectors.EVENT_READ, data=data)

def non_blocking_echo_server():
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((HOST, PORT))
    lsock.listen()
    print(f"Неблокирующий TCP Эхо-сервер запущен на {HOST}:{PORT}")
    lsock.setblocking(False) # Устанавливаем слушающий сокет как неблокирующий
    
    # Регистрируем слушающий сокет для мониторинга событий чтения
    sel.register(lsock, selectors.EVENT_READ, data=None)

    try:
        while True:
            # Блокируется до тех пор, пока какой-либо зарегистрированный сокет не будет готов
            events = sel.select(timeout=None) # timeout=None - блокируется бесконечно
            for key, mask in events:
                if key.data is None: # Это наш слушающий сокет
                    accept_wrapper(key.fileobj)
                else: # Это клиентский сокет
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("Сервер остановлен пользователем.")
    finally:
        sel.close()
        lsock.close()
        print("Сервер завершил работу.")

if __name__ == '__main__':
    non_blocking_echo_server()

TCP Эхо-клиент:
import socket

HOST = '127.0.0.1'
PORT = 65432

def echo_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print(f"Подключено к серверу {HOST}:{PORT}")
            while True:
                message = input("Введите сообщение для сервера (или 'exit' для выхода): ")
                if message.lower() == 'exit':
                    break
                s.sendall(message.encode('utf-8'))
                data = s.recv(1024)
                print(f"Получено от сервера: {data.decode('utf-8')}")
        except ConnectionRefusedError:
            print("Не удалось подключиться к серверу. Убедитесь, что сервер запущен.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
    print("Соединение закрыто.")

if __name__ == '__main__':
    echo_client()

Простой HTTP-сервер на сокетах:
import socket

HOST_HTTP = '127.0.0.1'
PORT_HTTP = 8080

html_response = b"""\
HTTP/1.1 200 OK\r\n
Content-Type: text/html; charset=utf-8\r\n
Content-Length: 70\r\n
\r\n
<html><head><title>Test</title></head><body><h1>Hello, HTTP!</h1></body></html>
"""

http_404_response = b"""\
HTTP/1.1 404 Not Found\r\n
Content-Type: text/html; charset=utf-8\r\n
Content-Length: 58\r\n
\r\n
<html><head><title>404</title></head><body><h1>Not Found</h1></body></html>
"""

def simple_http_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST_HTTP, PORT_HTTP))
        s.listen(1)
        print(f"HTTP Server запущен на http://{HOST_HTTP}:{PORT_HTTP}/")
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"HTTP-запрос от {addr}")
                try:
                    request = conn.recv(1024).decode('utf-8')
                    if not request:
                        continue
                    print(f"Запрос:\n{request}")

                    if request.startswith('GET / HTTP/1.1') or request.startswith('GET / HTTP/1.0'):
                        conn.sendall(html_response)
                    else:
                        conn.sendall(http_404_response)
                except Exception as e:
                    print(f"Ошибка обработки HTTP-запроса от {addr}: {e}")
                finally:
                    conn.close() # Безопасное закрытие соединения

if __name__ == '__main__':
    simple_http_server()
