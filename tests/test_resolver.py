import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import conflict_resolver.resolver as resolver


def test_suggest_intent_majority():
    intents = ['billing_issue', 'billing_issue', 'bug_report']
    text = 'I want a refund for a wrong charge'
    res = resolver.suggest_intent(intents, text)
    assert res['final_intent'] == 'billing_issue'
    assert res['confidence'] in ('medium', 'high')


def test_resolve_tie_uses_keywords():
    # three different intents -> rely on keywords in text
    sample = {'annotations': [
        {'annotator': 'a1', 'intent': 'bug_report', 'urgency': 'medium'},
        {'annotator': 'a2', 'intent': 'subscription_issue', 'urgency': 'high'},
        {'annotator': 'a3', 'intent': 'account_issue', 'urgency': 'low'},
    ], 'text': 'I need a refund, the payment failed during checkout'}

    out = resolver.resolve(sample)
    assert 'billing_issue' in out['final_label']
    assert out['confidence'] in ('low', 'medium', 'high')
