import socket
import threading

HOST = "127.0.0.1"
PORT = 5000

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode("utf-8")
            if not msg:
                break
            print("\n" + msg)
        except:
            break

nome = input("Digite seu nome: ")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    threading.Thread(target=receive_messages, args=(s,), daemon=True).start()

    while True:
        msg = input()
        if msg.lower() == "sair":
            break
        s.sendall(f"{nome}: {msg}".encode("utf-8"))
