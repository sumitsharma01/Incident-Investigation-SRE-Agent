# Changelog

## 0.4.0 — 2026-10-07

- Integrate the LibreSRE symbol in the README, workspace, favicon and project graphics.

- Release LibreSRE under the MIT License, preserving third-party notices.

- Adopt the LibreSRE name; retain existing repository, package and API identifiers.

- Persist investigation requests, results and interrupted-run status in SQLite.
- Add a local incident workspace with retained metric queries and recovery policies.
- Reject recovery claims when traffic drops or observation windows overlap.
- Add a real HTTP workload and manual worker-capacity recovery lab.
- Add optional tenant-scoped access and isolated OpenSRE environment profiles.
- Keep the OpenSRE investigation runtime and workspace responsibilities distinct.

## 0.3.0 — unpublished

Updated 7 October 2026. No package publication or release tag has been created.

- Added a recorded checkout overload case with baseline, incident and modeled recovery.
- Retained actual API/OpenSRE responses, the initial failed attempt and the successful narrowed retry.
- Added backend-aware plans and request-local review notes to investigation responses.
- Added a case-study dashboard with evidence and API navigation.
- Added architecture graphics for production placement, investigation flow and the recorded proof, with editable SVGs and attributed brand icons.
- Added real Grafana/Prometheus/agent screenshots, proposed fixes and replay steps.
- Added scenario, orchestration and output-escaping checks; 28 tests pass.

## 0.2.0 — previous code version

Updated 7 October 2026. No release tag or package publication has been created.

### Repository and dashboard update

- Moved the application into the repository root; no nested project folder is needed.
- Added an OpenSRE integration guide and a separate dashboard explaining the request flow, new behavior and setup requirements.
- Refreshed screenshots for the demo and integration guide.

### Added

- Optional OpenSRE backend selected through `backend: opensre` in investigation requests.
- Status, questions and denied tools in API responses, with explicit failures and no demo fallback for OpenSRE runs.
- Azure Foundry Responses support using the full target URI and deployment name.
- Repository assessment with upstream source commit and production limitations.
- Browser screenshots of desktop and mobile demo layouts, plus a reproducible capture script.

### Changed

- API responses now include the model's summary rather than only its provider mode.
- Demo responses and dashboard identify synthetic evidence.
- Package, API metadata, health response and dashboard report version 0.2.0.
- README documents current behavior, configuration and the limits of test coverage.
- Secret environment files and Python/test artifacts are ignored.

### Verification

19 tests passed with mocked OpenSRE and Azure calls. Desktop and mobile screenshots
were captured from the rendered dashboard. Live OpenSRE integrations and the
Azure deployment remain unverified.

## 0.1.0 — original baseline

Version declared by the repository before the integration work. No release date
is inferred from that declaration.

- FastAPI investigation endpoint and sample observability collectors.
- Fixed demo hypotheses, example dashboard and optional model wrapper.

Baseline reviewed: `be3bbb626f58b85ee38bf58940f8503e62dd32b4`.

### Live connectivity check — 7 October 2026

- Verified Azure Responses and OpenSRE headless Azure calls, plus both agent API paths.
- Added `OPENSRE_LLM_PROVIDER` to separate child-process provider configuration.
- Production observability access remains unverified; no diagnostic tools were configured.

### Grafana / Prometheus lab

- Added a local Docker Compose stack, provisioned dashboard and sample metrics.
- Added read-only datasource verification and local Viewer-token setup.
- Added three connection-check tests (22 tests total).

### Live lab screenshots and quickstart

- Captured populated Grafana and Prometheus pages after Docker recovery.
- Added an integration walkthrough and a browser capture script that requires actual samples.
- Fixed repeated local token setup by generating unique token names.

### Peak traffic demo

- Added a baseline/peak/recovery scenario with accumulating synthetic counters.
- Added a peak dashboard with current and maximum request-rate cards.
- Added live Grafana/Prometheus peak screenshots and captured observations.
- Added two scenario tests (24 tests total).
