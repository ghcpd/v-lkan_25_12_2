from collections import Counter
from typing import Dict, Any, List, Tuple

Intent = str
Urgency = str

INTENT_KEYWORDS = {
    "bug_report": ["crash", "error", "bug", "fail", "failed", "blank", "won't open", "wont open", "can't open", "cannot open", "not open", "won't load", "blank screen"],
    "billing_issue": ["payment", "refund", "charged", "billing", "invoice"],
    "subscription_issue": ["subscription", "renew", "auto-renew", "cancel", "benefits", "activated"],
    "account_issue": ["account", "login", "password", "verification", "locked", "recover", "delete"],
    "general_inquiry": ["how", "what", "when", "know", "policy", "inquire", "plan", "features", "promotions", "return"],
}

INTENT_PRIORITY = ["bug_report", "billing_issue", "subscription_issue", "account_issue", "general_inquiry"]
URGENCY_PRIORITY = ["critical", "high", "medium", "low"]

URGENCY_KEYWORDS = {
    "critical": ["crash", "error", "failed", "critical", "blank", "blank screen", "not open", "won't open", "cant open", "can't open"],
    "high": ["urgent", "immediately", "please", "assist", "unlock", "cannot", "can't", "wont", "won't"],
}


def _normalize(text: str) -> str:
    return text.lower()


def _keyword_vote(text: str, mapping: Dict[str, List[str]]) -> Counter:
    text_l = _normalize(text)
    votes = Counter()
    for label, keywords in mapping.items():
        for kw in keywords:
            if kw in text_l:
                votes[label] += 1
    return votes


def detect_conflict(record: Dict[str, Any]) -> bool:
    intents = {ann.get("intent") for ann in record.get("annotations", [])}
    urgencies = {ann.get("urgency") for ann in record.get("annotations", [])}
    return len(intents) > 1 or len(urgencies) > 1


def analyze_conflict(record: Dict[str, Any]) -> str:
    intents = {ann.get("intent") for ann in record.get("annotations", [])}
    urgencies = {ann.get("urgency") for ann in record.get("annotations", [])}
    reasons = []
    if len(intents) > 1:
        reasons.append(
            f"Annotators disagree on intent: {sorted(intents)}. Possible multiple aspects or ambiguous guidelines."
        )
    if len(urgencies) > 1:
        reasons.append(
            f"Annotators disagree on urgency: {sorted(urgencies)}. Severity perception may differ due to ambiguous severity cues."
        )
    return " ".join(reasons) if reasons else None


def _majority_vote(values: List[str]) -> Tuple[str, bool]:
    cnt = Counter(values)
    top_label, top_count = cnt.most_common(1)[0]
    tie = list(cnt.values()).count(top_count) > 1
    return top_label, tie


def _resolve_intent_with_keywords(text: str, fallback: str) -> str:
    votes = _keyword_vote(text, INTENT_KEYWORDS)
    if votes:
        top_count = max(votes.values())
        candidates = [label for label, c in votes.items() if c == top_count]
        for label in INTENT_PRIORITY:
            if label in candidates:
                return label
        return sorted(candidates)[0]
    return fallback


def _resolve_urgency_with_keywords(text: str, fallback: str) -> str:
    votes = _keyword_vote(text, URGENCY_KEYWORDS)
    if votes:
        top_count = max(votes.values())
        candidates = [label for label, c in votes.items() if c == top_count]
        for label in URGENCY_PRIORITY:
            if label in candidates:
                return label
        return sorted(candidates)[0]
    return fallback


def suggest_label(record: Dict[str, Any]) -> Dict[str, Any]:
    annotations = record.get("annotations", [])
    intents = [ann.get("intent") for ann in annotations if ann.get("intent")]
    urgencies = [ann.get("urgency") for ann in annotations if ann.get("urgency")]
    text = record.get("text", "")

    maj_intent, tie_intent = _majority_vote(intents) if intents else (None, False)
    maj_urgency, tie_urgency = _majority_vote(urgencies) if urgencies else (None, False)

    suggested_intent = maj_intent
    suggested_urgency = maj_urgency
    confidence = "high"
    conf_reason = "Unanimous agreement."
    explanation_parts = []

    if tie_intent:
        resolved_intent = _resolve_intent_with_keywords(text, maj_intent)
        if resolved_intent != maj_intent:
            explanation_parts.append(f"Intent tie resolved via text keywords → {resolved_intent}.")
        suggested_intent = resolved_intent
        confidence = "low"
        conf_reason = "Intent tie resolved heuristically." if tie_intent else conf_reason

    if tie_urgency:
        resolved_urgency = _resolve_urgency_with_keywords(text, maj_urgency)
        if resolved_urgency != maj_urgency:
            explanation_parts.append(f"Urgency tie resolved via text keywords → {resolved_urgency}.")
        suggested_urgency = resolved_urgency
        # downgrade confidence further if already low
        confidence = "low"
        conf_reason = "Urgency tie resolved heuristically." if tie_urgency else conf_reason

    # If no ties but conflicts exist (majority but not unanimous)
    conflict = detect_conflict(record)
    if conflict and confidence == "high":
        confidence = "medium"
        conf_reason = "Majority vote used; not unanimous."

    # If both intent and urgency unanimous
    if not conflict:
        conf_reason = "Unanimous across annotators."
        explanation_parts.append("No conflict detected; adopting unanimous labels.")

    explanation = " ".join(explanation_parts).strip() or None

    return {
        "intent": suggested_intent,
        "urgency": suggested_urgency,
        "majority_label": {"intent": maj_intent, "urgency": maj_urgency},
        "confidence": confidence,
        "confidence_reason": conf_reason,
        "explanation": explanation,
    }


def process_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single record into the output schema."""
    is_conflict = detect_conflict(record)
    conflict_reason = analyze_conflict(record)
    suggestion = suggest_label(record)

    labels = [
        {
            "annotator": ann.get("annotator"),
            "intent": ann.get("intent"),
            "urgency": ann.get("urgency"),
            "label": f"intent={ann.get('intent')}, urgency={ann.get('urgency')}",
        }
        for ann in record.get("annotations", [])
    ]

    return {
        "id": record.get("id"),
        "text": record.get("text"),
        "labels": labels,
        "is_conflict": is_conflict,
        "conflict_reason": conflict_reason,
        "suggested_label": suggestion,
    }
