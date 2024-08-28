from typing import List
from pydantic import BaseModel

class PlayerBase(BaseModel):
    chance_of_playing_next_round: int
    chance_of_playing_this_round: int
    code: int
    cost_change_event: int
    cost_change_event_fall: int
    cost_change_start: int
    cost_change_start_fall: int
    dreamteam_count: int
    element_type: int
    ep_next: str
    ep_this: str
    event_points: int
    first_name: str
    form: str
    id: int
    in_dreamteam: bool
    news: str
    news_added: str
    now_cost: int
    photo: str
    points_per_game: str
    second_name: str
    selected_by_percent: float
    special: bool
    squad_number: object
    status: str
    team: int
    team_code: int
    total_points: int
    transfers_in: int
    transfers_in_event: int
    transfers_out: int
    transfers_out_event: int
    value_form: str
    value_season: str
    web_name: str
    minutes: int
    goals_scored: int
    assists: int
    clean_sheets: int
    goals_conceded: int
    own_goals: int
    penalties_saved: int
    penalties_missed: int
    yellow_cards: int
    red_cards: int
    saves: int
    bonus: int
    bps: int
    influence: str
    creativity: str
    threat: str
    ict_index: str
    starts: int
    expected_goals: str
    expected_assists: str
    expected_goal_involvements: str
    expected_goals_conceded: str
    influence_rank: int
    influence_rank_type: int
    creativity_rank: int
    creativity_rank_type: int
    threat_rank: int
    threat_rank_type: int
    ict_index_rank: int
    ict_index_rank_type: int
    corners_and_indirect_freekicks_order: object
    corners_and_indirect_freekicks_text: str
    direct_freekicks_order: object
    direct_freekicks_text: str
    penalties_order: int
    penalties_text: str
    expected_goals_per_90: str
    saves_per_90: str
    expected_assists_per_90: str
    expected_goal_involvements_per_90: str
    expected_goals_conceded_per_90: str
    goals_conceded_per_90: str
    now_cost_rank: int
    now_cost_rank_type: int
    form_rank: int
    form_rank_type: int
    points_per_game_rank: int
    points_per_game_rank_type: int
    selected_rank: int
    selected_rank_type: int
    starts_per_90: str
    clean_sheets_per_90: str


class Goalkeeper(PlayerBase):
    pass

class Defender(PlayerBase):
    pass

class Midfielder(PlayerBase):
    pass

class Forward(PlayerBase):
    pass

class Player(BaseModel):
    id: int
    name: str
    position: int
    price: float
    team: str
    fdr: List[float]
    expectedPoints: float
    xGI: float
    totalPoints: float

