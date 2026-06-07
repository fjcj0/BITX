import socks
import threading
import json
from colorama import Fore, init
from crypto_chat import encrypt_message, decrypt_message
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit import print_formatted_text
init(autoreset=True)
session = PromptSession()
def print_logo():
    print(Fore.RED + r"""
 ____  ____  ____  _  _    ____  ____    __    ___  _____  _  _
(  _ \(_  _)(_  _)( \/ )  (  _ \(  _ \  /__\  / __)(  _  )( \( )
 ) _ < _)(_   )(   )  (    )(_) ))   / /(__)\( (_-. )(_)(  )  (
(____/(____) (__) (_/\_)  (____/(_)\_)(__)(__)\___/(_____)(_)\_)
    """)
    print(Fore.RED + "BUILT BY: https://github.com/fjcj0\n")
def receive_messages(sock):
    while True:
        try:
            encrypted_data = sock.recv(8192)
            if not encrypted_data:
                print_formatted_text("\nDisconnected from server.")
                sock.close()
                break
            data = decrypt_message(encrypted_data)
            if not data:
                continue
            msg = json.loads(data)
            text = f"[{msg['time']}] {msg['sender']}: {msg['message']}"
            print_formatted_text(text)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print_formatted_text(f"ERROR: {e}")
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
        print(f"{Fore.RED}Failed to connect: {e}")
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
    print("\nWaiting for admin approval...")
    while True:
        response = s.recv(1024).decode()
        if "accepted" in response.lower():
            print(Fore.GREEN + "You have been accepted!")
            break
        if "rejected" in response.lower() or "blocked" in response.lower():
            print(Fore.RED + response)
            s.close()
            return
    threading.Thread(
        target=receive_messages,
        args=(s,),
        daemon=True
    ).start()
    with patch_stdout():
        while True:
            try:
                msg = session.prompt(f"\n\n\n{username} > ")
                if msg.lower() == "/exit":
                    s.close()
                    break
                if msg:
                    s.send(encrypt_message(msg))
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                print(f"\n{Fore.RED}Disconnected: {e}")
                break
if __name__ == "__main__":
    main()