"""
Run the production API against a JSONL dataset and store predictions +
evaluation metrics. Fulfills the prod-readiness checklist requirement
for automated evaluation.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

DEFAULT_API_URL = "http://localhost:5000"
DEFAULT_OUTPUT_DIR = Path("reports")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate AI Ticket Classifier on a dataset."
    )
    parser.add_argument(
        "--input", required=True, help="Path to input JSONL file with tickets."
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path to predictions JSONL file. Defaults to reports/predictions_<timestamp>.jsonl",
    )
    parser.add_argument(
        "--report",
        default=None,
        help="Path to metrics summary JSON. Defaults to reports/eval_<timestamp>.json",
    )
    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help="Base API URL (default: http://localhost:5000)",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("EVAL_API_KEY"),
        help="API key or MASTER key for authentication",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Limit number of samples processed",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP timeout per request in seconds (default: 30)",
    )
    return parser.parse_args()


def load_jsonl(path: Path, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
            if max_samples and len(records) >= max_samples:
                break
    return records


def ensure_reports_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def call_api(
    session: requests.Session,
    api_url: str,
    api_key: str,
    text: str,
    timeout: int,
) -> Dict[str, Any]:
    url = api_url.rstrip("/") + "/api/v1/classify"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key

    start = time.perf_counter()
    response = session.post(
        url, json={"ticket": text}, headers=headers, timeout=timeout
    )
    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    data = response.json()
    data["latency_ms"] = latency_ms
    data.setdefault("request_id", response.headers.get("X-Request-ID"))
    data["status_code"] = response.status_code
    return data


def compute_metrics(records: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    y_true: List[str] = []
    y_pred: List[str] = []

    for record in records:
        if record.get("status") != "ok":
            continue
        expected = record.get("expected_label")
        predicted = record.get("predicted_label")
        if expected is None or predicted is None:
            continue
        y_true.append(expected.strip())
        y_pred.append(predicted.strip())

    if not y_true:
        return None

    labels = sorted({*y_true, *y_pred})
    confusion = {label: defaultdict(int) for label in labels}

    for true_label, pred_label in zip(y_true, y_pred):
        confusion[true_label][pred_label] += 1

    per_label = {}
    precisions = []
    recalls = []
    f1s = []

    for label in labels:
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in labels if other != label)
        fn = sum(confusion[label][other] for other in labels if other != label)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (
            (2 * precision * recall / (precision + recall))
            if (precision + recall)
            else 0.0
        )
        support = sum(confusion[label].values())

        per_label[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": support,
        }

        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)

    accuracy = sum(1 for t, p in zip(y_true, y_pred) if t == p) / len(y_true)

    metrics = {
        "samples": len(y_true),
        "accuracy": round(accuracy, 4),
        "macro_precision": round(sum(precisions) / len(labels), 4),
        "macro_recall": round(sum(recalls) / len(labels), 4),
        "macro_f1": round(sum(f1s) / len(labels), 4),
        "per_label": per_label,
        "confusion_matrix": {label: dict(confusion[label]) for label in labels},
    }

    return metrics


def write_jsonl(path: Path, records: List[Dict[str, Any]]) -> None:
    ensure_reports_dir(path)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_report(path: Path, metrics: Dict[str, Any], predictions_file: Path) -> None:
    ensure_reports_dir(path)
    timestamp = datetime.utcnow().isoformat()
    payload = {
        "generated_at": timestamp,
        "predictions_file": str(predictions_file),
        "metrics": metrics,
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)

    md_path = path.with_suffix(".md")
    with md_path.open("w", encoding="utf-8") as handle:
        handle.write(f"# Evaluation Summary ({timestamp})\n\n")
        handle.write(f"- Samples: **{metrics['samples']}**\n")
        handle.write(f"- Accuracy: **{metrics['accuracy']}**\n")
        handle.write(f"- Macro F1: **{metrics['macro_f1']}**\n")
        handle.write(f"- Predictions file: `{predictions_file}`\n\n")
        handle.write("## Per-label metrics\n\n")
        for label, values in metrics["per_label"].items():
            handle.write(
                f"- **{label}** — P: {values['precision']}, R: {values['recall']}, F1: {values['f1']} (support {values['support']})\n"
            )


def main():
    args = parse_args()

    if not args.api_key:
        raise SystemExit(
            "API key is required. Provide via --api-key or EVAL_API_KEY env var."
        )

    dataset_path = Path(args.input)
    records = load_jsonl(dataset_path, max_samples=args.max_samples)
    if not records:
        raise SystemExit("Input dataset is empty.")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_path = (
        Path(args.output)
        if args.output
        else DEFAULT_OUTPUT_DIR / f"predictions_{timestamp}.jsonl"
    )
    report_path = (
        Path(args.report)
        if args.report
        else DEFAULT_OUTPUT_DIR / f"eval_{timestamp}.json"
    )

    session = requests.Session()

    predictions: List[Dict[str, Any]] = []
    for idx, record in enumerate(records, start=1):
        text = record.get("text") or record.get("ticket")
        if not text:
            predictions.append(
                {
                    "id": record.get("id", idx),
                    "status": "error",
                    "error": "Missing text field",
                }
            )
            continue

        try:
            api_result = call_api(
                session, args.api_url, args.api_key, text, args.timeout
            )
            status = "ok" if api_result.get("status_code", 500) == 200 else "error"
            predictions.append(
                {
                    "id": record.get("id", idx),
                    "text": text,
                    "expected_label": record.get("label"),
                    "predicted_label": api_result.get("category"),
                    "confidence": api_result.get("confidence"),
                    "provider": api_result.get("provider"),
                    "latency_ms": api_result.get("latency_ms"),
                    "request_id": api_result.get("request_id"),
                    "status": status,
                    "raw_response": api_result,
                }
            )
        except Exception as exc:  # noqa: BLE001
            predictions.append(
                {
                    "id": record.get("id", idx),
                    "text": text,
                    "expected_label": record.get("label"),
                    "status": "error",
                    "error": str(exc),
                }
            )

    write_jsonl(output_path, predictions)

    metrics = compute_metrics(predictions)
    if metrics:
        write_report(report_path, metrics, output_path)
        print(f"✅ Evaluation complete. Metrics saved to {report_path}")
    else:
        print("⚠️ Predictions saved but no labels were provided, skipping metrics.")
    print(f"Predictions file: {output_path}")


if __name__ == "__main__":
    main()
