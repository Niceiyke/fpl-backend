from fastapi import APIRouter,Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from services.team_service import get_captain_vice_suggestions, get_differential_players, get_players_from_manager_team, get_team_info, get_team_points,select_best_lineup_with_bench, transfer_suggester



router=APIRouter()


@router.get("/get-team-info", status_code=status.HTTP_200_OK)
async def get_team_detail(team_id: int,gameweek_id, db: AsyncSession=Depends(get_db)):
    team= await get_team_info(team_id=team_id,gameweek_id=gameweek_id,db=db)
    
    return {"team": "completed"}

@router.get("/get-manager-team", status_code=status.HTTP_200_OK)
async def get_manager_team(fpl_id: int, db: AsyncSession = Depends(get_db)):
   team =await get_players_from_manager_team(fpl_id=fpl_id, session=db)
   if team is not None:
      return {"team": team}

@router.get("/get-best-lineup", status_code=status.HTTP_200_OK)
async def get_best_lineup(fpl_id: int, gameweek_id: int, db: AsyncSession = Depends(get_db)):
    
    lineup= await select_best_lineup_with_bench(fpl_id, db)
    

    return {
       "lineup":lineup
    }


@router.get("/get-captain-suggestions", status_code=status.HTTP_200_OK)
async def get_captain_suggestions(fpl_id: int,int, db: AsyncSession = Depends(get_db)):
    suggestion =await get_captain_vice_suggestions(fpl_id,db)
    return{"suggestions":suggestion['captain']}

@router.get("/get-expected-points", status_code=status.HTTP_200_OK)
async def get_team_expected_points(fpl_id: int, db: AsyncSession = Depends(get_db)):
    points=await get_team_points(fpl_id,db)

    return{"Team Expected Points":points}

@router.get("/get-differentials", status_code=status.HTTP_200_OK)
async def get_avaliable_differentials(max_ownership:int,min_games_played:int,db: AsyncSession = Depends(get_db)):
   defferentials=await get_differential_players(db=db,max_ownership=max_ownership,min_games_played=min_games_played)

   return{
       "differentials":defferentials
   }

@router.get("/transfer-suggestions",status_code=status.HTTP_200_OK)
async def transfer_suggestions(fpl_id:int,budget:float,db:AsyncSession=Depends(get_db)):
    suggestions=await transfer_suggester(fpl_id,db,budget)

    return {f"transfer out {len(suggestions)} players":suggestions}
    