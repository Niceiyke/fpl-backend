from sqlalchemy import Column, Integer, String, Boolean,JSON
from sqlalchemy.ext.declarative import declarative_base
from db.base import Base


class Fixture(Base):
    __tablename__ = 'fixtures'
    code = Column(Integer)
    event = Column(Integer)
    finished = Column(Boolean)
    finished_provisional = Column(Boolean)
    id = Column(Integer, primary_key=True)
    kickoff_time = Column(String)
    minutes = Column(Integer)
    provisional_start_time = Column(Boolean)
    started = Column(Boolean)
    team_a = Column(Integer)
    team_a_score = Column(Integer)
    team_h = Column(Integer)
    team_h_score = Column(Integer)
    team_h_difficulty = Column(Integer)
    team_a_difficulty = Column(Integer)
    pulse_id = Column(Integer)
    stats = Column(JSON)
