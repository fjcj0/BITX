import socks, socket, threading, random, sys
from colorama import Fore, Style, init
init(autoreset=True)
user_color = Fore.GREEN
other_colors = [Fore.RED, Fore.BLUE, Fore.CYAN, Fore.MAGENTA, Fore.YELLOW, Fore.WHITE]
user_colors = {}
def receive_messages(sock, my_username):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                print(f"\n{Fore.RED}Disconnected from server.{Style.RESET_ALL}")
                sock.close()
                break
            if "rejected" in msg.lower() or "blocked" in msg.lower():
                print(f"\n{Fore.RED}{msg}{Style.RESET_ALL}")
                sock.close()
                break
            if msg.startswith("[+]"):
                parts = msg.split(":", 1)
                if len(parts) == 2:
                    user_part, msg_part = parts
                    username = user_part.replace("[+]", "").strip()
                    if username != my_username and username not in user_colors:
                        user_colors[username] = random.choice(other_colors)
                    color = user_colors.get(username, Fore.WHITE)
                    sys.stdout.write(f"\r{color}[+] {username}{Style.RESET_ALL}: {Fore.CYAN}{msg_part.strip()}{Style.RESET_ALL}\n")
                    sys.stdout.write(f"{user_color}{my_username} > {Style.RESET_ALL}")
                    sys.stdout.flush()
                    continue
            sys.stdout.write(f"\r{msg}\n{user_color}{my_username} > {Style.RESET_ALL}")
            sys.stdout.flush()
        except Exception:
            print(f"\n{Fore.RED}Disconnected from server.{Style.RESET_ALL}")
            sock.close()
            break
def main():
    print(f"{Fore.CYAN}=== Global Chat Client ==={Style.RESET_ALL}")
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
    s.send(username.encode())
    print("\nWaiting for admin approval... (you cannot chat until accepted)")
    threading.Thread(target=receive_messages, args=(s, username), daemon=True).start()
    while True:
        try:
            msg = input(f"{user_color}{username} > {Style.RESET_ALL}").strip()
            if msg.lower() == "/exit":
                s.close()
                break
            if msg:
                s.send(msg.encode())
        except Exception:
            print(f"\n{Fore.RED}Disconnected.{Style.RESET_ALL}")
            break
if __name__ == "__main__":
    main()