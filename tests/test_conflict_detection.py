import json
from pathlib import Path

import tickets_conflict as tc


def make_record(annotations, text="test"):
    return {"id": "X", "text": text, "annotations": annotations}


def test_detect_conflict_none():
    record = make_record([
        {"annotator": "a1", "intent": "bug_report", "urgency": "high"},
        {"annotator": "a2", "intent": "bug_report", "urgency": "high"},
    ])
    assert tc.detect_conflict(record) is False
    out = tc.process_record(record)
    assert out["is_conflict"] is False
    assert out["suggested_label"]["intent"] == "bug_report"
    assert out["suggested_label"]["urgency"] == "high"
    assert out["suggested_label"]["confidence"] == "high"


def test_detect_conflict_intent_and_heuristic_resolution():
    record = make_record(
        [
            {"annotator": "a1", "intent": "billing_issue", "urgency": "medium"},
            {"annotator": "a2", "intent": "bug_report", "urgency": "medium"},
        ],
        text="The app crashes during payment",
    )
    assert tc.detect_conflict(record) is True
    out = tc.process_record(record)
    assert out["is_conflict"] is True
    assert "intent" in out["conflict_reason"].lower()
    # heuristic should pick bug_report due to "crash"
    assert out["suggested_label"]["intent"] == "bug_report"
    assert out["suggested_label"]["confidence"] == "low"


def test_detect_conflict_urgency_only():
    record = make_record(
        [
            {"annotator": "a1", "intent": "account_issue", "urgency": "high"},
            {"annotator": "a2", "intent": "account_issue", "urgency": "medium"},
        ],
        text="Cannot login",
    )
    assert tc.detect_conflict(record) is True
    out = tc.process_record(record)
    assert "urgency" in out["conflict_reason"].lower()
    assert out["suggested_label"]["intent"] == "account_issue"
    # majority is high? tie? here high vs medium => majority high
    assert out["suggested_label"]["urgency"] in {"high", "medium"}
    assert out["suggested_label"]["confidence"] in {"medium", "low"}


def test_process_multiple_records_and_cli(tmp_path: Path):
    records = [
        make_record([
            {"annotator": "a1", "intent": "account_issue", "urgency": "medium"},
            {"annotator": "a2", "intent": "account_issue", "urgency": "medium"},
        ], text="Login failed"),
        make_record([
            {"annotator": "a1", "intent": "billing_issue", "urgency": "high"},
            {"annotator": "a2", "intent": "bug_report", "urgency": "critical"},
        ], text="Payment failed and app crashed"),
    ]
    infile = tmp_path / "in.jsonl"
    with infile.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    outfile = tmp_path / "out.jsonl"
    from tickets_conflict.cli import main as cli_main

    cli_main(["--input", str(infile), "--output", str(outfile), "--conflicts-only"])

    out_records = tc.load_jsonl(str(outfile))
    # only one conflict should be present
    assert len(out_records) == 1
    out = out_records[0]
    assert out["is_conflict"] is True
    assert out["conflict_reason"] is not None
    assert out["suggested_label"]["intent"] in {"billing_issue", "bug_report"}


def test_report_template_exists():
    report_tpl = Path(__file__).resolve().parents[1] / "reports" / "test_report_template.md"
    assert report_tpl.exists()
