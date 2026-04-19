from datetime import datetime

logs = []


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}"
    logs.append(entry)
    print(entry)


def show_status(clients):
    print("\n--- STATUS ---")
    print(f"Active clients: {len(clients)}")

    for name in clients.values():
        print(f" - {name}")

    print("--------------\n")


def show_logs():
    print("\n--- LOGS ---")
    for entry in logs[-20:]:
        print(entry)
    print("-------------\n")


def admin_console(clients, broadcast):
    while True:
        cmd = input("SERVER> ").strip()

        if cmd == "status":
            show_status(clients)

        elif cmd == "logs":
            show_logs()

        elif cmd.startswith("say "):
            msg = cmd[4:]
            broadcast(f"[SERVER] {msg}\n".encode())
            log(f"SERVER: {msg}")

        elif cmd == "help":
            print("""
status  → show users
logs    → show logs
say msg → broadcast
help    → commands
""")

        else:
            print("unknown command")