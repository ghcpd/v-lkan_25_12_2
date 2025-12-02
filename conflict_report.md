# Annotation Conflict Detection Report

## Summary Statistics
- **Total Samples**: 50
- **Conflicted Samples**: 7
- **Unanimous Samples**: 43
- **Conflict Rate**: 14.0%

## Conflicted Samples Details

### Sample ID: TICK-0026
**Text**: I want a refund but the app says payment failed.

**Annotations**:
- ann_01: intent=billing_issue, urgency=high
- ann_02: intent=bug_report, urgency=medium
- ann_03: intent=billing_issue, urgency=high

**Conflict Reason**: Ambiguous or vague text description | Text contains multiple issues or mixed sentiment | Inconsistent intent classification: most annotators chose 'billing_issue' but some chose ['bug_report'] | Different urgency assessment: most consider it 'high' but some consider ['medium'] | Billing-related issues may overlap with system errors, causing different categorizations

**Suggested Resolution**: 
- Intent: billing_issue
- Urgency: high
- Confidence: 0.67
- Reasoning: Despite conflicts, 'billing_issue' is chosen by 2/3 annotators (67% confidence). Urgency level 'high' agreed upon by 2/3 annotators (67% confidence).

---

### Sample ID: TICK-0027
**Text**: The app crashes and payment didn't go through.

**Annotations**:
- ann_01: intent=bug_report, urgency=critical
- ann_02: intent=billing_issue, urgency=high
- ann_03: intent=bug_report, urgency=critical

**Conflict Reason**: Ambiguous or vague text description | Text contains multiple issues or mixed sentiment | Inconsistent intent classification: most annotators chose 'bug_report' but some chose ['billing_issue'] | Different urgency assessment: most consider it 'critical' but some consider ['high'] | Technical issues can be classified as either 'bug_report' or related issue (billing/account) depending on interpretation | Billing-related issues may overlap with system errors, causing different categorizations

**Suggested Resolution**: 
- Intent: bug_report
- Urgency: critical
- Confidence: 0.67
- Reasoning: Despite conflicts, 'bug_report' is chosen by 2/3 annotators (67% confidence). Urgency level 'critical' agreed upon by 2/3 annotators (67% confidence). Text clearly indicates a technical issue, supporting 'bug_report' classification. Multiple critical indicators (crash, unable to access, service down) justify 'critical' urgency.

---

### Sample ID: TICK-0028
**Text**: I need to cancel my subscription, but the system shows an error.

**Annotations**:
- ann_01: intent=subscription_issue, urgency=medium
- ann_02: intent=account_issue, urgency=medium
- ann_03: intent=subscription_issue, urgency=high

**Conflict Reason**: Text contains multiple issues or mixed sentiment | Inconsistent intent classification: most annotators chose 'subscription_issue' but some chose ['account_issue'] | Different urgency assessment: most consider it 'medium' but some consider ['high'] | Technical issues can be classified as either 'bug_report' or related issue (billing/account) depending on interpretation

**Suggested Resolution**: 
- Intent: subscription_issue
- Urgency: medium
- Confidence: 0.67
- Reasoning: Despite conflicts, 'subscription_issue' is chosen by 2/3 annotators (67% confidence). Urgency level 'medium' agreed upon by 2/3 annotators (67% confidence).

---

### Sample ID: TICK-0046
**Text**: I want a refund but the app crashed during payment.

**Annotations**:
- ann_01: intent=billing_issue, urgency=high
- ann_02: intent=bug_report, urgency=critical
- ann_03: intent=billing_issue, urgency=high

**Conflict Reason**: Text contains multiple issues or mixed sentiment | Inconsistent intent classification: most annotators chose 'billing_issue' but some chose ['bug_report'] | Different urgency assessment: most consider it 'high' but some consider ['critical'] | Technical issues can be classified as either 'bug_report' or related issue (billing/account) depending on interpretation | Billing-related issues may overlap with system errors, causing different categorizations

**Suggested Resolution**: 
- Intent: billing_issue
- Urgency: high
- Confidence: 0.67
- Reasoning: Despite conflicts, 'billing_issue' is chosen by 2/3 annotators (67% confidence). Urgency level 'high' agreed upon by 2/3 annotators (67% confidence).

---

### Sample ID: TICK-0047
**Text**: App crashes and subscription did not start.

**Annotations**:
- ann_01: intent=bug_report, urgency=critical
- ann_02: intent=subscription_issue, urgency=high
- ann_03: intent=bug_report, urgency=critical

**Conflict Reason**: Ambiguous or vague text description | Text contains multiple issues or mixed sentiment | Inconsistent intent classification: most annotators chose 'bug_report' but some chose ['subscription_issue'] | Different urgency assessment: most consider it 'critical' but some consider ['high'] | Technical issues can be classified as either 'bug_report' or related issue (billing/account) depending on interpretation

**Suggested Resolution**: 
- Intent: bug_report
- Urgency: critical
- Confidence: 0.67
- Reasoning: Despite conflicts, 'bug_report' is chosen by 2/3 annotators (67% confidence). Urgency level 'critical' agreed upon by 2/3 annotators (67% confidence). Text clearly indicates a technical issue, supporting 'bug_report' classification. Multiple critical indicators (crash, unable to access, service down) justify 'critical' urgency.

---

### Sample ID: TICK-0048
**Text**: Account locked but payment went through.

**Annotations**:
- ann_01: intent=account_issue, urgency=high
- ann_02: intent=billing_issue, urgency=medium
- ann_03: intent=account_issue, urgency=high

**Conflict Reason**: Ambiguous or vague text description | Text contains multiple issues or mixed sentiment | Inconsistent intent classification: most annotators chose 'account_issue' but some chose ['billing_issue'] | Different urgency assessment: most consider it 'high' but some consider ['medium'] | Billing-related issues may overlap with system errors, causing different categorizations

**Suggested Resolution**: 
- Intent: account_issue
- Urgency: high
- Confidence: 0.67
- Reasoning: Despite conflicts, 'account_issue' is chosen by 2/3 annotators (67% confidence). Urgency level 'high' agreed upon by 2/3 annotators (67% confidence).

---

### Sample ID: TICK-0049
**Text**: Payment failed and app won't open.

**Annotations**:
- ann_01: intent=billing_issue, urgency=critical
- ann_02: intent=bug_report, urgency=critical
- ann_03: intent=billing_issue, urgency=critical

**Conflict Reason**: Ambiguous or vague text description | Text contains multiple issues or mixed sentiment | Inconsistent intent classification: most annotators chose 'billing_issue' but some chose ['bug_report'] | Billing-related issues may overlap with system errors, causing different categorizations

**Suggested Resolution**: 
- Intent: billing_issue
- Urgency: critical
- Confidence: 0.83
- Reasoning: Despite conflicts, 'billing_issue' is chosen by 2/3 annotators (67% confidence). Urgency level 'critical' agreed upon by 3/3 annotators (100% confidence). Multiple critical indicators (crash, unable to access, service down) justify 'critical' urgency.

---

