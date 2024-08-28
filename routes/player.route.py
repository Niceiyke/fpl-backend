from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.player_model import Player
from data import FPLDataFetcher



router=APIRouter()

fetcher= FPLDataFetcher()


@router.get('/update-info',)
async def pull_update_info(db:AsyncSession=Depends(get_db)):
    response = await fetcher.fetch_fpl_data()
    playes_data=response['elements']
    teams_data=response['teams']
    gameweeks_data=response['events']

    for team_data in teams_data:
        team = Team(**team_data)
        db.add(team)
    for gameweek_data in gameweeks_data:
        gameweek = Gameweek(**gameweek_data)
        db.add(gameweek)
    
    for player_data in playes_data:
        player = Player(**player_data)
        db.add(player)

    db.commit()
    

