"""Simple BALLDONTLIE API client."""

import os

import requests
from dotenv import load_dotenv


load_dotenv()

TEAMS_URL = "https://api.balldontlie.io/v1/teams"
API_KEY_ENV_VAR = "BALLDONTLIE_API_KEY"


def fetch_teams():
    """Fetch NBA teams from BALLDONTLIE and return the response data list."""
    api_key = os.getenv(API_KEY_ENV_VAR)

    if not api_key:
        raise ValueError(
            "BALLDONTLIE_API_KEY is missing. Add it to your .env file."
        )

    # BALLDONTLIE expects the API key in the Authorization header.
    headers = {"Authorization": api_key}

    try:
        response = requests.get(TEAMS_URL, headers=headers)
        response.raise_for_status()
    except requests.RequestException as error:
        raise RuntimeError(
            "BALLDONTLIE teams request failed. Check your API key and internet "
            "connection."
        ) from error

    return response.json()["data"]
