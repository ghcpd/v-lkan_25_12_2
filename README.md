# Multi-Annotator Dataset Conflict Detection and Resolution System

A comprehensive system for detecting, analyzing, and resolving annotation conflicts in multi-annotator datasets. This tool helps identify disagreements among annotators, analyze the root causes, and suggest reliable final labels based on intelligent reasoning.

## 🎯 Features

- **Conflict Detection**: Automatically identifies samples where annotators disagree on labels
- **Multi-Dimensional Analysis**: Detects conflicts across multiple label dimensions (intent, urgency, etc.)
- **Root Cause Analysis**: Explains why annotators disagreed with detailed reasoning
- **Intelligent Resolution**: Suggests final labels using majority vote + contextual analysis
- **Detailed Reporting**: Generates comprehensive markdown reports with statistics and examples
- **Batch Processing**: Efficiently processes large datasets
- **Reproducible Environment**: Docker support and setup scripts for easy deployment
- **Comprehensive Testing**: Automated test suite with detailed validation

## 📋 Requirements

- Python 3.9 or higher
- Dependencies listed in `requirements.txt`
- (Optional) Docker for containerized deployment

## 🚀 Quick Start

### Installation

#### Option 1: Using Setup Scripts (Recommended)

**On Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

**On Windows:**
```cmd
setup.bat
```

#### Option 2: Manual Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

#### Option 3: Using Docker

```bash
# Build Docker image
docker build -t conflict-detector .

# Run with your data
docker run -v $(pwd)/data:/app/data -v $(pwd)/output:/app/output \
  conflict-detector python main.py --input /app/data/tickets_label.jsonl \
  --output /app/output/results.jsonl
```

### Basic Usage

```bash
# Process entire dataset
python main.py --input tickets_label.jsonl --output results.jsonl

# Extract conflicts only
python main.py --input tickets_label.jsonl --output conflicts_only.jsonl --conflicts-only

# Generate detailed report
python main.py --input tickets_label.jsonl --output results.jsonl --report report.md

# Verbose output
python main.py --input tickets_label.jsonl --output results.jsonl --verbose
```

## 📊 Input Format

The input dataset should be in JSONL format (one JSON object per line) with the following structure:

```json
{
  "id": "TICK-0001",
  "text": "I want to request a refund, but the payment has already been processed.",
  "annotations": [
    {"annotator": "ann_01", "intent": "billing_issue", "urgency": "high"},
    {"annotator": "ann_02", "intent": "billing_issue", "urgency": "high"},
    {"annotator": "ann_03", "intent": "billing_issue", "urgency": "high"}
  ]
}
```

### Required Fields

- `id`: Unique identifier for the sample
- `text`: The text being annotated
- `annotations`: Array of annotator labels
  - `annotator`: Annotator identifier
  - `intent`: Intent classification label
  - `urgency`: Urgency level label

## 📤 Output Format

The output is in JSONL format with detailed conflict analysis:

```json
{
  "id": "TICK-0026",
  "text": "I want a refund but the app says payment failed.",
  "labels": [
    {"annotator": "ann_01", "label": "billing_issue|high"},
    {"annotator": "ann_02", "label": "bug_report|medium"},
    {"annotator": "ann_03", "label": "billing_issue|high"}
  ],
  "is_conflict": true,
  "conflict_reason": "Ambiguous text: Contains terms like 'payment failed' which can be interpreted as multiple intent types | Mixed aspects: Text contains 'but' (contrasting elements), indicating multiple simultaneous issues | Intent classification ambiguity: Mixed technical and business aspects (distribution: billing_issue(2), bug_report(1)), requiring clearer annotation guidelines on prioritizing primary vs. secondary issues",
  "suggested_label": "billing_issue|high",
  "conflict_details": {
    "intent_distribution": {"billing_issue": 2, "bug_report": 1},
    "urgency_distribution": {"high": 2, "medium": 1},
    "has_intent_conflict": true,
    "has_urgency_conflict": true,
    "total_annotators": 3,
    "unique_labels": 3,
    "resolution_reasoning": {
      "majority_intent": "billing_issue",
      "intent_votes": {"billing_issue": 2, "bug_report": 1},
      "intent_confidence": 0.67,
      "majority_urgency": "high",
      "urgency_votes": {"high": 2, "medium": 1},
      "urgency_confidence": 0.67,
      "resolution_strategy": "majority_vote_with_contextual_analysis",
      "explanation": "Intent 'billing_issue' selected by majority (67% confidence, votes: {'billing_issue': 2, 'bug_report': 1}). urgency 'high' selected by majority (67% confidence, votes: {'high': 2, 'medium': 1})."
    }
  }
}
```

### Output Fields

- `id`: Sample identifier
- `text`: Original text
- `labels`: List of annotator labels in simplified format
- `is_conflict`: Boolean indicating if conflict exists
- `conflict_reason`: Detailed explanation of disagreement causes (null if no conflict)
- `suggested_label`: Recommended final label (format: `intent|urgency`)
- `conflict_details`: Detailed statistics and resolution reasoning (optional)

## 📈 Report Generation

Generate comprehensive markdown reports with statistics and examples:

