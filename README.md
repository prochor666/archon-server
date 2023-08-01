# 👽 Archon server

Content and device control server

---

## ✅ Prerequisities

* Python 3.10.0+ is installed
* Python Pip is installed
* MongoDb is installed

---

## 💾 Installation

This guide shows, how to install the server.

### 💻 Linux & Mac

```bash
cd /opt
git clone https://github.com/prochor666/archon-server.git
cd archon-server
chmod +x preinstall install
./preinstall
./install
```
Later use `archon-update.sh` for system update:
```bash
cd /opt
./archon-update.sh
```


### 💻 Windows 

```powershell
.\install.cmd
```

---

## 🚀 Running the server

Running the webserver guide.

### 💻 Linux & Mac

Only for development, installer creates Linux service automaticaly

```bash
cd /opt/archon-server
./server
```
Or regular service control

```bash
systemctl status archon-server
```
```bash
systemctl restart archon-server
```
```bash
systemctl start archon-server
```
```bash
systemctl stop archon-server
```


### 💻 Windows 

```powershell
.\server.cmd
```

---

## 🧪 CLI (Commnad line interface)

Command line interface. 

How to run (and command list incoming **soon**).

### 💻 Linux & Mac

Global command

```bash
arc command [-argument argument_value]
```

or in your archon home /opt/archon-server

```bash
./arc command [-argument argument_value]
```

### 💻 Windows 

```powershell
.\arc.cmd command [-argument argument_value]
```

---

## 🧪 Commands

### 💻 Linux & Mac

```bash
arc help
```
### 💻 Windows 

```powershell
.\arc.cmd help
```

