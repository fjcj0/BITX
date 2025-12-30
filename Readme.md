# Encrypted Global Chat On Tor Network

This project provides an **automated Bash script** that:

* Detects the operating system (Linux / macOS)
* Installs and starts **Tor + torsocks**
* Verifies that Tor is running on **SOCKS port 9050**
* Checks for **Python / Python3** and installs them if missing
* Activates a Python virtual environment (venv)
* Installs project dependencies
* Runs the Python client **through Tor**

---

## 🧩 Requirements

* Linux (Kali / Debian / Ubuntu) or macOS
* Internet connection
* `sudo` privileges (for installation)

---

## 📦 What Does the Script Install Automatically?

### On Linux

* `tor`
* `torsocks`
* `python3`
* `python3-pip`
* `python3-venv`

### On macOS

* Homebrew (if not already installed)
* `tor`
* `torsocks`
* `python` (Python 3)

---

## ▶️ Usage

```bash
chmod +x run.sh
./run.sh
```

> ⚠️ Before running, make sure the following files exist:
>
> * `requirements.txt`
> * Virtual environment directory: `env/`
> * `client.py`

---

## 🌐 Tor Details

* Tor is used via a SOCKS proxy on:

```text
127.0.0.1:9050
```

* On macOS (Apple Silicon):

  * Tor binary is usually located at:

    ```text
    /opt/homebrew/bin/tor
    ```
  * Tor data directory:

    ```text
    /opt/homebrew/var/lib/tor
    ```

---

## 🐍 Python

* The script checks for:

  * `python`
  * `python3`

* If either one is missing, it will be installed automatically based on the OS

---

## 🔒 Security Notes (OPSEC)

* All Python network traffic is routed through Tor using `torsocks`
* No local DNS resolution is used
* It is recommended to run this script in a clean environment

---

## ❗ Important Notice

Before running the client:

* Enter the **correct onion address**
* Enter the **correct port** for the group/chat server

---

## 🛠️ Troubleshooting

### Tor is not running on port 9050

Linux:

```bash
sudo systemctl restart tor
```

macOS:

```bash
brew services restart tor
```

---

## 📄 License

This project is for **educational purposes only**.
The user is fully responsible for how it is used.

---

## ✨ Future Improvements

* Automatically create the virtual environment if missing
* Enforce minimum Python versi
