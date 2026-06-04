"""Load a small list of NBA teams into the raw.teams table."""

from src.utils.db import get_connection


# Use a small hardcoded dataset until an API is added later in the project.
TEAMS = [
    {
        "team_id": 1,
        "abbreviation": "ATL",
        "city": "Atlanta",
        "conference": "East",
        "division": "Southeast",
        "full_name": "Atlanta Hawks",
        "name": "Hawks",
    },
    {
        "team_id": 2,
        "abbreviation": "BOS",
        "city": "Boston",
        "conference": "East",
        "division": "Atlantic",
        "full_name": "Boston Celtics",
        "name": "Celtics",
    },
    {
        "team_id": 14,
        "abbreviation": "LAL",
        "city": "Los Angeles",
        "conference": "West",
        "division": "Pacific",
        "full_name": "Los Angeles Lakers",
        "name": "Lakers",
    },
    {
        "team_id": 15,
        "abbreviation": "MEM",
        "city": "Memphis",
        "conference": "West",
        "division": "Southwest",
        "full_name": "Memphis Grizzlies",
        "name": "Grizzlies",
    },
    {
        "team_id": 22,
        "abbreviation": "PHI",
        "city": "Philadelphia",
        "conference": "East",
        "division": "Atlantic",
        "full_name": "Philadelphia 76ers",
        "name": "76ers",
    },
]


def load_teams():
    """Insert or update the hardcoded teams in PostgreSQL."""
    connection = None
    cursor = None

    try:
        # Open a database connection and create a cursor for running SQL.
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

        # Run the same upsert for each team in the list.
        for team in TEAMS:
            cursor.execute(upsert_query, team)

        # Save all inserts and updates as one transaction.
        connection.commit()
        print(f"Successfully loaded {len(TEAMS)} teams into raw.teams.")
    except Exception:
        # Undo any partial changes if one of the database operations fails.
        if connection is not None:
            connection.rollback()
        raise
    finally:
        # Always release database resources when the script finishes.
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    load_teams()
