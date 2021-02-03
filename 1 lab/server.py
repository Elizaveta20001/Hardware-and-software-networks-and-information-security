import socket
import threading
import mimetypes

PORT = 8080
ADDR = socket.gethostbyname(socket.gethostname())


def start_work():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("localhost", PORT))
        server.listen(10)
        while True:
            conn, addr = server.accept()
            message = conn.recv(1024)
            print(message.decode())
            header, response = parse_request(message.decode().split(" "))
            print(header)
            print(response)
            data = header
            data += "\r\n"
            data += response.decode()
            conn.sendall(data.encode())


def parse_request(text):
    method = text[0]
    print(method)
    if method == "GET":
        return get_request(text)
    elif method == "POST":
        pass
    else:
        pass


def get_request(text):
    file = text[1]
    file = file.split('/')[1]
    print(file)
    try:
        with open(file, 'rb') as my_file:
            response = my_file.read()
        header = "HTTP/1.1 200 OK\r\n"
    except Exception as e:
        header = "HTTP/1.1 404 Not Found\n\n"
        response = '<html><body><center><h3>Error 404: File not found</h3><p>Python HTTP Server</p></center></body></html>'.encode(
            'utf-8')
    else:
        extension = file.split(".")[1]
        content_type = mimetypes.types_map["." + extension]
        header += 'Content-Type: ' + content_type + "\r\n"

    return header, response


def connected_user(conn, addr):
    pass


if __name__ == '__main__':
    start_work()
