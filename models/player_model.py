from sqlalchemy import JSON, Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from models.manager_model import Team,team_players
from db.base import Base

class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    chance_of_playing_next_round = Column(Integer)
    chance_of_playing_this_round = Column(Integer)
    code = Column(Integer)
    cost_change_event = Column(Integer)
    cost_change_event_fall = Column(Integer)
    cost_change_start = Column(Integer)
    cost_change_start_fall = Column(Integer)
    dreamteam_count = Column(Integer)
    element_type = Column(Integer)
    ep_next = Column(String)
    ep_this = Column(String)
    event_points = Column(Integer)
    first_name = Column(String)
    form = Column(String)
    in_dreamteam = Column(Boolean)
    news = Column(String)
    news_added = Column(String)
    now_cost = Column(Integer)
    photo = Column(String)
    points_per_game = Column(String)
    second_name = Column(String)
    selected_by_percent = Column(String)
    special = Column(Boolean)
    squad_number = Column(String)  # Assuming this is a string, but could be an integer?
    status = Column(String)
    team = Column(Integer)
    team_code = Column(Integer)
    total_points = Column(Integer)
    transfers_in = Column(Integer)
    transfers_in_event = Column(Integer)
    transfers_out = Column(Integer)
    transfers_out_event = Column(Integer)
    value_form = Column(String)
    value_season = Column(String)
    web_name = Column(String)
    minutes = Column(Integer)
    goals_scored = Column(Integer)
    assists = Column(Integer)
    clean_sheets = Column(Integer)
    goals_conceded = Column(Integer)
    own_goals = Column(Integer)
    penalties_saved = Column(Integer)
    penalties_missed = Column(Integer)
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)
    saves = Column(Integer)
    bonus = Column(Integer)
    bps = Column(Integer)
    influence = Column(String)
    creativity = Column(String)
    threat = Column(String)
    ict_index = Column(String)
    starts = Column(Integer)
    expected_goals = Column(String)
    expected_assists = Column(String)
    expected_goal_involvements = Column(String)
    expected_goals_conceded = Column(String)
    influence_rank = Column(Integer)
    influence_rank_type = Column(Integer)
    creativity_rank = Column(Integer)
    creativity_rank_type = Column(Integer)
    threat_rank = Column(Integer)
    threat_rank_type = Column(Integer)
    ict_index_rank = Column(Integer)
    ict_index_rank_type = Column(Integer)
    corners_and_indirect_freekicks_order = Column(Integer)  # Assuming this is a string, but could be an integer?
    corners_and_indirect_freekicks_text = Column(String)
    direct_freekicks_order = Column(Integer)  # Assuming this is a string, but could be an integer?
    direct_freekicks_text = Column(String)
    penalties_order = Column(Integer)
    penalties_text = Column(String)
    expected_goals_per_90 = Column(Integer)
    saves_per_90 = Column(Integer)
    expected_assists_per_90 = Column(Integer)
    expected_goal_involvements_per_90 = Column(Integer)
    expected_goals_conceded_per_90 = Column(Integer)
    goals_conceded_per_90 = Column(Integer)
    now_cost_rank = Column(Integer)
    now_cost_rank_type = Column(Integer)
    form_rank = Column(Integer)
    form_rank_type = Column(Integer)
    points_per_game_rank = Column(Integer)
    points_per_game_rank_type = Column(Integer)
    selected_rank = Column(Integer)
    selected_rank_type = Column(Integer)
    starts_per_90 = Column(Integer)
    clean_sheets_per_90 = Column(Integer)
    teams = relationship("Team", secondary=team_players, back_populates="players")