```bash
python main.py --input tickets_label.jsonl --output results.jsonl --report analysis_report.md
```

The report includes:

- **Executive Summary**: Key findings and conflict rates
- **Detailed Statistics**: Conflict distribution by type
- **Conflict Cause Analysis**: Categorized root causes
- **Example Cases**: Conflict and agreement examples
- **Recommendations**: Actionable suggestions for improving annotation quality

## 🧪 Testing

### Run All Tests

```bash
# Run tests with verbose output
python -m pytest test_conflict_detector.py -v

# Run tests with coverage
python -m pytest test_conflict_detector.py --cov=. --cov-report=html

# Run specific test class
python -m pytest test_conflict_detector.py::TestConflictDetection -v
```

### Run Test Suite with Report

```bash
python test_conflict_detector.py
```

This generates a detailed test report in `test_report.txt`.

### Test Coverage

The test suite covers:

- ✅ Correct detection of conflicts (unanimous, intent-only, urgency-only, both)
- ✅ Accurate extraction of conflict samples
- ✅ Reliability of suggested final labels
- ✅ Correct reasoning and explanation for disagreements
- ✅ Handling datasets with multiple documents/batches
- ✅ Dataset format validation
- ✅ Report generation
- ✅ Utility functions

## 🔍 Conflict Analysis Features

### Conflict Detection

The system detects conflicts across multiple dimensions:

1. **Intent Conflicts**: Annotators assigned different intent categories
2. **Urgency Conflicts**: Annotators assessed different urgency levels
3. **Combined Conflicts**: Both intent and urgency differ

### Root Cause Analysis

The system analyzes why disagreements occur:

- **Ambiguous Text**: Keywords that can indicate multiple intents
- **Mixed Aspects**: Text contains multiple simultaneous issues
- **Urgency Variance**: Subjective assessment differences
- **Intent Ambiguity**: Unclear primary vs. secondary issues
- **Brief Text**: Limited context leading to interpretation variance
- **Subjective Interpretation**: Need for clearer guidelines

### Resolution Strategy

The system suggests final labels using:

1. **Majority Vote**: Base resolution on most common label
2. **Contextual Analysis**: Adjust based on keywords and patterns
3. **Confidence Scoring**: Calculate agreement strength
4. **Reasoning Documentation**: Explain resolution decisions

## 📁 Project Structure

```
.
├── conflict_detector.py      # Core conflict detection logic
├── config.py                 # Configuration settings
├── utils.py                  # Utility functions and report generator
├── main.py                   # CLI application
├── test_conflict_detector.py # Comprehensive test suite
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── setup.sh                 # Linux/Mac setup script
├── setup.bat                # Windows setup script
├── tickets_label.jsonl      # Sample input dataset
└── README.md               # This file
```

## 🔧 Configuration

Edit `config.py` to customize:

- Default file paths
- Analysis settings
- Output formatting
- Report generation options
- Logging configuration

## 📊 Example Statistics Output

```
==============================================================
CONFLICT DETECTION STATISTICS
==============================================================
Total Samples Processed: 50
Samples with Conflicts: 5 (10.0%)
Samples without Conflicts: 45 (90.0%)

Conflict Breakdown:
  - Intent conflicts only: 2
  - Urgency conflicts only: 1
  - Both intent and urgency conflicts: 2

Output Samples: 50
==============================================================
```

## 🎓 Use Cases

This system is valuable for:

- **Dataset Quality Assessment**: Evaluate annotator agreement
- **Annotation Guideline Improvement**: Identify ambiguous cases
- **Annotator Training**: Find patterns requiring calibration
- **Ground Truth Establishment**: Resolve disagreements systematically
- **Machine Learning**: Create high-quality training data

## 🔄 Workflow Recommendations

1. **Initial Analysis**: Process full dataset to identify conflict rate
2. **Review Conflicts**: Examine high-conflict samples
3. **Update Guidelines**: Clarify ambiguous annotation rules
4. **Annotator Calibration**: Discuss disagreement patterns
5. **Re-annotation**: Address high-conflict samples
6. **Quality Monitoring**: Track conflict rates over time

## 🐛 Troubleshooting

### Common Issues

**Issue**: `FileNotFoundError: tickets_label.jsonl`
- **Solution**: Ensure input file exists or specify correct path with `--input`

**Issue**: `Dataset format validation failed`
- **Solution**: Verify JSON format and required fields using `--validate-only`

**Issue**: Tests failing
- **Solution**: Check Python version (3.9+) and reinstall dependencies

**Issue**: Docker build fails
- **Solution**: Ensure Docker is installed and running

## 📝 License

This project is open source and available for educational and research purposes.

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:

- Support for additional label dimensions
- Advanced resolution algorithms
- Interactive annotation review interface
- Integration with annotation platforms
- Multi-language support

## 📧 Support

For issues, questions, or suggestions, please open an issue on the project repository.

## 🙏 Acknowledgments

Built for comprehensive multi-annotator dataset analysis with focus on:
- Accuracy in conflict detection
- Quality of disagreement reasoning
- Reliability of suggested labels
- Reproducible environment
- Comprehensive testing
- Clear documentation

---

**Version**: 1.0.0  
**Last Updated**: December 2024