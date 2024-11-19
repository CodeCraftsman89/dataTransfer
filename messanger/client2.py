import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 35533  # The port used by the server

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connect to {HOST}:{PORT}")
    s.connect((HOST, PORT))
    print("Connect")
    while True:
        user_message = input("Введите сообщение: ")
        s.send(user_message.encode("utf-8"))
        user_message = s.recv(1024)
        if user_message.decode("utf-8") == "end":
            break
