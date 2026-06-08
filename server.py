import socket
import threading
import os
import random
import json
from datetime import datetime
from colorama import Fore, init
from crypto_chat import encrypt_message, decrypt_message
init(autoreset=True)
PORT = 5010
HOST = "127.0.0.1"
clients = {}
pending_users = []  
blocked_users = set()
user_colors = {}
COLOR_MAP = {
    "RED": Fore.RED,
    "GREEN": Fore.GREEN,
    "YELLOW": Fore.YELLOW,
    "BLUE": Fore.BLUE,
    "MAGENTA": Fore.MAGENTA,
    "CYAN": Fore.CYAN,
    "WHITE": Fore.WHITE
}
def print_logo():
    print(Fore.RED + r"""
 ____  ____  ____  _  _    ____  ____    __    ___  _____  _  _ 
(  _ \(_  _)(_  _)( \/ )  (  _ \(  _ \  /__\  / __)(  _  )( \( )
 ) _ < _)(_   )(   )  (    )(_) ))   / /(__)\( (_-. )(_)(  )  ( 
(____/(____) (__) (_/\_)  (____/(_)\_)(__)(__)\___/(_____)(_)\_)
    """)
    print(Fore.RED + "BUILT BY: https://github.com/fjcj0\n")
def broadcast(sender, message):
    payload = json.dumps({
        "time": datetime.now().strftime("%H:%M:%S"),
        "sender": sender,
        "message": message
    })
    for user, conn in list(clients.items()):
        try:
            conn.send(encrypt_message(payload))
        except:
            remove_client(user)
def remove_client(username):
    if username in clients:
        try:
            clients[username].close()
        except:
            pass
        clients.pop(username, None)
        broadcast("Server", f"{username} left chat")
def handle_client(conn, addr):
    username = None
    try:
        conn.send(b"username")
        username = decrypt_message(conn.recv(4096)).strip()
        conn.send(b"password")
        password = decrypt_message(conn.recv(4096)).strip()
        if username in blocked_users:
            conn.send(b"blocked")
            conn.close()
            return
        if username in clients:
            conn.send(b"exists")
            conn.close()
            return
        approved = threading.Event()
        status = {"value": "pending"}
        pending_users.append((username, conn, password, approved, status))
        print(f"[PENDING] {username}")
        approved.wait()
        if status["value"] == "rejected":
            conn.close()
            return
        clients[username] = conn
        user_colors[username] = random.choice(list(COLOR_MAP.keys()))
        broadcast("Server", f"{username} joined chat")
        while True:
            data = conn.recv(8192)
            if not data:
                break
            msg = decrypt_message(data)
            broadcast(username, msg)
    except Exception as e:
        print("Error:", e)
    finally:
        if username:
            remove_client(username)
        conn.close()
def admin_interface():
    while True:
        print("\n1. Show pending users")
        print("2. Accept user")
        print("3. Reject user")
        print("4. Connected users")
        print("5. Block user")
        print("6. Exit")
        choice = input("> ").strip()
        if choice == "1":
            if not pending_users:
                print("No pending users")
            else:
                for i, (u, _, _, _, _) in enumerate(pending_users):
                    print(f"{i+1}. {u}")
        elif choice == "2":
            if not pending_users:
                print("No pending users")
                continue
            for i, (u, _, _, _, _) in enumerate(pending_users):
                print(f"{i+1}. {u}")
            idx = int(input("Select user: ")) - 1
            if 0 <= idx < len(pending_users):
                u, conn, p, approved, status = pending_users.pop(idx)
                status["value"] = "accepted"
                try:
                    conn.send(encrypt_message("accepted"))
                except:
                    pass
                approved.set()
                print(f"[+] Accepted {u}")
        elif choice == "3":
            if not pending_users:
                print("No pending users")
                continue
            for i, (u, _, _, _, _) in enumerate(pending_users):
                print(f"{i+1}. {u}")
            idx = int(input("Select user: ")) - 1
            if 0 <= idx < len(pending_users):
                u, conn, p, approved, status = pending_users.pop(idx)
                status["value"] = "rejected"
                try:
                    conn.send(encrypt_message("rejected"))
                except:
                    pass
                approved.set()
                print(f"[-] Rejected {u}")
        elif choice == "4":
            if not clients:
                print("No connected users")
            else:
                for u in clients:
                    print("✔", u)
        elif choice == "5":
            u = input("User to block: ").strip()
            blocked_users.add(u)
            if u in clients:
                remove_client(u)
            print(f"[BLOCKED] {u}")
        elif choice == "6":
            try:
                print("stop server...")
                server.close()
                os._exit(0)
            except:
                pass
            return
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print_logo()
print(f"Server running on {HOST}:{PORT}")
threading.Thread(target=admin_interface, daemon=True).start()
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()