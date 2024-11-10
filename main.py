import socket, time

soc_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
soc_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
soc_send.bind(("127.0.0.1", 55555))
soc_recv.bind(("127.0.0.1", 54321))

user_message = input("Введите сообщение: ")
i = 1
while True:
    user_message = input("Введите сообщение: ")
    soc_send.sendto(bytearray(f"№{i} {user_message}!!!,", "utf-8"), ("127.0.0.1", 54321))
    time.sleep(1)

    message = soc_recv.recv(128)
    print(message.decode("utf-8"))
    i+=1