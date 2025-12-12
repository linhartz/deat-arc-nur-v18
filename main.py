# main.py
import os
import json
import logging
from typing import Any, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deat")

app = FastAPI(title="DEAT ARC–CR–NUR Stabilizer", version="v18-resilient")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/editor", include_in_schema=False)
def serve_editor():
    editor_path = os.path.join(STATIC_DIR, "editor.html")
    if not os.path.exists(editor_path):
        return {"error": "editor.html not found in static folder"}
    return FileResponse(editor_path)


# ---------- compute helpers ----------
def safe_get_signals(payload: Dict[str, Any]):
    # supports both structured dict { "signals": { "CN":..., "RU":..., "US":... }, "adapt_delta": {...} }
    # and older style lists (not used here). Normalize to expected shape.
    if not isinstance(payload, dict):
        return {"CN": {"concentration": 0.0}, "RU": {"entropy": 0.0}, "US": {"profit_bias": 0.0}}, {}
    signals = payload.get("signals") if isinstance(payload.get("signals"), dict) else payload.get("signals", {})
    # ensure each sub-dict exists
    s_cn = signals.get("CN", {}) if isinstance(signals, dict) else {}
    s_ru = signals.get("RU", {}) if isinstance(signals, dict) else {}
    s_us = signals.get("US", {}) if isinstance(signals, dict) else {}
    adapt = payload.get("adapt_delta", {}) if isinstance(payload.get("adapt_delta", {}), dict) else {}
    return {"CN": s_cn, "RU": s_ru, "US": s_us}, adapt


def clamp01(x: float) -> float:
    try:
        return max(0.0, min(1.0, float(x)))
    except Exception:
        return 0.0


def compute_arc(payload: Dict[str, Any]) -> Dict[str, Any]:
    signals, adapt = safe_get_signals(payload)
    cn = clamp01(signals.get("CN", {}).get("concentration", 0.0))
    ru = clamp01(signals.get("RU", {}).get("entropy", 0.0))
    us = clamp01(signals.get("US", {}).get("profit_bias", 0.0))
    dr = abs(float(adapt.get("ru", 0.0) or 0.0))

    # equation: 1 - RU*0.6 + CN*0.4 - |dr|*0.5
    raw = 1.0 - ru * 0.6 + cn * 0.4 - dr * 0.5
    val = clamp01(raw)
    eq = f"1 - RU({ru})*0.6 + CN({cn})*0.4 - |dr|({dr})*0.5 = {val:.3f}"
    comment = (
        "Vysoká hodnota: populace se ztotožňuje se stabilní/agresivní politikou. "
        "Nízká hodnota: blíží se převzetí nebo revoluce."
    )
    return {"metric": "reliability", "value": round(val, 3), "equation": eq, "interpretation": comment, "raw": raw}


def compute_cr(payload: Dict[str, Any]) -> Dict[str, Any]:
    signals, adapt = safe_get_signals(payload)
    ru = clamp01(signals.get("RU", {}).get("entropy", 0.0))
    cn = clamp01(signals.get("CN", {}).get("concentration", 0.0))
    dr = abs(float(adapt.get("ru", 0.0) or 0.0))

    # equation: RU*0.7 + (1-CN)*0.3 + |dr|*0.4
    raw = ru * 0.7 + (1.0 - cn) * 0.3 + dr * 0.4
    val = clamp01(raw)
    eq = f"RU({ru})*0.7 + (1-CN({cn}))*0.3 + |dr|({dr})*0.4 = {val:.3f}"
    comment = (
        "Vysoká hodnota: CR provokatéři dokážou vyvolat systémový chaos / destabilizaci. "
        "Nízká: CR jsou směšní. Vysoká CR při vysoké ARC → provokace posílena propagandou."
    )
    return {"metric": "chaos", "value": round(val, 3), "equation": eq, "interpretation": comment, "raw": raw}


def compute_nur(payload: Dict[str, Any]) -> Dict[str, Any]:
    signals, adapt = safe_get_signals(payload)
    cn = clamp01(signals.get("CN", {}).get("concentration", 0.0))
    ru = clamp01(signals.get("RU", {}).get("entropy", 0.0))
    dr = abs(float(adapt.get("cn", 0.0) or 0.0))

    # equation: CN*0.4 + (1-RU)*0.4 - |dr|*0.2
    raw = cn * 0.4 + (1.0 - ru) * 0.4 - dr * 0.2
    val = clamp01(raw)
    eq = f"CN({cn})*0.4 + (1-RU({ru}))*0.4 - |dr|({dr})*0.2 = {val:.3f}"
    comment = (
        "Vysoká hodnota: uživatel rozumí, nezesiluje cizí propagandu; má understanding, novelty, reflection. "
        "Nízká: zranitelný vůči manipulaci."
    )
    return {"metric": "stability", "value": round(val, 3), "equation": eq, "interpretation": comment, "raw": raw}


# ---------- resilient websocket handler ----------
@app.websocket("/ws/{module}")
async def websocket_module(websocket: WebSocket, module: str):
    module_up = (module or "").upper()
    logger.info(f"WS connection request for module={module_up}")
    await websocket.accept()
    logger.info("connection accepted")
    try:
        while True:
            try:
                raw = await websocket.receive_text()
            except WebSocketDisconnect:
                logger.info("client disconnected")
                break
            except Exception as e:
                logger.exception("error receiving text")
                # keep socket open
                try:
                    await websocket.send_json({"error": "receive_error", "msg": str(e)})
                except Exception:
                    pass
                continue

            if raw is None or raw == "":
                # ignore heartbeats or empty messages
                continue

            # parse json safely
            try:
                data = json.loads(raw)
            except Exception as e:
                logger.warning("invalid json received: %s", raw)
                try:
                    await websocket.send_json({"error": "invalid_json", "msg": "Could not parse JSON"})
                except Exception:
                    pass
                continue

            # payload can be directly the payload or wrapped {"payload": {...}}
            payload = data.get("payload", data) if isinstance(data, dict) else data

            try:
                if module_up == "ARC":
                    res = compute_arc(payload)
                elif module_up == "CR":
                    res = compute_cr(payload)
                elif module_up == "NUR":
                    res = compute_nur(payload)
                else:
                    # unknown module: return helpful message, keep socket open
                    res = {"error": "unknown_module", "module": module_up}
                # send structured response
                await websocket.send_json({"module": module_up, "result": res})
            except Exception as ex:
                logger.exception("error computing result")
                try:
                    await websocket.send_json({"error": "compute_error", "msg": str(ex)})
                except Exception:
                    pass
                # continue loop (don't close)
                continue

    finally:
        logger.info("connection closed")
