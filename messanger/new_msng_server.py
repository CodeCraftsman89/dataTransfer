import socket
from threading import Thread

# Константы
SEP_HEAD = b'\x00'
SEP_FIELDS = b'\x01'
CONSTANTS = ["CONN_NICK", "GET_NICKS", "SEND", "SEND_ALL", "DISCONN"]

# Система хранения данных подключенных клиентов
clients = {}  # {socket: nick}

def broadcast(message: str, sender=None):
    """Рассылает сообщение всем подключенным клиентам."""
    for client in clients.keys():
        try:
            if client != sender:
                client.send(message.encode("utf-8"))
        except Exception as e:
            print(f"Error broadcasting to {client}: {e}")

def handle_client(client: socket.socket):
    """Обрабатывает взаимодействие с клиентом."""
    try:
        while True:
            # Получение данных от клиента
            data = client.recv(1024)
            if not data:
                break
            parts = data.split(SEP_FIELDS)
            if len(parts) < 2:
                continue

            packet_type = parts[0].decode("utf-8")
            if packet_type == CONSTANTS[0]:  # CONN_NICK
                # Получение ника
                nick = parts[1].decode("utf-8")
                clients[client] = nick
                print(f"Client connected with nickname: {nick}")

            elif packet_type == CONSTANTS[1]:  # GET_NICKS
                # Отправка списка ников
                nick_list = ",".join(clients.values())
                client.send(nick_list.encode("utf-8"))

            elif packet_type == CONSTANTS[3]:  # SEND_ALL
                # Отправка сообщения всем клиентам
                nick = clients.get(client, "Unknown")
                message = f"{nick}: {parts[2].decode('utf-8')}"
                print(f"Broadcasting message: {message}")
                broadcast(message, sender=client)

            elif packet_type == CONSTANTS[4]:  # DISCONN
                print(f"Client {clients.get(client, 'Unknown')} disconnected")
                break

    except Exception as e:
        print(f"Error handling client {clients.get(client, 'Unknown')}: {e}")
    finally:
        # Удаление клиента из списка и закрытие соединения
        if client in clients:
            print(f"Removing client: {clients[client]}")
            del clients[client]
        client.close()

HOST = "0.0.0.0"
PORT = 35533

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server started on {HOST}:{PORT}")

    try:
        while True:
            print("Waiting for a connection...")
            client, addr = s.accept()
            print(f"Connected to {addr}")
            Thread(target=handle_client, args=(client,), daemon=True).start()
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        s.close()
