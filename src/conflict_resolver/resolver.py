import re
from collections import Counter
from typing import Dict, Any


KEYWORD_INTENT_MAP = {
    'refund': 'billing_issue',
    'charged': 'billing_issue',
    'payment': 'billing_issue',
    'payment failed': 'billing_issue',
    'payment page': 'bug_report',
    'crash': 'bug_report',
    'crashes': 'bug_report',
    'error': 'bug_report',
    'app': 'bug_report',
    'subscription': 'subscription_issue',
    'cancel subscription': 'subscription_issue',
    'locked': 'account_issue',
    'password': 'account_issue',
    'login': 'account_issue',
    'delete my account': 'account_issue',
    'return': 'general_inquiry',
    'return policy': 'general_inquiry',
    'phone number': 'general_inquiry',
}


def text_keyword_intent(text: str) -> str:
    t = text.lower()
    # look for best keyword match
    for k, v in KEYWORD_INTENT_MAP.items():
        if k in t:
            return v
    return 'ambiguous'


def suggest_intent(intents: list, text: str) -> Dict[str, Any]:
    # majority first
    ctr = Counter(intents)
    most_common, freq = ctr.most_common(1)[0]
    total = sum(ctr.values())

    if freq / total >= 0.66:
        # strong majority
        confidence = 'high'
        reason = f"Majority voting: '{most_common}' ({freq}/{total})"
        final = most_common
    elif freq / total >= 0.5:
        confidence = 'medium'
        reason = f"Weak majority: '{most_common}' ({freq}/{total})"
        final = most_common
    else:
        # no majority -- use text heuristic
        inferred = text_keyword_intent(text)
        if inferred != 'ambiguous':
            final = inferred
            confidence = 'medium'
            reason = f"No clear annotator majority; used keyword inference '{inferred}' from text"
        else:
            # fallback to most common anyway but mark low confidence
            final = most_common
            confidence = 'low'
            reason = "No clear consensus and no keyword match — low-confidence fallback to most common"

    return {'final_intent': final, 'confidence': confidence, 'reason': reason}


def suggest_urgency(urgencies: list, text: str) -> Dict[str, Any]:
    ctr = Counter(urgencies)
    most_common, freq = ctr.most_common(1)[0]
    total = sum(ctr.values())

    # map textual cues to urgency
    high_words = ['crash', 'cannot', 'cannot', "can't", 'critical', 'denied', 'suddenly', 'locked', 'failure']

    if freq / total >= 0.66:
        confidence = 'high'
        reason = f"Majority voting: '{most_common}' ({freq}/{total})"
        final = most_common
    elif freq / total >= 0.5:
        confidence = 'medium'
        reason = f"Weak majority: '{most_common}' ({freq}/{total})"
        final = most_common
    else:
        # check text for severity
        low = any(w in text.lower() for w in high_words)
        if low:
            final = 'critical' if 'crash' in text.lower() or 'critical' in text.lower() else 'high'
            confidence = 'medium'
            reason = f"Mixed annotator urgencies; inferred '{final}' from severity cues in text"
        else:
            final = most_common
            confidence = 'low'
            reason = 'No clear consensus and no severity cues — low-confidence fallback to most common'

    return {'final_urgency': final, 'confidence': confidence, 'reason': reason}


def resolve(sample: Dict[str, Any]) -> Dict[str, Any]:
    annotations = sample.get('annotations', [])
    intents = [ann.get('intent') for ann in annotations]
    urgencies = [ann.get('urgency') for ann in annotations]
    text = sample.get('text', '')

    intent_out = suggest_intent(intents, text)
    urgency_out = suggest_urgency(urgencies, text)

    final_label = f"{intent_out['final_intent']}|{urgency_out['final_urgency']}"

    # Compose an explanation summarizing the decision
    explanation_parts = [intent_out['reason'], urgency_out['reason']]
    explanation = ' ; '.join(explanation_parts)

    confidence = 'high' if intent_out['confidence'] == 'high' and urgency_out['confidence'] == 'high' else (
        'medium' if 'high' in (intent_out['confidence'], urgency_out['confidence']) or 
        intent_out['confidence'] == 'medium' or urgency_out['confidence'] == 'medium' else 'low')

    return {
        'final_label': final_label,
        'final_intent': intent_out['final_intent'],
        'final_urgency': urgency_out['final_urgency'],
        'confidence': confidence,
        'explanation': explanation
    }
