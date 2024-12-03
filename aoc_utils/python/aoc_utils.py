import argparse
from pathlib import Path
import logging

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_path',
        type = Path,
        help = 'Input data path',
    )
    parser.add_argument(
        '-l', '--log-level',
        default = 'WARNING',
        help    = 'Logging level'
    )
    parser.add_argument(
        '-n', '--max-lines',
        type = int,
        help = "Max lines of input file to process",
    )
    return parser.parse_args()

def configure_logging(level: str) -> None:
    logging.basicConfig(
        level  = level,
        format = "%(message)s",
        force  = True,
    )
