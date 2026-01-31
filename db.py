from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

Base = declarative_base()

class Scales(Base):
    __tablename__ = "scales"
    id = Column(Integer, primary_key=True)
    date = Column(String)
    scale = Column(String)
    intonation = Column(JSON) # array of dicts, score followed by wrong notes
    cv_evenness = Column(Integer) 
    tempo_slope = Column(Integer)
    tempo_r = Column(Integer)

engine = create_engine("sqlite:///scales.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def save(analytics, scale):
    res_intonation, res_tempo_evenness, res_detached_evenness = analytics

    session = Session()
    session.add(Scales(date=datetime.now(),scale=scale, intonation=analytics))
