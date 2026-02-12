# Scale Tracker

A practice tool that analyzes scale recordings and tracks progress over time. Upload a recording of a major scale and get feedback on intonation, rhythmic evenness, and tempo consistency. Works with any instrument.

## What it measures

- **Intonation** — detects the notes you played and checks them against the expected scale (scored out of 7)
- **Evenness (CV)** — how consistent the timing is between notes, using coefficient of variation
- **Tempo slope** — whether you sped up or slowed down through the scale
- **Tempo consistency (r)** — how linear your tempo change was
- **Mean tempo** — average BPM across the recording

## Setup

### Backend

```bash
pip install fastapi uvicorn librosa scipy sqlalchemy pydantic numpy soundfile
python -m uvicorn main:app --reload
```

Runs on `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:5173`.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze?scale=C major` | Upload audio file, returns analysis |
| GET | `/scales` | All records |
| GET | `/scales/{scale}` | Records for a specific scale |
| GET | `/id/{id}` | Single record by ID |
| GET | `/trends/all` | Regression trends across all records |
| GET | `/trends/{scale}` | Regression trends for a specific scale |
| DELETE | `/delete` | Delete all records |



