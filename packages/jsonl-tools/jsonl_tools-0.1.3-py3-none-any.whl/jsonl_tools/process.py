import json
from typing import Callable, Any, Optional, Union


def find(
    jsonl_path: str,
    predicate: Callable[[dict], bool],
    encoding: str = 'utf-8',
    limit: Optional[int] = None
) -> list[dict]:
    """
    Find and return objects in a JSONL file that match a given predicate.

    Parameters:
    - predicate: function taking a dict and returning True if it matches
    - limit: max number of results to return
    """
    results = []
    with open(jsonl_path, 'r', encoding=encoding) as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            if predicate(obj):
                results.append(obj)
                if limit is not None and len(results) >= limit:
                    break
    return results


def transform(
    input_path: str,
    output_path: str,
    transform: Callable[[dict], dict],
    encoding: str = 'utf-8'
) -> None:
    """
    Apply a transformation function to each object in a JSONL file
    and write the transformed objects to a new JSONL file.
    """
    with open(input_path, 'r', encoding=encoding) as fin, \
         open(output_path, 'w', encoding=encoding) as fout:
        write = fout.write
        dumps_ = json.dumps
        for line in fin:
            if not line.strip():
                continue
            obj = json.loads(line)
            new_obj = transform(obj)
            write(dumps_(new_obj) + '\n')


def remove_key(
    input_path: str,
    output_path: str,
    keys: Union[str, list[str]],
    encoding: str = 'utf-8'
) -> None:
    """
    Remove one or more keys from each object in a JSONL file.

    Parameters:
    - input_path: path to source JSONL file
    - output_path: path to output JSONL file with keys removed
    - keys: a single key or list of keys to remove
    - encoding: file encoding (default: utf-8)
    """
    if isinstance(keys, str):
        keys = [keys]

    with open(input_path, 'r', encoding=encoding) as fin, \
         open(output_path, 'w', encoding=encoding) as fout:
        write = fout.write
        dumps_ = json.dumps
        for line in fin:
            if not line.strip():
                continue
            obj = json.loads(line)
            for key in keys:
                obj.pop(key, None)
            write(dumps_(obj) + '\n')
