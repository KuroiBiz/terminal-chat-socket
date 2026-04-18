import socket
import threading

HOST = "0.0.0.0"
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = {}

def broadcast(msg, sender=None):
    for c in list(clients):
        if c != sender:
            try:
                c.sendall(msg)
            except:
                c.close()
                clients.pop(c, None)

def handle(client):
    try:
        name = client.recv(1024).decode().strip()
        clients[client] = name
        broadcast(f"[+] {name} joined\n".encode())

        while True:
            data = client.recv(1024)
            if not data:
                break
            broadcast(data, sender=client)

    finally:
        name = clients.get(client, "unknown")
        clients.pop(client, None)
        broadcast(f"[-] {name} left\n".encode())
        client.close()

print("Server running...")
while True:
    client, _ = server.accept()
    threading.Thread(target=handle, args=(client,), daemon=True).start()