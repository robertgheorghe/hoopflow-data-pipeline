"""PostgreSQL connection helper."""

import os

import psycopg2
from dotenv import load_dotenv


# Load variables from the project's .env file into the environment.
load_dotenv()


def get_connection():
    """Create and return a connection to the PostgreSQL database."""
    try:
        # Read the database settings from environment variables.
        connection = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )

        # Return the open connection so callers can run database queries.
        return connection
    except psycopg2.Error as error:
        raise ConnectionError(
            "Could not connect to PostgreSQL. Check your POSTGRES_* "
            "environment variables and make sure the database is running."
        ) from error
