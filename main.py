#!/usr/bin/env python3
"""
Multi-Annotator Conflict Detection System - Main Application

Command-line interface for detecting and analyzing annotation conflicts
in multi-annotator datasets.
"""

import argparse
import sys
import os
from datetime import datetime

from conflict_detector import ConflictDetector, load_dataset
from utils import (
    generate_statistics_summary, 
    ReportGenerator,
    validate_dataset_format,
    ensure_directory
)
from config import Config


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Multi-Annotator Conflict Detection and Resolution System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process entire dataset
  python main.py --input tickets_label.jsonl --output results.jsonl
  
  # Extract conflicts only
  python main.py --input tickets_label.jsonl --output results.jsonl --conflicts-only
  
  # Generate detailed report
  python main.py --input tickets_label.jsonl --output results.jsonl --report report.md
  
  # Disable detailed analysis for faster processing
  python main.py --input tickets_label.jsonl --output results.jsonl --no-details
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--input', '-i',
        type=str,
        default=Config.DEFAULT_INPUT_FILE,
        help=f'Input JSONL file path (default: {Config.DEFAULT_INPUT_FILE})'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=Config.DEFAULT_OUTPUT_FILE,
        help=f'Output JSONL file path (default: {Config.DEFAULT_OUTPUT_FILE})'
    )
    
    # Optional arguments
    parser.add_argument(
        '--conflicts-only',
        action='store_true',
        help='Output only samples with conflicts'
    )
    
    parser.add_argument(
        '--report', '-r',
        type=str,
        default=None,
        help='Generate markdown report at specified path'
    )
    
    parser.add_argument(
        '--no-details',
        action='store_true',
        help='Disable detailed conflict analysis (faster processing)'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate dataset format without processing'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Multi-Annotator Conflict Detector v1.0.0'
    )
    
    return parser.parse_args()


def validate_input_file(file_path: str) -> bool:
    """Validate input file exists and is readable"""
    if not os.path.exists(file_path):
        print(f"Error: Input file '{file_path}' does not exist.", file=sys.stderr)
        return False
    
    if not os.path.isfile(file_path):
        print(f"Error: '{file_path}' is not a file.", file=sys.stderr)
        return False
    
    if not os.access(file_path, os.R_OK):
        print(f"Error: Input file '{file_path}' is not readable.", file=sys.stderr)
        return False
    
    return True


def validate_dataset(file_path: str, verbose: bool = False) -> bool:
    """Validate dataset format"""
    if verbose:
        print(f"Validating dataset format...")
    
    try:
        data = load_dataset(file_path)
        is_valid, message = validate_dataset_format(data)
        
        if is_valid:
            if verbose:
                print(f"✓ Dataset format is valid ({len(data)} samples)")
            return True
        else:
            print(f"Error: {message}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"Error validating dataset: {e}", file=sys.stderr)
        return False


def main():
    """Main application entry point"""
    args = parse_arguments()
    
    # Print header
    if args.verbose:
        print("=" * 70)
        print("Multi-Annotator Conflict Detection System")
        print("=" * 70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    # Validate input file
    if not validate_input_file(args.input):
        return 1
    
    # Validate dataset format
    if not validate_dataset(args.input, args.verbose):
        return 1
    
    # If validation-only mode, exit here
    if args.validate_only:
        print("✓ Dataset validation passed")
        return 0
    
    # Create detector
    detector = ConflictDetector(detailed_analysis=not args.no_details)
    
    if args.verbose:
        print(f"Input file: {args.input}")
        print(f"Output file: {args.output}")
        print(f"Conflicts only: {args.conflicts_only}")
        print(f"Detailed analysis: {not args.no_details}")
        print()
        print("Processing dataset...")
    
    # Process dataset
    try:
        stats = detector.process_dataset(
            input_path=args.input,
            output_path=args.output,
            conflicts_only=args.conflicts_only
        )
    except Exception as e:
        print(f"Error processing dataset: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    # Print statistics
    if args.verbose:
        print()
        print(generate_statistics_summary(stats))
    else:
        # Brief output for non-verbose mode
        print(f"Processed {stats['total_samples']} samples")
        print(f"Found {stats['conflict_samples']} conflicts ({stats['conflict_samples']/stats['total_samples']*100:.1f}%)")
        print(f"Results saved to: {args.output}")
    
    # Generate report if requested
    if args.report:
        if args.verbose:
            print()
            print(f"Generating detailed report: {args.report}")
        
        try:
            # Load results
            results = load_dataset(args.output)
            
            # Generate report
            generator = ReportGenerator(results, stats)
            generator.generate(
                output_path=args.report,
                include_examples=Config.INCLUDE_EXAMPLES,
                max_examples=Config.MAX_EXAMPLES_PER_CATEGORY
            )
            
            print(f"✓ Report generated: {args.report}")
        except Exception as e:
            print(f"Warning: Failed to generate report: {e}", file=sys.stderr)
            if args.verbose:
                import traceback
                traceback.print_exc()
    
    # Print completion
    if args.verbose:
        print()
        print("=" * 70)
        print("Processing completed successfully")
        print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
