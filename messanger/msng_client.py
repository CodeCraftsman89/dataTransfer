import socket
from threading import Thread
from time import sleep

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 35533  # The port used by the server
NICK = "||ePBb|Y"
SEP_HEAD = b'/x00'
SEP_FIELDS = b'/x01'
CONSTANTS = ["CONN_NICK", "GET_NICKS", "SEND", "SEND_ALL", "DISCONN"]

CONNECT_TRY_SHORT = 3
CONNECT_TRY_SHORT_SLEEP = 1
CONNECT_TRY_LONG = 5
CONNECT_TRY_LONG_SLEEP = 30

def send_connect(sock: socket.socket) -> bool:
    send_msg = CONSTANTS[0].encode('utf-8') + SEP_FIELDS + NICK.encode('utf-8') + SEP_FIELDS + SEP_HEAD
    send_msg = len(send_msg).to_bytes(2, byteorder='big') + send_msg
    return send_message(sock, send_msg)

def send_get_nicks(sock: socket.socket) -> bool:
    send_msg = CONSTANTS[1].encode('utf-8') + SEP_FIELDS + SEP_FIELDS + SEP_HEAD
    send_msg = len(send_msg).to_bytes(2, byteorder='big') + send_msg
    return send_message(sock, send_msg)

def send_to_all_nicks(sock: socket.socket, text: str) -> bool:
    send_msg = CONSTANTS[3].encode('utf-8') + SEP_FIELDS + NICK.encode('utf-8') + SEP_FIELDS + SEP_HEAD + text.encode('utf-8')
    send_msg = len(send_msg).to_bytes(2, byteorder='big') + send_msg
    return send_message(sock, send_msg)

def receiver(sock: socket.socket, close: bool) -> None:
    while True:
        try:
            recv_msg = sock.recv(2)
            recv_msg = sock.recv(int.from_bytes(recv_msg))
        except ConnectionResetError:
            print(f"Disconnect {sock}")
            break
        full_pack = recv_msg.split(SEP_HEAD)
        head = [field.decode('utf-8') for field in full_pack[0].split(SEP_FIELDS)]
        if head[0] == CONSTANTS[1]:
            if len(full_pack) > 1:
                print(f"Users: {full_pack[1].decode('utf-8')}")
        elif head[0] == CONSTANTS[3]:
            if len(full_pack) > 1:
                if full_pack[1].decode('utf-8').lower() == "end":
                    print("Disconnection")
                    break
                else:
                    print(f"Message: {full_pack[1].decode('utf-8')}")

def send_message(sock: socket.socket, mesg: bytes) -> bool:
    try:
        sock.send(mesg)
    except ConnectionResetError:
        print(f"Disconnect {sock}")
        return False
    return True

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connect to {HOST}:{PORT}")
    connected = False
    connect_try = 0
    connect_try_error = 0
    while not connected:
        try:
            s.connect((HOST, PORT))
            connected = True
            break
        except ConnectionRefusedError:
            print("Do not connected.")
            connect_try += 1
            if connect_try == CONNECT_TRY_SHORT:
                print(f"{CONNECT_TRY_SHORT}")
                connect_try_error += 1
                connect_try = 0
                if connect_try_error == CONNECT_TRY_LONG:
                    print(f"Using {CONNECT_TRY_SHORT * CONNECT_TRY_LONG} try to connect.")
                    print("End program")
                    break
                else:
                    print(f"Try {CONNECT_TRY_LONG_SLEEP}")
                    sleep(CONNECT_TRY_LONG_SLEEP)
            else:
                print(f"Stop {CONNECT_TRY_SHORT_SLEEP}")
                sleep(CONNECT_TRY_SHORT_SLEEP)
    if connected:
        print("Connected")
        close_sock = False
        t = Thread(target=receiver, args=(s, close_sock), daemon=True)
        t.start()
        if send_connect(s):
            while True:
                if not send_get_nicks(s):
                    break
                msg = input("Enter message: ")
                if not send_to_all_nicks(s, msg):
                    break

    s.close()