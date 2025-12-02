"""Conflict detection and resolution for multi-annotator datasets."""

from .models import Annotation, Ticket, OutputSample
from .core import load_jsonl, process_tickets, write_output

__all__ = [
    "Annotation",
    "Ticket",
    "OutputSample",
    "load_jsonl",
    "process_tickets",
    "write_output",
]
