import json
from collections import Counter
from typing import Dict, Iterable, List, Tuple, Any


def load_jsonl(path: str) -> Iterable[Dict[str, Any]]:
    with open(path, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def normalize_label(annotation: Dict[str, str]) -> str:
    # We'll keep both intent and urgency in a compact label form
    intent = annotation.get('intent', '').strip()
    urgency = annotation.get('urgency', '').strip()
    return f"{intent}|{urgency}"


def extract_annotator_labels(sample: Dict[str, Any]) -> List[Dict[str, str]]:
    # Return list of {annotator, label}
    result = []
    for ann in sample.get('annotations', []):
        result.append({'annotator': ann.get('annotator'), 'label': normalize_label(ann)})
    return result


def detect_conflict(sample: Dict[str, Any]) -> Dict[str, Any]:
    # Determine whether the annotators disagree on intent or urgency
    annotations = sample.get('annotations', [])
    intents = [ann.get('intent') for ann in annotations]
    urgencies = [ann.get('urgency') for ann in annotations]

    unique_intents = sorted(set(intents))
    unique_urgencies = sorted(set(urgencies))

    intent_conflict = len(unique_intents) > 1
    urgency_conflict = len(unique_urgencies) > 1

    is_conflict = intent_conflict or urgency_conflict

    return {
        'id': sample.get('id'),
        'text': sample.get('text'),
        'labels': extract_annotator_labels(sample),
        'is_conflict': is_conflict,
        'intent_conflict': intent_conflict,
        'urgency_conflict': urgency_conflict,
        'unique_intents': unique_intents,
        'unique_urgencies': unique_urgencies,
    }


def filter_conflicts(samples: Iterable[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
    for s in samples:
        info = detect_conflict(s)
        if info['is_conflict']:
            yield info
