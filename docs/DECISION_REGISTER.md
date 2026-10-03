# Start a prospective decision register

`config/decision_register.json` intentionally starts empty. No probabilities are retrospectively assigned to historical decisions. Keep rejected forecasts and losses; define how ambiguous events will be resolved before publication.

Create an input JSON file following this schema, replacing every example with an owner-approved forecast. This is a **schema example**, not an investment prediction:

```json
{
  "id": "your-unique-forecast-id",
  "kind": "forecast",
  "information_cutoff": "2026-10-03T10:00:00Z",
  "deadline": "2026-12-31T23:59:00Z",
  "probability": 0.50,
  "event": "Define one observable binary event",
  "resolution_rule": "Specify exact threshold, currency, date and treatment of missing data",
  "source_url": "https://replace-with-primary-source.example",
  "alternative": "State the strongest competing hypothesis",
  "invalidation": "State what evidence would change the thesis"
}
```

Run `python scripts/record_decision.py your_record.json`. The script stamps the current UTC creation time, appends a SHA-256 chained record and validates chronology. Review the diff and publish its Git commit **before** the event. Never edit an old forecast silently. A later revised probability should be a new uniquely named forecast that explicitly references the old thesis in its event text; retain the original for scoring.

After the specified deadline, append a resolution JSON containing `id`, `kind: "resolution"`, `forecast_id`, `outcome` (integer 0 or 1), and `evidence_url`. The script stamps its time. Duplicate or premature resolutions are rejected. Unresolved records remain visible; do not drop inconvenient outcomes. For cancellations or unresolvable events, retain the forecast and document the reason separately; do not force a binary score.

Run `python -m investment_lab decision-log` to validate the chain and score resolved forecasts. Binary Brier loss is `(p − outcome)²`, range 0–1; lower is better. Publish sample size and a prespecified base-rate benchmark before making claims about skill. Calibration, discrimination and investment returns are different properties.

A hash chain is not immutable storage: rewriting the complete chain is possible. External publication timestamps, Git history and source archives provide additional anchors, not an independent audit. Source links alone do not verify the information available at the original decision time. There are no private credentials in this register; public records should contain only material intended for recruiters to see.
