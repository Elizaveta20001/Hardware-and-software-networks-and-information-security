import socket
import threading
import mimetypes
import logging
import json
import argparse

logging.basicConfig(filename="log.txt", level=logging.INFO, filemode='w')


def start_work(port, path):
    global FILE_PATH
    FILE_PATH = path
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("localhost", port))
        logging.info(f"Server is running on localhost:{port}.")
        server.listen(5)
        logging.info("Server is waiting for connection.")
        while True:
            conn, addr = server.accept()
            logging.info(f"Server connected with {addr}")
            thread = threading.Thread(target=connected_user, args=(conn, addr))
            thread.start()


def parse_request(text: str):
    method = text.split(" ")[0]
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


def get_dict(text: str) -> dict:
    list_of_messages = text.split("\n")
    body_of_message = list_of_messages[list_of_messages.index('\r') + 1].split('&')
    dict_of_messages = dict()
    for item in body_of_message:
        try:
            dict_of_messages[item.split('=')[0]] = item.split('=')[1]
        except Exception as e:
            continue
    return dict_of_messages


def post_request(text):
    dict_messages = get_dict(text)
    try:
        with open("report.json", "w") as file:
            json.dump(dict_messages, file)
        with open("report.json", "rb") as file:
            response = file.read()

    except Exception as e:
        header = build_header('500', 'Internal Server Error')
        header += 'Content-Type: ' + mimetypes.types_map['.html'] + "\r\n"
        response = '<html><body><center><h3>Error 500: Internal Server Error</h3><p>Python HTTP Server</p></center></body></html>'.encode(
            'utf-8')
        logging.info('\n'+ header)
        print('Post request 500: Internal server error')
    else:
        header = build_header('200', 'OK')
        logging.info('\n' + header)
        header += "Content-Type: " + mimetypes.types_map['.json'] + '\r\n'
        print('Post request 200 OK')

    return header, response


def option_request():
    logging.info("\n" + build_header("200", "OK"))
    print("OPTIONS request 200 OK")
    response = ""
    return build_header("200", "OK"), response.encode()


def get_request(text):
    file = FILE_PATH
    file += text.split(' ')[1].split('?')[0]
    try:
        with open(file, 'rb') as my_file:
            response = my_file.read()
    except Exception as e:
        header = build_header("404", "Not Found")
        header += 'Content-Type: ' + mimetypes.types_map['.html'] + "\r\n"
        response = '<html><body><center><h3>Error 404: File not found</h3><p>Python HTTP Server</p></center></body></html>'.encode(
            'utf-8')
        logging.info('\n' + header)
        print("Get request 404: File not found")
    else:
        content_type = mimetypes.types_map["." + file.split(".")[1]]
        header = build_header("200", "OK")
        header += 'Content-Type: ' + content_type + "\r\n"
        logging.info('\n' + header)
        print("Get request 200 OK")

    return header, response


def connected_user(conn, addr):
    message = conn.recv(4096)
    logging.info(f"Server received from {conn} request.")
    if not message:
        return
    header, response = parse_request(message.decode())
    print(header)
    data = header
    data = data.encode()
    if len(response) != 0:
        data += "\r\n".encode()
        data += response
    conn.sendall(data)
    logging.info(f"Server sent {addr} message,\n message ={data} ")


if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument("--port", '-p', type=int, help='Set server port', default=8080)
    parse.add_argument("--directory", "-d", type=str, help='Set directory',
                       default='D:/PyCharm/Hardware-and-software-networks-and-information-security/1 lab')
    args = parse.parse_args()
    start_work(port=args.port, path=args.directory)
