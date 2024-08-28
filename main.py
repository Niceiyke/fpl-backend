from fastapi import FastAPI,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.player_model import Player 
from db.session import get_db 
from routes import management,team

app = FastAPI()


@app.get("/ping")
async def ping(db:AsyncSession=Depends(get_db)):
    result = await db.execute(select(Player))
   
    return {"data": result.scalars().first()}

app.include_router(management.router,prefix='/api/management',tags=['management'])
app.include_router(team.router,prefix='/api/team',tags=['team'])