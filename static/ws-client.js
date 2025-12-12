console.log("WS client loaded");

const proto = location.protocol === "https:" ? "wss://" : "ws://";
const wsUrl = proto + location.host + "/ws/nur";

window.ws = new WebSocket(wsUrl);

ws.onopen = () => console.log("WS connected");

ws.onmessage = (ev) => {
    console.log("WS result:", ev.data);
    const msg = JSON.parse(ev.data);
    const module = msg.module;
    const res = msg.result;
    const numeric = Object.values(res.out)[0];

    let row = document.querySelector("#respTable tbody").insertRow(-1);
    row.insertCell(0).innerText = module + "-" + (editor.version || "A");
    row.insertCell(1).innerHTML = "<pre>"+JSON.stringify(editor.getValue(),null,2)+"</pre>";

    const c = row.insertCell(2);
    c.innerHTML = "<pre>"+JSON.stringify(res.out,null,2)+"</pre>";
    if(numeric>0.7) c.className = "green";
    else if(numeric>0.4) c.className = "orange";
    else c.className = "red";

    row.insertCell(3).innerHTML = res.comment + "\n" + res.equation;
};
