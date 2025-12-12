let socket = null;

function connectWS(moduleName) {
    if (socket !== null && socket.readyState === WebSocket.OPEN) {
        socket.close();
    }

    const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
    const host = window.location.host;

    const wsUrl = `${protocol}${host}/ws/${moduleName}`;
    console.log("Connecting to:", wsUrl);

    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        console.log("WS opened:", wsUrl);
    };

    socket.onmessage = (event) => {
        const resultBox = document.getElementById("result");
        resultBox.textContent = event.data;
    };

    socket.onclose = () => console.log("WS closed");
    socket.onerror = (err) => console.error("WS error:", err);
}

document.getElementById("runBtn").onclick = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
        const input = document.getElementById("jsonInput").value;
        socket.send(input);
    } else {
        alert("WebSocket není připojen!");
    }
};
