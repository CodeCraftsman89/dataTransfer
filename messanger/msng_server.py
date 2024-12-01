import socket
from sqlite3 import connect
from threading import Thread

def connection(client: socket.socket):
    while True:
        msg = client.recv(1024)
        print(msg.decode("utf-8"))
        msg_d = msg.decode("utf-8")
        client.send(msg) #connect[-1][0].send(msg)
        '''if msg_d[-3] == "/":
            clients.append(msg_d)
        if msg_d.lower() == "get clients":
            client.send(msg)'''
        if msg.decode("utf-8") == "end":
            client.close()
            break

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
        print(f"Connected {connect[-1]}")

        #msg = s.recv(1024)
        #print(msg.decode("utf-8"))
        #s.send(msg)  # connect[-1][0].send(msg)

        t = Thread(target=connection, args=(connect[-1][0],), daemon=True)
        t.start()

    #for cn in connect:
    #    cn[0].close()

    #s.close()