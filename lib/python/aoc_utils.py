# Standard library
import argparse
import builtins
import functools
import itertools
import logging
import sys
from collections.abc import Collection, Iterable, Iterator
from typing import Any, Callable

# Globals
log = logging.getLogger('AoC')

################################################################################
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

class Chainable[T](Iterable):
    def __init__(self, iterable: Iterable[T], method: Callable | None = None):
        self.iterable   = iterable
        self.method = method
        # TODO: Add debugging options like printing each step or saving the
        # steps

    def __str__(self) -> str:
        return f'Chainable({self.iterable})'

    def __repr__(self) -> str:
        return f'Chainable({self.iterable!r})'

    def __iter__(self) -> Iterator[T]:
        return iter(self.iterable)

    def collect(self) -> Collection[T]:
        if not isinstance(self.iterable, Collection):
            self.iterable = list(self.iterable)
        return self.iterable

    def __getattr__(self, name) -> 'Chainable[T]':
        for obj in (self.iterable, builtins, itertools, functools):
            try:
                method = getattr(obj, name)
                break
            except AttributeError:
                continue
        else:
            raise AttributeError(name)
        return Chainable(self.iterable, method)

    def __call__(self, *args, **kwargs) -> T | 'Chainable[Any]':
        try:
            # e.g. reduce(lambda x,y : x*y, self.iterable, 1)
            function, args2 = args[0], args[1:]
            result = self.method(function, self.iterable, *args2, **kwargs)
        except (IndexError, TypeError, ValueError) as e1:
            try:
                # e.g. sorted(self.iterable, key, reverse=True)
                result = self.method(self.iterable, *args, **kwargs)
            except TypeError as e2:
                if self.method is None:
                    raise NotImplementedError('Chainable.__call__')
                args   = ','.join(map(repr, args))
                kwargs = ','.join(itertools.starmap(lambda k,v : f'{k }= {v!r}', kwargs.items()))
                msg    = f'{self}.{self.method.__name__}({args},{kwargs})'
                raise RuntimeError(msg) from e2
        if not isinstance(result, Iterable):
            return result
        return Chainable(result)

