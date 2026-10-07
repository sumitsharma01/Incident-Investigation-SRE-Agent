# Grafana and Prometheus

Use Grafana as the entry point to Prometheus. OpenSRE discovers the metrics
datasource through Grafana and queries it through the datasource proxy. No
separate Prometheus credential needs to be sent to this agent.

## Configure

In your existing Grafana instance, create a service account with read access
to the required datasource and add a token. Store the token locally in the
ignored `.env`, not in chat or Git:

```dotenv
GRAFANA_INSTANCE_URL=https://your-stack.grafana.net
GRAFANA_READ_TOKEN=
GRAFANA_VERIFY_SSL=true
GRAFANA_MIMIR_DATASOURCE_UID=
```

Use `GRAFANA_MIMIR_DATASOURCE_UID` for the Prometheus datasource UID, despite
the setting's name. OpenSRE uses it for Prometheus-style metrics. If there is
only one Prometheus datasource, the connection checker selects it. If there
are several, select one explicitly. Set `GRAFANA_CA_BUNDLE` for a private CA.

Start the API with `uvicorn app.main:app --env-file .env` so these settings
reach the OpenSRE subprocess. The default demo backend remains synthetic.

## Verify in stages

First, run the model-free, read-only connection check from the repository root:

```bash
python examples/verify_grafana.py
```

It performs `GET /api/datasources`, then queries `up` through the selected
Prometheus datasource. It reports the datasource UID and series count without
printing the token or metric labels. An empty result is not evidence that any
service is healthy. The checker keeps certificate verification enabled and
permits plain HTTP only for loopback development instances.

Next, submit a scoped request through the OpenSRE backend:

```bash
curl http://127.0.0.1:8000/investigate \
  -H 'Content-Type: application/json' \
  -d '{"service":"YOUR_SERVICE","description":"Use Grafana metrics only. Check scrape health and available metric names for this service over the last 15 minutes. Report datasource UID, queries, time window and any missing evidence. Do not change configuration.","backend":"opensre"}'
```

Replace the service name with the one used in your telemetry. Agree on the
service label and actual metric names before asking for error rate or latency;
those labels and metrics vary between applications. A metrics-only setup
cannot establish deployment history, logs or trace evidence.

## What still needs verification

The repository includes the setup path and connection checker. Grafana access
and a real metrics investigation require your instance URL, datasource access
and read-only token. The local lab initially passed datasource discovery and an `up` query. Subsequent checks hit Docker storage I/O errors, Grafana login failures and a token authorization failure. After an approved Docker Desktop restart, Grafana token access and metric queries recovered. Both dashboard and query screenshots now show populated samples. The subsequent scoped OpenSRE metrics investigation completed with status success and no denied tools; its report included a 4.2553% failed-request rate. This verifies the local synthetic lab path, not production access.

References: [OpenSRE Grafana integration](https://github.com/Tracer-Cloud/opensre/blob/288a82456af27ce75487527b2b21c7ab1cbf5d6b/docs/integrations/monitoring/grafana.mdx),
[Grafana service accounts](https://grafana.com/docs/grafana/latest/administration/service-accounts/),
[Prometheus HTTP API](https://prometheus.io/docs/prometheus/latest/querying/api/).

## Local demo stack

The lab uses real Grafana and Prometheus with synthetic checkout metrics.
It does not connect to production. Start Docker Desktop, then run these
commands from the repository root:

```bash
python -c 'from pathlib import Path; import secrets; p=Path(".env.observability"); p.exists() or p.write_text("SRE_DEMO_GRAFANA_ADMIN_PASSWORD="+secrets.token_urlsafe(24)+"\n"); p.chmod(0o600)'
docker compose --env-file .env.observability -f docker/observability/compose.yml up -d
python examples/setup_local_grafana.py
python examples/verify_grafana.py
```

The setup script creates a Viewer service account token valid for seven days
and writes it to the ignored `.env`. It uses the local admin password from the
ignored `.env.observability`; neither secret is printed. This setup script is
only for the provided local lab. Rerunning it creates a new expiring token.

- Grafana: http://127.0.0.1:3000/d/sre-checkout-demo
- Prometheus: http://127.0.0.1:9090
- Dashboard: scrape health, request rate, error percentage and synthetic p95 latency.
- Login: `admin`; password is stored in your local `.env.observability`.

The metrics exporter represents approximately 45 successful and 2 failed
requests per second, with p95 latency fixed at 420 ms. Wait at least a minute
for rate panels to populate. These values are generated samples, not an
actual checkout service's performance.

Start the agent with `uvicorn app.main:app --env-file .env`. Select the OpenSRE
backend and ask it to query the demo Prometheus datasource for checkout
metrics. The earlier Azure/OpenSRE settings remain separate from Grafana.

To stop the lab while keeping its data:

```bash
docker compose --env-file .env.observability -f docker/observability/compose.yml down
```

## Local runtime issue observed

The first live check returned two `up` series. Docker subsequently reported
`overlay2 ... input/output error`, and Grafana login returned HTTP 500. Later
token checks returned HTTP 401. The host had approximately 3.7 GiB available.
Grafana reported version 13.2.3 and Prometheus 3.15.0; images are pinned by
digest in Compose. Restore Docker storage health before relying on this lab.
No existing Docker data was deleted or pruned.

## Recovery and screenshots

Docker Desktop was restarted with approval on 7 October 2026. The lab was
recreated with its existing volumes, the Viewer token renewed and access
checked again. Prometheus returned scrape health 1, request rate 47 and
latency 0.42 seconds. Grafana panels show approximately 4.26% errors.
Both browser screenshots were visually checked. Follow the
[step-by-step quickstart](GRAFANA_PROMETHEUS_QUICKSTART.md).
