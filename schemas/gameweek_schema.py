from pydantic import BaseModel
from typing import List

class ChipPlay(BaseModel):
    chip_name: str
    num_played: int

class TopElementInfo(BaseModel):
    id: int
    points: int

class Gameweek(BaseModel):
    id: int
    name: str
    deadline_time: str
    release_time: str = None
    average_entry_score: int
    finished: bool
    data_checked: bool
    highest_scoring_entry: int
    deadline_time_epoch: int
    deadline_time_game_offset: int
    highest_score: int
    is_previous: bool
    is_current: bool
    is_next: bool
    cup_leagues_created: bool
    h2h_ko_matches_created: bool
    ranked_count: int
    chip_plays: List[ChipPlay]
    most_selected: int
    most_transferred_in: int
    top_element: int
    top_element_info: TopElementInfo
    transfers_made: int
    most_captained: int
    most_vice_captained: int