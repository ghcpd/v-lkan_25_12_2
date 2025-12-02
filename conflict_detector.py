"""
Multi-Annotator Dataset Conflict Detection and Resolution System

This module provides comprehensive conflict detection, analysis, and resolution
for multi-annotator datasets with support for multiple label dimensions.
"""

import json
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter
from dataclasses import dataclass, asdict
import re


@dataclass
class AnnotatorLabel:
    """Represents a single annotator's label"""
    annotator: str
    intent: str
    urgency: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format"""
        return {"annotator": self.annotator, "label": f"{self.intent}|{self.urgency}"}
    
    def get_composite_label(self) -> str:
        """Get combined label for comparison"""
        return f"{self.intent}|{self.urgency}"


@dataclass
class ConflictAnalysis:
    """Analysis result for a sample with potential conflicts"""
    id: str
    text: str
    labels: List[Dict[str, str]]
    is_conflict: bool
    conflict_reason: Optional[str]
    suggested_label: str
    conflict_details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON output"""
        result = {
            "id": self.id,
            "text": self.text,
            "labels": self.labels,
            "is_conflict": self.is_conflict,
            "conflict_reason": self.conflict_reason,
            "suggested_label": self.suggested_label
        }
        if self.conflict_details:
            result["conflict_details"] = self.conflict_details
        return result


