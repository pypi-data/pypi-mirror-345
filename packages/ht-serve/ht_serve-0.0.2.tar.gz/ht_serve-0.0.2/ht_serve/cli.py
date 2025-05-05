import typer
import socket
import shutil
import os
import webbrowser
from rich import print as rprint
from rich.panel import Panel
from ht_serve.server import run_server

app = typer.Typer(
    name="HT-Serve",
    help=(
        "[bold cyan]HT-Serve[/bold cyan]: A secure, zero-config HTTPS server "
        "with automatic live reload for HTML/CSS/JS prototyping.\n\n"
        "Ideal for frontend dashboards, component demos, or real-time UI preview flows. "
        "Auto-generates self-signed certificates, supports WebSocket reload events, "
        "and provides clean CLI control over serve, port checks, and demo resets."
    ),
    no_args_is_help=True,
    rich_markup_mode="rich"
)

def check_port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("0.0.0.0", port)) != 0

@app.command("serve", help=(
    "Start the secure HTTPS server with live-reload enabled.\n\n"
    "- Automatically injects [bold]inject.js[/bold] into HTML for reload support\n"
    "- Watches for changes to HTML/CSS/JS files and reloads browser instantly\n"
    "- Launches browser automatically if [cyan]--open-browser[/cyan] is used\n"
    "- Enables debug logging if [cyan]--debug[/cyan] is passed"
))
def serve(
    debug: bool = typer.Option(False, "--debug", help="Enable detailed debug output to console."),
    open_browser: bool = typer.Option(False, "--open-browser", help="Launch browser to https://localhost:<port>."),
    cert_refresh: bool = typer.Option(False, "--cert-refresh", help="Force regenerate HTTPS certificates before starting.")
):
    port = int(os.getenv("DASH_PORT", 443))
    if not check_port_available(port):
        rprint("[bold red]Error: HTTPS port is already in use.[/bold red]")
        raise typer.Exit(code=1)
    if debug:
        os.environ["HT_DEBUG"] = "1"
    if cert_refresh:
        os.environ["HT_FORCE_CERT"] = "1"
    if open_browser:
        webbrowser.open(f"https://localhost:{port}")
        rprint(f"[cyan]Opening browser: https://localhost:{port}[/cyan]")
    run_server()

@app.command("check", help=(
    "Test if the default server ports are currently free.\n\n"
    "- Port 443 is used for HTTPS file serving\n"
    "- Port 8001 is used for WebSocket reload signaling"
))
def check_ports():
    ports = [int(os.getenv("DASH_PORT", 443)), 8001]
    for p in ports:
        if check_port_available(p):
            rprint(f"[green]Port {p} is available.[/green]")
        else:
            rprint(f"[red]Port {p} is currently in use.[/red]")

@app.command("reset-demo", help=(
    "Reset the default test site served by HT-Serve.\n\n"
    "- Replaces [bold]ht_serve/testsite[/bold] with a sample HTML, CSS, and JS demo\n"
    "- Use this for quickly bootstrapping a working prototype environment"
))
def reset_demo():
    demo_path = os.path.join("ht_serve", "testsite")
    if os.path.exists(demo_path):
        shutil.rmtree(demo_path)
    os.makedirs(demo_path, exist_ok=True)
    with open(os.path.join(demo_path, "index.html"), "w") as f:
        f.write("<html><body><h1>HT-Serve Demo Page</h1></body></html>")
    with open(os.path.join(demo_path, "script.js"), "w") as f:
        f.write("console.log('HT-Serve demo running.');")
    with open(os.path.join(demo_path, "styles.css"), "w") as f:
        f.write("body { background: #111; color: #0f0; padding: 2rem; font-family: sans-serif; }")
    rprint("[green]Demo site reset and regenerated.[/green]")

@app.command("about", help="Display feature summary and example usage for HT-Serve.")
def about():
    rprint(Panel.fit(
        "[bold cyan]HT-Serve - Features:[/bold cyan]\n\n"
        "• Zero-config TLS via auto-generated self-signed certificates\n"
        "• Live reload of HTML/CSS/JS on file changes\n"
        "• WebSocket-based push reload mechanism (port 8001)\n"
        "• Structured CLI interface (serve, check, reset-demo, about)\n"
        "• Health check endpoint at [green]/healthz[/green]\n"
        "• Debug mode via [bold]HT_DEBUG=1[/bold] or [cyan]--debug[/cyan]\n\n"
        "[bold magenta]Usage:[/bold magenta]\n"
        "• Start server: [yellow]ht-serve serve --open-browser[/yellow]\n"
        "• Check ports: [yellow]ht-serve check[/yellow]\n"
        "• Reset demo site: [yellow]ht-serve reset-demo[/yellow]\n",
        title="HT-Serve: Live TLS Dev Server",
        border_style="cyan"
    ))