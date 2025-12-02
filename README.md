# Multi-Annotator Conflict Detection & Resolution

This small project identifies annotation conflicts among multiple annotators, explains possible reasons for disagreements, and suggests a resolved label (intent + urgency) with confidence reasoning.

Quick usage (from repo root):

1. Run the CLI to extract conflicts from the example dataset:

   python -m src.conflict_resolver.main tickets_label.jsonl conflicts_output.jsonl

2. Output format: each line in `conflicts_output.jsonl` is a JSON object:

   {
     "id": "TICK-0026",
     "text": "I want a refund but the app says payment failed.",
     "labels": [{"annotator":"ann_01","label":"billing_issue|high"}, ...],
     "is_conflict": true,
     "conflict_reason": "annotators disagreed on intent: billing_issue,bug_report",
     "suggested_label": "billing_issue|high",
     "suggested_label_details": { "final_intent": ..., "final_urgency": ..., "confidence":..., "explanation": ... }
   }

3. Run tests:

   pip install -r requirements.txt
   pytest -q

Code layout
- src/conflict_resolver/detector.py  - conflict detection and parsing utilities
- src/conflict_resolver/resolver.py  - heuristics to suggest final labels and explanation
- src/conflict_resolver/main.py      - CLI to run extraction and output conflict-only JSONL
# v-lkan_25_12_2