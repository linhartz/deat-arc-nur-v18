# main.py
import os
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title='DEAT ARC–NUR Stabilizer', version='0.2')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# /editor endpoint
@app.get("/editor", include_in_schema=False)
def serve_editor():
    editor_path = os.path.join(STATIC_DIR, "editor.html")
    if not os.path.exists(editor_path):
        return {"error": "editor.html not found in static folder"}
    return FileResponse(editor_path)

# ------------------------
# WebSocket manager
# ------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        living = []
        for conn in self.active_connections:
            try:
                await conn.send_text(message)
                living.append(conn)
            except Exception:
                pass
        self.active_connections = living

manager = ConnectionManager()

@app.websocket("/ws/nur")
async def websocket_nur(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            data = json.loads(msg)
            module = data["module"]
            payload = data["payload"]
            result = compute_result(module, payload)
            await websocket.send_json({
                "module": module,
                "result": result
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ------------------------
# Výpočet výsledků s interpretací
# ------------------------
def compute_result(module, payload):
    s = payload.get("signals", {})
    d = payload.get("adapt_delta", {})

    if module == "ARC":
        rel = 1 - (s.get("RU", {}).get("entropy",0)*0.6) + \
                  (s.get("CN", {}).get("concentration",0)*0.4) - abs(d.get("ru",0))*0.5
        rel = max(0, min(1, rel))
        equation = f"1 - RU_entropy*0.6 + CN_concentration*0.4 - |adapt_delta_ru|*0.5 = {rel:.3f}"
        comment = ("Vysoká hodnota ukazuje, že politika “stabilní” nebo “agresivní” "
                   "a populace se ztotožňuje. Nízká hodnota → možnost převzetí nebo revoluce.")
        return {"out":{"reliability": rel}, "equation": equation, "comment": comment}

    if module == "CR":
        ch = s.get("RU", {}).get("entropy",0)*0.7 + \
             (1 - s.get("CN", {}).get("concentration",0))*0.3 + abs(d.get("ru",0))*0.4
        ch = max(0, min(1, ch))
        equation = f"RU_entropy*0.7 + (1-CN_concentration)*0.3 + |adapt_delta_ru|*0.4 = {ch:.3f}"
        comment = ("Vysoká hodnota ukazuje schopnost CR provokatérů vyvolat systémový chaos / destabilizaci. "
                   "Nízká hodnota → jsou směšní. Vysoká CR při vysoké ARC → provokace posílena propagandou.")
        return {"out":{"chaos": ch}, "equation": equation, "comment": comment}

    if module == "NUR":
        st = (s.get("CN", {}).get("concentration",0)*0.4) + \
             (1 - s.get("RU", {}).get("entropy",0))*0.4 - abs(d.get("cn",0))*0.2
        st = max(0, min(1, st))
        equation = f"CN_concentration*0.4 + (1-RU_entropy)*0.4 - |adapt_delta_cn|*0.2 = {st:.3f}"
        comment = ("Vysoká hodnota → uživatel rozumí informacím, netýká se ho propaganda ARC ani chaos CR, "
                   "dokáže porozumět (understanding), zvládnout akci (novelty) a testovat účinnost (reflection).")
        return {"out":{"stability": st}, "equation": equation, "comment": comment}

    return {"error": "Unknown module"}

# ------------------------
# Lokální run / Railway port
# ------------------------
if __name__ == "__main__":
    import uvico
