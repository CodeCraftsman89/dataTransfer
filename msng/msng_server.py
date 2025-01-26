import queue
import socket
from threading import Thread, Lock
from queue import Queue

SERVER_IP = "0.0.0.0"
SERVER_PORT = 35533
SEP_HEAD = b'/x00'
SEP_FIELDS = b'/x01'
CONNECT = "CONN_NICK"
GET_ALL = "GET_NICKS"
SEND_NICK = "SEND"
SEND_ALL_NICKS = "SEND_ALL"
DISCONNECT = "DISCONN"
DISCONNECT_ALL = "DISCONN_ALL"

connect = {}

def send_message(sock: socket, msng: bytes) -> bool:
    try:
        sock.send(msng)
    except ConnectionError:
        print(f"Соединение {sock} разорвано")
        sock.close()
        return False
    return True

def send_nicks(sock: socket, clients: dict) -> bool:
    nicks = "  ".join([k for k in clients])
    msg_get_all = GET_ALL.encode('utf-8') + SEP_FIELDS + SEP_FIELDS + SEP_HEAD + nicks.encode('utf-8')
    msg_get_all = len(msg_get_all).to_bytes(2) + msg_get_all
    return send_message(sock, msg_get_all)

def send_to_all_nicks(client_dict: dict, nick: str, msg: bytes) -> bool:
    msg_all = SEND_ALL_NICKS.encode('utf-8') + SEP_FIELDS + SEP_FIELDS + SEP_HEAD + msg
    msg_all = len(msg_all).to_bytes(2) + msg_all
    for cl in client_dict.keys():
        client_dict[cl][2].put(msg_all)
    return True

def send_disconnect(sock: socket) -> bool:
    msg_end = DISCONNECT.encode('utf-8') + SEP_FIELDS + SEP_FIELDS + SEP_HEAD
    msg_end = len(msg_end).to_bytes(2) + msg_end
    return send_message(sock, msg_end)

def  client_conversations(client: socket.socket, client_addr: tuple, all_clients: dict, lock: Lock, queue: Queue) -> None:
    while True:
        disconnect = False
        if not queue.empty():
            msg = queue.get()
            send_message(client, msg)
            queue.task_done()
            continue
        try:
            msg = client.recv(2)
            msg = client.recv(int.from_bytes(msg))
        except TimeoutError:
            continue
        except ConnectionResetError:
            print(f"Соединение {client} разорвано")
            client.close()
            break
        print(f"Получено сообщение: [{msg.decode('utf-8')}]")
        full_pack = msg.split(SEP_HEAD)
        head =[field.decode('utf-8') for field in full_pack[0].split(SEP_FIELDS)]
        if head[0] == CONNECT:
            all_clients[head[1]] = (client, client_addr, queue)
            if not send_to_all_nicks(all_clients):
                break
        elif head[0] == GET_ALL:
            if not send_nicks(client, all_clients):
                break
        elif head[0] == SEND_ALL_NICKS:
            if len(full_pack) > 1:
                if not send_to_all_nicks(all_clients, head[1], full_pack[1]):
                    break
        elif head[0] == DISCONNECT:
            if not send_disconnect(client):
                break
            disconnect = True
        if disconnect:
            print(f"Соединение {client} разорвано")
            client.close()
            with lock:
                all_clients.pop(head[1])
            break

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((SERVER_IP, SERVER_PORT))
    lock_threads = Lock()

    while True:
        print(f"Ожидаем подключения к {SERVER_IP}:{SERVER_PORT}...")
        s.listen()

        sock_cli, addr_cli = s.accept()
        print(f"Получено подключение {addr_cli}")
        sock_cli.settimeout(1)

        q = Queue()
        t = Thread(target=client_conversations, args=(sock_cli, addr_cli, connect, lock_threads, q), daemon=True)
        t.start()