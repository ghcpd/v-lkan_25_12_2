"""Multi-annotator ticket conflict detection and resolution package."""

from .logic import detect_conflict, analyze_conflict, suggest_label, process_record
from .io import load_jsonl, write_jsonl

__all__ = [
    "detect_conflict",
    "analyze_conflict",
    "suggest_label",
    "process_record",
    "load_jsonl",
    "write_jsonl",
]
