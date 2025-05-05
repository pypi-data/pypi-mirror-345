(function connectLiveReload() {
  const ws = new WebSocket(`wss://${location.hostname}:8001`);

  ws.onopen = () => {
    console.log("[HT-Serve] Live reload connected.");
  };

  ws.onmessage = () => {
    console.log("[HT-Serve] Reload triggered.");
    location.reload();
  };

  ws.onerror = err => {
    console.warn("[HT-Serve] WebSocket error:", err);
  };

  ws.onclose = () => {
    console.warn("[HT-Serve] Connection closed. Reconnecting in 3s...");
    setTimeout(connectLiveReload, 3000);
  };
})();