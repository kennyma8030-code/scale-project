from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from scales import Functions
import db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/analyze")
def analyze_scales(scale: str, filepath: UploadFile=File(...)):
    analytics = Functions.run(filepath, scale)
    db.save(analytics)
    
    return

@app.get("/scales")
def get_all():
    return db.get_all()

@app.get("/scales/{scale}")
def get_scale(scale: str):
    return db.get_scale(scale)

