import socket
from base64 import encode
from threading import Thread
from time import sleep
from messanger.msng_client import CONNECT_TRY_SHORT

SERVER_IP = "127.0.0.1"
SERVER_PORT = 35533
NICK = "||ePBb|Y"
SEP_HEAD = b'/x00'
SEP_FIELDS = b'/x01'
CONNECT = "CONN_NICK"
GET_ALL = "GET_NICKS"
SEND_NICK = "SEND"
SEND_ALL_NICKS = "SEND_ALL"
DISCONNECT = "DISCONN"

CONNECT_TRY_SHORT = 3
CONNECT_TRY_SHORT_SLEEP = 1
CONNECT_TRY_LONG = 5
CONNECT_TRY_LONG_SLEEP = 30

def send_message(sock: socket.socket, mesg: bytes) -> bool:
    try:
        sock.send(mesg)

    except ConnectionResetError:
        print(f"Соединение {sock} разорвано")
        return False
    return True

def send_connect(sock: socket.socket) -> bool:
    send_msg = GET_ALL.encode("utf-8") + SEP_FIELDS + NICK.encode("utf-8") + SEP_FIELDS + SEP_HEAD
    send_msg = len(send_msg).to_bytes(2) + send_msg
    return send_message(sock, send_msg)

def send_get_nicks(sock: socket.socket) -> bool:
    send_msg = GET_ALL.encode("utf-8") + SEP_FIELDS + SEP_FIELDS + SEP_HEAD
    send_msg = len(send_msg).to_bytes(2) + send_msg
    return send_message(sock, send_msg)

def send_to_all_nicks(sock: socket.socket, text: str) -> bool:
    send_msg = (SEND_ALL_NICKS.encode("utf-8") + SEP_FIELDS + NICK.encode("utf-8") + SEP_FIELDS +
                SEP_HEAD + text.encode("utf-8"))
    send_msg = len(send_msg).to_bytes(2) + send_msg
    return send_message(sock, send_msg)

def send_disconnect(sock: socket.socket) -> bool:
    send_msg = DISCONNECT.encode("utf-8") + SEP_FIELDS + NICK.encode("utf-8") + SEP_FIELDS + SEP_HEAD
    send_msg = len(send_msg).to_bytes(2) + send_msg
    return send_message(sock, send_msg)

def receiver (sock: socket.socket) -> None:
    while True:
        try:
            recv_msg = sock.recv(2)
            recv_msg = sock.recv(int.from_bytes(recv_msg))
        except ConnectionResetError:
            print(f"Соединение {sock} разорвано")
            break
        full_pack = recv_msg.split(SEP_HEAD)
        head = [field.decode("utf-8") for field in full_pack[0].split(SEP_FIELDS)]
        if head[0] == GET_ALL:
            if len(full_pack) > 1:
                print(f"Получены все ники: {full_pack[1].decode('utf-8')}")
        elif head[0] == SEND_ALL_NICKS:
            if len(full_pack) > 1:
                print(f"Сообщение для всех {full_pack[1].decode('utf-8')}")
        elif head[0] == DISCONNECT:
            print(f"Соединение разорвано")
            break

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Соединение с {SERVER_IP}:{SERVER_PORT}")
    connected = False
    connect_try = 0
    connect_try_to_error = 0
    while not connected:
        try:
            s.connect((SERVER_IP, SERVER_PORT))
            connected = True
            break
        except ConnectionRefusedError:
            print(f"Нет соединения с {SERVER_IP}:{SERVER_PORT}")
            connect_try += 1
        if connect_try == CONNECT_TRY_SHORT:
            print(f"Не удалось подключиться через {CONNECT_TRY_SHORT} попыток")
            connect_try_to_error += 1
            connect_try = 0
            if connect_try_to_error == CONNECT_TRY_LONG:
                print(f"Не удалось подключиться через {CONNECT_TRY_LONG} попыток")
                print("Программа завершена")
                break
            else:
                print(f"Попытка подключения через {CONNECT_TRY_LONG_SLEEP} секунд")
                sleep(CONNECT_TRY_LONG_SLEEP)
        else:
            print(f"Попытка подключения через {CONNECT_TRY_SHORT_SLEEP} секунд")
            sleep(CONNECT_TRY_SHORT_SLEEP)
    if connected:
        print(f"Соединение с {SERVER_IP}:{SERVER_PORT} установлено")
        t = Thread(target=receiver, args=(s,), daemon=True)
        t.start()
        if send_connect(s):
            while True:
                if not send_get_nicks(s):
                    break
                msg = input("Введите сообщение: ")
                if msg == "exit":
                    send_disconnect(s)
                    t.join()
                    break
                if not send_to_all_nicks(s, msg):
                    break
    s.close()