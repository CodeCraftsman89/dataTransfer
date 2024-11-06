import socket, time

soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    soc.sendto(bytearray("hello,", "utf-8"), ("127.0.0.1", 54321))
    time.sleep(1)