# main.py
import os
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="DEAT ARC–CR–NUR Stabilizer", version="0.18")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/editor", include_in_schema=False)
def serve_editor():
    return FileResponse(os.path.join(STATIC_DIR, "editor.html"))

# ---- compute functions (named members in equations) ----
def compute_arc(payload):
    s = payload.get("signals", {})
    d = payload.get("adapt_delta", {})
    cn = s.get("CN", {}).get("concentration", 0.0)
    ru = s.get("RU", {}).get("entropy", 0.0)
    us = s.get("US", {}).get("profit_bias", 0.0)
    dr = abs(d.get("ru", 0.0))
    # equation: 1 - RU*0.6 + CN*0.4 - |dr|*0.5
    value = max(0.0, min(1.0, 1 - ru*0.6 + cn*0.4 - dr*0.5))
    eq = f"1 - RU({ru})*0.6 + CN({cn})*0.4 - |dr|({dr})*0.5 = {value:.3f}"
    comment = ("Vysoká hodnota: populace se ztotožňuje se stabilní/agresivní politikou. "
               "Nízká hodnota: blíží se převzetí nebo revoluce.")
    return {"metric":"reliability","value":round(value,3),"equation":eq,"interpretation":comment}

def compute_cr(payload):
    s = payload.get("signals", {})
    d = payload.get("adapt_delta", {})
    ru = s.get("RU", {}).get("entropy", 0.0)
    cn = s.get("CN", {}).get("concentration", 0.0)
    dr = abs(d.get("ru", 0.0))
    # equation: RU*0.7 + (1-CN)*0.3 + |dr|*0.4
    value = max(0.0, min(1.0, ru*0.7 + (1-cn)*0.3 + dr*0.4))
    eq = f"RU({ru})*0.7 + (1-CN({cn}))*0.3 + |dr|({dr})*0.4 = {value:.3f}"
    comment = ("Vysoká hodnota: CR provokatéři dokážou vyvolat systémový chaos. "
               "Nízká: CR jsou směšní. Vysoká CR při vysoké ARC → provokace posílena propagandou.")
    return {"metric":"chaos","value":round(value,3),"equation":eq,"interpretation":comment}

def compute_nur(payload):
    s = payload.get("signals", {})
    d = payload.get("adapt_delta", {})
    cn = s.get("CN", {}).get("concentration", 0.0)
    ru = s.get("RU", {}).get("entropy", 0.0)
    dr = abs(d.get("cn", 0.0))
    # equation: CN*0.4 + (1-RU)*0.4 - |dr|*0.2
    value = max(0.0, min(1.0, cn*0.4 + (1-ru)*0.4 - dr*0.2))
    eq = f"CN({cn})*0.4 + (1-RU({ru}))*0.4 - |dr|({dr})*0.2 = {value:.3f}"
    comment = ("Vysoká hodnota: uživatel rozumí, nezesiluje cizí propagandu; má understanding, novelty, reflection. "
               "Nízká: zranitelný vůči manipulaci.")
    return {"metric":"stability","value":round(value,3),"equation":eq,"interpretation":comment}

# ---- websocket endpoint accepting module path param ----
@app.websocket("/ws/{module}")
async def websocket_module(websocket: WebSocket, module: str):
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except Exception:
                await websocket.send_json({"error":"invalid json"})
                continue

            module_up = module.upper()
            if module_up == "ARC":
                res = compute_arc(data.get("payload", data))
            elif module_up == "CR":
                res = compute_cr(data.get("payload", data))
            elif module_up == "NUR":
                res = compute_nur(data.get("payload", data))
            else:
                res = {"error":"unknown module"}

            await websocket.send_json({"module": module_up, "result": res})
    except WebSocketDisconnect:
        return

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
