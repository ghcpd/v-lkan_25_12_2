"""
Utility functions for the conflict detection system
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import os


def format_timestamp() -> str:
    """Get formatted timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate_percentage(numerator: int, denominator: int) -> float:
    """Calculate percentage safely"""
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def extract_conflict_type(conflict_reason: Optional[str]) -> str:
    """Extract primary conflict type from reason"""
    if not conflict_reason:
        return "no_conflict"
    
    reason_lower = conflict_reason.lower()
    
    if "ambiguous text" in reason_lower:
        return "ambiguous_text"
    elif "mixed aspects" in reason_lower:
        return "mixed_aspects"
    elif "urgency assessment" in reason_lower:
        return "urgency_disagreement"
    elif "intent" in reason_lower and "disagreement" in reason_lower:
        return "intent_disagreement"
    elif "brief text" in reason_lower:
        return "brief_text"
    else:
        return "subjective"


def generate_statistics_summary(stats: Dict[str, Any]) -> str:
    """Generate formatted statistics summary"""
    lines = [
        "=" * 60,
        "CONFLICT DETECTION STATISTICS",
        "=" * 60,
        f"Total Samples Processed: {stats['total_samples']}",
        f"Samples with Conflicts: {stats['conflict_samples']} "
        f"({calculate_percentage(stats['conflict_samples'], stats['total_samples'])}%)",
        f"Samples without Conflicts: {stats['no_conflict_samples']} "
        f"({calculate_percentage(stats['no_conflict_samples'], stats['total_samples'])}%)",
        "",
        "Conflict Breakdown:",
        f"  - Intent conflicts only: {stats['intent_conflicts'] - stats.get('both_conflicts', 0)}",
        f"  - Urgency conflicts only: {stats['urgency_conflicts'] - stats.get('both_conflicts', 0)}",
        f"  - Both intent and urgency conflicts: {stats.get('both_conflicts', 0)}",
        "",
        f"Output Samples: {stats['output_samples']}",
        "=" * 60
    ]
    return "\n".join(lines)


def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """Load data from JSONL file"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def save_jsonl(data: List[Dict[str, Any]], file_path: str) -> None:
    """Save data to JSONL file"""
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


def ensure_directory(file_path: str) -> None:
    """Ensure directory exists for file path"""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


class ReportGenerator:
    """Generate detailed markdown reports for conflict analysis"""
    
    def __init__(self, results: List[Dict[str, Any]], stats: Dict[str, Any]):
        self.results = results
        self.stats = stats
        self.conflicts = [r for r in results if r.get("is_conflict", False)]
        self.no_conflicts = [r for r in results if not r.get("is_conflict", False)]
    
    def generate(self, output_path: str, include_examples: bool = True, 
                 max_examples: int = 5) -> None:
        """Generate complete markdown report"""
        sections = [
            self._generate_header(),
            self._generate_overview(),
            self._generate_statistics(),
            self._generate_conflict_analysis(),
        ]
        
        if include_examples:
            sections.append(self._generate_examples(max_examples))
        
        sections.extend([
            self._generate_recommendations(),
            self._generate_footer()
        ])
        
        report = "\n\n".join(sections)
        
        ensure_directory(output_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
    
    def _generate_header(self) -> str:
        """Generate report header"""
        return f"""# Multi-Annotator Conflict Detection Report

**Generated:** {format_timestamp()}

---"""
    
    def _generate_overview(self) -> str:
        """Generate overview section"""
        total = self.stats['total_samples']
        conflicts = self.stats['conflict_samples']
        conflict_rate = calculate_percentage(conflicts, total)
        
        return f"""## Executive Summary

This report presents a comprehensive analysis of annotator agreement and conflicts 
in the multi-annotator dataset.

### Key Findings

- **Total Samples:** {total}
- **Conflict Rate:** {conflict_rate}% ({conflicts} samples)
- **Agreement Rate:** {100 - conflict_rate}% ({self.stats['no_conflict_samples']} samples)
- **Primary Conflict Type:** {'Intent Classification' if self.stats['intent_conflicts'] > self.stats['urgency_conflicts'] else 'Urgency Assessment'}"""
    
    def _generate_statistics(self) -> str:
        """Generate statistics section"""
        intent_only = self.stats['intent_conflicts'] - self.stats.get('both_conflicts', 0)
        urgency_only = self.stats['urgency_conflicts'] - self.stats.get('both_conflicts', 0)
        both = self.stats.get('both_conflicts', 0)
        
        return f"""## Detailed Statistics

### Conflict Distribution

| Conflict Type | Count | Percentage |
|--------------|-------|------------|
| Intent Only | {intent_only} | {calculate_percentage(intent_only, self.stats['conflict_samples'])}% |
| Urgency Only | {urgency_only} | {calculate_percentage(urgency_only, self.stats['conflict_samples'])}% |
| Both Intent & Urgency | {both} | {calculate_percentage(both, self.stats['conflict_samples'])}% |
| **Total Conflicts** | **{self.stats['conflict_samples']}** | **100%** |"""
    
    def _generate_conflict_analysis(self) -> str:
        """Generate conflict cause analysis"""
        # Categorize conflicts by reason
        categories = {}
        for result in self.conflicts:
            reason_type = extract_conflict_type(result.get('conflict_reason'))
            categories[reason_type] = categories.get(reason_type, 0) + 1
        
        total_conflicts = self.stats['conflict_samples']
        
        table_rows = []
        for reason_type, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            pct = calculate_percentage(count, total_conflicts)
            table_rows.append(f"| {reason_type.replace('_', ' ').title()} | {count} | {pct}% |")
        
        return f"""## Conflict Cause Analysis

