import os
import ssl
import threading
import http.server
import socketserver
import socket
import asyncio
import websockets
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console
from rich.panel import Panel

console = Console()
logger = logging.getLogger("HTServe")
logging.basicConfig(
    level=logging.DEBUG if os.getenv("HT_DEBUG") else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

CERT_PATH = os.getenv("DASH_CERT_PATH", ".certs/cert.pem")
KEY_PATH = os.getenv("DASH_KEY_PATH", ".certs/key.pem")
PORT = int(os.getenv("DASH_PORT", 443))
RELOAD_PORT = 8001
INJECT_JS_PATH = Path(__file__).parent / "templates" / "inject.js"

class ReloadHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self._should_inject = self.path.endswith(".html")
        super().end_headers()

    def send_head(self):
        if self.path == "/healthz":
            return self.handle_healthz()

        path = self.translate_path(self.path)
        if os.path.isdir(path):
            path = os.path.join(path, "index.html")

        try:
            with open(path, "rb") as f:
                content = f.read()

            if getattr(self, "_should_inject", False) and b"</body>" in content:
                try:
                    with open(INJECT_JS_PATH, "r", encoding="utf-8") as js_file:
                        inject_script = f"<script>{js_file.read()}</script>".encode()
                    content = content.replace(b"</body>", inject_script + b"</body>")
                except Exception as e:
                    logger.warning(f"[WARN] Inject script failed: {e}")

            self.send_response(200)
            self.send_header("Content-Type", self.guess_type(path))
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return None

        except Exception as e:
            self.send_error(404, f"File not found: {e}")
            return None

    def handle_healthz(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')
        return None

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, notify_reload):
        self.notify_reload = notify_reload

    def on_any_event(self, event):
        if not event.is_directory:
            logger.info(f"File changed: {event.src_path}")
            self.notify_reload()

async def websocket_reload(notify_event, ssl_context):
    clients = set()

    async def handler(websocket, path):
        clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            clients.discard(websocket)

    async def notifier():
        while True:
            await notify_event.wait()
            notify_event.clear()
            await asyncio.gather(*(ws.send("reload") for ws in list(clients)), return_exceptions=True)

    async def ping_loop():
        while True:
            for ws in list(clients):
                try:
                    await ws.ping()
                except:
                    clients.discard(ws)
            await asyncio.sleep(30)

    server = websockets.serve(handler, "0.0.0.0", RELOAD_PORT, ssl=ssl_context)
    logger.info(f"WebSocket server listening on wss://0.0.0.0:{RELOAD_PORT}")
    await asyncio.gather(server, notifier(), ping_loop())

def run_server():
    if os.getenv("HT_FORCE_CERT") == "1":
        for cert in [CERT_PATH, KEY_PATH]:
            try:
                os.remove(cert)
            except FileNotFoundError:
                pass

    if not os.path.exists(CERT_PATH) or not os.path.exists(KEY_PATH):
        console.print("[yellow]No certificates found. Generating self-signed certs...[/yellow]")
        os.makedirs(os.path.dirname(CERT_PATH), exist_ok=True)
        os.system(
            f"openssl req -x509 -nodes -days 365 -newkey rsa:2048 "
            f"-keyout {KEY_PATH} -out {CERT_PATH} "
            f"-subj \"/C=US/ST=HT/L=Serve/O=Local/CN=localhost\""
        )
        logger.info("Self-signed certificates generated.")

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile=CERT_PATH, keyfile=KEY_PATH)

    notify_event = asyncio.Event()
    observer = Observer()
    observer.schedule(ChangeHandler(lambda: notify_event.set()), path=".", recursive=True)
    observer.start()

    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("0.0.0.0", PORT), ReloadHandler)
    httpd.socket = ssl_context.wrap_socket(httpd.socket, server_side=True)

    console.print(Panel(f"HT-Serve running on https://localhost:{PORT}", title="HT-Serve"))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    asyncio.run(websocket_reload(notify_event, ssl_context))