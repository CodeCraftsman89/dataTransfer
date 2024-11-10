import socket
from sqlite3 import connect

HOST = "0.0.0.0"  # The server's hostname or IP address
PORT = 35533  # The port used by the server

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    print(f"Waiting for connect to {HOST}:{PORT}...")
    s.listen()

    connect = s.accept()
    print(f"Connected {connect}")

    connect[0].close()
    print(f"Disconnect {connect}")
    s.close()