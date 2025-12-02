# Multi-Annotator Conflict Detector

Detects label conflicts in multi-annotator datasets, explains disagreements, and suggests resolved labels with reasoning.

## Quickstart

### 1) Create virtual environment
- Using the user-provided interpreter:
	- `D:\package\venv310\Scripts\python.exe -m venv .venv`
- Activate (PowerShell): `./.venv/Scripts/Activate.ps1`
- Install deps: `python -m pip install -r requirements.txt`

### 2) Run CLI
```
python -m conflict_detector.cli \
	--input tickets_label.jsonl \
	--output output.jsonl \
	--format jsonl \
	--conflicts-only
```

Outputs JSON/JSONL with fields:
- `id`, `text`
- `labels`: list of `{annotator, label}` where `label = intent|urgency`
- `is_conflict`: bool
- `conflict_reason`: explanation (or null)
- `suggested_label`: resolved label
- `resolution`: `{majority_label, confidence, explanation}`

## Tests
```
python -m pytest
```
- JUnit XML: `reports/junit.xml`
- Coverage: `--cov=conflict_detector` (configured in `pytest.ini`)

## Docker
```
docker build -t conflict-detector .
docker run --rm -v %CD%:/data conflict-detector \
	--input /data/tickets_label.jsonl --output /data/out.jsonl --format jsonl
```

## Project Layout
- `conflict_detector/`: library & CLI
- `tests/`: pytest suite
- `reports/`: JUnit & templates
- `tickets_label.jsonl`: sample dataset

## Notes
- Conflict reasoning uses keyword heuristics for intents/urgency and detects contrasting language.
- Suggested label balances majority vote, text cues, and urgency weighting.