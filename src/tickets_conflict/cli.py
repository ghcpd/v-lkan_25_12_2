import argparse
import sys
from pathlib import Path
from typing import List

from .io import load_jsonl, write_jsonl
from .logic import process_record


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect and resolve annotation conflicts in tickets JSONL.")
    parser.add_argument("--input", "-i", required=True, help="Path to input JSONL file")
    parser.add_argument("--output", "-o", required=True, help="Path to output JSONL file")
    parser.add_argument(
        "--conflicts-only",
        action="store_true",
        help="If set, output only records that have conflicts",
    )
    return parser.parse_args(argv)


def main(argv: List[str] = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    input_path = Path(args.input)
    output_path = Path(args.output)

    records = load_jsonl(str(input_path))
    processed = [process_record(r) for r in records]
    if args.conflicts_only:
        processed = [r for r in processed if r.get("is_conflict")]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(str(output_path), processed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
