from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from typing import Optional, Dict, Any

from arc import ARC
from nur_engine import NUREngine
from storage import init_db, log_experiment


# ---------- DATA MODELY ----------

class ARCInput(BaseModel):
    CN: float
    RU: float
    US: float


class AssetsInput(BaseModel):
    cash: float = 0.0
    real_estate: float = 0.0
    gold: float = 0.0
    stocks: float = 0.0
    crypto: float = 0.0


class AIRInput(BaseModel):
    skills: float = 0.0
    technology: float = 0.0


class NURRequest(BaseModel):
    event: Optional[str] = "manual_test"
    arc: ARCInput
    chaotic_risk: float
    assets: AssetsInput
    air: Optional[AIRInput] = None
    rsz: Optional[Dict[str, Any]] = None


# ---------- INIT ----------

app = FastAPI(
    title="DEAT · ARC · NUR Survival Engine",
    description="Behavioral stabilization and experiment logging system",
    version="0.18"
)

arc_engine = ARC()
nur_engine = NUREngine()


@app.on_event("startup")
def startup():
    init_db()


# ---------- API ENDPOINTS ----------

@app.post("/nur/evaluate")
def evaluate_nur(req: NURRequest):
    arc_reliability = arc_engine.process(req.arc.dict())

    result = nur_engine.stabilize(
        arc_reliability=arc_reliability,
        chaotic_risk=req.chaotic_risk,
        assets=req.assets.dict(),
        air=req.air.dict() if req.air else {},
        rsz=req.rsz
    )

    log_experiment(
        event_label=req.event,
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

        arc_reliability = arc_engine.process(data["arc"])

        result = nur_engine.stabilize(
            arc_reliability=arc_reliability,
            chaotic_risk=data["chaotic_risk"],
            assets=data["assets"],
            air=data.get("air", {}),
            rsz=data.get("rsz")
        )

        log_experiment(
            event_label=data.get("event", "ws_event"),
            arc=data["arc"],
            chaotic_risk=data["chaotic_risk"],
            nur_result=result,
            assets=data["assets"],
            air=data.get("air", {}),
            rsz=data.get("rsz")
        )

        await ws.send_json(result)


# ---------- STATS / DIAGNOSTICS ----------

@app.get("/stats/count")
def stats_count():
    import sqlite3
    conn = sqlite3.connect("experiment.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM experiments")
    count = c.fetchone()[0]
    conn.close()
    return {"records": count}
