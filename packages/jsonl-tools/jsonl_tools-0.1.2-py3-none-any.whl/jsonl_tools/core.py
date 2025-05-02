import json
from typing import IO, Iterable, Any


def load(fp: IO) -> list:
    """Read a JSONL file object and return a list of Python objects."""
    return [json.loads(line) for line in fp if line.strip()]


def loads(s: str) -> list:
    """Parse a JSONL string and return a list of Python objects."""
    return [json.loads(line) for line in s.strip().splitlines() if line]


def dump(objs: Iterable[Any], fp: IO) -> None:
    """Write an iterable of Python objects to a file in JSONL format."""
    for obj in objs:
        fp.write(json.dumps(obj) + '\n')


def dumps(objs: Iterable[Any]) -> str:
    """Convert an iterable of Python objects to a JSONL string."""
    return '\n'.join(json.dumps(obj) for obj in objs)
