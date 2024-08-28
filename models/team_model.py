from sqlalchemy import Column, Integer, String, Boolean
from db.base import Base

class Club(Base):
    __tablename__ = 'clubs'

    id = Column(Integer, primary_key=True)
    code = Column(Integer)
    draw = Column(Integer)
    form = Column(String)
    loss = Column(Integer)
    name = Column(String)
    played = Column(Integer)
    points = Column(Integer)
    position = Column(Integer)
    short_name = Column(String)
    strength = Column(Integer)
    team_division = Column(String)
    unavailable = Column(Boolean)
    win = Column(Integer)
    strength_overall_home = Column(Integer)
    strength_overall_away = Column(Integer)
    strength_attack_home = Column(Integer)
    strength_attack_away = Column(Integer)
    strength_defence_home = Column(Integer)
    strength_defence_away = Column(Integer)
    pulse_id = Column(Integer)
