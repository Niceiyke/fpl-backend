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

    if team_id:
        # Query players from team_players through a join
        stmt = (
            select(Player)
            .join(team_players, team_players.c.player_id == Player.id)
            .filter(team_players.c.team_id == team_id)
        )
        
        result = await session.execute(stmt)
        players = result.scalars().all()
        
        return players
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
    
    response=await get_players_from_manager_team(fpl_id=fpl_id,session=db)
    players=await Parse_player_data(response,db)
   
    

        # Function to sort and select players based on a weighted score
    def get_weighted_score(player):
            return (
                player['total_points'] * 0.5 +
                float(player['expected_goal_involvements']) * 0.3 -
                player['fixture_difficulty'] * 0.2
            )
        
    # Sort players in each position by their weighted score
    goalkeepers = sorted(players['goalkeepers'], key=get_weighted_score, reverse=True)
    defenders = sorted(players['defenders'], key=get_weighted_score, reverse=True)
    midfielders = sorted(players['midfielders'], key=get_weighted_score, reverse=True)
    forwards = sorted(players['forwards'], key=get_weighted_score, reverse=True)
    
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
            best_lineup = lineup
            best_score = total_score
    
    # Ensure we are not selecting starting players again for the bench
    remaining_goalkeepers = [player for player in goalkeepers if player not in best_lineup['goalkeeper']]
    remaining_defenders = [player for player in defenders if player not in best_lineup['defenders']]
    remaining_midfielders = [player for player in midfielders if player not in best_lineup['midfielders']]
    remaining_forwards = [player for player in forwards if player not in best_lineup['forwards']]
    
    # Select bench players: 1 GK, 1 DEF, 1 MID, 1 FWD
    bench = {
'goalkeepers': remaining_goalkeepers[:1],  # 1 GK on the bench
'defenders': remaining_defenders[:3],  # Up to 3 DEFs on the bench
'midfielders': remaining_midfielders[:3],  # Up to 3 MIDs on the bench
'forwards': remaining_forwards[:3],  # Up to 3 FWDs on the bench
}

    # Combine bench positions into a single list and trim to ensure the total squad size is 15
    bench_combined = bench['goalkeepers'] + bench['defenders'] + bench['midfielders'] + bench['forwards']
    bench_combined = bench_combined[:4]  # Ensuring exactly 4 bench players to maintain the 15-player squad

    bench = {
        'goalkeeper': [player for player in bench_combined if player['position'] == 1],
        'defenders': [player for player in bench_combined if player['position'] == 2],
        'midfielders': [player for player in bench_combined if player['position'] == 3],
        'forwards': [player for player in bench_combined if player['position'] == 4],
    }
    return best_lineup


async def select_captain_and_vice(best_lineup):
        # Combine all players into one list
        all_players = (
            best_lineup['goalkeeper'] +
            best_lineup['defenders'] +
            best_lineup['midfielders'] +
            best_lineup['forwards']
        )
        
        # Convert 'expected_point' to float for comparison
        for player in all_players:
            player['expected_point'] = float(player['expected_point'])
            player['fixture_difficulty'] = float(player['fixture_difficulty'])
        
        # Sort players by a weighted combination of ICT index, expected points, and fixture difficulty
        # Higher ICT index and expected points are better, lower fixture difficulty is better
        sorted_players = sorted(all_players, key=lambda x: (
            float(x['ict_index']) * 0.5 + 
            x['expected_point'] * 0.3 - 
            x['fixture_difficulty'] * 0.2
        ), reverse=True)
        
        if len(sorted_players) < 2:
            raise ValueError("Not enough players to select captain and vice-captain.")
        
        # Select the top player as captain
        captain = sorted_players[0]
        
        # Select the second top player as vice-captain
        vice_captain = sorted_players[1]
        
        return captain, vice_captain

async def get_captain_vice_suggestions(fpl_id:int,db:AsyncSession):
    lineup= await select_best_lineup_with_bench(fpl_id,db)


    captain, vice_captain= await select_captain_and_vice(lineup)

    return {
        'captain': captain,
        'vice_captain': vice_captain
    }

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
            print("Player number",len(player_out))
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
        difficulty = fdr_scores.get(player.team, 5)  # Default FDR if team not found


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
            fdr =fdr_score.get(player.team,5)
            ep=float(player.ep_next)  

            player.weighted_score = (ep * 0.7) - (fdr*0.3)
        
        return sorted(candidates, key=lambda x: x.weighted_score, reverse=True)[:5]
#  Transfer out evaluation function considering injuries
async def evaluate_transfer_out(players: List[Dict]):
    # Sorting criteria:
    # 1. Status (Injured first, then available/unavailable)
    # 2. Form (ascending)
    # 3. Expected points (ascending)
    # 4. Minutes played (ascending)
    
    return sorted(players, key=lambda player: (player.status == 'a', player.form, player.ep_next, player.minutes))[:3]

