import socket
import threading
from rich.console import Console

HOST = "127.0.0.1"
PORT = 12345

console = Console()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

username = None
authenticated = False


# ------------------------
# RECEIVE THREAD
# ------------------------
def receive():
    global authenticated

    while True:
        try:
            data = client.recv(1024)
            if not data:
                break

            msg = data.decode().strip()

            # detect login success
            if "[+] login success" in msg:
                authenticated = True

            # styling
            if msg.startswith("[+]"):
                console.print(msg, style="bold green")
            elif msg.startswith("[-]"):
                console.print(msg, style="bold red")
            elif msg.startswith("[AUTH]") or msg.startswith("[!]"):
                console.print(msg, style="bold yellow")
            else:
                console.print(msg, style="cyan")

        except:
            break


threading.Thread(target=receive, daemon=True).start()


# ------------------------
# INPUT LOOP
# ------------------------
console.print("[bold magenta]Use /login or /register[/]")

while True:
    try:
        text = console.input("[bold yellow]> [/]").strip()

        if text == "/quit":
            break

        # track username after login command
        if text.startswith("/login"):
            parts = text.split()
            if len(parts) >= 2:
                username = parts[1]

        client.sendall((text + "\n").encode())

    except KeyboardInterrupt:
        break


client.close()
console.print("[bold red]Disconnected[/]")