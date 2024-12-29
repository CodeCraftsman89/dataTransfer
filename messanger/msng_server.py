import socket
from threading import Thread

SEP_HEAD = b'\x00'
SEP_FIELDS = b'\x01'
CONSTANTS = ["CONN_NICK", "GET_NICKS", "SEND", "SEND_ALL", "DISCONN"]

connect = {}
def connection(client: socket.socket, client_addr: tuple, all_clients: dict):
    while True:
        disconnect = False
        msg_send = b""
        try:
            msg = client.recv(2)
            msg_length = int.from_bytes(msg, byteorder='big')
            msg = client.recv(msg_length)
        except ConnectionResetError:
            print(f"Disconnect {client}")
            client.close()
            break
        print(f"Message: {msg.decode('utf-8')}")
        full_pack = msg.split(SEP_HEAD)
        head = [field.decode('utf-8') for field in full_pack[0].split(SEP_FIELDS)]

        if head[0] == CONSTANTS[0]:
            all_clients[head[1]] = (client, client_addr)

        elif head[0] == CONSTANTS[1]:
            nicks = "  ".join([k for k in all_clients])
            msg_get_all = CONSTANTS[1].encode('utf-8') + SEP_FIELDS + SEP_FIELDS + SEP_HEAD + nicks.encode('utf-8')
            msg_get_all = len(msg_get_all).to_bytes(2) + msg_get_all
            msg_send = msg_get_all

        elif head[0] == CONSTANTS[3]:
            if len(full_pack) > 1:
                if full_pack[1].decode('utf-8').lower() == "end":
                    msg_end = (CONSTANTS[2].encode('utf-8') +
                               SEP_FIELDS + head[1].encode('utf-8') +
                               SEP_FIELDS + head[1].encode('utf-8') +
                               SEP_HEAD + full_pack[1])
                    msg_end = len(msg_end).to_bytes(2) + msg_end
                    msg_end = msg_end
                    disconnect = True
                else:
                    msg_all = CONSTANTS[3].encode('utf-8') + SEP_FIELDS + SEP_FIELDS + SEP_HEAD + full_pack[1]
                    msg_all = len(msg_all).to_bytes(2) + msg_all
                    client.send(msg_all)

        try:
            client.send(msg_send)
        except ConnectionResetError:
            print(f"Disconnect {client}")
            client.close()
            break
        if disconnect:
            print(f"Disconnect {client}")
            client.close()
            break

HOST = "0.0.0.0"  # The server's hostname or IP address
PORT = 35533  # The port used by the server

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    while True:
        print(f"Waiting for connect to {HOST}:{PORT}...")
        s.listen()

        sock_cli, addr_cli = s.accept()
        print(f"Connected to {(sock_cli, addr_cli)}")

        t = Thread(target=connection, args=(sock_cli, addr_cli, connect), daemon=True)
        t.start()
