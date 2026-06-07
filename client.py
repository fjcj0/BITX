import socks, threading
from colorama import Fore, Style, init
from crypto_chat import encrypt_message, decrypt_message
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import json
init(autoreset=True)
COLOR_MAP = {
    "RED": Fore.RED,
    "GREEN": Fore.GREEN,
    "YELLOW": Fore.YELLOW,
    "BLUE": Fore.BLUE,
    "MAGENTA": Fore.MAGENTA,
    "CYAN": Fore.CYAN,
    "WHITE": Fore.WHITE
}
session = PromptSession()
user_color = Fore.GREEN
other_colors = [Fore.RED, Fore.BLUE, Fore.CYAN, Fore.MAGENTA, Fore.YELLOW, Fore.WHITE]
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
def receive_messages(sock, username):
    while True:
        try:
            encrypted_data = sock.recv(8192)
            data = decrypt_message(encrypted_data)
            if not data:
                print(f"\n{Fore.RED}Disconnected from server.{Style.RESET_ALL}")
                sock.close()
                break
            msg = json.loads(data)
            color_code = COLOR_MAP.get(msg["color"], Fore.WHITE)
            print(
                f"{color_code}[{msg['time']}] [+] {msg['sender']}: "
                f"{Fore.CYAN}{msg['message']}{Style.RESET_ALL}"
            )
        except Exception:
            print(f"\n{Fore.RED}Disconnected from server.{Style.RESET_ALL}")
            sock.close()
            break
def main():
    print_logo()
    server_onion = input("Enter server address: ").strip()
    port = int(input("Enter server port: ").strip())
    s = socks.socksocket()
    s.set_proxy(socks.SOCKS5, "127.0.0.1", 9050)
    try:
        s.connect((server_onion, port))
    except Exception as e:
        print(f"{Fore.RED}Failed to connect: {e}{Style.RESET_ALL}")
        return
    while True:
        username = input("Enter your username: ").strip()
        if len(username) > 3:
            break
        print("Username must be more than 3 characters long.")
    password = input("Enter your password: ").strip()
    if len(password) < 3:
        print("Password must be at least 3 characters long.")
        return
    s.recv(1024)  
    s.send(encrypt_message(username))
    s.recv(1024)  
    s.send(encrypt_message(password))
    print("\nWaiting for admin approval... (you cannot chat until accepted)")
    while True:
        response = s.recv(1024).decode()
        if "accepted" in response.lower():
            print(f"{Fore.GREEN}You have been accepted!{Style.RESET_ALL}")
            break
        elif "rejected" in response.lower() or "blocked" in response.lower():
            print(f"{Fore.RED}{response}{Style.RESET_ALL}")
            s.close()
            return
    threading.Thread(target=receive_messages, args=(s, username), daemon=True).start()
    while True:
        try:
            with patch_stdout():
                msg = session.prompt(
                    f"{user_color}{username} > {Style.RESET_ALL}"
                ).strip()
            if msg.lower() == "/exit":
                s.close()
                break
            if msg:
                s.send(encrypt_message(msg))
        except Exception:
            print(f"\n{Fore.RED}Disconnected.{Style.RESET_ALL}")
            break
if __name__ == "__main__":
    main()