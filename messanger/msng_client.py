import socket
from threading import Thread

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 35533  # The port used by the server
NICK = "||ePBb|Y"
SEP_HEAD = b'/x00'
SEP_FIELDS = b'/x01'
CONSTANTS = ["CONN_NICK", "GET_NICKS", "SEND", "SEND_ALL", "DISCONN"]

def receiver(sock: socket.socket, close: bool) -> None:
    while True:
        recv_msg = sock.recv(2)
        recv_msng = sock.recv(int.from_bytes(recv_msg))
        full_pack = recv_msg.split(SEP_HEAD)
        head = [faild.decode('utf-8') for faild in full_pack[0].split(SEP_FIELDS)]
        if head[0] == CONSTANTS[1]:
            if len(full_pack) > 1:
                print(f"Users: {full_pack[1].decode('utf-8')}")
        elif head[0] == CONSTANTS[3]:
            if len(full_pack) > 1:
                if full_pack[1].decode('utf-8').lower() == "end":
                    close= True
                    break
                else:
                    print(f"Message: {full_pack[1].decode('utf-8')}")


if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connect to {HOST}:{PORT}")
    s.connect((HOST, PORT))
    print("Connect")
    close_sock = False
    t = Thread(target=receiver, args=(s, close_sock), daemon=True)
    t.start()
    msg_nick = CONSTANTS[0].encode("utf-8") + SEP_FIELDS + NICK.encode("utf-8") + SEP_FIELDS +SEP_HEAD
    msg_nick = len(msg_nick).to_bytes(2) + msg_nick
    s.send(msg_nick)
    while not close_sock:
        msg_get_all = CONSTANTS[1].encode('utf-8') + SEP_FIELDS + NICK.encode("utf-8") + SEP_FIELDS + SEP_HEAD
        msg_get_all = len(msg_get_all).to_bytes(2) + msg_get_all
        s.send(msg_get_all)
        msg = input(">>")
        msg_all = CONSTANTS[3].encode("utf-8") + SEP_FIELDS + NICK.encode("utf-8") +SEP_FIELDS + SEP_HEAD + msg.encode("utf-8")
        msg_all = len(msg_all).to_bytes(2) + msg_all
        s.send(msg_all)
    s.close()
