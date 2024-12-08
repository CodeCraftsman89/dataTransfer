import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 35533  # The port used by the server
NICK = "ABC"
SEP_HEAD = b'/x00'
SEP_FIELDS = b'/x01'
CONSTANTS = ["CONN_NICK", "GET_NICKS", "SEND", "SEND_ALL", "DISCONN"]
if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connect to {HOST}:{PORT}")
    s.connect((HOST, PORT))
    print("Connect")
    msg_nick = CONSTANTS[0].encode("utf-8") + SEP_FIELDS + NICK.encode("utf-8") + SEP_FIELDS +SEP_HEAD
    s.send(msg_nick)
    while True:
        msg_get_all = CONSTANTS[1].encode('utf-8') + SEP_FIELDS + NICK.encode("utf-8") + SEP_FIELDS + SEP_HEAD
        s.send(msg_get_all)
        msg = s.recv(1024)
        print(f"Users: {msg.decode('utf-8')}")
        msg = input(">>")
        msg_all = CONSTANTS[3].encode("utf-8") + SEP_FIELDS + NICK.encode("utf-8") +SEP_FIELDS + SEP_HEAD + msg.encode("utf-8")
        s.send(msg_all)
        msg = s.recv(1024)
        '''user_message = input("Введите сообщение: ")
        s.send(user_message.encode("utf-8"))
        user_message = s.recv(1024)'''
        print(f"Message: {msg.decode('utf-8')}")
        if msg.decode("utf-8") == "end":
            break
