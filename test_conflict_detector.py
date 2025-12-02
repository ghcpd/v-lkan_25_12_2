"""
Comprehensive test suite for the conflict detection system

Tests cover:
- Correct detection of conflicts
- Accurate extraction of conflict samples
- Reliability of suggested final labels
- Correct reasoning and explanation for disagreements
- Handling datasets with multiple documents or batches
"""

import unittest
import json
import os
import tempfile
from typing import List, Dict, Any

from conflict_detector import (
    ConflictDetector, AnnotatorLabel, ConflictAnalysis,
    load_dataset, save_dataset
)
from utils import (
    calculate_percentage, extract_conflict_type, 
    validate_dataset_format, ReportGenerator
)
from config import Config


class TestConflictDetection(unittest.TestCase):
    """Test conflict detection functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = ConflictDetector(detailed_analysis=True)
    
    def test_unanimous_agreement_no_conflict(self):
        """Test that unanimous agreement is not flagged as conflict"""
        labels = [
            AnnotatorLabel("ann_01", "bug_report", "high"),
            AnnotatorLabel("ann_02", "bug_report", "high"),
            AnnotatorLabel("ann_03", "bug_report", "high"),
        ]
        
        is_conflict, details = self.detector.detect_conflict(labels)
        
        self.assertFalse(is_conflict)
        self.assertFalse(details["has_intent_conflict"])
        self.assertFalse(details["has_urgency_conflict"])
        self.assertEqual(details["unique_labels"], 1)
    
    def test_intent_conflict_detection(self):
        """Test detection of intent conflicts"""
        labels = [
            AnnotatorLabel("ann_01", "bug_report", "high"),
            AnnotatorLabel("ann_02", "billing_issue", "high"),
            AnnotatorLabel("ann_03", "bug_report", "high"),
        ]
        
        is_conflict, details = self.detector.detect_conflict(labels)
        
        self.assertTrue(is_conflict)
        self.assertTrue(details["has_intent_conflict"])
        self.assertFalse(details["has_urgency_conflict"])
        self.assertEqual(details["intent_distribution"]["bug_report"], 2)
        self.assertEqual(details["intent_distribution"]["billing_issue"], 1)
    
    def test_urgency_conflict_detection(self):
        """Test detection of urgency conflicts"""
        labels = [
            AnnotatorLabel("ann_01", "bug_report", "high"),
            AnnotatorLabel("ann_02", "bug_report", "medium"),
            AnnotatorLabel("ann_03", "bug_report", "high"),
        ]
        
        is_conflict, details = self.detector.detect_conflict(labels)
        
        self.assertTrue(is_conflict)
        self.assertFalse(details["has_intent_conflict"])
        self.assertTrue(details["has_urgency_conflict"])
        self.assertEqual(details["urgency_distribution"]["high"], 2)
        self.assertEqual(details["urgency_distribution"]["medium"], 1)
    
    def test_both_dimensions_conflict(self):
        """Test detection when both intent and urgency have conflicts"""
        labels = [
            AnnotatorLabel("ann_01", "bug_report", "critical"),
            AnnotatorLabel("ann_02", "billing_issue", "high"),
            AnnotatorLabel("ann_03", "bug_report", "high"),
        ]
        
        is_conflict, details = self.detector.detect_conflict(labels)
        
        self.assertTrue(is_conflict)
        self.assertTrue(details["has_intent_conflict"])
        self.assertTrue(details["has_urgency_conflict"])
        self.assertEqual(details["unique_labels"], 3)


class TestConflictCauseAnalysis(unittest.TestCase):
    """Test conflict cause analysis"""
    
    def setUp(self):
        self.detector = ConflictDetector(detailed_analysis=True)
    
    def test_ambiguous_keyword_detection(self):
        """Test detection of ambiguous keywords"""
        text = "Payment failed due to network error."
        labels = [
            AnnotatorLabel("ann_01", "billing_issue", "high"),
            AnnotatorLabel("ann_02", "bug_report", "medium"),
            AnnotatorLabel("ann_03", "billing_issue", "high"),
        ]
        
        _, conflict_details = self.detector.detect_conflict(labels)
        reason = self.detector.analyze_conflict_cause(text, labels, conflict_details)
        
        self.assertIn("ambiguous", reason.lower())
        self.assertIn("network error", reason.lower())
    
    def test_mixed_aspects_detection(self):
        """Test detection of mixed aspects in text"""
        text = "I want a refund but the app crashed during payment."
        labels = [
            AnnotatorLabel("ann_01", "billing_issue", "high"),
            AnnotatorLabel("ann_02", "bug_report", "critical"),
            AnnotatorLabel("ann_03", "billing_issue", "high"),
        ]
        
        _, conflict_details = self.detector.detect_conflict(labels)
        reason = self.detector.analyze_conflict_cause(text, labels, conflict_details)
        
        self.assertIn("mixed aspects", reason.lower())
        self.assertIn("but", reason.lower())
    
    def test_urgency_variance_analysis(self):
        """Test analysis of urgency disagreement"""
        text = "The app shows an error message."
        labels = [
            AnnotatorLabel("ann_01", "bug_report", "low"),
            AnnotatorLabel("ann_02", "bug_report", "high"),
            AnnotatorLabel("ann_03", "bug_report", "medium"),
        ]
        
        _, conflict_details = self.detector.detect_conflict(labels)
        reason = self.detector.analyze_conflict_cause(text, labels, conflict_details)
        
        self.assertIn("urgency", reason.lower())
    
    def test_brief_text_detection(self):
        """Test detection of brief text as conflict cause"""
        text = "App crashed."
        labels = [
            AnnotatorLabel("ann_01", "bug_report", "high"),
            AnnotatorLabel("ann_02", "bug_report", "critical"),
            AnnotatorLabel("ann_03", "bug_report", "medium"),
        ]
        
        _, conflict_details = self.detector.detect_conflict(labels)
        reason = self.detector.analyze_conflict_cause(text, labels, conflict_details)
        
        self.assertIn("brief text", reason.lower())


class TestResolutionSuggestion(unittest.TestCase):
    """Test resolution suggestion functionality"""
    
    def setUp(self):
        self.detector = ConflictDetector(detailed_analysis=True)
    
    def test_majority_vote_resolution(self):
        """Test basic majority vote resolution"""
        labels = [
            AnnotatorLabel("ann_01", "bug_report", "high"),
            AnnotatorLabel("ann_02", "billing_issue", "high"),
            AnnotatorLabel("ann_03", "bug_report", "high"),
        ]
        text = "The app shows an error."
        
        _, conflict_details = self.detector.detect_conflict(labels)
        suggested, reasoning = self.detector.suggest_resolution(labels, text, conflict_details)
        
        self.assertEqual(suggested, "bug_report|high")
        self.assertEqual(reasoning["majority_intent"], "bug_report")
        self.assertEqual(reasoning["majority_urgency"], "high")
        self.assertAlmostEqual(reasoning["intent_confidence"], 0.67, places=1)
    
    def test_contextual_adjustment_bug_report(self):
        """Test contextual adjustment for bug reports"""
        labels = [
            AnnotatorLabel("ann_01", "bug_report", "high"),
            AnnotatorLabel("ann_02", "bug_report", "high"),
            AnnotatorLabel("ann_03", "account_issue", "medium"),
        ]
        text = "App crashes when I try to login."
        
        _, conflict_details = self.detector.detect_conflict(labels)
        suggested, reasoning = self.detector.suggest_resolution(labels, text, conflict_details)
        
        # Should detect crash keyword and suggest bug_report with majority vote
        self.assertIn("bug_report", suggested)
        self.assertEqual(reasoning["majority_intent"], "bug_report")
    
    def test_unanimous_resolution(self):
        """Test resolution when all annotators agree"""
        labels = [
            AnnotatorLabel("ann_01", "billing_issue", "high"),
            AnnotatorLabel("ann_02", "billing_issue", "high"),
            AnnotatorLabel("ann_03", "billing_issue", "high"),
        ]
        text = "I need a refund for duplicate charge."
        
        _, conflict_details = self.detector.detect_conflict(labels)
        suggested, reasoning = self.detector.suggest_resolution(labels, text, conflict_details)
        
        self.assertEqual(suggested, "billing_issue|high")
        self.assertEqual(reasoning["intent_confidence"], 1.0)
        self.assertEqual(reasoning["urgency_confidence"], 1.0)
    
    def test_critical_urgency_adjustment(self):
        """Test urgency adjustment for critical cases"""
        labels = [
            AnnotatorLabel("ann_01", "bug_report", "high"),
            AnnotatorLabel("ann_02", "bug_report", "medium"),
            AnnotatorLabel("ann_03", "bug_report", "medium"),
        ]
        text = "App crashes during payment transaction."
        
        _, conflict_details = self.detector.detect_conflict(labels)
        suggested, reasoning = self.detector.suggest_resolution(labels, text, conflict_details)
        
        # Should detect crash + payment and adjust to critical
        self.assertIn("critical", suggested)


class TestSampleAnalysis(unittest.TestCase):
    """Test complete sample analysis"""
    
    def setUp(self):
        self.detector = ConflictDetector(detailed_analysis=True)
    
    def test_analyze_conflict_sample(self):
        """Test analysis of a sample with conflict"""
        sample = {
            "id": "TEST-001",
            "text": "I want a refund but the app crashed.",
            "annotations": [
                {"annotator": "ann_01", "intent": "billing_issue", "urgency": "high"},
                {"annotator": "ann_02", "intent": "bug_report", "urgency": "critical"},
                {"annotator": "ann_03", "intent": "billing_issue", "urgency": "high"},
            ]
        }
        
        analysis = self.detector.analyze_sample(sample)
        
        self.assertEqual(analysis.id, "TEST-001")
        self.assertTrue(analysis.is_conflict)
        self.assertIsNotNone(analysis.conflict_reason)
        self.assertIsNotNone(analysis.suggested_label)
        self.assertEqual(len(analysis.labels), 3)
    
    def test_analyze_no_conflict_sample(self):
        """Test analysis of a sample without conflict"""
        sample = {
            "id": "TEST-002",
            "text": "How do I reset my password?",
            "annotations": [
                {"annotator": "ann_01", "intent": "account_issue", "urgency": "low"},
                {"annotator": "ann_02", "intent": "account_issue", "urgency": "low"},
                {"annotator": "ann_03", "intent": "account_issue", "urgency": "low"},
            ]
        }
        
        analysis = self.detector.analyze_sample(sample)
        
        self.assertEqual(analysis.id, "TEST-002")
        self.assertFalse(analysis.is_conflict)
        self.assertIsNone(analysis.conflict_reason)
        self.assertEqual(analysis.suggested_label, "account_issue|low")


class TestBatchProcessing(unittest.TestCase):
    """Test batch dataset processing"""
    
    def setUp(self):
        self.detector = ConflictDetector(detailed_analysis=True)
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_process_small_dataset(self):
        """Test processing a small dataset"""
        # Create test dataset
        samples = [
            {
                "id": "TEST-001",
                "text": "App crashes.",
                "annotations": [
                    {"annotator": "ann_01", "intent": "bug_report", "urgency": "high"},
                    {"annotator": "ann_02", "intent": "bug_report", "urgency": "high"},
                    {"annotator": "ann_03", "intent": "bug_report", "urgency": "high"},
                ]
            },
            {
                "id": "TEST-002",
                "text": "Payment failed but app crashed.",
                "annotations": [
                    {"annotator": "ann_01", "intent": "billing_issue", "urgency": "high"},
                    {"annotator": "ann_02", "intent": "bug_report", "urgency": "critical"},
                    {"annotator": "ann_03", "intent": "billing_issue", "urgency": "high"},
                ]
            },
        ]
        
        input_path = os.path.join(self.test_dir, "test_input.jsonl")
        output_path = os.path.join(self.test_dir, "test_output.jsonl")
        
        # Save test data
        with open(input_path, 'w', encoding='utf-8') as f:
            for sample in samples:
                f.write(json.dumps(sample) + '\n')
        
        # Process dataset
        stats = self.detector.process_dataset(input_path, output_path)
        
        self.assertEqual(stats["total_samples"], 2)
        self.assertEqual(stats["conflict_samples"], 1)
        self.assertEqual(stats["no_conflict_samples"], 1)
        self.assertEqual(stats["output_samples"], 2)
        
        # Verify output file exists and has correct content
        self.assertTrue(os.path.exists(output_path))
        results = load_dataset(output_path)
        self.assertEqual(len(results), 2)
    
    def test_process_conflicts_only(self):
        """Test processing with conflicts_only filter"""
        samples = [
            {
                "id": "TEST-001",
                "text": "App crashes.",
                "annotations": [
                    {"annotator": "ann_01", "intent": "bug_report", "urgency": "high"},
                    {"annotator": "ann_02", "intent": "bug_report", "urgency": "high"},
                    {"annotator": "ann_03", "intent": "bug_report", "urgency": "high"},
                ]
            },
            {
                "id": "TEST-002",
                "text": "Payment failed.",
                "annotations": [
                    {"annotator": "ann_01", "intent": "billing_issue", "urgency": "high"},
                    {"annotator": "ann_02", "intent": "bug_report", "urgency": "medium"},
                    {"annotator": "ann_03", "intent": "billing_issue", "urgency": "high"},
                ]
            },
        ]
        
        input_path = os.path.join(self.test_dir, "test_input.jsonl")
        output_path = os.path.join(self.test_dir, "test_output.jsonl")
        
        with open(input_path, 'w', encoding='utf-8') as f:
            for sample in samples:
                f.write(json.dumps(sample) + '\n')
        
        stats = self.detector.process_dataset(input_path, output_path, conflicts_only=True)
        
        self.assertEqual(stats["total_samples"], 2)
        self.assertEqual(stats["output_samples"], 1)  # Only conflict sample


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def test_calculate_percentage(self):
        """Test percentage calculation"""
        self.assertEqual(calculate_percentage(50, 100), 50.0)
        self.assertEqual(calculate_percentage(1, 3), 33.33)
        self.assertEqual(calculate_percentage(0, 100), 0.0)
        self.assertEqual(calculate_percentage(10, 0), 0.0)  # Safe division
    
    def test_extract_conflict_type(self):
        """Test conflict type extraction"""
        self.assertEqual(
            extract_conflict_type("Ambiguous text: Contains terms..."),
            "ambiguous_text"
        )
        self.assertEqual(
            extract_conflict_type("Mixed aspects: Text contains..."),
            "mixed_aspects"
        )
        self.assertEqual(
            extract_conflict_type("Urgency assessment varies..."),
            "urgency_disagreement"
        )
        self.assertEqual(extract_conflict_type(None), "no_conflict")
    
    def test_validate_dataset_format_valid(self):
        """Test validation with valid dataset"""
        data = [
            {
                "id": "TEST-001",
                "text": "Test text",
                "annotations": [
                    {"annotator": "ann_01", "intent": "bug_report", "urgency": "high"}
                ]
            }
        ]
        
        is_valid, message = validate_dataset_format(data)
        self.assertTrue(is_valid)
    
    def test_validate_dataset_format_invalid(self):
        """Test validation with invalid dataset"""
        # Missing required field
        data = [{"id": "TEST-001", "text": "Test"}]
        is_valid, message = validate_dataset_format(data)
        self.assertFalse(is_valid)
        
        # Empty annotations
        data = [{"id": "TEST-001", "text": "Test", "annotations": []}]
        is_valid, message = validate_dataset_format(data)
        self.assertFalse(is_valid)


class TestReportGeneration(unittest.TestCase):
    """Test report generation"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.results = [
            {
                "id": "TEST-001",
                "text": "Test text",
                "labels": [
                    {"annotator": "ann_01", "label": "bug_report|high"},
                    {"annotator": "ann_02", "label": "bug_report|high"},
                ],
                "is_conflict": False,
                "conflict_reason": None,
                "suggested_label": "bug_report|high"
            },
            {
                "id": "TEST-002",
                "text": "Payment failed but app crashed.",
                "labels": [
                    {"annotator": "ann_01", "label": "billing_issue|high"},
                    {"annotator": "ann_02", "label": "bug_report|critical"},
                ],
                "is_conflict": True,
                "conflict_reason": "Ambiguous text: Contains multiple issue types",
                "suggested_label": "billing_issue|high"
            }
        ]
        self.stats = {
            "total_samples": 2,
            "conflict_samples": 1,
            "no_conflict_samples": 1,
            "intent_conflicts": 1,
            "urgency_conflicts": 1,
            "both_conflicts": 0,
            "output_samples": 2
        }
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_generate_report(self):
        """Test markdown report generation"""
        report_path = os.path.join(self.test_dir, "test_report.md")
        generator = ReportGenerator(self.results, self.stats)
        generator.generate(report_path, include_examples=True, max_examples=2)
        
        self.assertTrue(os.path.exists(report_path))
        
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn("Multi-Annotator Conflict Detection Report", content)
        self.assertIn("Executive Summary", content)
        self.assertIn("Detailed Statistics", content)
        self.assertIn("Conflict Cause Analysis", content)
        self.assertIn("Example Cases", content)
        self.assertIn("Recommendations", content)


