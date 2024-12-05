import argparse
import logging
import sys

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input',
        nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdin,
        help='input file path (use - for stdin)'
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

def read_input(input) -> list[str]:
    try:
        with input as f:
            # Read the entire content
            return f.read()
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        log.info("\nOperation cancelled by user")
        sys.exit(1)
    except BrokenPipeError:
        # Handle broken pipe (e.g., when piping to head/tail)
        sys.stderr.close()
        sys.exit(0)


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level  = level,
        format = "%(message)s",
        force  = True,
    )
