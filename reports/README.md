# Reports Directory

Evaluation outputs, confusion matrices, latency trends, and production
readiness evidence live here. The new `scripts/eval_on_dataset.py`
automatically writes:

- `predictions_<timestamp>.jsonl` — raw per-ticket predictions with request IDs
- `eval_<timestamp>.json` — aggregated metrics (accuracy, precision, recall, F1)
- `eval_<timestamp>.md` — human-friendly summary for sharing in readiness reviews

Keep this directory committed so history of evaluations is tracked (avoid
checking in raw customer data; anonymise before running evaluations).

