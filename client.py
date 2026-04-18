import socket
import threading
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text

HOST = "127.0.0.1"
PORT = 12345

console = Console()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

name = Prompt.ask("[bold green]Enter your handle[/]")
client.sendall((name + "\n").encode())

def receive():
    while True:
        try:
            data = client.recv(1024)
            if not data:
                break
            msg = data.decode()

            # simple styling rules
            if msg.startswith("[+]"):
                console.print(msg.strip(), style="bold green")
            elif msg.startswith("[-]"):
                console.print(msg.strip(), style="bold red")
            else:
                console.print(msg.strip(), style="cyan")

        except:
            break

threading.Thread(target=receive, daemon=True).start()

console.print("[bold magenta]Connected. Type /quit to exit[/]")

while True:
    text = console.input("[bold yellow]> [/]")
    if text.strip() == "/quit":
        break

    payload = f"[{name}] {text}\n"
    client.sendall(payload.encode())

client.close()