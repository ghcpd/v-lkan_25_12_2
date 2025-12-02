from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, List, Tuple

from .models import Annotation, Ticket, OutputSample, LabelEntry, Resolution

# Keyword heuristics to infer possible intents from text
INTENT_KEYWORDS = {
    "bug_report": [
        "crash",
        "crashes",
        "error",
        "bug",
        "fault",
        "failed",
        "won't",
        "won’t",
        "blank",
        "freeze",
        "won t",
        "won’t",
    ],
    "billing_issue": [
        "refund",
        "charged",
        "payment",
        "billing",
        "invoice",
        "auto-renew",
        "auto renewal",
        "credit",
    ],
    "subscription_issue": [
        "subscription",
        "cancel",
        "renew",
        "plan",
        "activate",
        "activated",
        "renewal",
    ],
    "account_issue": [
        "account",
        "login",
        "password",
        "verification",
        "locked",
        "unlock",
        "delete",
    ],
    "general_inquiry": [
        "know",
        "policy",
        "phone",
        "return",
        "promotions",
        "inquire",
        "when will",
        "what is",
    ],
}

URGENCY_WEIGHTS = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}

URGENT_KEYWORDS = {
    "critical": ["crash", "crashes", "critical", "won't", "won t", "error"],
    "high": ["urgent", "asap", "immediately", "please", "failed", "cannot", "can't"],
}

CONTRASTIVE_CUES = [" but ", " however", " although", " yet "]


def load_jsonl(path: str | Path) -> List[Ticket]:
    """Load tickets from a JSONL file into Ticket models."""
    p = Path(path)
    tickets: List[Ticket] = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            tickets.append(Ticket.model_validate(data))
    return tickets


def write_output(path: str | Path, samples: Iterable[OutputSample], fmt: str = "jsonl") -> None:
    """Write output samples as JSONL or JSON."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "jsonl":
        with p.open("w", encoding="utf-8") as f:
            for sample in samples:
                f.write(sample.model_dump_json())
                f.write("\n")
    elif fmt == "json":
        with p.open("w", encoding="utf-8") as f:
            json.dump([s.model_dump() for s in samples], f, indent=2)
    else:
        raise ValueError(f"Unsupported format: {fmt}")


def _infer_intent_scores(text: str) -> dict[str, int]:
    text_lower = text.lower()
    scores = defaultdict(int)
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[intent] += 1
    return dict(scores)


def _infer_urgency_scores(text: str) -> dict[str, int]:
    text_lower = text.lower()
    scores = defaultdict(int)
    for urgency, keywords in URGENT_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[urgency] += 1
    return dict(scores)


def _is_contrastive(text: str) -> bool:
    tl = text.lower()
    return any(cue in tl for cue in CONTRASTIVE_CUES)


def is_conflict(ticket: Ticket) -> bool:
    labels = {ann.label for ann in ticket.annotations}
    return len(labels) > 1


def _conflict_reason(ticket: Ticket, counts: Counter, intents: set[str], urgencies: set[str]) -> str:
    parts: List[str] = []
    if len(intents) > 1:
        parts.append(
            "Intent disagreement: "
            + ", ".join(f"{intent} ({sum(1 for a in ticket.annotations if a.intent==intent)})" for intent in sorted(intents))
        )
    if len(urgencies) > 1:
        parts.append(
            "Urgency disagreement: "
            + ", ".join(
                f"{urgency} ({sum(1 for a in ticket.annotations if a.urgency==urgency)})" for urgency in sorted(urgencies)
            )
        )
    intent_scores = _infer_intent_scores(ticket.text)
    if len(intent_scores) > 1:
        parts.append(
            "Text cues multiple intents: "
            + ", ".join(f"{intent}:{score}" for intent, score in intent_scores.items())
        )
    urgency_scores = _infer_urgency_scores(ticket.text)
    if len(urgency_scores) > 1:
        parts.append(
            "Ambiguous urgency cues: "
            + ", ".join(f"{urgency}:{score}" for urgency, score in urgency_scores.items())
        )
    if _is_contrastive(ticket.text):
        parts.append("Contrasting language suggests mixed aspects")
    if not parts:
        parts.append("Labels differ but no obvious textual cues; possible guideline inconsistency")
    return "; ".join(parts)


def _score_label(label: str, counts: Counter, intent_scores: dict[str, int], urgency_scores: dict[str, int]) -> float:
    intent, urgency = label.split("|", 1)
    base = counts[label] * 2.0  # weight agreement strongly
    base += intent_scores.get(intent, 0)
    # Map urgency_scores keys (critical, high) to labels
    base += urgency_scores.get(urgency.lower(), 0)
    base += URGENCY_WEIGHTS.get(urgency.lower(), 0) * 0.5
    return base


def suggest_label(ticket: Ticket) -> Tuple[str, Resolution]:
    counts = Counter(ann.label for ann in ticket.annotations)
    majority_label, majority_count = counts.most_common(1)[0]
    intent_scores = _infer_intent_scores(ticket.text)
    urgency_scores = _infer_urgency_scores(ticket.text)

    def _key(label: str):
        return (
            _score_label(label, counts, intent_scores, urgency_scores),
            counts[label],
            URGENCY_WEIGHTS.get(label.split("|", 1)[1].lower(), 0),
        )

    best_label = max(counts.keys(), key=_key)
    confidence = counts[best_label] / len(ticket.annotations)

    # Build explanation
    explanation_parts = [f"Majority: {majority_label} ({majority_count}/{len(ticket.annotations)})"]
    if best_label != majority_label:
        explanation_parts.append(f"Adjusted by text cues towards {best_label}")
    if intent_scores:
        explanation_parts.append("Intent cues: " + ", ".join(f"{k}:{v}" for k, v in intent_scores.items()))
    if urgency_scores:
        explanation_parts.append("Urgency cues: " + ", ".join(f"{k}:{v}" for k, v in urgency_scores.items()))
    explanation = "; ".join(explanation_parts)

    resolution = Resolution(
        majority_label=majority_label,
        confidence=round(confidence, 3),
        explanation=explanation,
    )
    return best_label, resolution


def process_tickets(tickets: Iterable[Ticket], conflicts_only: bool = False) -> List[OutputSample]:
    outputs: List[OutputSample] = []
    for t in tickets:
        intents = {a.intent for a in t.annotations}
        urgencies = {a.urgency for a in t.annotations}
        conflict = is_conflict(t)
        if conflicts_only and not conflict:
            continue
        labels = [LabelEntry(annotator=a.annotator, label=a.label) for a in t.annotations]
        conflict_reason = _conflict_reason(t, None, intents, urgencies) if conflict else None
        suggested_label, resolution = suggest_label(t)
        outputs.append(
            OutputSample(
                id=t.id,
                text=t.text,
                labels=labels,
                is_conflict=conflict,
                conflict_reason=conflict_reason,
                suggested_label=suggested_label,
                resolution=resolution,
            )
        )
    return outputs
