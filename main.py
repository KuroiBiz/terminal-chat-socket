import socket
import threading
from datetime import datetime

HOST = "0.0.0.0"
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = {}
logs = []

# ------------------------
# LOG SYSTEM
# ------------------------
def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    logs.append(entry)
    print(entry)


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
    try:
        name = client.recv(1024).decode().strip()
        clients[client] = name

        log(f"{name} joined")
        broadcast(f"[+] {name} joined\n".encode())

        while True:
            data = client.recv(1024)
            if not data:
                break

            log(f"{name}: {data.decode().strip()}")
            broadcast(data, sender=client)

    finally:
        name = clients.get(client, "unknown")
        clients.pop(client, None)

        log(f"{name} left")
        broadcast(f"[-] {name} left\n".encode())
        client.close()


# ------------------------
# STATUS PANEL
# ------------------------
def show_status():
    print("\n--- STATUS ---")
    print(f"Active clients: {len(clients)}")

    for name in clients.values():
        print(f" - {name}")

    print("--------------\n")


# ------------------------
# LOG VIEWER
# ------------------------
def show_logs():
    print("\n--- LOGS ---")
    for entry in logs[-20:]:  # last 20 logs
        print(entry)
    print("-------------\n")


# ------------------------
# SERVER COMMAND INPUT
# ------------------------
def admin_console():
    while True:
        cmd = input("SERVER> ").strip()

        if cmd == "status":
            show_status()

        elif cmd == "logs":
            show_logs()

        elif cmd.startswith("say "):
            msg = cmd[4:]
            broadcast(f"[SERVER] {msg}\n".encode())
            log(f"SERVER broadcast: {msg}")

        elif cmd == "help":
            print("""
Commands:
 status  → show active users
 logs    → show recent logs
 say msg → broadcast as server
 help    → show commands
""")

        else:
            print("Unknown command. type 'help'")


# ------------------------
# START THREADS
# ------------------------
threading.Thread(target=admin_console, daemon=True).start()

log("Server running...")

while True:
    client, _ = server.accept()
    threading.Thread(target=handle, args=(client,), daemon=True).start()