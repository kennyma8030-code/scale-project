from pydantic import BaseModel 

class analytics(BaseModel):
    intonation: list[dict]
    cv_evenness: float
    tempo_slope: float
    tempo_r: float
    mean_tempo: float