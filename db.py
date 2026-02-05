from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

Base = declarative_base()

class Scales(Base):
    __tablename__ = "scales"
    id = Column(Integer, primary_key=True)
    date = Column(String)
    scale = Column(String)
    intonation = Column(Integer) 
    cv_evenness = Column(Float) 
    tempo_slope = Column(Float)
    tempo_r = Column(Float)
    mean_tempo = Column(Float)

engine = create_engine("sqlite:///scales.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
    
def save(analytics, scale):
    session = Session()
    new_record = Scales(date=datetime.now(),scale=scale, 
                       cv_evenness=analytics.cv_evenness, 
                       tempo_slope=analytics.tempo_slope, 
                       tempo_r=analytics.tempo_r,
                       mean_tempo=analytics.mean_tempo)
    session.add(new_record)
    session.commit()
    new_id = new_record.id
    session.close()

    return new_id

def get_id(id: int):
    session = Session()
    row = session.query(Scales).filter(Scales.id == id).first()
    session.close()
    return row

def get_scale(scale: str):
    session = Session()
    scale_analytics = session.query(Scales).filter(Scales.scale == scale).order_by(Scales.id).all()
    session.close()
    return scale_analytics

def get_all():
    session = Session()
    all_analytics = session.query(Scales).order_by(Scales.id).all()
    session.close()
    return all_analytics


