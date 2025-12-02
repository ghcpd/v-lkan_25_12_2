import tempfile
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from conflict_resolver.main import process


def test_integration_process_sample_file():
    repo_root = os.path.join(os.path.dirname(__file__), '..')
    data_path = os.path.join(repo_root, 'tickets_label.jsonl')
    # adapt path for running tests in repo root
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tickets_label.jsonl'))

    assert os.path.exists(data_path), 'Input dataset not found for integration test'

    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    try:
        count = process(data_path, tmp.name)
        # We expect some conflicts in the provided dataset
        assert count > 0
        with open(tmp.name, 'r', encoding='utf-8') as fh:
            lines = fh.read().strip().splitlines()
            assert len(lines) == count
            # pick first JSON line and ensure keys exist
            import json
            sample = json.loads(lines[0])
            assert 'id' in sample and 'labels' in sample and 'conflict_reason' in sample
    finally:
        os.unlink(tmp.name)
