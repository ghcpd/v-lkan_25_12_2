# Multi-Annotator Conflict Detection Report

**Generated:** 2025-12-02 13:28:05

---

## Executive Summary

This report presents a comprehensive analysis of annotator agreement and conflicts 
in the multi-annotator dataset.

### Key Findings

- **Total Samples:** 50
- **Conflict Rate:** 14.0% (7 samples)
- **Agreement Rate:** 86.0% (43 samples)
- **Primary Conflict Type:** Intent Classification

## Detailed Statistics

### Conflict Distribution

| Conflict Type | Count | Percentage |
|--------------|-------|------------|
| Intent Only | 1 | 14.29% |
| Urgency Only | 0 | 0.0% |
| Both Intent & Urgency | 6 | 85.71% |
| **Total Conflicts** | **7** | **100%** |

## Conflict Cause Analysis

### Root Causes of Disagreement

| Cause Category | Count | Percentage |
|---------------|-------|------------|
| Ambiguous Text | 6 | 85.71% |
| Mixed Aspects | 1 | 14.29% |

## Example Cases
### Conflict Examples

#### Example 1: TICK-0026

**Text:** I want a refund but the app says payment failed.

**Annotator Labels:**
- ann_01: `billing_issue|high`
- ann_02: `bug_report|medium`
- ann_03: `billing_issue|high`

**Conflict Reason:** Ambiguous text: Contains terms like 'payment failed' which can be interpreted as multiple intent types | Mixed aspects: Text contains 'but' (contrasting elements), indicating multiple simultaneous issues | Intent classification ambiguity: Mixed technical and business aspects (distribution: billing_issue(2), bug_report(1)), requiring clearer annotation guidelines on prioritizing primary vs. secondary issues

**Suggested Resolution:** `billing_issue|high`


#### Example 2: TICK-0027

**Text:** The app crashes and payment didn't go through.

**Annotator Labels:**
- ann_01: `bug_report|critical`
- ann_02: `billing_issue|high`
- ann_03: `bug_report|critical`

**Conflict Reason:** Mixed aspects: Text contains 'and' (multiple aspects), indicating multiple simultaneous issues | Intent classification ambiguity: Mixed technical and business aspects (distribution: bug_report(2), billing_issue(1)), requiring clearer annotation guidelines on prioritizing primary vs. secondary issues

**Suggested Resolution:** `bug_report|critical`


#### Example 3: TICK-0028

**Text:** I need to cancel my subscription, but the system shows an error.

**Annotator Labels:**
- ann_01: `subscription_issue|medium`
- ann_02: `account_issue|medium`
- ann_03: `subscription_issue|high`

**Conflict Reason:** Ambiguous text: Contains terms like 'subscription, cancel' which can be interpreted as multiple intent types | Mixed aspects: Text contains 'but' (contrasting elements), indicating multiple simultaneous issues | Intent classification ambiguity: Mixed technical and business aspects (distribution: subscription_issue(2), account_issue(1)), requiring clearer annotation guidelines on prioritizing primary vs. secondary issues

**Suggested Resolution:** `subscription_issue|medium`


#### Example 4: TICK-0046

**Text:** I want a refund but the app crashed during payment.

**Annotator Labels:**
- ann_01: `billing_issue|high`
- ann_02: `bug_report|critical`
- ann_03: `billing_issue|high`

**Conflict Reason:** Ambiguous text: Contains terms like 'app crashed' which can be interpreted as multiple intent types | Mixed aspects: Text contains 'but' (contrasting elements), indicating multiple simultaneous issues | Intent classification ambiguity: Mixed technical and business aspects (distribution: billing_issue(2), bug_report(1)), requiring clearer annotation guidelines on prioritizing primary vs. secondary issues

**Suggested Resolution:** `billing_issue|critical`


#### Example 5: TICK-0047

**Text:** App crashes and subscription did not start.

**Annotator Labels:**
- ann_01: `bug_report|critical`
- ann_02: `subscription_issue|high`
- ann_03: `bug_report|critical`

**Conflict Reason:** Ambiguous text: Contains terms like 'subscription' which can be interpreted as multiple intent types | Mixed aspects: Text contains 'and' (multiple aspects), indicating multiple simultaneous issues | Intent classification ambiguity: Mixed technical and business aspects (distribution: bug_report(2), subscription_issue(1)), requiring clearer annotation guidelines on prioritizing primary vs. secondary issues | Brief text (7 words): Limited context may lead to varying interpretations of user intent and urgency

**Suggested Resolution:** `bug_report|critical`

### Agreement Examples (No Conflicts)

#### Example 1: TICK-0001

**Text:** I want to request a refund, but the payment has already been processed.

**Unanimous Label:** `billing_issue|high`


#### Example 2: TICK-0002

**Text:** The app crashes every time I try to log in.

**Unanimous Label:** `bug_report|critical`


#### Example 3: TICK-0003

**Text:** How can I change my account password?

**Unanimous Label:** `account_issue|low`


## Recommendations

### Improving Annotation Quality

- **Intent classification is the primary source of disagreement.** Provide clearer definitions and examples for each intent category, particularly for cases involving multiple simultaneous issues.
- **6 conflicts involve ambiguous text.** Develop decision trees or rules for handling texts with multiple interpretations.
- **Implement regular calibration sessions** where annotators discuss disagreement cases to align understanding and interpretation.
- **Consider adjudication workflow** for high-conflict samples to establish ground truth through expert review or consensus discussion.

### Next Steps

1. Review conflict examples to identify common patterns
2. Update annotation guidelines based on identified ambiguities
3. Conduct annotator training on updated guidelines
4. Re-annotate high-conflict samples after guideline improvements
5. Monitor conflict rate trends over time

---

## Methodology

This analysis uses automated conflict detection with the following approach:

1. **Conflict Detection:** Identify samples where annotators assigned different labels
2. **Cause Analysis:** Analyze text characteristics and label patterns to determine disagreement causes
3. **Resolution Suggestion:** Provide recommended labels based on majority vote with contextual analysis
4. **Quality Metrics:** Calculate agreement rates and conflict distributions

**Report Generated by:** Multi-Annotator Conflict Detection System  
**Timestamp:** 2025-12-02 13:28:05