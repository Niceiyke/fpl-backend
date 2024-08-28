from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from models.gameweek_model import Gameweek
from models.team_model import Club
from models.player_model import Player
from models.fixture_model import Fixture
from data import FPLDataFetcher

async def fetch_and_persist_fpl_data(db: AsyncSession):
    """
    Fetches FPL data and persists it to the database.
    """
    try:
        data_fetcher = FPLDataFetcher()
        
        response = await data_fetcher.fetch_fpl_data()
        fixtures_data =await data_fetcher.fetch_fixtures()

        players_data = response['elements']
        teams_data = response['teams']
        gameweeks_data = response['events']

        print(f"No of players: {len(players_data)}, No. Teams: {len(teams_data)}, No of Gameweeks: {len(gameweeks_data)}")

        if len(teams_data) >= 20:
            await _truncate_and_persist_teams(db, teams_data)

        if len(gameweeks_data) >= 38:
            await _truncate_and_persist_gameweeks(db, gameweeks_data)

        if len(players_data) >= 500:
            await _truncate_and_persist_players(db, players_data)

        if len(players_data) >= 380:
            await _truncate_and_persist_fixtures(db, fixtures_data)
        else:
            raise ValueError("Couldn't truncate fixtures")

    except Exception as e:
        print(e)


async def _truncate_and_persist_teams(db: AsyncSession, teams_data):
    """
    Truncates the teams table and persists the teams data.
    """
    await db.execute(text("TRUNCATE TABLE teams RESTART IDENTITY CASCADE;"))
    await db.commit()
    for team_data in teams_data:
        team = Club(**team_data)
        db.add(team)
    await db.commit()


async def _truncate_and_persist_gameweeks(db: AsyncSession, gameweeks_data):
    """
    Truncates the gameweeks table and persists the gameweeks data.
    """
    await db.execute(text("TRUNCATE TABLE gameweeks RESTART IDENTITY CASCADE;"))
    await db.commit()
    for gameweek_data in gameweeks_data:
        gameweek = Gameweek(**gameweek_data)
        db.add(gameweek)
    await db.commit()


async def _truncate_and_persist_players(db: AsyncSession, players_data):
    """
    Truncates the players table and persists the players data.
    """
    await db.execute(text("TRUNCATE TABLE players RESTART IDENTITY CASCADE;"))
    await db.commit()
    for player_data in players_data:
        player = Player(**player_data)
        db.add(player)
    await db.commit()

async def _truncate_and_persist_fixtures(db: AsyncSession, fixtures):
    """
    Truncates the players table and persists the players data.
    """
    await db.execute(text("TRUNCATE TABLE fixtures RESTART IDENTITY CASCADE;"))
    await db.commit()
    for fixture in fixtures:
        item = Fixture(**fixture)
        db.add(item)
    await db.commit()