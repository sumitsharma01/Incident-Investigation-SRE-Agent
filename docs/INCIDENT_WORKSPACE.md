# Persistent incident workspace and recovery verification

[Project home](../README.md) · [Documentation](index.md)

Version 0.4.0 adds a durable workspace around the investigation API.
OpenSRE still owns the live investigation loop. This project now owns the saved
incident record, independently captured query evidence, and recovery evaluation.
The demo backend remains available, and its summaries remain sample evidence.

## Start and navigate

```bash
pip install -e '.[test]'
export SRE_WORKSPACE_DB="$PWD/data/workspace.sqlite3"
export SRE_PROMETHEUS_URL=http://127.0.0.1:9090
export SRE_METRIC_PREFIX=sre_lab
uvicorn app.main:app --host 127.0.0.1 --port 8010
```

Open [the workspace](http://127.0.0.1:8010/workspace) or
[the API reference](http://127.0.0.1:8010/docs). Run an investigation, select the
saved record, capture a **before** observation, perform an engineer-reviewed
intervention, and capture **after** once a complete 30-second window has passed.
Enter the intervention description and check recovery. The UI uses conservative
lab defaults; the API lets you supply your own thresholds.

Live OpenSRE investigations require the existing [provider and tool configuration](OPENSRE_INTEGRATION.md).
The workspace itself makes read-only queries directly to the operator-configured
Prometheus endpoint; it does not need an LLM to determine a recovery verdict.

## What persists

`POST /investigate` keeps its response shape and adds `incident_id`. Before
execution it saves a running record, then stores the returned summary, status,
plan and notes. A restart keeps completed records and marks unfinished runs as
`interrupted`. It does not silently retry model calls or label an interrupted run
successful. A client that loses its connection can find the record in the list.

Each observation stores the exact PromQL, evaluation timestamp, sample timestamp,
values and raw Prometheus result. These queries are independent of OpenSRE's
narrative: saving a model report is not proof that every statement in it was
verified. OpenSRE tool traces are not automatically imported.

| Endpoint | Purpose |
| --- | --- |
| `POST /investigate` | Investigate and retain the result |
| `GET /incidents` | Latest 200 saved incidents |
| `GET /incidents/{id}` | Report, observations and recovery checks |
| `POST /incidents/{id}/observations` | Capture `{"label":"before"}` or `{"label":"after"}` |
| `POST /incidents/{id}/recovery` | Compare two snapshots using supplied targets |

## How recovery is judged

The configured queries cover request rate, P95 latency, error ratio and queue
depth. The default prefix `sre_lab` matches the real-request recovery lab.
`SRE_METRIC_PREFIX=sre_demo` targets the older synthetic exporter, whose recovery
must not be described as a real intervention. Other metric schemas need a query
adapter; merely changing a prefix cannot support arbitrary production metrics.

A `recovered` verdict requires lower P95, P95 ≤ 0.5 seconds, errors ≤ 1%, queue
≤ 20, and at least 80% of the before request rate plus a minimum 1 RPS by default.
The recorded lab tightens that minimum to 40 RPS. Overlapping windows or inadequate
traffic return `inconclusive`; failed targets return `not_recovered`. Missing,
ambiguous, non-finite or stale metrics reject capture rather than producing a
positive verdict. Each verdict retains its policy and snapshot IDs.

Two windows demonstrate an observed improvement. They do not establish causation,
a proven root cause, an SLO compliance period, or sustained recovery. The P95 lab
gauge is calculated from actual requests; production histogram queries require
a suitable adapter. The intervention note is operator-supplied, not attested by
the server, and the API never performs a fix.

## Local operating boundaries

Without `SRE_TENANTS_FILE`, this release is a **single local workspace**, with no authentication. Optional tenant mode is described below.
Bind the API to localhost. SQLite startup recovery assumes one application process
(no multiple Uvicorn workers or replicas). The synchronous investigation request
can take minutes; durable asynchronous jobs are a later step. Keep the DB on a
persistent local volume and back it up with SQLite's backup API. Deleting the DB
removes the records. Incident text and reports may contain sensitive evidence;
the ignored `data/` directory must not be published or shared casually.

## Optional tenant isolation

Set `SRE_TENANTS_FILE` to an operator-owned JSON file outside version control.
Generate a different key for each tenant with `python -c "import secrets; print(secrets.token_urlsafe(32))"`.
The ignored `tenants.local.json` can hold your local configuration:

```json
{
  "team-a": {
    "api_key": "REPLACE_WITH_A_GENERATED_KEY_AT_LEAST_32_CHARACTERS",
    "services": ["checkout-a"],
    "prometheus_url": "https://metrics.team-a.example",
    "metric_prefix": "sre_lab",
    "opensre_home": "/absolute/path/to/isolated/team-a-opensre",
    "model_env": {"LLM_PROVIDER": "azure-openai", "LLM_MODEL": "your-deployment"}
  }
}
```

Use `Authorization: Bearer <tenant-key>` for every incident endpoint. The UI has
a password field and keeps the key only in page memory. The server derives the
tenant from the key, checks its allowed services, and scopes record reads and
writes in SQLite. A foreign incident or snapshot returns 404. Records created
before tenant mode remain in the `local` workspace and aren't exposed to tenants.
Health, UI shell and API schema are public; incident data is not.

Each tenant needs its own read-only Prometheus endpoint or an independently
restricted datasource gateway. Optional `prometheus_token` supplies a bearer
credential. Service filtering alone is not a substitute for datasource isolation.
Live OpenSRE runs require distinct, non-overlapping `opensre_home` directories.
Provision each profile's integrations there using OpenSRE's supported
`OPENSRE_HOME` setting. The child process receives a minimal environment plus
that tenant's explicitly configured model settings, runs from its own directory,
and does not inherit the shared Grafana/model credentials. Demo runs in tenant
mode use a credential-free summary. A missing OpenSRE home rejects live execution.

A separate two-tenant HTTP run also verified 401/404 access denials and records
surviving a process restart; [results](case-studies/worker-capacity/tenant-isolation.json).
Tests cover foreign-record reads, observation/recovery access, service restrictions,
restart persistence, and runtime credential selection. Two tenants' live external
integrations have not been exercised in this recorded lab. This is application
isolation in a shared host/process/database, not an OS sandbox, SSO, encrypted
secret vault, or production certification. Protect the config file (for example
`chmod 600 tenants.local.json`) and use TLS before remote access. A host administrator
can access all records. Do not execute untrusted tool code on the shared host.