### Root Causes of Disagreement

| Cause Category | Count | Percentage |
|---------------|-------|------------|
{chr(10).join(table_rows)}"""
    
    def _generate_examples(self, max_examples: int) -> str:
        """Generate example cases"""
        sections = ["## Example Cases", "### Conflict Examples"]
        
        # Show diverse conflict examples
        shown = 0
        for result in self.conflicts[:max_examples]:
            sections.append(f"""
#### Example {shown + 1}: {result['id']}

**Text:** {result['text']}

**Annotator Labels:**
{self._format_labels(result['labels'])}

**Conflict Reason:** {result.get('conflict_reason', 'N/A')}

**Suggested Resolution:** `{result['suggested_label']}`
""")
            shown += 1
            if shown >= max_examples:
                break
        
        # Show agreement examples
        if self.no_conflicts:
            sections.append("### Agreement Examples (No Conflicts)")
            shown = 0
            for result in self.no_conflicts[:min(3, max_examples)]:
                sections.append(f"""
#### Example {shown + 1}: {result['id']}

**Text:** {result['text']}

**Unanimous Label:** `{result['suggested_label']}`
""")
                shown += 1
        
        return "\n".join(sections)
    
    def _format_labels(self, labels: List[Dict[str, str]]) -> str:
        """Format annotator labels for display"""
        lines = []
        for label in labels:
            lines.append(f"- {label['annotator']}: `{label['label']}`")
        return "\n".join(lines)
    
    def _generate_recommendations(self) -> str:
        """Generate recommendations"""
        conflict_rate = calculate_percentage(
            self.stats['conflict_samples'], 
            self.stats['total_samples']
        )
        
        recommendations = []
        
        if conflict_rate > 30:
            recommendations.append(
                "- **High conflict rate detected (>30%).** Review and clarify annotation guidelines, "
                "especially for intent classification and urgency assessment criteria."
            )
        
        if self.stats['intent_conflicts'] > self.stats['urgency_conflicts']:
            recommendations.append(
                "- **Intent classification is the primary source of disagreement.** "
                "Provide clearer definitions and examples for each intent category, "
                "particularly for cases involving multiple simultaneous issues."
            )
        else:
            recommendations.append(
                "- **Urgency assessment shows significant variance.** "
                "Establish objective criteria for urgency levels (e.g., impact severity, "
                "time sensitivity) to reduce subjective interpretation."
            )
        
        # Analyze conflict patterns
        ambiguous_count = sum(1 for r in self.conflicts 
                             if 'ambiguous' in r.get('conflict_reason', '').lower())
        if ambiguous_count > len(self.conflicts) * 0.3:
            recommendations.append(
                f"- **{ambiguous_count} conflicts involve ambiguous text.** "
                "Develop decision trees or rules for handling texts with multiple interpretations."
            )
        
        recommendations.append(
            "- **Implement regular calibration sessions** where annotators discuss "
            "disagreement cases to align understanding and interpretation."
        )
        
        recommendations.append(
            "- **Consider adjudication workflow** for high-conflict samples to establish "
            "ground truth through expert review or consensus discussion."
        )
        
        return f"""## Recommendations

### Improving Annotation Quality

{chr(10).join(recommendations)}

### Next Steps

1. Review conflict examples to identify common patterns
2. Update annotation guidelines based on identified ambiguities
3. Conduct annotator training on updated guidelines
4. Re-annotate high-conflict samples after guideline improvements
5. Monitor conflict rate trends over time"""
    
    def _generate_footer(self) -> str:
        """Generate report footer"""
        return f"""---

## Methodology

This analysis uses automated conflict detection with the following approach:

1. **Conflict Detection:** Identify samples where annotators assigned different labels
2. **Cause Analysis:** Analyze text characteristics and label patterns to determine disagreement causes
3. **Resolution Suggestion:** Provide recommended labels based on majority vote with contextual analysis
4. **Quality Metrics:** Calculate agreement rates and conflict distributions

**Report Generated by:** Multi-Annotator Conflict Detection System  
**Timestamp:** {format_timestamp()}"""


def validate_dataset_format(data: List[Dict[str, Any]]) -> tuple[bool, str]:
    """Validate dataset format"""
    required_fields = {'id', 'text', 'annotations'}
    
    for i, sample in enumerate(data):
        # Check required fields
        if not all(field in sample for field in required_fields):
            return False, f"Sample {i} missing required fields"
        
        # Check annotations format
        if not isinstance(sample['annotations'], list):
            return False, f"Sample {i} annotations must be a list"
        
        if len(sample['annotations']) == 0:
            return False, f"Sample {i} has no annotations"
        
        # Check annotation structure
        for j, ann in enumerate(sample['annotations']):
            if not all(key in ann for key in ['annotator', 'intent', 'urgency']):
                return False, f"Sample {i}, annotation {j} missing required fields"
    
    return True, "Dataset format is valid"
