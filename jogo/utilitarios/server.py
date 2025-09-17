import socket
import threading

HOST = "127.0.0.1"
PORT = 5000

clients = []

def broadcast(message, conn):
    for client in clients:
        if client != conn:
            try:
                client.sendall(message)
            except:
                clients.remove(client)

def handle_client(conn, addr):
    print(f"Novo cliente conectado: {addr}")
    clients.append(conn)
    try:
        while True:
            msg = conn.recv(1024)
            if not msg:
                break
            broadcast(msg, conn)
    finally:
        clients.remove(conn)
        conn.close()
        print(f"Cliente {addr} saiu.")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor de chat rodando em {HOST}:{PORT}...")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    start_server()
