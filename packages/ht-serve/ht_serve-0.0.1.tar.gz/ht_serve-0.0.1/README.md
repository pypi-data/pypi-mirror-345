# HT-Serve

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

**HT-Serve** is a secure HTTPS file server with live reload support, built for UI/dashboard prototyping. It enables frontend developers to test real-time changes under TLS with zero configuration, WebSocket-triggered reloads, and a CLI interface for orchestration.

---

## 🔧 Features

- 🔒 Auto HTTPS via self-signed certificates (or use custom certs)
- 🔁 WebSocket-based live reload on file changes
- 🧩 Automatic HTML injection of live-reload script
- 🧪 Built-in test UI (`ht-serve reset-demo`)
- 🔍 Health check endpoint at `/healthz`
- 🧠 CLI interface with `serve`, `check`, and `reset-demo`
- 🧾 Production-grade logging and debug mode (`HT_DEBUG=1`)

---

## 📦 Installation

```bash
pip install .
```

---

## 🚀 Usage

Launch the development server:

```bash
ht-serve serve --open-browser
```

Check if HTTPS/WebSocket ports are available:

```bash
ht-serve check
```

Reset and regenerate a demo UI site:

```bash
ht-serve reset-demo
```

---

## ⚙️ Environment Variables

| Variable         | Description                                                     |
|------------------|-----------------------------------------------------------------|
| `DASH_CERT_PATH` | Full path to the HTTPS certificate (`.pem`)                    |
| `DASH_KEY_PATH`  | Full path to the HTTPS private key (`.key`)                    |
| `DASH_PORT`      | Port to serve HTTPS on (default: `443`; fallback: `8443`)      |
| `HT_DEBUG`       | Set to `1` to enable verbose logging and file event tracking   |
| `HT_FORCE_CERT`  | Set to `1` to regenerate the TLS cert/key on next launch       |

---

## 📁 Directory Structure

```
HT-Serve/
├── ht_serve/
│   ├── cli.py               # Typer-based CLI commands
│   ├── server.py            # Core HTTPS + WebSocket server logic
│   ├── templates/
│   │   └── inject.js        # Injected live-reload script
│   └── testsite/            # Sample demo UI assets
├── pyproject.toml
├── requirements.txt
├── setup.py
└── README.md
```

---

## 🪪 License

MIT © [HermiTech Labs](https://github.com/HermiTech-LLC)
