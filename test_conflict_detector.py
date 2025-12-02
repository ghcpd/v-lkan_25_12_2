"""
Unit tests for the Conflict Detection and Resolution System

Tests verify:
1. Correct detection of conflicts
2. Accurate extraction of conflict samples
3. Reliability of suggested final labels
4. Quality of reasoning and explanations
5. Handling of edge cases
"""

import json
import unittest
import tempfile
import os
from conflict_detector import (
    ConflictDetector,
    ConflictAnalysis,
    AnnotationLabel
)


class TestConflictDetection(unittest.TestCase):
    """Test cases for conflict detection"""

    def setUp(self):
        """Set up test fixtures"""
        self.detector = ConflictDetector()

    def test_unanimous_annotation_no_conflict(self):
        """Test that unanimous annotations are not marked as conflicts"""
        sample = {
            "id": "TEST-001",
            "text": "The app crashes on startup.",
            "annotations": [
                {"annotator": "A1", "intent": "bug_report", "urgency": "critical"},
                {"annotator": "A2", "intent": "bug_report", "urgency": "critical"},
                {"annotator": "A3", "intent": "bug_report", "urgency": "critical"},
            ]
        }

        has_conflict, reason = self.detector.detect_conflicts_in_sample(sample)
        self.assertFalse(has_conflict)
        self.assertIsNone(reason)

    def test_intent_conflict_detection(self):
        """Test detection of intent mismatches"""
        sample = {
            "id": "TEST-002",
            "text": "I want a refund but the app crashed during payment.",
            "annotations": [
                {"annotator": "A1", "intent": "billing_issue", "urgency": "high"},
                {"annotator": "A2", "intent": "bug_report", "urgency": "high"},
                {"annotator": "A3", "intent": "billing_issue", "urgency": "high"},
            ]
        }

        has_conflict, reason = self.detector.detect_conflicts_in_sample(sample)
        self.assertTrue(has_conflict)
        self.assertIn("Intent mismatch", reason)

    def test_urgency_conflict_detection(self):
        """Test detection of urgency level differences"""
        sample = {
            "id": "TEST-003",
            "text": "Payment processing issue.",
            "annotations": [
                {"annotator": "A1", "intent": "billing_issue", "urgency": "high"},
                {"annotator": "A2", "intent": "billing_issue", "urgency": "medium"},
                {"annotator": "A3", "intent": "billing_issue", "urgency": "high"},
            ]
        }

        has_conflict, reason = self.detector.detect_conflicts_in_sample(sample)
        self.assertTrue(has_conflict)
        self.assertIn("Urgency mismatch", reason)

    def test_both_intent_and_urgency_conflict(self):
        """Test detection when both intent and urgency conflict"""
        sample = {
            "id": "TEST-004",
            "text": "Complex issue with account and payment.",
            "annotations": [
                {"annotator": "A1", "intent": "billing_issue", "urgency": "high"},
                {"annotator": "A2", "intent": "account_issue", "urgency": "medium"},
                {"annotator": "A3", "intent": "billing_issue", "urgency": "critical"},
            ]
        }

        has_conflict, reason = self.detector.detect_conflicts_in_sample(sample)
        self.assertTrue(has_conflict)
        self.assertIn("Intent mismatch", reason)
        self.assertIn("Urgency mismatch", reason)


class TestConflictAnalysis(unittest.TestCase):
    """Test cases for conflict cause analysis"""

    def setUp(self):
        """Set up test fixtures"""
        self.detector = ConflictDetector()

    def test_ambiguous_text_analysis(self):
        """Test analysis of ambiguous text"""
        text = "Issue"
        annotations = [
            {"annotator": "A1", "intent": "bug_report", "urgency": "high"},
            {"annotator": "A2", "intent": "bug_report", "urgency": "high"},
        ]
        
        reason = self.detector.analyze_conflict_causes(text, annotations, "Conflict")
        self.assertIn("Ambiguous", reason)

    def test_multiple_issues_text_analysis(self):
        """Test analysis of text with multiple issues"""
        text = "Payment failed and app won't open."
        annotations = [
            {"annotator": "A1", "intent": "billing_issue", "urgency": "high"},
            {"annotator": "A2", "intent": "bug_report", "urgency": "critical"},
        ]
        
        reason = self.detector.analyze_conflict_causes(text, annotations, "Conflict")
        self.assertIn("multiple issues", reason)

    def test_technical_issue_analysis(self):
        """Test analysis of technical issues"""
        text = "App crashes during payment processing."
        annotations = [
            {"annotator": "A1", "intent": "bug_report", "urgency": "critical"},
            {"annotator": "A2", "intent": "billing_issue", "urgency": "high"},
        ]
        
        reason = self.detector.analyze_conflict_causes(text, annotations, "Conflict")
        self.assertTrue(len(reason) > 0)


