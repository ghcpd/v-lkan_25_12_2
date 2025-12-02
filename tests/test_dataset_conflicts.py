import os, sys, json, tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from conflict_resolver.main import process


def test_expected_conflicts_in_dataset():
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tickets_label.jsonl'))
    assert os.path.exists(data_path), 'dataset not found'

    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    try:
        count = process(data_path, tmp.name)
        assert count > 0

        with open(tmp.name, 'r', encoding='utf-8') as fh:
            rows = [json.loads(l) for l in fh.read().strip().splitlines() if l.strip()]

        ids = [r['id'] for r in rows]

        # Based on manual inspection of the dataset, these tickets have annotator intent-level disagreements
        expected_conflict_ids = set(['TICK-0026','TICK-0027','TICK-0028','TICK-0046','TICK-0047','TICK-0048','TICK-0049'])

        # Ensure the expected conflicted IDs are present
        assert expected_conflict_ids.issubset(set(ids))

        # Ensure each conflict sample has suggestion metadata
        for r in rows:
            assert r.get('suggested_label') is not None
            assert isinstance(r.get('suggested_label_details'), dict)

    finally:
        os.unlink(tmp.name)
