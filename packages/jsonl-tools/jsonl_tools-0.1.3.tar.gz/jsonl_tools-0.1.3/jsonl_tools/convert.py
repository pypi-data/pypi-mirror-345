import json
import csv
from .core import load, dump
from typing import Any, Optional


def json_to_jsonl(
    json_path: str,
    jsonl_path: str,
    encoding: str = 'utf-8',
    **json_load_kwargs: Any
) -> None:
    """Convert a JSON file (list of objects) to JSONL format."""
    with open(json_path, 'r', encoding=encoding) as json_file:
        data = json.load(json_file, **json_load_kwargs)

    if not isinstance(data, list):
        raise ValueError("Top-level JSON must be a list to convert to JSONL.")

    with open(jsonl_path, 'w', encoding=encoding) as jsonl_file:
        dump(data, jsonl_file)


def jsonl_to_json(
    jsonl_path: str,
    json_path: str,
    encoding: str = 'utf-8',
    indent: int = 2,
    ensure_ascii: bool = False,
    **json_dump_kwargs: Any
) -> None:
    """Convert a JSONL file to a JSON array and save as a JSON file."""
    with open(jsonl_path, 'r', encoding=encoding) as jsonl_file:
        data = load(jsonl_file)

    with open(json_path, 'w', encoding=encoding) as json_file:
        json.dump(data, json_file, indent=indent, ensure_ascii=ensure_ascii, **json_dump_kwargs)


def jsonl_to_csv(
    jsonl_path: str,
    csv_path: str,
    encoding: str = 'utf-8',
    fieldnames: Optional[list[str]] = None
) -> None:
    """
    Convert a JSONL file to a CSV file. If fieldnames are not provided,
    they will be inferred from the first object.
    """
    with open(jsonl_path, 'r', encoding=encoding) as jsonl_file:
        reader = (json.loads(line) for line in jsonl_file if line.strip())
        first = next(reader, None)

        if first is None:
            raise ValueError("Input JSONL file is empty.")

        if fieldnames is None:
            fieldnames = list(first.keys())

        with open(csv_path, 'w', newline='', encoding=encoding) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(first)
            for obj in reader:
                writer.writerow(obj)


def csv_to_jsonl(
    csv_path: str,
    jsonl_path: str,
    encoding: str = 'utf-8'
) -> None:
    """Convert a CSV file to a JSONL file (each row becomes a JSON object)."""
    with open(csv_path, 'r', encoding=encoding, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        with open(jsonl_path, 'w', encoding=encoding) as jsonl_file:
            write = jsonl_file.write
            dumps_ = json.dumps
            for row in reader:
                write(dumps_(row) + '\n')
