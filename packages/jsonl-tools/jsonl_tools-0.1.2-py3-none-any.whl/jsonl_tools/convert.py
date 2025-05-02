import json
from .core import load, dump


def json_to_jsonl(json_path: str, jsonl_path: str) -> None:
    """Convert a JSON file (list) to JSONL format."""
    with open(json_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    if not isinstance(data, list):
        raise ValueError("Top-level JSON must be a list to convert to JSONL.")

    with open(jsonl_path, 'w', encoding='utf-8') as jsonl_file:
        dump(data, jsonl_file)


def jsonl_to_json(jsonl_path: str, json_path: str) -> None:
    """Convert a JSONL file to a JSON array in a JSON file."""
    with open(jsonl_path, 'r', encoding='utf-8') as jsonl_file:
        data = load(jsonl_file)

    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=2, ensure_ascii=False)
