# Load Testing

This folder contains k6 scenarios for validating the AI Ticket Classifier
under different loads (smoke 50 rps, steady 200 rps, stress 1000 rps).

## Prerequisites

- k6 installed locally (`brew install k6` / download from k6.io).
- Running instance of the API (Docker Compose or remote staging).
- Valid API key with enough rate limit headroom.

## Running the tests

```bash
export BASE_URL="http://localhost:5000"
export API_KEY="atc_your_key"
# optional overrides: SMOKE_RPS, STEADY_RPS, STRESS_RPS

k6 run loadtests/k6_scenarios.js \
  --summary-export reports/loadtests/k6_summary.json \
  --console-output reports/loadtests/k6_console.log
```

This will:

- execute all three scenarios (smoke/steady/stress) sequentially,
- emit k6 metrics (latency, http failures),
- store raw outputs under `reports/loadtests/`.

## Reports & follow-up

1. Capture Prometheus/Grafana snapshots plus k6 JSON summary.
2. Compare `classify_latency_ms` p95/p99 with SLOs.
3. Tune timeouts or circuit breaker thresholds if error rate > 2%.

If you need to run a single scenario, use the `--execution-segment` flag
from k6 or comment unwanted entries in `options.scenarios`.

