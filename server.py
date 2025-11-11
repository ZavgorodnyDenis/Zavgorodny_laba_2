import socket
import threading
import urllib.parse

HOST = '127.0.0.1'
PORT = 8080

def factorial(n):
    if n < 0:
        raise ValueError("Факториал для отрицательных чисел не определён")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def evaluate_expression(expr):
    allowed_chars = "0123456789+-*/(). "
    if any(c not in allowed_chars for c in expr):
        raise ValueError("Неверное выражение")
    return eval(expr, {"__builtins__": None}, {})

def handle_client(conn, addr):
    try:
        data = conn.recv(1024).decode('utf-8')
        if not data:
            conn.close()
            return
        request_line = data.splitlines()[0]
        parts = request_line.split()
        if len(parts) < 2:
            response = "HTTP/1.1 400 Bad Request\r\n\r\nНеверный запрос"
            conn.sendall(response.encode())
            conn.close()
            return
        method, path = parts[0], parts[1]
        if method != 'GET':
            response = "HTTP/1.1 405 Method Not Allowed\r\n\r\nТолько GET поддерживается"
            conn.sendall(response.encode())
            conn.close()
            return
        parsed_url = urllib.parse.urlparse(path)
        query = urllib.parse.parse_qs(parsed_url.query)
        response_body = ""
        try:
            if 'factorial' in query:
                n = int(query['factorial'][0])
                result = factorial(n)
                response_body = f"Факториал {n} = {result}"
            elif 'expr' in query:
                expr = query['expr'][0]
                result = evaluate_expression(expr)
                response_body = f"Результат выражения {expr} = {result}"
            else:
                response_body = "Параметр factorial или expr не указан"
        except Exception as e:
            response_body = f"Ошибка вычисления: {e}"

        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain; charset=utf-8\r\n"
            f"Content-Length: {len(response_body.encode('utf-8'))}\r\n"
            "Connection: close\r\n"
            "\r\n" +
            response_body
        )
        conn.sendall(response.encode('utf-8'))
    except Exception as e:
        print(f"Ошибка обработки клиента {addr}: {e}")
    finally:
        conn.close()

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"HTTP сервер запущен на http://{HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    run_server()
