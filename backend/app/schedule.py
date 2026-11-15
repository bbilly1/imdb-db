"""Build a Supercronic crontab from SCHEDULE and execute scheduled ingests."""

import argparse
import asyncio
import logging
import os
import shlex
import sys
from pathlib import Path


def build_crontab(schedule: str) -> str:
    """Translate dataset:cron jobs separated by pipes into fixed commands."""
    if not schedule.strip():
        return ""
    entries = []
    for job in schedule.split("|"):
        selection, cron = job.split(":", 1)
        datasets = [name.strip() for name in selection.split(",")]
        command = shlex.join([sys.executable, str(Path(__file__).resolve()), "--run", *datasets])
        entries.append(f"{cron.strip()} {command}")

    return "\n".join(entries) + "\n"


def main() -> None:
    """Print the crontab, or run the datasets selected by a generated job."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", nargs="+", metavar="DATASET", help="Run dataset filenames, or 'all'")
    args = parser.parse_args()

    try:
        if args.run is None:
            sys.stdout.write(build_crontab(os.environ.get("SCHEDULE", "")))
        else:
            from src.import_handler import import_datasets

            logging.basicConfig(level=logging.INFO, format="[%(asctime)s][%(levelname)s][%(name)s] %(message)s")
            datasets = None if args.run == ["all"] else args.run
            asyncio.run(import_datasets(dataset_names=datasets))
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
