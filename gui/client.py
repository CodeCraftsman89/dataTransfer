import socket
from queue import Queue
from threading import Thread
from time import sleep


SERVER_IP = "25.38.241.107"
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

class Conversation:
    def __init__(self, server_ip: int , server_port: int, nick: str, q_send: Queue, q_recv: Queue):
        self.server_ip = server_ip
        self.server_port = server_port
        self.nick = nick
        self.q_send = q_send
        self.q_recv = q_recv

        self.connected = False

        self.s = socket.socket(socket.AF_IRDA, socket.SOCK_STREAM)
        print(f"Соединяемся с {SERVER_IP}:{SERVER_PORT}...")
        self.t_connect = Thread(target=self.connect, daemon=True)
        self.t_sender = Thread(target=self.sender, daemon=True)
        self.t_receiver = Thread(target=self.receiver, daemon=True)

        self.t_connect.start()


    def wait_threads(self):
        self.t_connect.join()
        self.t_sender.join()
        self.t_receiver.join()
        self.s.close()

    def connected(self):
        connected_to_serv = False
        connect_try = 0
        connect_try_to_error = 0
        while not connected_to_serv:
            try:
                self.s.connect((self.server_ip, self.server_port))
                connected_to_serv = True
                break
            except ConnectionRefusedError:
                print("Подключение не установлено")
                connect_try += 1
            if connect_try == CONNECT_TRY_SHORT:
                print("Не удалось подключиться через 3 попытки")
                connect_try_to_error += 1
                connect_try = 0
                if connect_try_to_error == CONNECT_TRY_LONG:
                    print(f"Не удалось подключиться {CONNECT_TRY_SHORT * CONNECT_TRY_LONG} попыток")
                    connect_try_to_error = 0
                else:
                    print(f"Попытка подключения через {CONNECT_TRY_LONG_SLEEP} секунд")
                    sleep(CONNECT_TRY_LONG_SLEEP)
            else:
                print(f"Попытка подключения через {CONNECT_TRY_SHORT_SLEEP} секунд")
                sleep(CONNECT_TRY_SHORT_SLEEP)

        if connected_to_serv:
            print(f"Соединение с {SERVER_IP}:{SERVER_PORT} установлено")
            if send_connect(self.s, self.nick):
                self.t_connect = True
                self.t_sender.start()
                self.t_receiver.start()
            else:
                print("Не удалось подключиться")

    def sender(self):
        pass

    def receiver(self):
        pass


def send_message(sock: socket.socket, mesg: bytes) -> bool:
    try:
        sock.send(mesg)
    except ConnectionResetError:
        print(f"Соединение {sock} разорвано")
        return False
    return True

def send_connect(sock: socket.socket, nic_from: str) -> bool:
    send_msg = CONNECT.encode("utf-8") + SEP_FIELDS + nic_from.encode("utf-8") + SEP_FIELDS + SEP_HEAD
    send_msg = len(send_msg).to_bytes(2) + send_msg
    return send_message(sock, send_msg)

def send_get_nicks(sock: socket.socket) -> bool:
    send_msg = GET_ALL.encode("utf-8") + SEP_FIELDS + SEP_FIELDS + SEP_HEAD
    send_msg = len(send_msg).to_bytes(2) + send_msg
    return send_message(sock, send_msg)

def send_to_nick(sock: socket.socket, nic_from: str, nic_to: str,  text: str) -> bool:
        send_msg = (SEND_NICK.encode("utf-8") + SEP_FIELDS + nic_from.encode("utf-8") + SEP_FIELDS +
                    nic_to.encode("utf-8") + SEP_HEAD + text.encode("utf-8"))
        send_msg = len(send_msg).to_bytes(2) + send_msg
        return send_message(sock, send_msg)

def send_to_all_nicks(sock: socket.socket, nic_from: str, text: str) -> bool:
    send_msg = (SEND_ALL_NICKS.encode("utf-8") + SEP_FIELDS + nic_from.encode("utf-8") + SEP_FIELDS +
                SEP_HEAD + text.encode("utf-8"))
    send_msg = len(send_msg).to_bytes(2) + send_msg
    return send_message(sock, send_msg)

def send_disconnect(sock: socket.socket, nic_from: str) -> bool:
    send_msg = DISCONNECT.encode("utf-8") + SEP_FIELDS + nic_from.encode("utf-8") + SEP_FIELDS + SEP_HEAD
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
                print(f"От [{head[1]}] cообщение для всех: {full_pack[1].decode('utf-8')}")
        elif head[0] == SEND_NICK:
            if len(full_pack) > 1:
                print(f"От [{head[1]}] сообщение: {full_pack[1].decode('utf-8')}")
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
                to = input("Введите ник: ")
                msg = input("Введите сообщение: ")
                if msg.lower() == "exit" or to.lower() == "exit":
                    send_disconnect(s)
                    t.join()
                    break
                if not to:
                    if not send_to_all_nicks(s, msg):
                        break
                else:
                    if not send_to_nick(s, to, msg):
                        break
    s.close()

if __name__ == "__main__":
    pass