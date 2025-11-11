import socket

HOST = '127.0.0.1'  
PORT = 8080         

def send_request(path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        request = f"GET {path} HTTP/1.1\r\nHost: {HOST}\r\nConnection: close\r\n\r\n"
        sock.sendall(request.encode('utf-8'))
        response = b""
        while True:
            data = sock.recv(1024)
            if not data:
                break
            response += data
    header, _, body = response.partition(b"\r\n\r\n")
    print(body.decode('utf-8'))

if __name__ == "__main__":
    while True:
        print("Введите запрос: factorial=число или expr=выражение (без пробелов)")
        user_input = input(">>> ")
        if user_input.lower() in ['exit', 'выход']:
            break
        path = "/?" + user_input
        send_request(path)
