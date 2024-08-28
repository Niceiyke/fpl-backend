from sqlalchemy import Column, Integer , ForeignKey, Table
from sqlalchemy.orm import relationship
from db.base import Base

team_players = Table(
    "team_players", Base.metadata,
    Column("team_id", Integer, ForeignKey("teams.id"), primary_key=True),
    Column("player_id", Integer, ForeignKey("players.id"), primary_key=True)
)

class Manager(Base):
    __tablename__ = "managers"
    id = Column(Integer, primary_key=True)
    fpl_id = Column(Integer, unique=True, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), unique=True)
    team = relationship("Team", back_populates="manager")


class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    manager = relationship("Manager", back_populates="team", uselist=False)
    players = relationship("Player", secondary=team_players, back_populates="teams")
    
    