"""
convert formats as needed
"""

import sys
from csv import DictWriter
from typing import Any, Dict, List

from .loaders import load_jsonl


def write_jsonl_to_csv(in_file: str, out_file: str = "converted.csv") -> None:
    """
    convert jsonl to csv
    """
    items = load_jsonl(in_file)
    return write_list_to_csv(items, out_file)


def write_list_to_csv(
    items: List[Dict[str, Any]], out_file: str = "converted.csv"
) -> None:
    """
    convert jsonl to csv
    """

    if len(items) == 0:
        print("No items found")
        return

    headers = items[0].keys()
    with open(out_file, "w", encoding="utf-8") as f:
        writer = DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for item in items:
            writer.writerow(item)
    print(f"Converted {len(items)} items to {out_file}")


if __name__ == "__main__":

    write_jsonl_to_csv(sys.argv[1], sys.argv[2])
