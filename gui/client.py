import socket
from queue import Queue
from threading import Thread
from time import sleep
from parameters import Message


SERVER_IP = "127.0.0.1"
SERVER_PORT = 35533
NICK = "|RomAm"
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
    def __init__(self, server_ip: str , server_port: int,
                  nick: str, q_send: Queue, q_recv: Queue, gui=None, event=None):
        self.server_ip = server_ip
        self.server_port = server_port
        self.nick = nick
        self.q_send = q_send
        self.q_recv = q_recv

        self.gui = gui
        self.event = event

        self.connected = False

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

    def connect(self):
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
        while True:
            seng_msg = self.q_send.get()
            self.q_send.task_done()

            types = Message.basic_types()

            if send_msg.type_msg == types[1]: # если это сообщение
                if not send_to_all_nicks(self.s, self.nick, send_msg.message):
                    break
            elif send_msg.type_msg == types[2]:
                if not send_to_nick(self.s, self.nick, send_msg.nick_to, send_msg.message):
                    break
            elif send_msg.type_msg == types[3]:
                if not send_disconnect(self.s, self.nick):
                    break
                break

        self.connected = False

    def receiver(self):
        while True:
            try:
                recv_msg = self.s.recv(2)
                recv_msg = self.s.recv(int.from_bytes(recv_msg))
            except ConnectionResetError:
                print(f"Соединение {self.s} разорвано")
                break
            full_pack = recv_msg.split(SEP_HEAD)
            head = [field.decode('utf-8') for field in full_pack[0].split(SEP_FIELDS)]

            types = Message.basic_types()

            if head[0] == GET_ALL:
                if len(full_pack) > 1:
                    msg_send = Message(types[0], message=full_pack[1].decode('utf-8'))
                    self.q_recv.put(msg_send)
                    if not self.gui is None:
                        self.gui.event_generate(self.event)
            elif head[0] == SEND_ALL_NICKS:
                if len(full_pack) > 1:
                    msg_send = Message(types[0], nick_from=head[1], message=full_pack[1].decode('utf-8'))
                    self.q_recv.put(msg_send)
                    if not self.gui is None:
                        self.gui.event_generate(self.event)
            elif head[0] == SEND_NICK:
                if len(full_pack) > 1:
                    msg_send = Message(types[0], head[1], full_pack[1].decode('utf-8'))
                    self.q_recv.put(msg_send)
                    if not self.gui is None:
                        self.gui.event_generate(self.event)
            elif head[0] == DISCONNECT:
                msg_send = Message(types[3])
                self.q_send.put(msg_send)
                if not self.gui is None:
                    self.gui.event_generate(self.event)
                break

        self.connected = False


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

def console_recv(queue: Queue) -> None:
    while True:
        if not queue.empty():
            recv_msg = queue.get()
            queue.task_done()
        else:
            continue

        types  = Message.basic_types()

        if recv_msg.type_msg == types[0]:
            print("Подключенные пользователи: " + recv_msg.message)
        elif recv_msg.type_msg == types[1]:
            print(f"От [{recv_msg.nick_from}] сообщение для всех: {recv_msg.message}")
        elif recv_msg.type_msg == types[2]:
            print(f"От [{recv_msg.nick_from}] сообщение: {recv_msg.message}")
        elif recv_msg.type_msg == types[3]:
            print("Соединение разорвано")
            break

if __name__ == "__main__":
    q_send = Queue()
    q_recv = Queue()
    messanger = Conversation(SERVER_IP, SERVER_PORT, NICK, q_send, q_recv)
    t_receiver = Thread(target=console_recv, args=(q_recv,), daemon=True)
    t_receiver.start()
    types = Message.basic_types()
    while not messanger.connected:
        pass
    while True:
        if not messanger.connected:
            print("Ожидание подключения...")
            messanger.connect()
            continue
        to = input("Введите имя: ")
        msg = input("Cообщение: ")

        if msg.lower() == "exit" or to.lower() == "exit":
            msg_send = Message(types[3], NICK)
            q_send.put(msg_send)
            break

        if not to:
            msg_send = Message(types[1], NICK, None, msg)
            q_send.put(msg_send)
        else:
            msg_send = Message(types[2], to, msg)
            q_send.put(msg_send)

    t_receiver.join()
    messanger.wait_threads()