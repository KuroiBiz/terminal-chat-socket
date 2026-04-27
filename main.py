import socket
import threading
import time

from auth import authenticate, init_db
from admin import log, admin_console
from msg import init_msg_db, save_message, get_last_messages


HOST = "0.0.0.0"
PORT = 12345

init_db()
init_msg_db()

# ------------------------
# SERVER SETUP
# ------------------------
def make_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(128)
    return s


server = make_server()
clients = {}

# ------------------------
# RATE LIMITING
# ------------------------
last_msg_time = {}
MSG_INTERVAL = 1.0  # seconds per message

def can_send(username):
    now = time.time()

    if username not in last_msg_time:
        last_msg_time[username] = now
        return True

    if now - last_msg_time[username] >= MSG_INTERVAL:
        last_msg_time[username] = now
        return True

    return False


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

    if username in clients.values():
        send(client, "[-] already online")
        client.close()
        return

    clients[client] = username
    log(f"{username} joined")

    broadcast(f"\n[+] {username} joined\n".encode())

    # send last messages
    history = get_last_messages(10)
    for user, msg, ts in history:
        send(client, f"[{ts}] {user}: {msg}")

    try:
        while True:
            data = client.recv(1024)
            if not data:
                break

            msg = data.decode().strip()

            # ignore empty messages
            if not msg:
                continue

            # ✅ RATE LIMIT CHECK
            if not can_send(username):
                send(client, "[-] slow down")
                continue

            # store message
            save_message(username, msg)

            log(f"{username}: {msg}")
            broadcast(f"[{username}] {msg}\n".encode(), sender=client)

    finally:
        name = clients.get(client, "unknown")
        clients.pop(client, None)

        log(f"{name} left")
        broadcast(f"\n[-] {name} left\n".encode())

        # cleanup rate limit data
        if name in last_msg_time:
            del last_msg_time[name]

        client.close()


# ------------------------
# START ADMIN THREAD
# ------------------------
threading.Thread(
    target=admin_console,
    args=(clients, broadcast),
    daemon=True
).start()

log("Server running...")

# ------------------------
# MAIN LOOP
# ------------------------
while True:
    try:
        client, _ = server.accept()
        threading.Thread(target=handle, args=(client,), daemon=True).start()

    except OSError as e:
        log(f"[accept error] {e}")
        try:
            server.close()
        except:
            pass
        server = make_server()
