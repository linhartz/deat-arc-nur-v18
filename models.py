# models.py
from pydantic import BaseModel
from typing import Optional, Dict

class ARCInput(BaseModel):
    CN: float
    RU: float
    US: float

class Assets(BaseModel):
    real_estate: float = 0
    cash: float = 0
    bank: float = 0
    funds: float = 0
    stocks: float = 0
    gold: float = 0

class AIR(BaseModel):
    skills: float = 0
    tech: float = 0
    adaptability: float = 0

class NURRequest(BaseModel):
    arc: ARCInput
    chaotic_risk: float
    assets: Assets
    air: Optional[AIR] = None
    rsz: Optional[Dict[str, float]] = None
