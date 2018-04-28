import socket
import struct
import sys
import threading
import datetime
PORT = 8888
HEADER_LENGTH = 2


def receive_fixed_length_msg(sock, msglen):
    message = b''
    while len(message) < msglen:
        chunk = sock.recv(msglen - len(message))  # preberi nekaj bajtov
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        message = message + chunk  # pripni prebrane bajte sporocilu

    return message


def receive_message(sock):
    header = receive_fixed_length_msg(sock,
                                      HEADER_LENGTH)  # preberi glavo sporocila (v prvih 2 bytih je dolzina sporocila)
    message_length = struct.unpack("!H", header)[0]  # pretvori dolzino sporocila v int
    message = None
    if message_length > 0:  # ce je vse OK
        message = receive_fixed_length_msg(sock, message_length)  # preberi sporocilo
        message = message.decode("utf-8")

    return message


def send_message(sock, message):
    if message.split(" ")[0] == "!private":
        send_private_message(sock, message)
    encoded_message = message.encode("utf-8")  # pretvori sporocilo v niz bajtov, uporabi UTF-8 kodno tabelo

    # ustvari glavo v prvih 2 bytih je dolzina sporocila (HEADER_LENGTH)
    # metoda pack "!H" : !=network byte order, H=unsigned short
    header = struct.pack("!H", len(encoded_message))

    message = header + encoded_message  # najprj posljemo dolzino sporocilo, slee nato sporocilo samo
    sock.sendall(message)




# message_receiver funkcija tece v loceni niti
def message_receiver():
    while True:
        msg_received = receive_message(sock)
        #print(msg_received, sock)
        if len(msg_received) > 0:  # ce obstaja sporocilo
            cas = str(datetime.datetime.now()).split(".")[0]
            datum, ura = cas.split(" ")[0], cas.split(" ")[1]
            user = msg_received.split(" ")[0]
            message = msg_received.split(" ", 1)[1]
            print(f"[{ura}] {user}: {message}")  # izpisi


# povezi se na streznik
print("[system] connecting to chat server ...")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect(("localhost", PORT))
    print("[system] connected!")
except ConnectionError:
    print("Error connecting, try setting up the server maybe, idk al pa nek druzga")
    sys.exit(1)

# zazeni message_receiver funkcijo v loceni niti
thread = threading.Thread(target=message_receiver)
thread.daemon = True
thread.start()

username = ""
while not username:
    try:
        username = input("Vnesi uporabnisko ime\n")
        send_message(sock, username)
    except KeyboardInterrupt:
        continue
print(f'welcome {username!r}')

# pocakaj da uporabnik nekaj natipka in poslji na streznik
while True:
    try:
        msg_send = input("")
        if msg_send.lower() not in ("exit", "q", "quit", "esc"):
            send_message(sock, msg_send)
        else:
            print("exiting...")
            sys.exit()
    except KeyboardInterrupt:
        continue
