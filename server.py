import socket, threading, os, random
from colorama import Fore, init
from datetime import datetime
from cryptography.fernet import Fernet
init(autoreset=True)
PORT = 5010
HIDDEN_SERVICE_DIR = "./global_chat"
ADMIN_USERNAME = "admin"
USERS_FILE = os.path.join(HIDDEN_SERVICE_DIR, "users_status.enc")
KEY_FILE = os.path.join(HIDDEN_SERVICE_DIR, "secret.key")
clients = {}  
blocked_users = set()
pending_users = []
COLORS = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]
user_colors = {}
def print_logo():
    print(Fore.RED + r"""
 ____  ____  ____  _  _    ____  ____    __    ___  _____  _  _ 
(  _ \(_  _)(_  _)( \/ )  (  _ \(  _ \  /__\  / __)(  _  )( \( )
 ) _ < _)(_   )(   )  (    )(_) ))   / /(__)\( (_-. )(_)(  )  ( 
(____/(____) (__) (_/\_)  (____/(_)\_)(__)(__)\___/(_____)(_)\_)
    """)
    print(Fore.RED + r"""
BUILT BY: https://github.com/fjcj0
    """)
def generate_key():
    if not os.path.exists(KEY_FILE):
        os.makedirs(HIDDEN_SERVICE_DIR, exist_ok=True)
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
def load_key():
    with open(KEY_FILE, "rb") as f:
        return f.read()
generate_key()
fernet = Fernet(load_key())
def load_users():
    if not os.path.exists(USERS_FILE):
        os.makedirs(HIDDEN_SERVICE_DIR, exist_ok=True)
        with open(USERS_FILE, "wb") as f:
            f.write(b"")
    rows = []
    with open(USERS_FILE, "rb") as f:
        data = f.read()
        if data:
            decrypted = fernet.decrypt(data).decode()
            for line in decrypted.splitlines():
                parts = line.strip().split(",")
                if len(parts) == 3:  # username,password,status
                    if parts[2] == "block":
                        blocked_users.add(parts[0])
                    rows.append(parts)
    return rows
def save_users(rows):
    data = "\n".join([",".join(row) for row in rows])
    encrypted = fernet.encrypt(data.encode())
    with open(USERS_FILE, "wb") as f:
        f.write(encrypted)
def save_user(username, password, status):
    rows = load_users()
    found = False
    for row in rows:
        if row[0] == username:
            row[1] = password
            row[2] = status
            found = True
            break
    if not found:
        rows.append([username, password, status])
    save_users(rows)
def verify_user(username, password):
    rows = load_users()
    for row in rows:
        if row[0] == username and row[1] == password:
            return True
    return False
def broadcast_message(sender, message, is_user=True):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if is_user:
        formatted = f"[{timestamp}] [+] {sender}: {message}"
    else:
        formatted = f"[{timestamp}] [+] {sender}: {message}"
    for user, conn in clients.items():
        try:
            conn.send(formatted.encode())
        except:
            remove_client(user)
def remove_client(username):
    if username in clients:
        try: clients[username].close()
        except: pass
        del clients[username]
        broadcast_message("Server", f"{username} has left the chat", is_user=False)
def handle_client(conn, addr):
    try:
        conn.send("Enter your username:".encode())
        username = conn.recv(1024).decode().strip()
        conn.send("Enter your password:".encode())
        password = conn.recv(1024).decode().strip()
        if username in blocked_users or username == ADMIN_USERNAME:
            conn.send("Username blocked. Disconnecting...".encode())
            conn.close()
            return
        if username in clients or any(u==username for u,_ in pending_users):
            conn.send("Username already connected. Disconnecting...".encode())
            conn.close()
            return
        rows = load_users()
        user_exist = any(row[0]==username for row in rows)
        if user_exist:
            if not verify_user(username, password):
                conn.send("Incorrect password. Disconnecting...".encode())
                conn.close()
                return
        pending_users.append((username, conn, password))
        print(f"New user pending approval: {username}")
        while (username, conn, password) in pending_users:
            pass
        clients[username] = conn
        user_colors[username] = random.choice(COLORS)
        save_user(username, password, "unblock")
        broadcast_message("Server", f"{username} has joined the chat", is_user=False)
        print(f"{username} connected from {addr}")
        while True:
            data = conn.recv(8192)
            if not data:
                break
            message = data.decode()
            broadcast_message(username, message, is_user=True)
    except Exception as e:
        print(f"Error with {addr}: {e}")
    finally:
        remove_client(username)
def admin_interface():
    print_logo()
    while True:
        print("\n1. Accept pending users\n2. Show connected users\n3. Block a user\n4. Exit")
        choice = input("Choice: ").strip()
        if choice=="1":
            if not pending_users: 
                print("No pending users."); continue
            for username, conn, password in pending_users.copy():
                accept = input(f"Accept {username}? (y/n): ").strip().lower()
                if accept=="y":
                    pending_users.remove((username, conn, password))
                    conn.send("accepted".encode())
                    save_user(username, password, "unblock")
                else:
                    pending_users.remove((username, conn, password))
                    conn.send("rejected".encode())
                    conn.close()
                    save_user(username, password, "block")
        elif choice=="2":
            if not clients: print("No users connected.")
            else:
                print("Connected users:")
                for user in clients.keys(): print(f" [+] {user}")
        elif choice=="3":
            user_to_block = input("Enter username to block: ").strip()
            if user_to_block in clients:
                save_user(user_to_block, "dummy_password", "block")
                blocked_users.add(user_to_block)
                remove_client(user_to_block)
                print(f"{user_to_block} has been blocked.")
            else:
                print("User not found.")
        elif choice=="4":
            break
os.makedirs(HIDDEN_SERVICE_DIR, exist_ok=True)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", PORT))
server.listen()
print(f"Server running on 127.0.0.1:{PORT}")
threading.Thread(target=admin_interface, daemon=True).start()
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()