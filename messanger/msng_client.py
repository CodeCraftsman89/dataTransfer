import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 35533  # The port used by the server

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connect to {HOST}:{PORT}")
    s.connect((HOST, PORT))
    print("Connect")
    s.close()