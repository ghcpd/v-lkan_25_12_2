"""
Multi-Annotator Dataset Conflict Detection and Resolution System

This module provides tools to:
1. Detect conflicts among annotators
2. Analyze causes of disagreement
3. Suggest final resolved labels based on reasoning
"""

import json
from typing import Dict, List, Any, Tuple
from collections import Counter
from dataclasses import dataclass, asdict


@dataclass
class AnnotationLabel:
    """Represents a label assigned by an annotator"""
    annotator: str
    intent: str
    urgency: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass
class ConflictAnalysis:
    """Represents the analysis of a single sample"""
    id: str
    text: str
    labels: List[Dict[str, str]]
    is_conflict: bool
    conflict_reason: str = None
    suggested_label: Dict[str, str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "text": self.text,
            "labels": self.labels,
            "is_conflict": self.is_conflict,
            "conflict_reason": self.conflict_reason,
            "suggested_label": self.suggested_label,
        }
        return result


class ConflictDetector:
    """Main class for detecting and analyzing annotation conflicts"""

    def __init__(self):
        """Initialize the conflict detector"""
        self.samples = []
        self.conflicts = []
        self.statistics = {
            "total_samples": 0,
            "conflict_samples": 0,
            "unanimous_samples": 0,
            "partial_conflicts": 0,
        }

    def load_jsonl(self, file_path: str) -> None:
        """Load JSONL dataset"""
        self.samples = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    self.samples.append(json.loads(line))
        self.statistics["total_samples"] = len(self.samples)

    def detect_conflicts_in_sample(self, sample: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Detect if a sample has conflicts among annotators

        Returns:
            Tuple of (has_conflict, conflict_reason)
        """
        annotations = sample.get("annotations", [])
        if len(annotations) < 2:
            return False, None

        # Extract intent and urgency for each annotator
        intents = [ann.get("intent") for ann in annotations]
        urgencies = [ann.get("urgency") for ann in annotations]

        # Check for conflicts
        intent_unique = len(set(intents))
        urgency_unique = len(set(urgencies))
        total_annotators = len(annotations)

        has_conflict = intent_unique > 1 or urgency_unique > 1

        if has_conflict:
            reasons = []
            if intent_unique > 1:
                reasons.append(f"Intent mismatch: {intents}")
            if urgency_unique > 1:
                reasons.append(f"Urgency mismatch: {urgencies}")
            conflict_reason = "; ".join(reasons)
        else:
            conflict_reason = None

        return has_conflict, conflict_reason

    def analyze_conflict_causes(
        self, text: str, annotations: List[Dict[str, Any]], conflict_reason: str
    ) -> str:
        """
        Analyze possible causes of conflict

        Considers:
        - Text ambiguity (multiple topics, mixed sentiment)
        - Complexity (multiple issues mentioned)
        - Guideline clarity
        """
        causes = []

        # Analyze text characteristics
        if len(text) < 50:
            causes.append("Ambiguous or vague text description")
        
        if "and" in text.lower() or "but" in text.lower():
            causes.append("Text contains multiple issues or mixed sentiment")

        # Check for inconsistent annotation guidelines application
        intents = [ann.get("intent") for ann in annotations]
        urgencies = [ann.get("urgency") for ann in annotations]

        if len(set(intents)) > 1:
            intent_counter = Counter(intents)
            most_common_intent = intent_counter.most_common(1)[0][0]
            minority_intents = [
                intent for intent, count in intent_counter.items() 
                if intent != most_common_intent
            ]
            if minority_intents:
                causes.append(
                    f"Inconsistent intent classification: most annotators chose '{most_common_intent}' "
                    f"but some chose {minority_intents}"
                )

        if len(set(urgencies)) > 1:
            urgency_counter = Counter(urgencies)
            most_common_urgency = urgency_counter.most_common(1)[0][0]
            minority_urgencies = [
                urg for urg, count in urgency_counter.items() 
                if urg != most_common_urgency
            ]
            if minority_urgencies:
                causes.append(
                    f"Different urgency assessment: most consider it '{most_common_urgency}' "
                    f"but some consider {minority_urgencies}"
                )

        # Specific patterns
        if "error" in text.lower() or "crash" in text.lower():
            causes.append(
                "Technical issues can be classified as either 'bug_report' or related "
                "issue (billing/account) depending on interpretation"
            )

        if "payment" in text.lower() or "refund" in text.lower():
            causes.append(
                "Billing-related issues may overlap with system errors, "
                "causing different categorizations"
            )

        return " | ".join(causes) if causes else "Unable to determine specific cause"

    def suggest_final_label(
        self,
        text: str,
        annotations: List[Dict[str, Any]],
        has_conflict: bool
    ) -> Dict[str, Any]:
        """
        Suggest a final resolved label based on majority voting
        with confidence reasoning
        """
        if not annotations:
            return None

        intents = [ann.get("intent") for ann in annotations]
        urgencies = [ann.get("urgency") for ann in annotations]

        # Majority voting
        intent_counter = Counter(intents)
        urgency_counter = Counter(urgencies)

        majority_intent, intent_count = intent_counter.most_common(1)[0]
        majority_urgency, urgency_count = urgency_counter.most_common(1)[0]

        intent_confidence = intent_count / len(annotations)
        urgency_confidence = urgency_count / len(annotations)
        overall_confidence = (intent_confidence + urgency_confidence) / 2

        # Build reasoning
        reasoning_parts = []

        if has_conflict:
            reasoning_parts.append(
                f"Despite conflicts, '{majority_intent}' is chosen by {intent_count}/{len(annotations)} "
                f"annotators ({intent_confidence*100:.0f}% confidence)."
            )
            reasoning_parts.append(
                f"Urgency level '{majority_urgency}' agreed upon by {urgency_count}/{len(annotations)} "
                f"annotators ({urgency_confidence*100:.0f}% confidence)."
            )
        else:
            reasoning_parts.append("All annotators agreed on the labels.")

        # Add context-based reasoning
        if "error" in text.lower() or "crash" in text.lower():
            if majority_intent == "bug_report":
                reasoning_parts.append(
                    "Text clearly indicates a technical issue, supporting 'bug_report' classification."
                )

        if majority_urgency == "critical":
            reasoning_parts.append(
                "Multiple critical indicators (crash, unable to access, service down) justify 'critical' urgency."
            )

        reasoning = " ".join(reasoning_parts)

        return {
            "intent": majority_intent,
            "urgency": majority_urgency,
            "confidence": round(overall_confidence, 2),
            "reasoning": reasoning
        }

    def process_sample(self, sample: Dict[str, Any]) -> ConflictAnalysis:
        """Process a single sample and return analysis"""
        sample_id = sample.get("id")
        text = sample.get("text")
        annotations = sample.get("annotations", [])

        # Convert annotations to label format
        labels = [
            {
                "annotator": ann.get("annotator"),
                "intent": ann.get("intent"),
                "urgency": ann.get("urgency")
            }
            for ann in annotations
        ]

        # Detect conflicts
        has_conflict, conflict_reason = self.detect_conflicts_in_sample(sample)

        # Analyze causes if conflict exists
        if has_conflict:
            detailed_reason = self.analyze_conflict_causes(
                text, annotations, conflict_reason
            )
        else:
            detailed_reason = None

        # Suggest final label
        suggested_label = self.suggest_final_label(text, annotations, has_conflict)

        return ConflictAnalysis(
            id=sample_id,
            text=text,
            labels=labels,
            is_conflict=has_conflict,
            conflict_reason=detailed_reason,
            suggested_label=suggested_label
        )

    def process_all(self) -> List[ConflictAnalysis]:
        """Process all samples and return analyses"""
        self.conflicts = []
        for sample in self.samples:
            analysis = self.process_sample(sample)
            self.conflicts.append(analysis)

            # Update statistics
            if analysis.is_conflict:
                self.statistics["conflict_samples"] += 1
            else:
                self.statistics["unanimous_samples"] += 1

        return self.conflicts

    def save_results(self, output_file: str) -> None:
        """Save conflict analysis results to JSONL"""
        with open(output_file, 'w', encoding='utf-8') as f:
            for conflict in self.conflicts:
                f.write(json.dumps(conflict.to_dict()) + '\n')

    def save_conflicts_only(self, output_file: str) -> None:
        """Save only conflicted samples to JSONL"""
        with open(output_file, 'w', encoding='utf-8') as f:
            for conflict in self.conflicts:
                if conflict.is_conflict:
                    f.write(json.dumps(conflict.to_dict()) + '\n')

    def get_statistics(self) -> Dict[str, Any]:
        """Get summary statistics"""
        if self.statistics["total_samples"] == 0:
            return self.statistics

        stats = {
            "total_samples": self.statistics["total_samples"],
            "conflict_samples": self.statistics["conflict_samples"],
            "unanimous_samples": self.statistics["unanimous_samples"],
            "conflict_rate": round(
                self.statistics["conflict_samples"] / self.statistics["total_samples"], 2
            ),
        }
        return stats

    def generate_report(self, output_file: str) -> None:
        """Generate a detailed markdown report"""
        stats = self.get_statistics()
        conflict_samples = [c for c in self.conflicts if c.is_conflict]

        report = f"""# Annotation Conflict Detection Report

## Summary Statistics
- **Total Samples**: {stats['total_samples']}
- **Conflicted Samples**: {stats['conflict_samples']}
- **Unanimous Samples**: {stats['unanimous_samples']}
- **Conflict Rate**: {stats['conflict_rate']*100:.1f}%

## Conflicted Samples Details

"""

        for conflict in conflict_samples[:20]:  # Show first 20 conflicts
            report += f"""### Sample ID: {conflict.id}
**Text**: {conflict.text}

**Annotations**:
"""
            for label in conflict.labels:
                report += f"- {label['annotator']}: intent={label['intent']}, urgency={label['urgency']}\n"

            report += f"""
**Conflict Reason**: {conflict.conflict_reason}

**Suggested Resolution**: 
- Intent: {conflict.suggested_label['intent']}
- Urgency: {conflict.suggested_label['urgency']}
- Confidence: {conflict.suggested_label['confidence']}
- Reasoning: {conflict.suggested_label['reasoning']}

---

"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)


if __name__ == "__main__":
    detector = ConflictDetector()
    detector.load_jsonl("tickets_label.jsonl")
    detector.process_all()
    detector.save_results("conflict_analysis_results.jsonl")
    detector.save_conflicts_only("conflicts_only.jsonl")
    detector.generate_report("conflict_report.md")
    print(json.dumps(detector.get_statistics(), indent=2))
