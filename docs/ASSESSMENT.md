# Functionality assessment and integration decision

Reviewed original agent commit be3bbb626f58b85ee38bf58940f8503e62dd32b4 and OpenSRE commit 288a82456af27ce75487527b2b21c7ab1cbf5d6b.

## Is this useful?

The existing project is useful as a teaching/demo API and dashboard. It has a clean separation of orchestration, evidence, reasoning and presentation, but is not a production root-cause investigator:

- All five collectors use synthetic data.
- `generate_hypotheses` always returns two checkout scenarios regardless of service or observations. Confidence is based on evidence counts, not calibrated probability.
- The planner result is discarded. SLO/error-budget framing primarily lives in demo examples.
- Previously the LLM answer was discarded by the API; only its provider mode appeared.
- Cache and token-budget configuration existed without a working reasoning cache or exact token enforcement.
- SafetyGuard validates presence of inputs; it is not an infrastructure permission boundary.
- There is no authentication, incident persistence, request rate limit or production integration configuration.

## Chosen integration

Use the documented `opensre --json ask --ephemeral -` CLI boundary. It avoids importing OpenSRE's large source-only embedded runtime or copying upstream tools. Its HTTP `/alerts` endpoint queues alerts and does not return an investigation, so it is unsuitable as a synchronous backend.

OpenSRE supplies investigation and configured tools; this project supplies a small HTTP entry point and explicit backend/status reporting. The backend is selected per request. It never invokes shell execution or grants tools through `--allowed-tool` or approval bypass. OpenSRE's own read-only declarations and configured credentials are the permission boundary; run it with read-only cloud/observability credentials in an isolated service account. Prompt instructions alone cannot enforce permissions.

OpenSRE narrative is exposed as `summary`; structured hypotheses remain empty because its CLI response does not guarantee this project's hypothesis schema. Do not fabricate confidence scores or treat a successful agent turn as proof of sufficient evidence. Questions and denied tools are returned, with `safe_to_continue=false` for incomplete runs. Ephemeral requests deliberately have no resume support: supply missing context in a new request or use OpenSRE's interactive workflow for approval/resume. No production tool grants are exposed via HTTP.

## Changes and limits

- Opt-in OpenSRE backend with timeout, explicit errors and no mock fallback.
- Demo evidence is labeled; existing illustrative hypotheses retained for dashboard compatibility.
- Azure uses the exact Responses target URI with `api-key`, deployment name, bounded output and no temperature parameter; actual LLM narrative now reaches the API.
- Secret env files and Python/test artifacts are ignored.
- Contract tests use mocked subprocess and HTTP calls. No live provider or production tool execution was performed.

For production, add authentication/rate limits, job queue and concurrency limits, bounded transcript handling, deployment isolation, audited connector permissions, evidence provenance, and evaluation on real incidents. Current synchronous calls may occupy a worker for up to the configured timeout. The optional LLM still analyzes mock evidence on the demo backend; it does not turn that backend into real telemetry. OpenSRE requires its own model authentication; this application's Azure settings are not automatically forwarded into OpenSRE configuration.

Sources: [OpenSRE headless CLI](https://github.com/Tracer-Cloud/opensre/blob/288a82456af27ce75487527b2b21c7ab1cbf5d6b/docs/guides/headless-cli.mdx), [HTTP API](https://github.com/Tracer-Cloud/opensre/blob/288a82456af27ce75487527b2b21c7ab1cbf5d6b/docs/guides/api.mdx), [Azure Responses](https://learn.microsoft.com/en-us/azure/ai-services/openai/quickstart?pivots=rest-api).
