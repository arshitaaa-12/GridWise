from pydantic import BaseModel
from typing import List

class Reading(BaseModel):
    timestamp: str
    consumption_kwh: float
    temperature_c: float = 25.0
    humidity_pct: float = 50.0

class ForecastRequest(BaseModel):
    history: List[Reading]
    horizon: int = 24

class AnomalyRequest(BaseModel):
    history: List[Reading]
    residual_threshold: float = 2.5