class ConflictDetector:
    """Main class for detecting and analyzing annotation conflicts"""
    
    def __init__(self, detailed_analysis: bool = True):
        """
        Initialize the conflict detector
        
        Args:
            detailed_analysis: Whether to include detailed conflict analysis
        """
        self.detailed_analysis = detailed_analysis
        
        # Define ambiguous keywords that might cause disagreement
        self.ambiguous_keywords = {
            "network error": ["billing_issue", "bug_report"],
            "payment failed": ["billing_issue", "bug_report"],
            "app crashed": ["bug_report", "billing_issue"],
            "app shows error": ["bug_report", "account_issue"],
            "subscription": ["subscription_issue", "billing_issue"],
            "cancel": ["subscription_issue", "account_issue"],
            "locked": ["account_issue", "bug_report"],
        }
        
        # Mixed sentiment indicators
        self.mixed_indicators = [
            ("but", "contrasting elements"),
            ("and", "multiple aspects"),
            ("however", "contrasting elements"),
            ("while", "simultaneous issues"),
        ]
    
    def extract_labels(self, annotations: List[Dict[str, str]]) -> List[AnnotatorLabel]:
        """
        Extract annotator labels from annotations
        
        Args:
            annotations: List of annotation dictionaries
            
        Returns:
            List of AnnotatorLabel objects
        """
        labels = []
        for ann in annotations:
            labels.append(AnnotatorLabel(
                annotator=ann["annotator"],
                intent=ann["intent"],
                urgency=ann["urgency"]
            ))
        return labels
    
    def detect_conflict(self, labels: List[AnnotatorLabel]) -> Tuple[bool, Dict[str, Any]]:
        """
        Detect if there's a conflict among annotators
        
        Args:
            labels: List of AnnotatorLabel objects
            
        Returns:
            Tuple of (is_conflict, conflict_details)
        """
        # Check for intent conflicts
        intents = [label.intent for label in labels]
        intent_counts = Counter(intents)
        has_intent_conflict = len(intent_counts) > 1
        
        # Check for urgency conflicts
        urgencies = [label.urgency for label in labels]
        urgency_counts = Counter(urgencies)
        has_urgency_conflict = len(urgency_counts) > 1
        
        # Overall conflict exists if either dimension has disagreement
        is_conflict = has_intent_conflict or has_urgency_conflict
        
        conflict_details = {
            "intent_distribution": dict(intent_counts),
            "urgency_distribution": dict(urgency_counts),
            "has_intent_conflict": has_intent_conflict,
            "has_urgency_conflict": has_urgency_conflict,
            "total_annotators": len(labels),
            "unique_labels": len(set(label.get_composite_label() for label in labels))
        }
        
        return is_conflict, conflict_details
    
    def analyze_conflict_cause(self, text: str, labels: List[AnnotatorLabel], 
                               conflict_details: Dict[str, Any]) -> str:
        """
        Analyze and explain the cause of disagreement
        
        Args:
            text: The text being annotated
            labels: List of annotator labels
            conflict_details: Details about the conflict
            
        Returns:
            Explanation of the conflict cause
        """
        reasons = []
        text_lower = text.lower()
        
        # Check for ambiguous keywords
        ambiguous_found = []
        for keyword, possible_intents in self.ambiguous_keywords.items():
            if keyword in text_lower:
                intents_in_labels = [label.intent for label in labels]
                if any(intent in intents_in_labels for intent in possible_intents):
                    ambiguous_found.append(keyword)
        
        if ambiguous_found:
            reasons.append(
                f"Ambiguous text: Contains terms like '{', '.join(ambiguous_found)}' "
                f"which can be interpreted as multiple intent types"
            )
        
        # Check for mixed sentiment/multiple aspects
        mixed_found = []
        for indicator, description in self.mixed_indicators:
            if indicator in text_lower:
                mixed_found.append((indicator, description))
        
        if mixed_found:
            indicators = [f"'{ind}' ({desc})" for ind, desc in mixed_found]
            reasons.append(
                f"Mixed aspects: Text contains {', '.join(indicators)}, "
                f"indicating multiple simultaneous issues"
            )
        
        # Check for urgency ambiguity
        if conflict_details["has_urgency_conflict"] and not conflict_details["has_intent_conflict"]:
            urgency_dist = conflict_details["urgency_distribution"]
            reasons.append(
                f"Urgency assessment varies: Annotators disagreed on severity "
                f"(distribution: {urgency_dist}), suggesting subjective urgency interpretation"
            )
        
        # Check for intent disagreement with specific patterns
        if conflict_details["has_intent_conflict"]:
            intent_dist = conflict_details["intent_distribution"]
            intents_str = ", ".join([f"{k}({v})" for k, v in intent_dist.items()])
            
            # Identify if it's a technical vs. business issue
            technical_intents = {"bug_report", "account_issue"}
            business_intents = {"billing_issue", "subscription_issue"}
            
            label_intents = set(label.intent for label in labels)
            has_technical = bool(label_intents & technical_intents)
            has_business = bool(label_intents & business_intents)
            
            if has_technical and has_business:
                reasons.append(
                    f"Intent classification ambiguity: Mixed technical and business aspects "
                    f"(distribution: {intents_str}), requiring clearer annotation guidelines "
                    f"on prioritizing primary vs. secondary issues"
                )
            else:
                reasons.append(
                    f"Intent disagreement: Annotators categorized differently "
                    f"(distribution: {intents_str}), suggesting need for clearer "
                    f"intent definition guidelines"
                )
        
        # Check for short/vague text
        if len(text.split()) < 8:
            reasons.append(
                f"Brief text ({len(text.split())} words): Limited context may lead to "
                f"varying interpretations of user intent and urgency"
            )
        
        # Default reason if no specific cause found
        if not reasons:
            reasons.append(
                "Subjective interpretation: Annotators applied different judgment criteria "
                "without clear textual ambiguity, indicating possible need for "
                "standardized annotation guidelines"
            )
        
        return " | ".join(reasons)
    
    def suggest_resolution(self, labels: List[AnnotatorLabel], text: str,
                          conflict_details: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Suggest a final resolved label with reasoning
        
        Args:
            labels: List of annotator labels
            text: The text being annotated
            conflict_details: Details about the conflict
            
        Returns:
            Tuple of (suggested_label, reasoning_details)
        """
        # Get majority votes for each dimension
        intents = [label.intent for label in labels]
        urgencies = [label.urgency for label in labels]
        
        intent_counts = Counter(intents)
        urgency_counts = Counter(urgencies)
        
        majority_intent = intent_counts.most_common(1)[0][0]
        majority_urgency = urgency_counts.most_common(1)[0][0]
        
        # Calculate confidence
        intent_confidence = intent_counts[majority_intent] / len(labels)
        urgency_confidence = urgency_counts[majority_urgency] / len(labels)
        
        # Build reasoning
        reasoning = {
            "majority_intent": majority_intent,
            "intent_votes": dict(intent_counts),
            "intent_confidence": round(intent_confidence, 2),
            "majority_urgency": majority_urgency,
            "urgency_votes": dict(urgency_counts),
            "urgency_confidence": round(urgency_confidence, 2),
            "resolution_strategy": "majority_vote_with_contextual_analysis"
        }
        
        # Apply contextual analysis for tie-breaking or low confidence
        if intent_confidence < 1.0:
            # Analyze text for context clues
            text_lower = text.lower()
            
            # Priority rules based on keywords
            if any(word in text_lower for word in ["crash", "error", "blank", "won't open", "failed to"]):
                if "bug_report" in intent_counts:
                    reasoning["contextual_adjustment"] = "Technical failure keywords suggest bug_report"
                    if intent_confidence < 0.6:
                        majority_intent = "bug_report"
            
            elif any(word in text_lower for word in ["refund", "payment", "charged", "billing"]):
                if "billing_issue" in intent_counts:
                    reasoning["contextual_adjustment"] = "Payment-related keywords suggest billing_issue"
                    if intent_confidence < 0.6:
                        majority_intent = "billing_issue"
            
            elif any(word in text_lower for word in ["subscription", "renew", "activate"]):
                if "subscription_issue" in intent_counts:
                    reasoning["contextual_adjustment"] = "Subscription keywords suggest subscription_issue"
                    if intent_confidence < 0.6:
                        majority_intent = "subscription_issue"
        
        # Adjust urgency based on critical keywords
        if urgency_confidence < 1.0:
            text_lower = text.lower()
            if any(word in text_lower for word in ["critical", "urgent", "immediately", "asap"]):
                if urgency_confidence < 0.6:
                    majority_urgency = "high"
                    reasoning["urgency_adjustment"] = "Critical keywords suggest high urgency"
            elif "crash" in text_lower and "payment" in text_lower:
                majority_urgency = "critical"
                reasoning["urgency_adjustment"] = "Payment system crash suggests critical urgency"
        
        suggested_label = f"{majority_intent}|{majority_urgency}"
        
        reasoning["explanation"] = self._build_resolution_explanation(
            majority_intent, majority_urgency, intent_confidence, urgency_confidence, reasoning
        )
        
        return suggested_label, reasoning
    
    def _build_resolution_explanation(self, intent: str, urgency: str,
                                     intent_conf: float, urgency_conf: float,
                                     reasoning: Dict[str, Any]) -> str:
        """Build human-readable explanation for resolution"""
        parts = []
        
        # Intent explanation
        if intent_conf == 1.0:
            parts.append(f"Intent '{intent}' has unanimous agreement")
        else:
            parts.append(
                f"Intent '{intent}' selected by majority "
                f"({intent_conf:.0%} confidence, votes: {reasoning['intent_votes']})"
            )
        
        # Urgency explanation
        if urgency_conf == 1.0:
            parts.append(f"urgency '{urgency}' has unanimous agreement")
        else:
            parts.append(
                f"urgency '{urgency}' selected by majority "
                f"({urgency_conf:.0%} confidence, votes: {reasoning['urgency_votes']})"
            )
        
        # Add contextual adjustments
        if "contextual_adjustment" in reasoning:
            parts.append(f"Contextual analysis: {reasoning['contextual_adjustment']}")
        if "urgency_adjustment" in reasoning:
            parts.append(f"Urgency analysis: {reasoning['urgency_adjustment']}")
        
        return ". ".join(parts) + "."
    
    def analyze_sample(self, sample: Dict[str, Any]) -> ConflictAnalysis:
        """
        Analyze a single sample for conflicts
        
        Args:
            sample: Dictionary containing id, text, and annotations
            
        Returns:
            ConflictAnalysis object with complete analysis
        """
        sample_id = sample["id"]
        text = sample["text"]
        annotations = sample["annotations"]
        
        # Extract labels
        labels = self.extract_labels(annotations)
        
        # Detect conflicts
        is_conflict, conflict_details = self.detect_conflict(labels)
        
        # Format labels for output
        formatted_labels = [label.to_dict() for label in labels]
        
        # Analyze conflict cause if conflict exists
        if is_conflict:
            conflict_reason = self.analyze_conflict_cause(text, labels, conflict_details)
        else:
            conflict_reason = None
        
        # Suggest resolution
        suggested_label, resolution_reasoning = self.suggest_resolution(
            labels, text, conflict_details
        )
        
        # Build conflict analysis
        analysis = ConflictAnalysis(
            id=sample_id,
            text=text,
            labels=formatted_labels,
            is_conflict=is_conflict,
            conflict_reason=conflict_reason,
            suggested_label=suggested_label,
            conflict_details={
                **conflict_details,
                "resolution_reasoning": resolution_reasoning
            } if self.detailed_analysis else None
        )
        
        return analysis
    
    def process_dataset(self, input_path: str, output_path: str, 
                       conflicts_only: bool = False) -> Dict[str, Any]:
        """
        Process entire dataset and save results
        
        Args:
            input_path: Path to input JSONL file
            output_path: Path to output JSONL file
            conflicts_only: If True, only output samples with conflicts
            
        Returns:
            Summary statistics
        """
        results = []
        stats = {
            "total_samples": 0,
            "conflict_samples": 0,
            "no_conflict_samples": 0,
            "intent_conflicts": 0,
            "urgency_conflicts": 0,
            "both_conflicts": 0
        }
        
        # Process each sample
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                sample = json.loads(line.strip())
                analysis = self.analyze_sample(sample)
                
                stats["total_samples"] += 1
                
                if analysis.is_conflict:
                    stats["conflict_samples"] += 1
                    
                    if analysis.conflict_details:
                        if analysis.conflict_details["has_intent_conflict"]:
                            stats["intent_conflicts"] += 1
                        if analysis.conflict_details["has_urgency_conflict"]:
                            stats["urgency_conflicts"] += 1
                        if (analysis.conflict_details["has_intent_conflict"] and 
                            analysis.conflict_details["has_urgency_conflict"]):
                            stats["both_conflicts"] += 1
                else:
                    stats["no_conflict_samples"] += 1
                
                # Add to results based on filter
                if not conflicts_only or analysis.is_conflict:
                    results.append(analysis)
        
        # Write results
        with open(output_path, 'w', encoding='utf-8') as f:
            for analysis in results:
                f.write(json.dumps(analysis.to_dict(), ensure_ascii=False) + '\n')
        
        stats["output_samples"] = len(results)
        
        return stats


def load_dataset(file_path: str) -> List[Dict[str, Any]]:
    """Load dataset from JSONL file"""
    samples = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            samples.append(json.loads(line.strip()))
    return samples


def save_dataset(samples: List[Dict[str, Any]], file_path: str) -> None:
    """Save dataset to JSONL file"""
    with open(file_path, 'w', encoding='utf-8') as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