def run_test_suite():
    """Run all tests and generate report"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConflictDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestConflictCauseAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestResolutionSuggestion))
    suite.addTests(loader.loadTestsFromTestCase(TestSampleAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestBatchProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilityFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestReportGeneration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate test report
    generate_test_report(result)
    
    return result


def generate_test_report(result):
    """Generate detailed test report"""
    report_lines = [
        "=" * 70,
        "AUTOMATED TEST REPORT",
        "=" * 70,
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "Test Summary:",
        f"  Total Tests Run: {result.testsRun}",
        f"  Passed: {result.testsRun - len(result.failures) - len(result.errors)}",
        f"  Failed: {len(result.failures)}",
        f"  Errors: {len(result.errors)}",
        f"  Skipped: {len(result.skipped)}",
        "",
        f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.2f}%",
        "=" * 70,
    ]
    
    if result.failures:
        report_lines.extend([
            "",
            "FAILURES:",
            "-" * 70,
        ])
        for test, traceback in result.failures:
            report_lines.extend([
                f"\n{test}:",
                traceback,
                "-" * 70,
            ])
    
    if result.errors:
        report_lines.extend([
            "",
            "ERRORS:",
            "-" * 70,
        ])
        for test, traceback in result.errors:
            report_lines.extend([
                f"\n{test}:",
                traceback,
                "-" * 70,
            ])
    
    if result.wasSuccessful():
        report_lines.extend([
            "",
            "✓ ALL TESTS PASSED",
            "=" * 70,
        ])
    
    report = "\n".join(report_lines)
    
    # Save report
    report_path = "test_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(report)
    print(f"\nDetailed test report saved to: {report_path}")


if __name__ == '__main__':
    from datetime import datetime
    run_test_suite()
