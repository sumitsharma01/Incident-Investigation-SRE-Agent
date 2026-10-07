# Peak traffic in action

This scenario sends no traffic to a real service. The local exporter generates
counters and gauges, Prometheus scrapes them, and Grafana plots the live queries.
The screenshots show a controlled peak, not a production load test.

## Scenario

| Phase | Duration | Request rate | Failed requests | Synthetic p95 latency |
| --- | --- | --- | --- | --- |
| Baseline | First 60 seconds | 47/sec | About 4.26% | 420 ms |
| Peak | Next 90 seconds | 1,500/sec | 8% | 1.8 seconds |
| Recovery | After 150 seconds | 47/sec | About 4.26% | 420 ms |

The peak is approximately **32 times** the baseline. Counters accumulate across
phases, so a change in rate does not reset them. The PromQL rate uses a 30-second
window and therefore smooths the start and end of the peak. Restarting the
exporter resets counters; Prometheus handles that reset in `rate()`.

## Run and capture

Start the local lab using the [integration quickstart](GRAFANA_PROMETHEUS_QUICKSTART.md).
Then restart only the sample exporter in high-traffic mode:

```bash
SRE_DEMO_TRAFFIC_SCENARIO=high-traffic docker compose --env-file .env.observability \
  -f docker/observability/compose.yml up -d --force-recreate demo-metrics
python examples/capture_peak_traffic.py
```

The capture script waits for at least 1,450 requests/sec and checks that the
peak phase is active. It saves the observed values and captures the actual UI
pages. Use `--executable-path` for an installed Chrome executable if needed.

Open the peak dashboard at http://127.0.0.1:3000/d/sre-high-traffic. It includes
current and maximum request-rate cards, the traffic curve, failed-request
percentage, latency, and a peak-active indicator. The maximum card looks back
ten minutes and may include an earlier run. Restarting the exporter replays
the scenario without deleting Prometheus history.

## Live screenshots

Captured from the running local lab on 7 October 2026. The orange panels
highlight traffic volume; the request-rate peak should be compared with the
baseline, error percentage and latency rather than read on its own.

![Grafana showing the synthetic high-traffic peak](screenshots/grafana-peak-traffic.png)

![Prometheus tables showing traffic, errors, latency and the active peak](screenshots/prometheus-peak-traffic.png)

The Prometheus table is evaluated at **12:56:53 Europe/Berlin** (10:56:53 UTC),
during the recorded active peak. It shows **1,499.82 req/s**, **7.9993% errors**,
**1.8-second latency**, and **peak active = 1**. Grafana was captured live
during the same scenario, with its traffic cards rounded to 1.5K req/s.

The [captured observations](peak-traffic-observations.json) record the sample
values and query used for the peak. Screenshots are evidence of the local
telemetry path, not evidence of application capacity or causal relationships.
The exporter deliberately changes errors and latency with the peak.

## Queries

```promql
sum(rate(sre_demo_requests_total{job="checkout-demo"}[30s]))
```

```promql
100 * sum(rate(sre_demo_requests_total{job="checkout-demo",status="500"}[30s]))
  / sum(rate(sre_demo_requests_total{job="checkout-demo"}[30s]))
```

```promql
sre_demo_latency_seconds{job="checkout-demo",quantile="0.95"}
```

```promql
sre_demo_peak_active{job="checkout-demo"}
```

## Return to steady mode

The scenario returns to baseline automatically after 150 seconds. To restore
the original steady exporter configuration explicitly:

```bash
SRE_DEMO_TRAFFIC_SCENARIO=steady docker compose --env-file .env.observability \
  -f docker/observability/compose.yml up -d --force-recreate demo-metrics
```
