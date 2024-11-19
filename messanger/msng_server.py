import socket
from sqlite3 import connect

HOST = "0.0.0.0"  # The server's hostname or IP address
PORT = 35533  # The port used by the server

connect = []

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    while True:
        print(f"Waiting for connect to {HOST}:{PORT}...")
        s.listen()

        connect.append(s.accept())
        print(f"Connected {connect}")

        msg = connect[-1][0].recv(1024)
        print(msg.decode("utf-8"))
        connect[-1][0].send(msg) #connect[-1][0].send(msg)
        if msg.decode("utf-8") == "end":
            break

    for cn in connect:
        cn[0].close()

    s.close()