
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.player_model import Player 
from models.fixture_model import Fixture


async def  Parse_player_data(data,db):
    """
    Parses the FPL data and returns a list of Player objects.
    """
    result = await db.execute(select(Fixture))
    fixtures =result.scalars().all()
    parser = PlayerParser(data=data,fixtures=fixtures)
    return parser.players

async def map_selected_picks(player_selections, db: AsyncSession):
    result = await db.execute(select(Player))
    players = result.scalars().all()
    current_team = []
    goalkeepers = []
    defenders = []
    midfielders = []
    forwards = []
    
    for pick in player_selections:
        # Find the player with the matching id
        player = next((player for player in players if player.id == pick["element"]), None)
        if player:
            if player.element_type ==1:
                goalkeepers.append(player.id)
            elif player.element_type ==2:
                defenders.append(player.id)
            elif player.element_type ==3:
                midfielders.append(player.id)
            elif player.element_type ==4:
                forwards.append(player.id)
            current_team.append(player.id)

    
    return goalkeepers,defenders,midfielders,forwards,current_team

async def get_fdr_score(team_id:int,session:AsyncSession, num_fixtures: int = 5):
    results = await session.execute(select(Fixture).filter(Fixture.finished ==False))
    upcoming_fixtures = results.scalars().all()

    fdr_score = []
    for fixture in upcoming_fixtures:
        if team_id == fixture.team_h:
            fdr_score.append(fixture.team_h_difficulty)
        elif team_id == fixture.team_a:   
            fdr_score.append(fixture.team_a_difficulty)
    if len(fdr_score) == 0:
        return 5 
    fdr_score = sum(fdr_score[:num_fixtures]) / min(num_fixtures, len(fdr_score))
    return fdr_score
        

async def get_fdr_scores_for_teams(session: AsyncSession, num_fixtures: int = 5):
    # Fetch all upcoming fixtures ordered by kickoff time
    results = await session.execute(
        select(Fixture).filter(Fixture.finished == False).order_by(Fixture.kickoff_time)
    )
    upcoming_fixtures = results.scalars().all()

    # Initialize a dictionary to store FDR scores for each team
    fdr_scores = {}

    # Group FDR scores for each team, limiting to the next `num_fixtures` fixtures
    for fixture in upcoming_fixtures:
        fdr_scores.setdefault(fixture.team_h, [])
        fdr_scores.setdefault(fixture.team_a, [])

        if len(fdr_scores[fixture.team_h]) < num_fixtures:
            fdr_scores[fixture.team_h].append(fixture.team_h_difficulty)
        if len(fdr_scores[fixture.team_a]) < num_fixtures:
            fdr_scores[fixture.team_a].append(fixture.team_a_difficulty)

    # Create a dictionary to store both the average FDR and the list of FDRs
    fdr_summary = {}

    # Calculate the average FDR for each team based on the upcoming `num_fixtures` games
    for team_id, scores in fdr_scores.items():
        if len(scores) > 0:
            avg_fdr = sum(scores) / len(scores)
        else:
            avg_fdr = 5  # Default value if no fixtures are available

        # Store both the average FDR and the list of FDRs for each team
        fdr_summary[team_id] = {
            "average_fdr": avg_fdr,
            "fdr_list": scores
        }

    return fdr_summary



class PlayerParser:
    def __init__(self, data, fixtures):
        self.data = data
        self.fixtures = fixtures
        self.players = self.parse_players()

    def calculate_team_fixture_difficulty(self, team_id):
        num_upcoming_fixtures = 5
        team_fixtures = []
        
        for fixture in self.fixtures:
            if not fixture.finished:
                if fixture.team_h == team_id:
                    team_fixtures.append(fixture.team_h_difficulty)
                if fixture.team_a == team_id:
                    team_fixtures.append(fixture.team_a_difficulty)

        upcoming_difficulties = team_fixtures[:num_upcoming_fixtures]
        
        if len(upcoming_difficulties) > 0:
            avg_difficulty = sum(upcoming_difficulties) / len(upcoming_difficulties)
        else:
            avg_difficulty = 0
        
        return avg_difficulty


    def parse_players(self):
        if not self.data or not self.fixtures:
            print("Data is missing or in an unexpected format.")
            return {}

        element_types = {1: "goalkeepers", 2: "defenders", 3: "midfielders", 4: "forwards"}
        players = {position: [] for position in element_types.values()}

        for player in self.data:
            position = element_types[player.element_type]
            team_id = player.team
            form = float(player.form)
            fixture_difficulty = self.calculate_team_fixture_difficulty(team_id)

            players[position].append({
                "id": player.id,
                "name": player.web_name,
                "position": player.element_type,
                "status": player.status,
                "ict_index": player.ict_index,
                "price": player.now_cost / 10,
                "total_points": player.total_points,
                "goals": player.goals_scored,
                "assists": player.assists,
                "expected_goals": player.expected_goals,
                "expected_assists": player.expected_assists,
                "expected_goal_involvements": player.expected_goal_involvements,
                "saves_per_90": player.saves_per_90,
                "goals_conceded_per_90": player.goals_conceded_per_90,
                "bonus": player.bonus,
                "expected_point": player.ep_next,
                "form": form,
                "fdr": fixture_difficulty,
                "team": player.team,
                "starts": player.starts,
                "selected_by_percent": player.selected_by_percent,
                "clean_sheets": player.clean_sheets,
                "yellow_cards": player.yellow_cards,
                "red_cards": player.red_cards,
                "penalties_order": player.penalties_order,
                "value_season": player.value_season,
            })

        return players

    def calculate_upcoming_fixture_difficulty(self, num_weeks=5):
        team_fixtures = {team['id']: [] for team in self.data['teams']}
        
        for fixture in self.fixtures:
            if not fixture['finished']:
                home_team = fixture['team_h']
                away_team = fixture['team_a']
                
                if fixture['event'] <= num_weeks:
                    team_fixtures[home_team].append(fixture['team_h_difficulty'])
                    team_fixtures[away_team].append(fixture['team_a_difficulty'])

        avg_fixture_difficulty = {
            team_id: sum(difficulties) / len(difficulties) if len(difficulties) > 0 else 0
            for team_id, difficulties in team_fixtures.items()
        }

        return avg_fixture_difficulty

class FPLTransferStrategy:
    def __init__(self, all_players,manager_team,manager_budget,available_transfer,session:AsyncSession):
        self.all_players = all_players
        self.manager_team = manager_team
        self.budget = manager_budget
        self.available_transfer = available_transfer
        self.session = session


    def recommend_transfer(self,outgoing_player_id: int):
        replacements = self.get_replacement_candidates(outgoing_player_id)
        best_replacement = max(replacements, key=lambda p:p.form * 0.6 + p.fdr * 0.4)
        return best_replacement

    def get_replacement_candidates(self,outgoing_player_id: int):
        outgoing_player = self.session.query(Player).filter(Player.id == outgoing_player_id).first()
        position = outgoing_player.position
        replacements = self.session.query(Player).filter(Player.position == position).all()
        return replacements
    
    def should_transfer_out(self, player):
        try:
            form = float(player.form)
            expected_points = float(player.expected_point)
            status = player.status
            difficulty = float(player.fdr)
        except (ValueError, KeyError):
            return False
        if status in ['injured', 'suspended','doubtful']:
            return True
        dynamic_form_threshold = max(1.0, min(2 / difficulty, 2.5))
        if form < dynamic_form_threshold or expected_points < 3.0:
            return True
        return False