class TestLabelSuggestion(unittest.TestCase):
    """Test cases for final label suggestion"""

    def setUp(self):
        """Set up test fixtures"""
        self.detector = ConflictDetector()

    def test_majority_voting_single_issue(self):
        """Test majority voting with clear consensus"""
        text = "App crashes on login."
        annotations = [
            {"annotator": "A1", "intent": "bug_report", "urgency": "critical"},
            {"annotator": "A2", "intent": "bug_report", "urgency": "critical"},
            {"annotator": "A3", "intent": "bug_report", "urgency": "critical"},
        ]
        
        suggestion = self.detector.suggest_final_label(text, annotations, False)
        
        self.assertEqual(suggestion["intent"], "bug_report")
        self.assertEqual(suggestion["urgency"], "critical")
        self.assertEqual(suggestion["confidence"], 1.0)

    def test_majority_voting_with_conflict(self):
        """Test majority voting when conflict exists"""
        text = "Payment failed but app also crashed."
        annotations = [
            {"annotator": "A1", "intent": "billing_issue", "urgency": "high"},
            {"annotator": "A2", "intent": "bug_report", "urgency": "critical"},
            {"annotator": "A3", "intent": "billing_issue", "urgency": "high"},
        ]
        
        suggestion = self.detector.suggest_final_label(text, annotations, True)
        
        # Majority is billing_issue (2/3)
        self.assertEqual(suggestion["intent"], "billing_issue")
        self.assertGreater(suggestion["confidence"], 0.5)
        self.assertIn("reasoning", suggestion)

    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        annotations = [
            {"annotator": "A1", "intent": "bug_report", "urgency": "high"},
            {"annotator": "A2", "intent": "bug_report", "urgency": "high"},
            {"annotator": "A3", "intent": "account_issue", "urgency": "high"},
        ]
        
        suggestion = self.detector.suggest_final_label("text", annotations, True)
        
        # Intent confidence: 2/3 = 0.67, Urgency confidence: 3/3 = 1.0
        # Overall: (0.67 + 1.0) / 2 = 0.83
        self.assertAlmostEqual(suggestion["confidence"], 0.83, places=1)


