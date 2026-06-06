"""Simple BALLDONTLIE API client."""

import os

import requests
from dotenv import load_dotenv


load_dotenv()

TEAMS_URL = "https://api.balldontlie.io/v1/teams"
GAMES_URL = "https://api.balldontlie.io/v1/games"
API_KEY_ENV_VAR = "BALLDONTLIE_API_KEY"


def _get_headers():
    api_key = os.getenv(API_KEY_ENV_VAR)

    if not api_key:
        raise ValueError(
            "BALLDONTLIE_API_KEY is missing. Add it to your .env file."
        )

    # BALLDONTLIE expects the API key in the Authorization header.
    return {"Authorization": api_key}


def fetch_teams():
    """Fetch NBA teams from BALLDONTLIE and return the response data list."""
    headers = _get_headers()

    try:
        response = requests.get(TEAMS_URL, headers=headers)
        response.raise_for_status()
    except requests.RequestException as error:
        raise RuntimeError(
            "BALLDONTLIE teams request failed. Check your API key and internet "
            "connection."
        ) from error

    return response.json()["data"]


def fetch_games(season=2023, per_page=100):
    """Fetch NBA games from BALLDONTLIE and return the response data list."""
    headers = _get_headers()

    # The games endpoint accepts season filters as an array-style parameter.
    params = {"seasons[]": season, "per_page": per_page}

    try:
        response = requests.get(GAMES_URL, headers=headers, params=params)
        response.raise_for_status()
    except requests.RequestException as error:
        raise RuntimeError(
            "BALLDONTLIE games request failed. Check your API key and internet "
            "connection."
        ) from error

    return response.json()["data"]
