from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from db.session import get_db
from models.player_model import Player
from schemas.player_schema import PaginatedPlayersResponse, PlayerSummary

router=APIRouter()




def _safe_float(value: Optional[str]) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


@router.get('/get-players', response_model=PaginatedPlayersResponse)
async def get_all_players(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    position: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, description="Minimum price in millions"),
    max_price: Optional[float] = Query(None, description="Maximum price in millions"),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if position is not None:
        filters.append(Player.element_type == position)
    if status:
        filters.append(Player.status == status)
    if min_price is not None:
        filters.append(Player.now_cost >= int(min_price * 10))
    if max_price is not None:
        filters.append(Player.now_cost <= int(max_price * 10))

    count_query = select(func.count()).select_from(Player)
    if filters:
        count_query = count_query.filter(*filters)

    total = (await db.execute(count_query)).scalar_one()

    query = select(Player)
    if filters:
        query = query.filter(*filters)

    query = query.offset((page - 1) * page_size).limit(page_size)
    results = await db.execute(query)
    players = results.scalars().all()

    items = [
        PlayerSummary(
            id=player.id,
            name=player.web_name,
            position=player.element_type,
            price=player.now_cost / 10,
            status=player.status,
            form=_safe_float(player.form),
            expected_points=_safe_float(player.ep_next),
            xgi=_safe_float(player.expected_goal_involvements),
            total_points=player.total_points or 0,
            selected_by_percent=_safe_float(player.selected_by_percent),
            ict_index=_safe_float(player.ict_index),
            team_id=player.team,
            minutes=player.minutes,
        )
        for player in players
    ]

    return PaginatedPlayersResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
 
    

