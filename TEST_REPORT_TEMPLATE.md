# Conflict Detection Test Report Template

Use this template to document the results of running the conflict detection and resolution tests.

1. Summary

- Date: <date>
- Dataset: tickets_label.jsonl
- Tests run: <pytest command / CI link>
- Conflicts found: <N>

2. Expected vs Actual

- Expected conflicted IDs (manual): TICK-0026, TICK-0027, TICK-0028, TICK-0046, TICK-0047, TICK-0048, TICK-0049
- Actual conflicts found: <list>

3. Failure cases and notes

- Any false negatives or false positives => list ids and why

4. Suggested label quality

- For each conflict id, include the output suggestion and confidence

5. Next steps / Recommendations

- Adjust annotation instructions, add more heuristics, or enable reviewer override for ambiguous items.
