import socket

soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

soc.bind(("127.0.0.1", 54321))
while True:
    message = soc.recv(128)
    print(message)
