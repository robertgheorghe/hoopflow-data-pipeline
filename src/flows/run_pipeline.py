"""Prefect flow for running the HoopFlow data pipeline."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from prefect import flow, get_run_logger, task


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@task
def run_command(command_args: list[str], task_name: str):
    """Run a project command and raise a clear error if it fails."""
    logger = get_run_logger()
    command_text = " ".join(command_args)
    env = os.environ.copy()
    python_path = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{PROJECT_ROOT}{os.pathsep}{python_path}" if python_path else str(PROJECT_ROOT)
    )

    logger.info("Running %s: %s", task_name, command_text)

    result = subprocess.run(
        command_args,
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    if result.stdout:
        logger.info("%s stdout:\n%s", task_name, result.stdout)

    if result.stderr:
        logger.warning("%s stderr:\n%s", task_name, result.stderr)

    if result.returncode != 0:
        raise RuntimeError(
            f"{task_name} failed with exit code {result.returncode}: {command_text}"
        )


@flow
def hoopflow_pipeline(refresh_raw: bool = False):
    """Run the HoopFlow pipeline."""
    logger = get_run_logger()

    if refresh_raw:
        run_command([sys.executable, "src/load/load_teams.py"], "load teams")
        run_command([sys.executable, "src/load/load_games.py"], "load games")
    else:
        logger.info("Skipping raw API ingestion. Use --refresh-raw to run it.")

    run_command(
        ["dbt", "run", "--project-dir", "dbt", "--profiles-dir", "dbt"],
        "dbt run",
    )
    run_command(
        ["dbt", "test", "--project-dir", "dbt", "--profiles-dir", "dbt"],
        "dbt test",
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Run the HoopFlow pipeline.")
    parser.add_argument(
        "--refresh-raw",
        action="store_true",
        help="Refresh raw API data before running dbt.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    hoopflow_pipeline(refresh_raw=args.refresh_raw)
