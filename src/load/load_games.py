"""Load NBA games from BALLDONTLIE into the raw.games table."""

from src.extract.balldontlie_client import fetch_games
from src.utils.db import get_connection


def load_games():
    """Fetch NBA games from the API and upsert them into PostgreSQL."""
    connection = None
    cursor = None

    try:
        games = fetch_games(season=2023, per_page=100)
        connection = get_connection()
        cursor = connection.cursor()

        upsert_query = """
            INSERT INTO raw.games (
                game_id,
                game_date,
                season,
                status,
                period,
                postseason,
                home_team_id,
                home_team_score,
                visitor_team_id,
                visitor_team_score
            )
            VALUES (
                %(game_id)s,
                %(game_date)s,
                %(season)s,
                %(status)s,
                %(period)s,
                %(postseason)s,
                %(home_team_id)s,
                %(home_team_score)s,
                %(visitor_team_id)s,
                %(visitor_team_score)s
            )
            ON CONFLICT (game_id) DO UPDATE SET
                game_date = EXCLUDED.game_date,
                season = EXCLUDED.season,
                status = EXCLUDED.status,
                period = EXCLUDED.period,
                postseason = EXCLUDED.postseason,
                home_team_id = EXCLUDED.home_team_id,
                home_team_score = EXCLUDED.home_team_score,
                visitor_team_id = EXCLUDED.visitor_team_id,
                visitor_team_score = EXCLUDED.visitor_team_score;
        """

        for game in games:
            # Team IDs are nested inside the home_team and visitor_team objects.
            game_row = {
                "game_id": game["id"],
                "game_date": game["date"],
                "season": game["season"],
                "status": game["status"],
                "period": game["period"],
                "postseason": game["postseason"],
                "home_team_id": game["home_team"]["id"],
                "home_team_score": game["home_team_score"],
                "visitor_team_id": game["visitor_team"]["id"],
                "visitor_team_score": game["visitor_team_score"],
            }
            cursor.execute(upsert_query, game_row)

        connection.commit()
        print(f"Successfully loaded {len(games)} games into raw.games.")
    except Exception:
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    load_games()
