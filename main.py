# main.py
from fastapi import FastAPI, WebSocket
from arc import ARC
from nur_engine import NUREngine
from models import NURRequest

app = FastAPI(title="DEAT · ARC · NUR Survival Engine")

arc = ARC()
nur = NUREngine()


@app.post("/nur/evaluate")
def evaluate_nur(req: NURRequest):
    arc_rel = arc.process(req.arc.dict())
    result = nur.stabilize(
        arc_reliability=arc_rel,
        chaotic_risk=req.chaotic_risk,
        assets=req.assets.dict(),
        air=req.air.dict() if req.air else {},
        rsz=req.rsz
    )

    # ⬇️ AUTOMATICKÝ ZÁPIS
    log_experiment(
        event_label="manual_api_test",
        arc=req.arc.dict(),
        chaotic_risk=req.chaotic_risk,
        nur_result=result,
        assets=req.assets.dict(),
        air=req.air.dict() if req.air else {},
        rsz=req.rsz
    )

    return result


@app.websocket("/ws/nur")
async def nur_ws(ws: WebSocket):
    await ws.accept()
    while True:
        data = await ws.receive_json()
        arc_rel = arc.process(data["arc"])
        result = nur.stabilize(
            arc_rel,
            data["chaotic_risk"],
            data["assets"],
            data.get("air"),
            data.get("rsz")
        )

@app.get("/stats/count")
def stats_count():
    import sqlite3
    conn = sqlite3.connect("experiment.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM experiments")
    count = c.fetchone()[0]
    conn.close()
    return {"records": count}

        await ws.send_json(result)
