from fastapi import FastAPI,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.player_model import Player 
from db.session import get_db 
from routes import management,team
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:3001", 
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # allows specific origins
    allow_credentials=True,  # allow cookies to be sent
    allow_methods=["*"],  # allows all HTTP methods
    allow_headers=["*"],  # allows all headers
)


@app.get("/ping")
async def ping(db:AsyncSession=Depends(get_db)):
    result = await db.execute(select(Player))
   
    return {"data": result.scalars().first()}

app.include_router(management.router,prefix='/api/management',tags=['management'])
app.include_router(team.router,prefix='/api/team',tags=['team'])