# **BITX**

![BITX Logo](public/logo.png)

**BITX** is a secure, **Tor**-based networking chat application built with **Python 3**. It allows users to connect and chat anonymously over the **Tor network**, supporting **Linux** and **macOS** platforms.

---

## **Features**

* **Tor-network compatible** using **SOCKS5 proxy**.
* **Real-time chat** with multiple users.
* **Admin interface** for approving or blocking users.
* **Encrypted user credentials** using **Fernet (symmetric encryption)**.
* **Color-coded usernames** for easier readability.
* Works on **Linux** and **macOS**.
* Lightweight and simple **Python 3** implementation.

---

## **Table of Contents**

1. [Installation](#installation)
2. [Server Setup](#server-setup)
3. [Client Usage](#client-usage)
4. [Admin Interface](#admin-interface)
5. [Security](#security)
6. [Dependencies](#dependencies)
7. [License](#license)

---

## **Installation**

1. Clone the repository:

```bash
git clone https://github.com/fjcj0/BITX.git
cd BITX
```

2. Install required Python packages:

```bash
pip install -r requirements.txt
```

**Required packages:**

* **colorama**
* **cryptography**
* **PySocks**

3. Make sure **Tor** is installed and running on `127.0.0.1:9050` for **SOCKS5 proxy**.

---

## **Server Setup**

1. Navigate to the project directory:

```bash
cd BITX
```

2. Run the server script:

```bash
python server.py
```

3. Server will start on **127.0.0.1:5010** (default) and wait for clients to connect.

4. The **admin interface** runs in a separate thread, allowing you to:

   * **Accept or reject pending users**
   * **View connected users**
   * **Block unwanted users**
   * **Exit** the admin interface safely

---

## **Client Usage**

1. Run the client script:

```bash
python client.py
```

2. Enter the **server address** (e.g., `127.0.0.1`) and **port** (default `5010`).
3. Enter your **username** (minimum 4 characters) and **password** (minimum 3 characters).
4. Wait for **admin approval**. Only accepted users can chat.
5. Chat commands:

* `/exit` → Disconnect from the server.

**Notes:**

* Usernames are **color-coded**.
* Messages from other users are displayed in **random colors**.

---

## **Admin Interface**

Once the server is running, the **admin interface** allows you to manage users:

1. **Accept pending users** – Review and approve or reject new users.
2. **Show connected users** – List all currently connected users.
3. **Block a user** – Immediately block and disconnect a user.
4. **Exit** – Close the admin interface.

Blocked users are stored in **encrypted storage** and cannot reconnect without being unblocked manually.

---

## **Security**

* User credentials are stored **encrypted** using **Fernet symmetric encryption**.
* Only **approved users** can join the chat.
* Supports **Tor network connections** via **SOCKS5 proxy**, keeping IPs anonymous.
* Admin can **block users** in real-time, preventing unauthorized access.

---

## **Dependencies**

* **Python 3.x**
* [**colorama**](https://pypi.org/project/colorama/) – for colored terminal output
* [**cryptography**](https://pypi.org/project/cryptography/) – for encrypting user data
* [**PySocks**](https://pypi.org/project/PySocks/) – for Tor **SOCKS5 proxy**

Install all dependencies with:

```bash
pip install colorama cryptography pysocks
```

---

## **Project Structure**

```
BITX/
├─ server.py             # Main server script
├─ client.py             # Client connection script
├─ public/
│  ├─ logo.png           # Project logo
│  └─ example.png        # Example screenshot
├─ global_chat/          # Hidden service directory
│  ├─ secret.key         # Encryption key
│  └─ users_status.enc   # Encrypted user database
├─ README.md             # Project documentation
└─ requirements.txt      # Python dependencies
```

---

## **License**

This project is **MIT licensed** – free to use, modify, and share.

---

## **Author**

**BITX** is developed and maintained by [**fjcj0**](https://github.com/fjcj0).

![Example Screenshot](public/example.png)