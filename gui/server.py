import socket  # импортируем либу
from threading import Thread  # импортируем класс
from threading import Lock  # импортируем класс
from queue import Queue  # импортируем класс

SERVER_IP = "0.0.0.0"  # адрес сервера для прослушивания всех доступных IP
SERVER_PORT = 35533  # порт для подключения
SEP_HEAD = b'/x00'  # разделитель заголовка и сообщения
SEP_FIELDS = b'/x01'  # разделитель полей заголовка
CONNECT = "CONN_NICK"  # сообщаем свой ник
GET_ALL = "GET_NICKS"  # запрашиваем ники подключенных клиентов
SEND_NICK = "SEND"  # отправляем сообщение определённому клиенту
SEND_ALL_NICKS = "SEND_ALL"  # отправляем сообщение всем клиентам
DISCONNECT = "DISCONN"  # отключаемся

connect = {}  # словарь подключенных клиентов


def send_message(sock: socket.socket, mesg: bytes) -> bool:
    try:
        sock.send(mesg)  # отправка сообщения
    except ConnectionResetError:
        print(f"Соединение {sock} разорвано.")
        sock.close()  # закрываем сокет с клиентом
        return False  # отправка сообщения неудачна
    return True  # сообщение отправлено


def send_nicks(sock: socket.socket, clients: dict) -> bool:
    # формируем сообщение из всех ников
    nicks = "  ".join([k for k in clients])  # формирование ников
    msg_get_all = GET_ALL.encode("utf-8") + SEP_FIELDS + SEP_FIELDS + SEP_HEAD + nicks.encode("utf-8")
    msg_get_all = len(msg_get_all).to_bytes(2) + msg_get_all  # добавляем 2 байта длины
    return send_message(sock, msg_get_all)


def send_nicks_to_all(clients_dict: dict) -> bool:
    # формируем сообщение из всех ников
    nicks = "  ".join([k for k in clients_dict])  # формирование ников
    msg_get_all = GET_ALL.encode("utf-8") + SEP_FIELDS + SEP_FIELDS + SEP_HEAD + nicks.encode("utf-8")
    msg_get_all = len(msg_get_all).to_bytes(2) + msg_get_all  # добавляем 2 байта длины
    for cl in clients_dict.keys():  # перебираем ники клиентов
        clients_dict[cl][2].put(msg_get_all)  # добавление полного сообщения в очередь
    return True

def send_to_nick(clients_dict: dict, nick_from: str, nick_to: str, msg: bytes) -> bool:
    # формируем сообщение для отправки одному пользователю
    msg_to = (SEND_NICK.encode("utf-8") + SEP_FIELDS + nick_from.encode("utf-8") +
               SEP_FIELDS + nick_to.encode("utf-8") + SEP_HEAD + msg)
    msg_to = len(msg_to).to_bytes(2) + msg_to  # добавляем 2 байта длины
    cl = clients_dict.get(nick_to)  # выбираем ник конкретного клиента
    if cl:  # проверка, что получили данные этого ника
        cl[2].put(msg_to)  # добавление полного сообщения в очередь
    return True


def send_to_all_nicks(clients_dict: dict, nick: str, msg: bytes) -> bool:
    # формируем сообщение для отправки всем пользователям
    msg_all = SEND_ALL_NICKS.encode("utf-8") + SEP_FIELDS + nick.encode("utf-8") + SEP_FIELDS + SEP_HEAD + msg
    msg_all = len(msg_all).to_bytes(2) + msg_all  # добавляем 2 байта длины
    for cl in clients_dict.keys():  # перебираем ники клиентов
        if cl == nick:  # проверка на собственный ник
            continue
        clients_dict[cl][2].put(msg_all)  # добавление полного сообщения в очередь
    return True


def send_disconnect(sock: socket.socket) -> bool:
    # формируем сообщение отключения клиента
    msg_end = DISCONNECT.encode("utf-8") + SEP_FIELDS + SEP_FIELDS + SEP_HEAD
    msg_end = len(msg_end).to_bytes(2) + msg_end  # добавляем 2 байта длины
    return send_message(sock, msg_end)


