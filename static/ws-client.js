let ws = null;
let lastModule = "";
let lastVariant = "";

function loadSample(module, variant) {
    lastModule = module;
    lastVariant = variant;

    const presets = {
        "ARC": {
            "A": { "signals": [0.9, 0.8, 0.7] },
            "B": { "signals": [0.5, 0.4, 0.3] }
        },
        "CR": {
            "A": { "signals": [0.8, 0.6, 0.55] },
            "B": { "signals": [0.4, 0.35, 0.3] }
        },
        "NUR": {
            "A": { "signals": [0.7, 0.8, 0.85] },
            "B": { "signals": [0.3, 0.4, 0.5] }
        }
    };

    document.getElementById("jsonInput").value = JSON.stringify(
        presets[module][variant],
        null,
        2
    );
}

function connectWS() {
    ws = new WebSocket(`ws://${location.host}/ws/nur`);

    ws.onopen = () => {
        document.getElementById("status").textContent = "WebSocket připojen";
        document.getElementById("status").className = "good";
    };

    ws.onmessage = (ev) => {
        const data = JSON.parse(ev.data);
        addResult(data);
    };

    ws.onclose = () => {
        document.getElementById("status").textContent = "WebSocket není připojen";
        document.getElementById("status").className = "bad";
        setTimeout(connectWS, 2000);
    };
}

function send() {
    if (!ws || ws.readyState !== 1) {
        alert("WebSocket není připojen");
        return;
    }

    const payload = JSON.parse(document.getElementById("jsonInput").value);

    ws.send(JSON.stringify({
        module: lastModule,
        payload: payload
    }));
}

function addResult(r) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
        <td>${lastModule} – ${lastVariant}</td>
        <td>${r.metric}</td>
        <td>${r.value}</td>
        <td><pre>${r.equation}</pre></td>
        <td>${r.interpretation}</td>
    `;
    document.getElementById("results").appendChild(tr);
}

connectWS();
