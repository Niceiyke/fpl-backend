from pydantic import BaseModel
from typing import List
from schemas.player_schema import Defender, Forward, Goalkeeper, Midfielder

class Team(BaseModel):
    goalkeepers: List[Goalkeeper]
    defenders: List[Defender]
    midfielders: List[Midfielder]
    forwards: List[Forward]

class ManagerBase(BaseModel):
    id: int
    fpl_id: int
    team:Team

