import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="DEAT ARC–CR–NUR Stabilizer v18", version="0.18")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Mount statických souborů
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/editor", include_in_schema=False)
def serve_editor():
    return FileResponse(os.path.join(STATIC_DIR, "editor.html"))

# -------------------------------------------------------
# Výpočetní moduly
# -------------------------------------------------------

def compute_arc(payload):
    s = payload["signals"]
    reliability = round((s[0] * 0.4 + s[1] * 0.3 + s[2] * 0.3), 3)
    return {
        "metric": "reliability",
        "value": reliability,
        "equation": f"(signals[0]*0.4 + signals[1]*0.3 + signals[2]*0.3) = {reliability}"
    }

def compute_cr(payload):
    s = payload["signals"]
    chaos = round((s[0] * 0.55 + s[1] * 0.25 + s[2] * 0.2), 3)
    return {
        "metric": "chaos",
        "value": chaos,
        "equation": f"(signals[0]*0.55 + signals[1]*0.25 + signals[2]*0.2) = {chaos}"
    }

def compute_nur(payload):
    s = payload["signals"]
    stability = round((s[0] * 0.2 + s[1] * 0.4 + s[2] * 0.4), 3)
    return {
        "metric": "stability",
        "value": stability,
        "equation": f"(signals[0]*0.2 + signals[1]*0.4 + signals[2]*0.4) = {stability}"
    }

def interpret(module, result):
    v = result["value"]

    if module == "ARC":
        if v > 0.7:
            return "Obyvatelstvo souzní s politikou → stabilní/agresivní podpora."
        elif v > 0.4:
            return "Smíšená podpora → možnost zásahu CR."
        else:
            return "Blíží se převzetí nebo revoluce."

    if module == "CR":
        if v > 0.7:
            return "Provokatéři generují systémový chaos."
        elif v > 0.4:
            return "Částečný vliv, propagandu lze tlumit."
        else:
            return "CR jsou směšní, žádná destabilizace."

    if module == "NUR":
        if v > 0.7:
            return "Uživatel rozumí, analyzuje a není zranitelný propagandou."
        elif v > 0.4:
            return "Částečně odolný, ale může být ovlivněn."
        else:
            return "Slabé porozumění, náchylnost k manipulaci."

    return "Bez interpretace."

def compute(module, payload):
    if module == "ARC":
        r = compute_arc(payload)
    elif module == "CR":
        r = compute_cr(payload)
    else:
        r = compute_nur(payload)

    r["interpretation"] = interpret(module, r)
    return r

# -------------------------------------------------------
# WebSocket server
# -------------------------------------------------------

class ConnectionManager:
    def __init__(self):
        self.active = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

manager = ConnectionManager()

@app.websocket("/ws/nur")
async def ws_handler(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_json()
            module = data["module"]
            payload = data["payload"]

            result = compute(module, payload)

            await ws.send_json(result)
    except WebSocketDisconnect:
        manager.disconnect(ws)

# Lokální běh
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
