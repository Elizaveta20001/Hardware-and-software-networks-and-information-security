import socket
import threading
import mimetypes
import logging

PORT = 8080
ADDR = socket.gethostbyname(socket.gethostname())
logging.basicConfig(filename="log.txt", level=logging.INFO, filemode='w')
FILE_PATH = "D:/PyCharm/Hardware-and-software-networks-and-information-security/1 lab"


def start_work():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("localhost", PORT))
        logging.info(f"Server is running on localhost:{PORT}.")
        server.listen(10)
        logging.info("Server is waiting for connection.")
        while True:
            conn, addr = server.accept()
            logging.info(f"Server is connecting with {conn}")
            thread = threading.Thread(target=connected_user, args=(conn, addr))
            thread.start()


def parse_request(text: str):
    method = text.split(" ")[0]
    print(method)
    if method == "GET":
        return get_request(text)
    elif method == "POST":
        return post_request(text)
    elif method == "OPTIONS":
        return option_request()


def build_header(status_code, status_text):
    header = "HTTP/1.1 " + status_code + " " + status_text + " \r\n"
    header += "Access-Control-Allow-Origin: " + "http://localhost:8080/" + "\n"
    header += "Access-Control-Allow-Method: " + "POST, GET, OPTIONS" + "\r\n"
    return header


def post_request(text):
    list_message = text.split("\n")
    start_body_of_message = 0
    print(list_message)
    for i in list_message:
        if len(i) == 0:
            start_body_of_message = list_message.index(i)
    try:
        with open("post_request.txt", "w") as file:
            file.write("".join(list_message[start_body_of_message:len(list_message) - 1]))
            header = "HTTP/1.1 200 OK\r\n"
    except Exception as e:
        header = "HTTP/1.1  500 Internal server error\n\n"
        logging.info("Post request 500: Internal server error")
    response = ""
    return header, response


def option_request():
    response = ""
    return build_header("200", "OK"), response.encode()


def get_request(text):
    file = FILE_PATH
    file += text.split(' ')[1]
    print(file)
    try:
        with open(file, 'rb') as my_file:
            response = my_file.read()
        logging.info("Get request 200 OK")
    except Exception as e:
        header = build_header("404", "Not Found")
        header += 'Content-Type: ' + mimetypes.types_map['.html'] + "\r\n"
        response = '<html><body><center><h3>Error 404: File not found</h3><p>Python HTTP Server</p></center></body></html>'.encode(
            'utf-8')
        logging.info("Get request 404: File not found")
    else:
        extension = file.split(".")[1]
        content_type = mimetypes.types_map["." + extension]
        header = build_header("200", "OK")
        header += 'Content-Type: ' + content_type + "\r\n"

    return header, response


def connected_user(conn, addr):
    message = conn.recv(4096)
    logging.info(f"Server received from {conn} message.")
    if not message:
        logging.info("Disconnected")
        return
    header, response = parse_request(message.decode())
    print(header)
    data = header
    data += "\r\n"
    data = data.encode()
    if len(response) != 0:
        data += response
    conn.sendall(data)
    logging.info(f"Server sent {addr} message")


if __name__ == '__main__':
    start_work()
