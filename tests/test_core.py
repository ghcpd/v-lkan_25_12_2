import json
from pathlib import Path

import pytest

from conflict_detector.core import (
    load_jsonl,
    process_tickets,
    is_conflict,
    suggest_label,
)
from conflict_detector.models import Ticket


def make_ticket(data: dict) -> Ticket:
    return Ticket.model_validate(data)


def test_is_conflict_and_no_conflict():
    non_conflict = make_ticket(
        {
            "id": "T1",
            "text": "I want a refund.",
            "annotations": [
                {"annotator": "a1", "intent": "billing_issue", "urgency": "high"},
                {"annotator": "a2", "intent": "billing_issue", "urgency": "high"},
            ],
        }
    )
    conflict = make_ticket(
        {
            "id": "T2",
            "text": "I want a refund but the app crashed.",
            "annotations": [
                {"annotator": "a1", "intent": "billing_issue", "urgency": "high"},
                {"annotator": "a2", "intent": "bug_report", "urgency": "critical"},
            ],
        }
    )
    assert is_conflict(non_conflict) is False
    assert is_conflict(conflict) is True


def test_process_tickets_conflicts_only_filters():
    tickets = [
        {
            "id": "T1",
            "text": "Refund please.",
            "annotations": [
                {"annotator": "a1", "intent": "billing_issue", "urgency": "high"},
                {"annotator": "a2", "intent": "billing_issue", "urgency": "high"},
            ],
        },
        {
            "id": "T2",
            "text": "Refund but app says payment failed.",
            "annotations": [
                {"annotator": "a1", "intent": "billing_issue", "urgency": "high"},
                {"annotator": "a2", "intent": "bug_report", "urgency": "medium"},
                {"annotator": "a3", "intent": "billing_issue", "urgency": "high"},
            ],
        },
    ]
    tickets = [make_ticket(t) for t in tickets]
    outputs_all = process_tickets(tickets, conflicts_only=False)
    outputs_conflicts = process_tickets(tickets, conflicts_only=True)
    assert len(outputs_all) == 2
    assert len(outputs_conflicts) == 1
    assert outputs_conflicts[0].id == "T2"
    assert outputs_conflicts[0].is_conflict is True
    assert outputs_conflicts[0].conflict_reason is not None


def test_suggest_label_prefers_majority_with_text_cues():
    ticket = make_ticket(
        {
            "id": "T3",
            "text": "I want a refund but the app says payment failed.",
            "annotations": [
                {"annotator": "a1", "intent": "billing_issue", "urgency": "high"},
                {"annotator": "a2", "intent": "bug_report", "urgency": "medium"},
                {"annotator": "a3", "intent": "billing_issue", "urgency": "high"},
            ],
        }
    )
    label, resolution = suggest_label(ticket)
    assert label == "billing_issue|high"
    assert resolution.majority_label == "billing_issue|high"
    assert resolution.confidence == pytest.approx(2 / 3, rel=1e-3)
    assert "Majority" in resolution.explanation


def test_load_jsonl(tmp_path: Path):
    sample_path = tmp_path / "sample.jsonl"
    rows = [
        {
            "id": "X1",
            "text": "Sample",
            "annotations": [
                {"annotator": "a1", "intent": "general_inquiry", "urgency": "low"},
                {"annotator": "a2", "intent": "general_inquiry", "urgency": "low"},
            ],
        }
    ]
    with sample_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    loaded = load_jsonl(sample_path)
    assert len(loaded) == 1
    assert loaded[0].id == "X1"
    assert loaded[0].annotations[0].intent == "general_inquiry"


def test_dataset_conflict_count():
    repo_root = Path(__file__).resolve().parents[1]
    dataset_path = repo_root / "tickets_label.jsonl"
    tickets = load_jsonl(dataset_path)
    outputs_conflicts = process_tickets(tickets, conflicts_only=True)
    # Known conflicts in the supplied dataset
    assert len(outputs_conflicts) == 7
    # Ensure conflict reasons and suggested labels are present
    for out in outputs_conflicts:
        assert out.conflict_reason
        assert out.suggested_label
