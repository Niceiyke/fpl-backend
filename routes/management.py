from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from services.manager_service import fetch_and_persist_fpl_data
from db.session import get_db

router=APIRouter()

@router.get('/update-info',)
async def pull_update_info(db:AsyncSession=Depends(get_db)):  
    await fetch_and_persist_fpl_data(db)
    return {"message": "Data updated Successfully"}

    
    

