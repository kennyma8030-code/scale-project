from fastapi import FastAPI, UploadFile, File
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
    new_id = db.save(analytics, scale)
    return {"analytics": analytics, "id": new_id}


@app.get("/id/{id}")
def get_id(id: int):
    return db.get_id(id)

@app.get("/scales")
def get_all():
    return db.get_all()

@app.get("/trends/all")
def all_results():
    return Functions.all_trends()

@app.get("/scales/{scale}")
def get_scale(scale: str):
    return db.get_scale(scale)

@app.get("/trends/{scale}")
def scale_results(scale: str):
    return Functions.scale_trends(scale)
    



