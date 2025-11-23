from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data import FPLDataFetcher
from models.fixture_model import Fixture
from models.gameweek_model import Gameweek
from models.player_model import Player
from models.team_model import Club


async def fetch_and_persist_fpl_data(db: AsyncSession):
    """Fetches FPL data and persists it to the database."""
    try:
        data_fetcher = FPLDataFetcher()

        response = await data_fetcher.fetch_fpl_data()
        fixtures_data = await data_fetcher.fetch_fixtures()

        players_data = response["elements"]
        teams_data = response["teams"]
        gameweeks_data = response["events"]

        print(
            f"No of players: {len(players_data)}, No. Teams: {len(teams_data)}, No of Gameweeks: {len(gameweeks_data)}"
        )

        async with db.begin():
            if len(teams_data) >= 20:
                await _upsert_teams(db, teams_data)

            if len(gameweeks_data) >= 38:
                await _upsert_gameweeks(db, gameweeks_data)

            if len(players_data) >= 500:
                await _upsert_players(db, players_data)

            if len(fixtures_data) >= 380:
                await _upsert_fixtures(db, fixtures_data)
            else:
                raise ValueError("Couldn't persist fixtures")

    except Exception as e:
        print(e)


async def _bulk_insert_and_update(db: AsyncSession, model, payloads):
    if not payloads:
        return

    ids = [item.get("id") for item in payloads if item.get("id") is not None]
    if not ids:
        return

    existing_ids = set(
        (await db.execute(select(model.id).where(model.id.in_(ids)))).scalars().all()
    )

    new_records = [item for item in payloads if item.get("id") not in existing_ids]
    update_records = [item for item in payloads if item.get("id") in existing_ids]

    if new_records:
        await db.run_sync(
            lambda sync_session: sync_session.bulk_insert_mappings(model, new_records)
        )

    if update_records:
        await db.run_sync(
            lambda sync_session: sync_session.bulk_update_mappings(model, update_records)
        )


async def _upsert_teams(db: AsyncSession, teams_data):
    """Upserts team data without truncating the table."""

    await _bulk_insert_and_update(db, Club, teams_data)


async def _upsert_gameweeks(db: AsyncSession, gameweeks_data):
    """Upserts gameweek data without truncating the table."""

    await _bulk_insert_and_update(db, Gameweek, gameweeks_data)


async def _upsert_players(db: AsyncSession, players_data):
    """Upserts player data without truncating the table."""

    await _bulk_insert_and_update(db, Player, players_data)


async def _upsert_fixtures(db: AsyncSession, fixtures):
    """Upserts fixture data without truncating the table."""

    await _bulk_insert_and_update(db, Fixture, fixtures)
