// static/ws-client.js
window.onload = function () {
  let socket = null;
  let currentModule = "ARC";
  let currentVariant = "A";

  function buildWsUrl(moduleName) {
    const proto = (window.location.protocol === "https:") ? "wss://" : "ws://";
    // Module in path should be uppercase to match logging (server handles case-insensitive)
    const pathModule = moduleName.toUpperCase();
    return `${proto}${window.location.host}/ws/${pathModule}`;
  }

  function connect(moduleName) {
    if (socket && socket.readyState === WebSocket.OPEN) {
      try { socket.close(); } catch (e) { /* ignore */ }
    }

    const url = buildWsUrl(moduleName);
    console.log("Connecting WS:", url);
    try {
      socket = new WebSocket(url);
    } catch (e) {
      console.error("Failed to construct WebSocket:", e);
      updateStatus(false);
      return;
    }

    socket.onopen = () => {
      console.log("WS connected");
      updateStatus(true);
    };

    socket.onmessage = (ev) => {
      // Expect server JSON: { module: "ARC", result: { ... } }
      try {
        const msg = JSON.parse(ev.data);
        renderResponse(msg);
      } catch (e) {
        console.error("Invalid WS payload", ev.data);
      }
    };

    socket.onerror = (err) => {
      console.error("WS error:", err);
    };

    socket.onclose = (ev) => {
      console.log("WS closed");
      updateStatus(false);
      // try reconnect after small delay
      setTimeout(() => connect(currentModule), 1500);
    };
  }

  function updateStatus(connected) {
    const s = document.getElementById("status");
    if (!s) return;
    if (connected) {
      s.textContent = "WS připojen";
      s.style.color = "green";
    } else {
      s.textContent = "WS není připojen";
      s.style.color = "red";
    }
  }

  function loadPreset(module, variant) {
    const presets = {
      "ARC": {
        "A": { "signals": { "CN": {"concentration": 0.9}, "RU": {"entropy": 0.2}, "US": {"profit_bias": 0.4} }, "adapt_delta": {"cn": 0.01, "ru": -0.01} },
        "B": { "signals": { "CN": {"concentration": 0.5}, "RU": {"entropy": 0.6}, "US": {"profit_bias": 0.2} }, "adapt_delta": {"cn": 0.02, "ru": 0.03} }
      },
      "CR": {
        "A": { "signals": { "CN": {"concentration": 0.2}, "RU": {"entropy": 0.9}, "US": {"profit_bias": 0.6} }, "adapt_delta": {"cn": -0.01, "ru": 0.05} },
        "B": { "signals": { "CN": {"concentration": 0.4}, "RU": {"entropy": 0.5}, "US": {"profit_bias": 0.3} }, "adapt_delta": {"cn": 0.0, "ru": 0.02} }
      },
      "NUR": {
        "A": { "signals": { "CN": {"concentration": 0.8}, "RU": {"entropy": 0.1}, "US": {"profit_bias": 0.5} }, "adapt_delta": {"cn": 0.0, "ru": 0.0} },
        "B": { "signals": { "CN": {"concentration": 0.3}, "RU": {"entropy": 0.6}, "US": {"profit_bias": 0.2} }, "adapt_delta": {"cn": 0.02, "ru": 0.01} }
      }
    };

    const payload = presets[module][variant];
    document.getElementById("jsonInput").value = JSON.stringify(payload, null, 2);
    const label = document.getElementById("labelVariant");
    if (label) label.textContent = `${module} – ${variant}`;
  }

  function renderResponse(msg) {
    const module = msg.module || currentModule;
    const res = msg.result || msg;
    const numeric = res.value !== undefined ? res.value : (res.out ? Object.values(res.out)[0] : 0);

    const tbody = document.querySelector("#respTable tbody");
    if (!tbody) return;

    const row = tbody.insertRow(-1);
    row.insertCell(0).innerText = `${module} – ${currentVariant}`;
    row.insertCell(1).innerHTML = "<pre>" + document.getElementById("jsonInput").value + "</pre>";

    const outCell = row.insertCell(2);
    outCell.innerHTML = "<pre>" + JSON.stringify({ [res.metric || "value"]: res.value }, null, 2) + "</pre>";
    if (numeric > 0.7) outCell.className = "green";
    else if (numeric > 0.4) outCell.className = "orange";
    else outCell.className = "red";

    row.insertCell(3).innerHTML = "<pre>" + (res.equation || "") + "</pre>";
    row.insertCell(4).innerText = res.interpretation || "";

    // scroll to bottom
    row.scrollIntoView({ behavior: "smooth", block: "end" });
  }

  // UI wiring
  document.getElementById("arcBtn")?.addEventListener("click", function () {
    currentModule = "ARC"; connect(currentModule); loadPresetAndLabel();
  });
  document.getElementById("crBtn")?.addEventListener("click", function () {
    currentModule = "CR"; connect(currentModule); loadPresetAndLabel();
  });
  document.getElementById("nurBtn")?.addEventListener("click", function () {
    currentModule = "NUR"; connect(currentModule); loadPresetAndLabel();
  });

  document.getElementById("aBtn")?.addEventListener("click", function () {
    currentVariant = "A"; loadPresetAndLabel();
  });
  document.getElementById("bBtn")?.addEventListener("click", function () {
    currentVariant = "B"; loadPresetAndLabel();
  });

  document.getElementById("runBtn")?.addEventListener("click", function () {
    let payload = null;
    try {
      payload = JSON.parse(document.getElementById("jsonInput").value);
    } catch (e) {
      alert("Neplatný JSON");
      return;
    }
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      alert("WebSocket není připojen");
      return;
    }
    // send wrapper object with payload for uniform server handling
    socket.send(JSON.stringify({ payload: payload }));
  });

  function loadPresetAndLabel() {
    loadPreset(currentModule, currentVariant);
  }

  // initial state
  updateStatus(false);
  loadPresetAndLabel();
  // connect to default module
  connect(currentModule);
}; // window.onload end
