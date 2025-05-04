import json
from typing import IO, Iterable, Any


def load(fp: IO) -> list:
    """Load and parse a JSONL file object into a list of Python objects."""
    return [json.loads(line) for line in fp if line.strip()]


def loads(s: str) -> list:
    """Parse a JSONL string and return a list of Python objects."""
    return [json.loads(line) for line in s.strip().splitlines() if line.strip()]


def dump(objs: Iterable[Any], fp: IO) -> None:
    """Write an iterable of Python objects to a file in JSONL format."""
    write = fp.write
    dumps_ = json.dumps
    for obj in objs:
        write(dumps_(obj) + '\n')


def dumps(objs: Iterable[Any]) -> str:
    """Convert an iterable of Python objects into a JSONL-formatted string."""
    dumps_ = json.dumps
    return '\n'.join(dumps_(obj) for obj in objs)
