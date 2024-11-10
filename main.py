import socket, time

soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
soc.bind(("127.0.0.1", 54321))

while True:
    soc.sendto(bytearray("hello,", "utf-8"), ("127.0.0.1", 54321))
    time.sleep(5)

    message = soc.recv(128)
    print(message)
