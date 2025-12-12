window.onload = function () {
    let socket = null;

    function connectWS(moduleName) {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.close();
        }

        const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
        const host = window.location.host;
        const wsUrl = `${protocol}${host}/ws/${moduleName}`;

        console.log("Connecting to:", wsUrl);
        socket = new WebSocket(wsUrl);

        socket.onopen = () => console.log("WebSocket opened");
        socket.onclose = () => console.log("WebSocket closed");
        socket.onerror = (e) => console.error("WS error:", e);

        socket.onmessage = (event) => {
            document.getElementById("result").textContent = event.data;
        };
    }

    // CONNECT BUTTONS
    document.getElementById("arcBtn").onclick = () => connectWS("arc");
    document.getElementById("crBtn").onclick = () => connectWS("cr");
    document.getElementById("nurBtn").onclick = () => connectWS("nur");

    // RUN BUTTON
    document.getElementById("runBtn").onclick = () => {
        if (!socket || socket.readyState !== WebSocket.OPEN) {
            alert("WebSocket není připojen!");
            return;
        }

        const data = document.getElementById("jsonInput").value;
        socket.send(data);
    };
};
