from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.player_model import Player
from db.session import get_db
from sqlalchemy.future import select

router=APIRouter()




@router.get('/get-players',)
async def get_all_players(db:AsyncSession=Depends(get_db)):
    results =await db.execute(select(Player))
    players = results.scalars().all()
    return {"players": players}
 
    

