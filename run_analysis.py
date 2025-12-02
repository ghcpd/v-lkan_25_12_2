"""
Main entry point for running the conflict detection analysis
"""

import sys
import json
from conflict_detector import ConflictDetector


def main():
    """Run the full conflict detection and analysis pipeline"""
    
    print("=" * 70)
    print("Multi-Annotator Dataset Conflict Detection and Resolution")
    print("=" * 70)
    print()

    # Initialize detector
    detector = ConflictDetector()

    # Load dataset
    print("[1/4] Loading dataset...")
    try:
        detector.load_jsonl("tickets_label.jsonl")
        print(f"✓ Loaded {detector.statistics['total_samples']} samples")
    except FileNotFoundError:
        print("✗ Error: tickets_label.jsonl not found")
        sys.exit(1)
    print()

    # Process all samples
    print("[2/4] Processing and analyzing samples...")
    results = detector.process_all()
    print(f"✓ Processed {len(results)} samples")
    print()

    # Save results
    print("[3/4] Saving results...")
    detector.save_results("conflict_analysis_results.jsonl")
    print("✓ Full results saved to: conflict_analysis_results.jsonl")
    
    detector.save_conflicts_only("conflicts_only.jsonl")
    print("✓ Conflicts saved to: conflicts_only.jsonl")
    print()

    # Generate report
    print("[4/4] Generating report...")
    detector.generate_report("conflict_report.md")
    print("✓ Report saved to: conflict_report.md")
    print()

    # Display statistics
    print("=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    stats = detector.get_statistics()
    for key, value in stats.items():
        if key == "conflict_rate":
            print(f"{key.replace('_', ' ').title()}: {value*100:.1f}%")
        else:
            print(f"{key.replace('_', ' ').title()}: {value}")
    print()

    # Display sample conflicts
    conflict_samples = [c for c in detector.conflicts if c.is_conflict]
    if conflict_samples:
        print("=" * 70)
        print(f"SAMPLE CONFLICTS (showing first 5 of {len(conflict_samples)})")
        print("=" * 70)
        print()
        
        for i, conflict in enumerate(conflict_samples[:5], 1):
            print(f"[Conflict {i}] {conflict.id}")
            print(f"Text: {conflict.text}")
            print(f"Annotations:")
            for label in conflict.labels:
                print(f"  - {label['annotator']}: intent={label['intent']}, urgency={label['urgency']}")
            print(f"Reason: {conflict.conflict_reason[:100]}...")
            print(f"Suggested: intent={conflict.suggested_label['intent']}, urgency={conflict.suggested_label['urgency']}")
            print(f"Confidence: {conflict.suggested_label['confidence']}")
            print()

    print("=" * 70)
    print("Analysis complete! Check the output files for detailed results.")
    print("=" * 70)


if __name__ == "__main__":
    main()
