import json
import subprocess
import sys
from pathlib import Path


def test_cli_runs_and_writes_output(tmp_path: Path):
    sample_path = tmp_path / "sample.jsonl"
    output_path = tmp_path / "out.jsonl"
    rows = [
        {
            "id": "X1",
            "text": "Refund please.",
            "annotations": [
                {"annotator": "a1", "intent": "billing_issue", "urgency": "high"},
                {"annotator": "a2", "intent": "billing_issue", "urgency": "high"},
            ],
        },
        {
            "id": "X2",
            "text": "Refund but app crashed.",
            "annotations": [
                {"annotator": "a1", "intent": "billing_issue", "urgency": "high"},
                {"annotator": "a2", "intent": "bug_report", "urgency": "critical"},
            ],
        },
    ]
    with sample_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    cmd = [
        sys.executable,
        "-m",
        "conflict_detector.cli",
        "--input",
        str(sample_path),
        "--output",
        str(output_path),
        "--format",
        "jsonl",
        "--conflicts-only",
    ]
    subprocess.run(cmd, check=True, cwd=Path(__file__).resolve().parents[1])

    assert output_path.exists()
    lines = output_path.read_text(encoding="utf-8").strip().splitlines()
    # Only one conflict expected
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["id"] == "X2"
    assert data["is_conflict"] is True
    assert data["suggested_label"]
