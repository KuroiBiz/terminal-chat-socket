import hashlib

users = {}  # username -> password_hash


def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate(client, send):
    send(client, "[AUTH] /login user pass  OR  /register user pass")

    while True:
        data = client.recv(1024)
        if not data:
            return None

        cmd = data.decode().strip()
        parts = cmd.split()

        if len(parts) != 3:
            send(client, "[!] invalid format")
            continue

        action, username, password = parts

        if action == "/register":
            if username in users:
                send(client, "[-] username exists")
                continue

            users[username] = hash_pw(password)
            send(client, "[+] registered. now login")

        elif action == "/login":
            if username not in users:
                send(client, "[-] no such user")
                continue

            if users[username] != hash_pw(password):
                send(client, "[-] wrong password")
                continue

            send(client, "[+] login success")
            return username

        else:
            send(client, "[!] unknown command")