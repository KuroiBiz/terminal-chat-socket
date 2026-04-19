import socket
import threading

from auth import authenticate
from admin import log, admin_console

HOST = "0.0.0.0"
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = {}  # socket -> username


# ------------------------
# SEND HELPER
# ------------------------
def send(client, text):
    client.sendall((text + "\n").encode())


# ------------------------
# BROADCAST
# ------------------------
def broadcast(msg, sender=None):
    for c in list(clients):
        if c != sender:
            try:
                c.sendall(msg)
            except:
                c.close()
                clients.pop(c, None)


# ------------------------
# CLIENT HANDLER
# ------------------------
def handle(client):
    username = authenticate(client, send)

    if not username:
        client.close()
        return

    # prevent duplicate login
    if username in clients.values():
        send(client, "[-] already online")
        client.close()
        return

    clients[client] = username

    log(f"{username} joined")
    broadcast(f"[+] {username} joined\n".encode())

    try:
        while True:
            data = client.recv(1024)
            if not data:
                break

            msg = data.decode().strip()
            log(f"{username}: {msg}")
            broadcast(f"[{username}] {msg}\n".encode(), sender=client)

    finally:
        name = clients.get(client, "unknown")
        clients.pop(client, None)

        log(f"{name} left")
        broadcast(f"[-] {name} left\n".encode())
        client.close()


# ------------------------
# START SERVER
# ------------------------
threading.Thread(
    target=admin_console,
    args=(clients, broadcast),
    daemon=True
).start()

log("Server running...")

while True:
    client, _ = server.accept()
    threading.Thread(target=handle, args=(client,), daemon=True).start()