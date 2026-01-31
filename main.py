from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import librosa
import numpy as np
import os

app = FastAPI()





app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/analyze")
def analyze_scales(audio: UploadFile=File(...)):
    return

