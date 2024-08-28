from pydantic import BaseModel
from typing import List

class Stat(BaseModel):
    identifier: str
    a: List[dict]
    h: List[dict]

class Fixture(BaseModel):
    code: float
    event: float
    finished: bool
    finished_provisional: bool
    id: float
    kickoff_time: str
    minutes: float
    provisional_start_time: bool
    started: bool
    team_a: float
    team_a_score: float
    team_h: float
    team_h_score: float
    stats: List[Stat]
    team_h_difficulty: float
    team_a_difficulty: float
    pulse_id: float

