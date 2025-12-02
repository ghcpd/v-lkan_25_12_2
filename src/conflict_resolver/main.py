import argparse
import json
try:
    # When running as a top-level script where `src` is on PYTHONPATH
    from conflict_resolver.detector import load_jsonl, filter_conflicts, detect_conflict
    from conflict_resolver.resolver import resolve
except Exception:
    # When run as a module (python -m src.conflict_resolver.main) use relative imports
    from .detector import load_jsonl, filter_conflicts, detect_conflict
    from .resolver import resolve


def build_output_record(sample_raw: dict) -> dict:
    # Runs detection + resolution and produces final output schema
    det = detect_conflict(sample_raw)

    out = {
        'id': det['id'],
        'text': det['text'],
        'labels': det['labels'],
        'is_conflict': det['is_conflict'],
        'conflict_reason': None,
        'suggested_label': None,
        'suggested_label_details': None,
    }

    if det['is_conflict']:
        reasons = []
        if det['intent_conflict']:
            reasons.append('annotators disagreed on intent: ' + ','.join(det['unique_intents']))
        if det['urgency_conflict']:
            reasons.append('annotators disagreed on urgency: ' + ','.join(det['unique_urgencies']))
        out['conflict_reason'] = ' ; '.join(reasons)

        # Add suggestion
        suggestion = resolve(sample_raw)
        out['suggested_label'] = suggestion['final_label']
        out['suggested_label_details'] = suggestion

    return out


def process(input_path: str, output_path: str):
    src = load_jsonl(input_path)
    # We'll write only conflict samples per requirement
    with open(output_path, 'w', encoding='utf-8') as fh:
        count = 0
        for raw in src:
            out = build_output_record(raw)
            if out['is_conflict']:
                fh.write(json.dumps(out, ensure_ascii=False) + '\n')
                count += 1

    return count


def main():
    parser = argparse.ArgumentParser(description='Detect annotation conflicts and suggest resolutions')
    parser.add_argument('input', help='Input JSONL file')
    parser.add_argument('output', help='Output JSONL file for conflicts')
    args = parser.parse_args()
    n = process(args.input, args.output)
    print(f'Written {n} conflict records to {args.output}')


if __name__ == '__main__':
    main()
