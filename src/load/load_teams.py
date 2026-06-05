"""Load NBA teams from BALLDONTLIE into the raw.teams table."""

from src.extract.balldontlie_client import fetch_teams
from src.utils.db import get_connection


def load_teams():
    """Fetch NBA teams from the API and upsert them into PostgreSQL."""
    connection = None
    cursor = None

    try:
        teams = fetch_teams()
        connection = get_connection()
        cursor = connection.cursor()

        upsert_query = """
            INSERT INTO raw.teams (
                team_id,
                abbreviation,
                city,
                conference,
                division,
                full_name,
                name
            )
            VALUES (
                %(team_id)s,
                %(abbreviation)s,
                %(city)s,
                %(conference)s,
                %(division)s,
                %(full_name)s,
                %(name)s
            )
            ON CONFLICT (team_id) DO UPDATE SET
                abbreviation = EXCLUDED.abbreviation,
                city = EXCLUDED.city,
                conference = EXCLUDED.conference,
                division = EXCLUDED.division,
                full_name = EXCLUDED.full_name,
                name = EXCLUDED.name;
        """

        for team in teams:
            # BALLDONTLIE uses "id"; raw.teams stores the same value as "team_id".
            team_row = {
                "team_id": team["id"],
                "abbreviation": team["abbreviation"],
                "city": team["city"],
                "conference": team["conference"],
                "division": team["division"],
                "full_name": team["full_name"],
                "name": team["name"],
            }
            cursor.execute(upsert_query, team_row)

        connection.commit()
        print(f"Successfully loaded {len(teams)} teams into raw.teams.")
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
    load_teams()
