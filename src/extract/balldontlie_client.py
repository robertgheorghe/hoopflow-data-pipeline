"""Simple BALLDONTLIE API client."""

import os
import time

import requests
from dotenv import load_dotenv


load_dotenv()

TEAMS_URL = "https://api.balldontlie.io/v1/teams"
GAMES_URL = "https://api.balldontlie.io/v1/games"
API_KEY_ENV_VAR = "BALLDONTLIE_API_KEY"
REQUEST_DELAY_SECONDS = 13
MAX_RATE_LIMIT_RETRIES = 5
RATE_LIMIT_BUFFER_SECONDS = 2
DEFAULT_RATE_LIMIT_SLEEP_SECONDS = 15


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
    """Fetch all NBA games for a season from BALLDONTLIE."""
    headers = _get_headers()
    games = []
    cursor = None

    while True:
        # The games endpoint uses cursor pagination and array-style season filters.
        params = {"seasons[]": season, "per_page": per_page}
        if cursor:
            params["cursor"] = cursor

        response = None
        for attempt in range(1, MAX_RATE_LIMIT_RETRIES + 1):
            try:
                response = requests.get(GAMES_URL, headers=headers, params=params)

                if response.status_code != 429:
                    response.raise_for_status()
                    break

                retry_after = response.headers.get("Retry-After")
                try:
                    sleep_seconds = int(retry_after) + RATE_LIMIT_BUFFER_SECONDS
                except (TypeError, ValueError):
                    sleep_seconds = DEFAULT_RATE_LIMIT_SLEEP_SECONDS

                if attempt == MAX_RATE_LIMIT_RETRIES:
                    raise RuntimeError(
                        "BALLDONTLIE rate limit persisted while fetching games "
                        f"after {MAX_RATE_LIMIT_RETRIES} attempts."
                    )

                time.sleep(sleep_seconds)
            except requests.RequestException as error:
                status_code = getattr(error.response, "status_code", "unknown")
                raise RuntimeError(
                    f"BALLDONTLIE games request failed with status {status_code}. "
                    "Check your API key, rate limits, and internet connection."
                ) from error

        response_data = response.json()
        games.extend(response_data["data"])

        cursor = response_data.get("meta", {}).get("next_cursor")
        if not cursor:
            break

        # Pause between cursor pages to reduce the chance of hitting rate limits.
        time.sleep(REQUEST_DELAY_SECONDS)

    return games
