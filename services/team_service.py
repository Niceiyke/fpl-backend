from typing import Dict, List
from utility import FPLTransferStrategy, get_fdr_score, get_fdr_scores_for_teams, map_selected_picks,Parse_player_data
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from data import FPLDataFetcher
from models.manager_model import Manager, Team,team_players
from models.team_model import Club
from models.player_model import Player


fetcher = FPLDataFetcher()


async def get_team_info(team_id:int,gameweek_id:int,db:AsyncSession):
    team_info =await fetcher.fetch_team_data(team_id=team_id,gameweek_id=gameweek_id)
    if team_info is not None:
        selections=team_info['picks']
        GK,DF,MF,FW,CT=await map_selected_picks(selections,db)
        manager_data=await create_manager_and_team(fpl_id=team_id,player_data=CT,db=db)
        return {"data":manager_data.fpl_id}
             
             

async def get_players_from_manager_team(session: AsyncSession, fpl_id: int):
    # Get the team_id of the manager's team
    team_id_stmt = select(Team.id).filter(Team.manager.has(fpl_id=fpl_id))
    result = await session.execute(team_id_stmt)
    team_id = result.scalars().first()

    fdr_scores= await get_fdr_scores_for_teams(session=session)

    if team_id:
        # Query players from team_players through a join
        stmt = (
            select(Player)
            .join(team_players, team_players.c.player_id == Player.id)
            .filter(team_players.c.team_id == team_id)
        )
        
        result = await session.execute(stmt)
        players = result.scalars().all()

        players_return = [{"id": player.id,
                           "name": player.web_name,
                           "team": player.team,
                           "status": player.status,
                           "form": player.form,
                           "ictIndex": player.ict_index,
                           "selectedByPercent": player.selected_by_percent,
                           "position": player.element_type,
                           "price": player.now_cost / 10,
                           "xGI":player.expected_goal_involvements,
                           "totalPoints": player.total_points,
                           "expectedPoints": player.ep_next,
                           "fdr":fdr_scores.get(player.team)["fdr_list"]
                           } for player in players] 
        return players_return
    else:
        return None

async def create_manager_and_team(fpl_id: int, player_data: list,db:AsyncSession):
        query = select(Manager).where(Manager.fpl_id == fpl_id)
        result = await db.execute(query)
        existing_manager = result.scalars().first()

        # If manager exists, delete the entry
        if existing_manager:
            await db.delete(existing_manager)
            await db.commit()
            
        new_manager = Manager(fpl_id=fpl_id)
        
        # Create a new team and associate it with the manager
        new_team = Team(manager=new_manager)
        players = (await db.execute(select(Player).filter(Player.id.in_(player_data)))).scalars().all()
        
        # Create and add players to the team
        for player in players:
            new_team.players.append(player)
        
        # Add the new manager (and team) to the session
        db.add(new_manager)

        
        # Commit the transaction to save the manager, team, and players
        await db.commit()
        await db.refresh(new_manager)

        return new_manager        

async def select_best_lineup_with_bench(fpl_id, db:AsyncSession):
    
    players=await get_players_from_manager_team(fpl_id=fpl_id,session=db)

    fdr_scores=await get_fdr_scores_for_teams(db)
   
    

        # Function to sort and select players based on a weighted score
    def get_weighted_score(player):
            return (
                player['totalPoints'] * 0.5 +
                float(player['xGI']) * 0.3 -
                 float(fdr_scores.get(player['team'])["average_fdr"] )* 0.2
            )
        
    goalkeepers = sorted(
    [player for player in players if player['position'] == 1],
    key=get_weighted_score,
    reverse=True
    )

    defenders = sorted(
        [player for player in players if player['position'] == 2],
        key=get_weighted_score,
        reverse=True
    )

    midfielders = sorted(
        [player for player in players if player['position'] == 3],
        key=get_weighted_score,
        reverse=True
    )

    forwards = sorted(
        [player for player in players if player['position'] == 4],
        key=get_weighted_score,
        reverse=True
    )
    
    # Determine best formation based on the quality of players
    formations = [
        {'GK': 1, 'DEF': 3, 'MID': 4, 'FWD': 3},  # 3-4-3 formation
        {'GK': 1, 'DEF': 4, 'MID': 4, 'FWD': 2},  # 4-4-2 formation
        {'GK': 1, 'DEF': 3, 'MID': 5, 'FWD': 2},  # 3-5-2 formation
        {'GK': 1, 'DEF': 4, 'MID': 3, 'FWD': 3},  # 4-3-3 formation
        {'GK': 1, 'DEF': 5, 'MID': 3, 'FWD': 2},  # 5-3-2 formation
    ]
    
    best_lineup = None
    best_score = -float('inf')
    
    for formation in formations:
        lineup = {
            'goalkeeper': goalkeepers[:formation['GK']],
            'defenders': defenders[:formation['DEF']],
            'midfielders': midfielders[:formation['MID']],
            'forwards': forwards[:formation['FWD']],
        }
        
        # Calculate the total score for this lineup
        total_score = (
            sum(get_weighted_score(player) for player in lineup['goalkeeper']) +
            sum(get_weighted_score(player) for player in lineup['defenders']) +
            sum(get_weighted_score(player) for player in lineup['midfielders']) +
            sum(get_weighted_score(player) for player in lineup['forwards'])
        )
        
        if total_score > best_score:
            best_lineup = lineup["goalkeeper"] + lineup["defenders"] + lineup["midfielders"] + lineup["forwards"]
            best_score = total_score

    bench = [element for element in players if element not in best_lineup]
    

    return best_lineup, bench


