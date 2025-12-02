"""
Configuration settings for the conflict detection system
"""

import os
from typing import Dict, Any


class Config:
    """Configuration class for the conflict detection system"""
    
    # File paths
    DEFAULT_INPUT_FILE = "tickets_label.jsonl"
    DEFAULT_OUTPUT_FILE = "conflict_analysis_results.jsonl"
    DEFAULT_CONFLICTS_ONLY_FILE = "conflicts_only.jsonl"
    DEFAULT_REPORT_FILE = "conflict_analysis_report.md"
    
    # Analysis settings
    DETAILED_ANALYSIS = True
    INCLUDE_CONFLICT_DETAILS = True
    
    # Output settings
    OUTPUT_ENCODING = "utf-8"
    PRETTY_PRINT_JSON = False
    
    # Report settings
    GENERATE_MARKDOWN_REPORT = True
    INCLUDE_EXAMPLES = True
    MAX_EXAMPLES_PER_CATEGORY = 5
    
    # Logging settings
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """Create config from dictionary"""
        config = cls()
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }


# Conflict reason categories for reporting
CONFLICT_CATEGORIES = {
    "ambiguous_text": "Ambiguous Text",
    "mixed_aspects": "Mixed Aspects/Multiple Issues",
    "urgency_disagreement": "Urgency Assessment Variance",
    "intent_disagreement": "Intent Classification Ambiguity",
    "brief_text": "Limited Context",
    "subjective": "Subjective Interpretation"
}

# Label mappings
INTENT_LABELS = {
    "billing_issue": "Billing Issue",
    "bug_report": "Bug Report",
    "account_issue": "Account Issue",
    "subscription_issue": "Subscription Issue",
    "general_inquiry": "General Inquiry"
}

URGENCY_LABELS = {
    "low": "Low",
    "medium": "Medium",
    "high": "High",
    "critical": "Critical"
}
