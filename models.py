from pydantic import BaseModel 

class analytics(BaseModel):
    intonation: list[dict]
    cv_evenness: int
    tempo_slope: float
    tempo_r: float