class TestDatasetProcessing(unittest.TestCase):
    """Test cases for full dataset processing"""

    def setUp(self):
        """Set up test fixtures"""
        self.detector = ConflictDetector()
        
        # Create a temporary test dataset
        self.test_data = [
            {
                "id": "TEST-001",
                "text": "App crashes.",
                "annotations": [
                    {"annotator": "A1", "intent": "bug_report", "urgency": "critical"},
                    {"annotator": "A2", "intent": "bug_report", "urgency": "critical"},
                    {"annotator": "A3", "intent": "bug_report", "urgency": "critical"},
                ]
            },
            {
                "id": "TEST-002",
                "text": "Payment failed and app won't open.",
                "annotations": [
                    {"annotator": "A1", "intent": "billing_issue", "urgency": "high"},
                    {"annotator": "A2", "intent": "bug_report", "urgency": "critical"},
                    {"annotator": "A3", "intent": "billing_issue", "urgency": "high"},
                ]
            },
            {
                "id": "TEST-003",
                "text": "Account locked.",
                "annotations": [
                    {"annotator": "A1", "intent": "account_issue", "urgency": "high"},
                    {"annotator": "A2", "intent": "account_issue", "urgency": "high"},
                    {"annotator": "A3", "intent": "account_issue", "urgency": "high"},
                ]
            },
        ]
        
        # Write to temporary file
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.jsonl', delete=False, encoding='utf-8'
        )
        for item in self.test_data:
            self.temp_file.write(json.dumps(item) + '\n')
        self.temp_file.close()

    def tearDown(self):
        """Clean up temporary files"""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_load_jsonl(self):
        """Test loading JSONL dataset"""
        self.detector.load_jsonl(self.temp_file.name)
        
        self.assertEqual(len(self.detector.samples), 3)
        self.assertEqual(self.detector.statistics["total_samples"], 3)

    def test_process_all_samples(self):
        """Test processing all samples"""
        self.detector.load_jsonl(self.temp_file.name)
        results = self.detector.process_all()
        
        self.assertEqual(len(results), 3)
        
        # Check first sample (no conflict)
        self.assertFalse(results[0].is_conflict)
        self.assertIsNone(results[0].conflict_reason)
        
        # Check second sample (has conflict)
        self.assertTrue(results[1].is_conflict)
        self.assertIsNotNone(results[1].conflict_reason)
        
        # Check third sample (no conflict)
        self.assertFalse(results[2].is_conflict)

    def test_statistics_calculation(self):
        """Test statistics calculation"""
        self.detector.load_jsonl(self.temp_file.name)
        self.detector.process_all()
        
        stats = self.detector.get_statistics()
        
        self.assertEqual(stats["total_samples"], 3)
        self.assertEqual(stats["conflict_samples"], 1)
        self.assertEqual(stats["unanimous_samples"], 2)
        self.assertAlmostEqual(stats["conflict_rate"], 0.33, places=1)

    def test_save_results(self):
        """Test saving results to file"""
        self.detector.load_jsonl(self.temp_file.name)
        self.detector.process_all()
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.jsonl', delete=False, encoding='utf-8'
        ) as f:
            output_file = f.name
        
        try:
            self.detector.save_results(output_file)
            
            # Verify output file
            with open(output_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            self.assertEqual(len(lines), 3)
            
            # Parse and verify first result
            result = json.loads(lines[0])
            self.assertEqual(result["id"], "TEST-001")
            self.assertFalse(result["is_conflict"])
            self.assertIn("suggested_label", result)
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_save_conflicts_only(self):
        """Test saving only conflicted samples"""
        self.detector.load_jsonl(self.temp_file.name)
        self.detector.process_all()
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.jsonl', delete=False, encoding='utf-8'
        ) as f:
            output_file = f.name
        
        try:
            self.detector.save_conflicts_only(output_file)
            
            # Verify output file contains only conflicts
            with open(output_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            self.assertEqual(len(lines), 1)  # Only TEST-002 has conflict
            
            result = json.loads(lines[0])
            self.assertTrue(result["is_conflict"])
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_generate_report(self):
        """Test report generation"""
        self.detector.load_jsonl(self.temp_file.name)
        self.detector.process_all()
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.md', delete=False, encoding='utf-8'
        ) as f:
            output_file = f.name
        
        try:
            self.detector.generate_report(output_file)
            
            # Verify report file exists and contains expected content
            with open(output_file, 'r', encoding='utf-8') as f:
                report = f.read()
            
            self.assertIn("Summary Statistics", report)
            self.assertIn("Conflicted Samples Details", report)
            self.assertIn("TEST-002", report)
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)


class TestEdgeCases(unittest.TestCase):
    """Test cases for edge cases and error handling"""

    def setUp(self):
        """Set up test fixtures"""
        self.detector = ConflictDetector()

    def test_single_annotator(self):
        """Test handling single annotator"""
        sample = {
            "id": "TEST-001",
            "text": "Single annotator.",
            "annotations": [
                {"annotator": "A1", "intent": "bug_report", "urgency": "high"},
            ]
        }
        
        has_conflict, _ = self.detector.detect_conflicts_in_sample(sample)
        self.assertFalse(has_conflict)

    def test_empty_annotations(self):
        """Test handling empty annotations"""
        sample = {
            "id": "TEST-001",
            "text": "No annotations.",
            "annotations": []
        }
        
        has_conflict, _ = self.detector.detect_conflicts_in_sample(sample)
        self.assertFalse(has_conflict)

    def test_missing_fields(self):
        """Test handling missing fields"""
        sample = {
            "id": "TEST-001",
            "text": "Missing fields.",
        }
        
        has_conflict, _ = self.detector.detect_conflicts_in_sample(sample)
        self.assertFalse(has_conflict)


if __name__ == "__main__":
    unittest.main()