def client_conversations(client: socket.socket, client_addr: tuple, all_clients: dict, lock: Lock, queue: Queue) -> None:
    while True:
        disconnect = False
        # проверка, что очередь не пуста
        if not queue.empty():
            msg = queue.get()  # получение одного "сообщения" (задания или таска) из очереди
            send_message(client, msg)  # отправка этого сообщения
            queue.task_done()  # пометка, что задание (таск) выполнено
            continue  # переход к следующей итерации цикла, что бы проверить все таски очереди
        try:
            msg = client.recv(2)  # приём 2ух байтовой длины сообщения
            msg = client.recv(int.from_bytes(msg))  # приём сообщения исходя из принятой длины
        except TimeoutError: #except socket.timeout
            continue
        except ConnectionResetError:
            with lock:
                for key, val in all_clients.items():
                    if val[0] == client:
                        pop = key
                all_clients.pop(pop)
            print(f"Соединение {client} разорвано.")
            client.close()  # закрываем сокет с клиентом
            send_nicks_to_all(all_clients)  # отправка всем клиентам списка подключенных
            break  # выход из бесконечного цикла
        print(f"Сообщение [{msg.decode("utf-8")}]")
        full_pack = msg.split(SEP_HEAD)  # делим на заголовок и сообщение
        head = [field.decode("utf-8") for field in full_pack[0].split(SEP_FIELDS)]  # делим заголовок на поля

        # сообщение своего ника при подключении
        if head[0] == CONNECT:
            if head[1] in all_clients:
                print(f"{head[1]} никнейм уже зарегистрирован!!")
                client.close()  # закрываем соединение с клиентом
                break
            all_clients[head[1]] = (client, client_addr, queue)  # добавление клиента с ником в словарь
            if not send_nicks_to_all(all_clients):  # отправка всем клиентам списка подключенных
                break
        # запрос всех подключенных ников
        elif head[0] == GET_ALL:
            if not send_nicks(client, all_clients):  # отправка одному клиенту списка подключенных
                break
        # отправка конкретному нику
        elif head[0] == SEND_NICK:
            # если есть текст сообщения, кроме заголовка
            if len(full_pack) > 1:
                if not send_to_nick(all_clients, head[1], head[2], full_pack[1]):  # отправка сообщения
                    break
        # отправка всем никам
        elif head[0] == SEND_ALL_NICKS:
            # если есть текст сообщения, кроме заголовка
            if len(full_pack) > 1:
                if not send_to_all_nicks(all_clients, head[1], full_pack[1]):  # отправка сообщения всем
                    break
        # отключение клиента
        elif head[0] == DISCONNECT:
            if not send_disconnect(client):  # отправка подтверждения отключения
                break
            if not send_nicks_to_all(all_clients):  # отправка всем клиентам списка подключенных
                break
            disconnect = True

        if disconnect:
            print(f"Соединение {client} закрываем.")
            client.close()  # закрываем соединение с клиентом
            with lock:
                all_clients.pop(head[1])
            send_nicks_to_all(all_clients)  # отправка всем клиентам списка подключенных
            break  # выход из бесконечного цикла


if __name__ == "__main__":  # проверка, что запускаем как программу
    # создаём сокет и указываем, что это сокет потоковый - TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # биндим сокет на конкретный адрес
    s.bind((SERVER_IP, SERVER_PORT))
    # создаём объект блокиратора (критической секции)
    lock_threads = Lock()

    while True:  # бесконечный цикл
        print(f"Ожидаем подключения к {SERVER_IP}:{SERVER_PORT}...")
        s.listen()  # ожидаем подключения клиентов

        sock_cli, addr_cli = s.accept()  # принимаем подключение клиента
        print(f"Соединение {(sock_cli, addr_cli)} установлено.")
        sock_cli.settimeout(1)  # установка 1 секунды таймаута ожидания приёма/передачи сокета

        # создаём очередь для потока
        q = Queue()
        # создаём функцию поток, куда передаём сокет открытого соединения с клиентом
        t = Thread(target=client_conversations, args=(sock_cli, addr_cli, connect, lock_threads, q), daemon=True)
        t.start()  # запускаем поток на выполнение

    # s.close()  # закрываем сокет
