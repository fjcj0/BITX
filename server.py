import socket, threading, os, csv, random
from cryptography.fernet import Fernet
from colorama import Fore, Style, init
from datetime import datetime
init(autoreset=True)
PORT = 5010
HIDDEN_SERVICE_DIR = "./global_chat"
ADMIN_USERNAME = "admin"
USERS_FILE = os.path.join(HIDDEN_SERVICE_DIR, "users_status.enc")
KEY_FILE = os.path.join(HIDDEN_SERVICE_DIR, "secret.key")
clients = {}
user_colors = {}
blocked_users = set()
pending_users = []
COLORS = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]
def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        os.makedirs(HIDDEN_SERVICE_DIR, exist_ok=True)
        with open(KEY_FILE, "wb") as f: f.write(key)
def load_key():
    with open(KEY_FILE, "rb") as f: return f.read()
def decrypt_file(file_path, fernet):
    if not os.path.exists(file_path): return []
    with open(file_path, "rb") as f: encrypted_data = f.read()
    if not encrypted_data: return []
    decrypted_data = fernet.decrypt(encrypted_data).decode()
    return list(csv.reader(decrypted_data.splitlines()))
def encrypt_file(file_path, rows, fernet):
    data = "\n".join([",".join(row) for row in rows])
    encrypted = fernet.encrypt(data.encode())
    with open(file_path, "wb") as f: f.write(encrypted)
def load_users():
    generate_key()
    key = load_key()
    fernet = Fernet(key)
    rows = decrypt_file(USERS_FILE, fernet)
    for row in rows:
        if len(row)==2 and row[1]=="block":
            blocked_users.add(row[0])
    return fernet, rows
def save_user(username, status, fernet, rows):
    found=False
    for row in rows:
        if row[0]==username:
            row[1]=status
            found=True
            break
    if not found: rows.append([username,status])
    encrypt_file(USERS_FILE, rows, fernet)
def broadcast(username, message):
    color = user_colors.get(username, Fore.WHITE)
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted = f"{Fore.YELLOW}[{timestamp}]{Style.RESET_ALL} {color}[+] {username}{Style.RESET_ALL}: {Fore.CYAN}{message}{Style.RESET_ALL}"
    for user in list(clients.keys()):
        conn = clients[user]
        if user not in blocked_users:
            try: conn.send(formatted.encode())
            except: remove_client(user)
def remove_client(username):
    if username in clients:
        try: clients[username].close()
        except: pass
        del clients[username]
        if username in user_colors: del user_colors[username]
        broadcast("Server", f"{username} has left the chat")
def handle_client(conn, addr, fernet, rows):
    try:
        conn.send("Enter your username: ".encode())
        username = conn.recv(1024).decode().strip()
        if username in blocked_users or username==ADMIN_USERNAME:
            conn.send("Username blocked. Disconnecting...".encode())
            conn.close()
            return
        if username in clients or any(u==username for u, _ in pending_users):
            conn.send("Username already connected. Disconnecting...".encode())
            conn.close()
            return
        pending_users.append((username, conn))
        print(f"New user pending approval: {username}")
        while (username, conn) in pending_users:
            pass  
        clients[username] = conn
        user_colors[username] = random.choice(COLORS)
        save_user(username, "unblock", fernet, rows)
        broadcast("Server", f"{username} has joined the chat")
        print(f"{username} connected from {addr}")
        while True:
            msg = conn.recv(1024).decode()
            if not msg: break
            broadcast(username, msg)
    except Exception as e:
        print(f"Error with {addr}: {e}")
    finally:
        remove_client(username)
def admin_interface(fernet, rows):
    print("\n=== Admin Interface ===")
    while True:
        print("\n1. Accept pending users\n2. Show connected users\n3. Block a user\n4. Exit")
        choice = input("Choice: ").strip()
        if choice=="1":
            if not pending_users: print("No pending users."); continue
            for username, conn in pending_users.copy():
                accept = input(f"Accept {username}? (y/n): ").strip().lower()
                if accept=="y":
                    pending_users.remove((username, conn))
                    conn.send("You have been accepted. You can start chatting.".encode())
                else:
                    pending_users.remove((username, conn))
                    conn.send("You have been rejected. Disconnecting...".encode())
                    conn.close()
                    save_user(username, "block", fernet, rows)
        elif choice=="2":
            if not clients: print("No users connected.")
            else:
                print("Connected users:")
                for user in clients.keys(): print(f" [+] {user}")
        elif choice=="3":
            user_to_block = input("Enter username to block: ").strip()
            if user_to_block in clients:
                save_user(user_to_block, "block", fernet, rows)
                blocked_users.add(user_to_block)
                remove_client(user_to_block)
                print(f"{user_to_block} has been blocked.")
            else:
                print("User not found.")
        elif choice=="4":
            break
os.makedirs(HIDDEN_SERVICE_DIR, exist_ok=True)
fernet, rows = load_users()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", PORT))
server.listen()
print(f"Server running on 127.0.0.1:{PORT}")
threading.Thread(target=admin_interface, args=(fernet, rows), daemon=True).start()
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr, fernet, rows)).start()