async def get_team_points(fpl_id:int,db:AsyncSession):
     lineup= await select_best_lineup_with_bench(fpl_id,db)
     highest_expected_point=0
     total_expected_points = 0
     for position, players in lineup.items():
        for player in players:
            total_expected_points += float(player["expected_point"])
            if float(player["expected_point"]) > highest_expected_point:
                highest_expected_point = float(player["expected_point"])
     return total_expected_points+highest_expected_point


async def get_differential_players(db:AsyncSession,min_games_played=1, max_ownership=10): 
        results= await db.execute(select(Player))
        teams_result= await db.execute(select(Club))
        all_players = results.scalars().all()
        all_teams = teams_result.scalars().all()

        #all_players= await Parse_player_data(players,db)
        #("Players",all_players)

        teams = {team.id: team.name for team in all_teams}

        print("teams",teams)
        positions = {position.id for position in all_players}

        differential_players = []

        for player in all_players:
            ownership = float(player.selected_by_percent)
            games_played = player.minutes / 90

            if ownership < max_ownership and games_played >= min_games_played:
                differential_players.append(player)

        return sorted(differential_players, key=lambda x: x.form, reverse=True)

async def transfer_suggester(fpl_id, session, budget):
    manager_players = await get_players_from_manager_team(fpl_id=fpl_id, session=session)
    results= await session.execute(select(Player))
    all_players = results.scalars().all()
    transfer_out = []

    # Fetch FDR scores for all teams based on the next five games
    fdr_scores = await get_fdr_scores_for_teams(session)

    
    transfer = await should_transfer_out(manager_players=manager_players, fdr_scores=fdr_scores)
    if transfer is not None:
            player_out=await evaluate_transfer_out(transfer)
            for player in player_out:        
                transfer_candidate = await find_replacement_candidates(players_pool=all_players, budget=budget, outgoing_player=player)
                possible_replacement = await evaluate_replacements(candidates=transfer_candidate, fdr_score=fdr_scores)
                if possible_replacement is not None:
                    transfer_out.append({f"transfer out {player.web_name,player.weighted_score,player.now_cost/10} for": [(x.web_name,x.weighted_score,x.now_cost/10) for x in possible_replacement]})

    return transfer_out
             
     

async def should_transfer_out(manager_players, fdr_scores):
    transfer_out=[]
    for player in manager_players:
        
        form = float(player.form)
        expected_points = float(player.ep_next)
        status = player.status
        difficulty = float(fdr_scores.get(player.team)["average_fdr"] ) # Default FDR if team not found


        if status in ['injured', 'suspended', 'doubtful']:
            transfer_out.append(player)

        dynamic_form_threshold = max(1.0, min(2 / difficulty, 2.5))
        if form < dynamic_form_threshold or expected_points < 2.0:

            transfer_out.append(player)

    return transfer_out

async def find_replacement_candidates(players_pool, budget, outgoing_player):
        candidates = []
        outgoing_position = outgoing_player.element_type
        outgoing_price = float(outgoing_player.now_cost/10)

        for player in players_pool:
            if player.element_type== outgoing_position:
                try:
                    price = float(player.now_cost/10)
                except ValueError:
                    continue
                if price <= budget + outgoing_price:
                    candidates.append(player)    
        return candidates

async def evaluate_replacements(candidates,fdr_score):
        for player in candidates:
            fdr =float(fdr_score.get(player.team)["average_fdr"])
            ep=float(player.ep_next)  

            player.weighted_score = (ep * 0.7) - (fdr*0.3)
        
        return sorted(candidates, key=lambda x: x.weighted_score, reverse=True)[:5]
#  Transfer out evaluation function considering injuries
async def evaluate_transfer_out(players: List[Dict]):
    return sorted(players, key=lambda player: (player.status == 'a', player.form, player.ep_next, player.minutes))[:3]

weights = {
   "form": 0.3,
   "expectedPoints": 0.4,
   "xGI": 0.2,
   "fdr": 0.1
}
#make async
def calculate_captain_score(player):
    return (
        weights["form"] * float(player["form"]) +
        weights["expectedPoints"] * float(player["expectedPoints"]) +
        weights["xGI"] * float(player["xGI"]) +
        weights["fdr"] * float((1 / player["fdr"][0]))  # lower FDR is better
    )

async def select_captain_and_vice(fpl_id,db):
    players,_ =await select_best_lineup_with_bench(fpl_id=fpl_id,db=db)
    # Filter out only eligible players
    eligible_players = [player for player in players if player["status"] == "a"]
    
    # Sort players based on captain score
    eligible_players.sort(key=lambda player:  calculate_captain_score(player), reverse=True)

    if len(eligible_players) == 0:
        return None, None

    # Choose the captain (first player)
    captain = eligible_players[0]

    # Choose vice-captain (next best player from a different team if possible)
    for player in eligible_players[1:]:
        if player["team"] != captain["team"]:
            vice_captain = player
            break
    else:
        vice_captain = eligible_players[1]  # If all are from the same team, pick the next best

    return captain, vice_captain
