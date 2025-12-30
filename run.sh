#!/bin/bash
set -e
echo "[+] Detecting OS..."
OS="$(uname -s)"
detect_tor() {
    if command -v tor >/dev/null 2>&1; then
        TOR_BIN="$(command -v tor)"
    elif [ -x "/opt/homebrew/bin/tor" ]; then
        TOR_BIN="/opt/homebrew/bin/tor"
    else
        TOR_BIN=""
    fi
}
install_linux() {
    echo "[+] Installing Tor on Linux..."
    sudo apt update
    sudo apt install -y tor torsocks
    sudo systemctl enable tor
    sudo systemctl start tor
}
install_mac() {
    echo "[+] Installing Tor on macOS..."
    if ! command -v brew >/dev/null 2>&1; then
        echo "[!] Homebrew not found. Installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew update
    brew install tor torsocks
    brew services start tor
}
detect_tor
if [ -z "$TOR_BIN" ]; then
    case "$OS" in
        Linux*)  install_linux ;;
        Darwin*) install_mac ;;
        *)
            echo "[!] Unsupported OS"
            exit 1
            ;;
    esac
else
    echo "[+] Tor already installed at: $TOR_BIN"
fi
echo "[+] Checking Tor SOCKS port (9050)..."
sleep 2
if [[ "$OS" == "Linux" ]]; then
    ss -lnt 2>/dev/null | grep -q ':9050'
elif [[ "$OS" == "Darwin" ]]; then
    netstat -an | grep -q '\.9050 .*LISTEN'
fi
if [ $? -ne 0 ]; then
    echo "[!] Tor is NOT running on port 9050"
    echo "    Linux: sudo systemctl restart tor"
    echo "    macOS: brew services restart tor"
    exit 1
fi
echo "[✓] Tor is running on port 9050"
echo "[+] Checking Python installation..."
install_python_linux() {
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
}
install_python_mac() {
    brew install python
}
if ! command -v python >/dev/null 2>&1; then
    echo "[!] python not found"
    case "$OS" in
        Linux*)  install_python_linux ;;
        Darwin*) install_python_mac ;;
    esac
else
    echo "[✓] python found"
fi
if ! command -v python3 >/dev/null 2>&1; then
    echo "[!] python3 not found"
    case "$OS" in
        Linux*)  install_python_linux ;;
        Darwin*) install_python_mac ;;
    esac
else
    echo "[✓] python3 found"
fi
echo "[+] Activating virtual environment..."
if [ -f "env/bin/activate" ]; then
    source env/bin/activate
else
    echo "[!] Virtual environment not found (env/bin/activate)"
    exit 1
fi
echo "[+] Upgrading pip..."
pip install --upgrade pip
echo "[+] Installing requirements (python)..."
pip install -r requirements.txt
echo "[+] Installing requirements (python3)..."
pip3 install -r requirements.txt
echo "[!] Do not forget to enter the correct onion URL and port"
echo "[+] Joining server..."
sleep 1
if [[ "$OS" == "Darwin" ]]; then
    echo "[+] macOS detected → running via torsocks"
    exec torsocks python3 client.py
else
    echo "[+] Linux detected → running normally"
    exec python3 client.py
fi