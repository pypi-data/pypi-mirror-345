const statusEl = document.getElementById("status");
if (statusEl) {
  statusEl.textContent = "✅ Scripts loaded and watching for reloads.";
  console.log("[HT-Serve] Live status initialized.");
} else {
  console.warn("[HT-Serve] Status element not found.");
}
