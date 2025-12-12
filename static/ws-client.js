// static/ws-client.js
window.onload = function(){
  let socket = null;
  let currentModule = "ARC";
  let currentVariant = "A";

  function connect(moduleName){
    if(socket && socket.readyState === WebSocket.OPEN){
      socket.close();
    }
    const proto = window.location.protocol === "https:" ? "wss://" : "ws://";
    const url = proto + window.location.host + "/ws/" + moduleName.toLowerCase();
    console.log("Connecting WS:", url);
    socket = new WebSocket(url);

    socket.onopen = () => {
      console.log("WS connected");
      document.getElementById("status").textContent = "WS připojen";
      document.getElementById("status").style.color = "green";
    };
    socket.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        handleResponse(msg);
      } catch(e){
        console.error("Invalid WS message", e, ev.data);
      }
    };
    socket.onclose = () => {
      console.log("WS closed");
      document.getElementById("status").textContent = "WS není připojen";
      document.getElementById("status").style.color = "red";
      setTimeout(()=>connect(currentModule), 1500);
    };
    socket.onerror = (err) => {
      console.error("WS error:", err);
    };
  }

  // UI buttons
  document.getElementById("arcBtn")?.addEventListener("click", ()=>{
    currentModule = "ARC"; connect(currentModule);
  });
  document.getElementById("crBtn")?.addEventListener("click", ()=>{
    currentModule = "CR"; connect(currentModule);
  });
  document.getElementById("nurBtn")?.addEventListener("click", ()=>{
    currentModule = "NUR"; connect(currentModule);
  });

  // presets A/B buttons
  document.getElementById("aBtn")?.addEventListener("click", ()=>{
    currentVariant = "A";
    loadPreset(currentModule, "A");
  });
  document.getElementById("bBtn")?.addEventListener("click", ()=>{
    currentVariant = "B";
    loadPreset(currentModule, "B");
  });

  // send
  document.getElementById("runBtn")?.addEventListener("click", ()=>{
    let payload;
    try { payload = JSON.parse(document.getElementById("jsonInput").value); }
    catch(e){ alert("Neplatný JSON"); return; }
    if(!socket || socket.readyState !== WebSocket.OPEN){ alert("WebSocket není připojen"); return; }
    socket.send(JSON.stringify({ payload: payload }));
  });

  function loadPreset(module, variant){
    const presets = {
      ARC: {
        A: { signals: { CN:{concentration:0.9}, RU:{entropy:0.2}, US:{profit_bias:0.4} }, adapt_delta:{cn:0.01,ru:-0.01} },
        B: { signals: { CN:{concentration:0.5}, RU:{entropy:0.6}, US:{profit_bias:0.2} }, adapt_delta:{cn:0.02,ru:0.03} }
      },
      CR: {
        A: { signals: { CN:{concentration:0.2}, RU:{entropy:0.9}, US:{profit_bias:0.6} }, adapt_delta:{cn:-0.01,ru:0.05} },
        B: { signals: { CN:{concentration:0.4}, RU:{entropy:0.5}, US:{profit_bias:0.3} }, adapt_delta:{cn:0.0,ru:0.02} }
      },
      NUR: {
        A: { signals: { CN:{concentration:0.8}, RU:{entropy:0.1}, US:{profit_bias:0.5} }, adapt_delta:{cn:0.0,ru:0.0} },
        B: { signals: { CN:{concentration:0.3}, RU:{entropy:0.6}, US:{profit_bias:0.2} }, adapt_delta:{cn:0.02,ru:0.01} }
      }
    };
    document.getElementById("jsonInput").value = JSON.stringify(presets[module][variant], null, 2);
    document.getElementById("labelVariant").textContent = module + " – " + variant;
  }

  function handleResponse(msg){
    const module = msg.module || currentModule;
    const res = msg.result || {};
    const numeric = res.value || (res.out && Object.values(res.out)[0]) || 0;

    const tbody = document.querySelector("#respTable tbody");
    const row = tbody.insertRow(-1);

    row.insertCell(0).innerText = module + " – " + currentVariant;
    row.insertCell(1).innerHTML = "<pre>" + document.getElementById("jsonInput").value + "</pre>";

    const outCell = row.insertCell(2);
    outCell.innerHTML = "<pre>" + JSON.stringify({[res.metric || "value"]: res.value}, null, 2) + "</pre>";
    if(numeric > 0.7) outCell.className = "green";
    else if(numeric > 0.4) outCell.className = "orange";
    else outCell.className = "red";

    row.insertCell(3).innerHTML = "<pre>" + (res.equation || (res.out && res.equation)) + "</pre>";
    row.insertCell(4).innerText = res.interpretation || res.comment || "";

    // scroll last into view
    row.scrollIntoView({behavior:"smooth", block:"end"});
  }

  // initial UI state
  document.getElementById("labelVariant") && (document.getElementById("labelVariant").textContent = currentModule + " – " + currentVariant);
  connect(currentModule);
  loadPreset(currentModule, currentVariant);
}; // window.onload end
