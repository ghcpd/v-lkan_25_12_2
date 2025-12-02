import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import conflict_resolver.detector as detector


def test_detect_conflict_simple_agreement():
    sample = {
        'id': 'S1',
        'text': 'All annotators agree',
        'annotations': [
            {'annotator': 'a1', 'intent': 'account_issue', 'urgency': 'low'},
            {'annotator': 'a2', 'intent': 'account_issue', 'urgency': 'low'},
            {'annotator': 'a3', 'intent': 'account_issue', 'urgency': 'low'},
        ]
    }

    out = detector.detect_conflict(sample)
    assert out['is_conflict'] is False
    assert out['intent_conflict'] is False
    assert out['urgency_conflict'] is False


def test_detect_conflict_intent_disagreement():
    sample = {
        'id': 'S2',
        'text': 'Different intents',
        'annotations': [
            {'annotator': 'a1', 'intent': 'bug_report', 'urgency': 'high'},
            {'annotator': 'a2', 'intent': 'billing_issue', 'urgency': 'high'},
            {'annotator': 'a3', 'intent': 'bug_report', 'urgency': 'high'},
        ]
    }
    out = detector.detect_conflict(sample)
    assert out['is_conflict'] is True
    assert out['intent_conflict'] is True
    assert out['urgency_conflict'] is False
