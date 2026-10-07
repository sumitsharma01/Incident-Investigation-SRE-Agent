# Changelog

## 0.2.0 — unpublished

Updated 7 October 2026. Code version on `codex/opensre-integration`; no release
tag or package publication has been created.

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

18 tests passed with mocked OpenSRE and Azure calls. Desktop and mobile screenshots
were captured from the rendered dashboard. Live OpenSRE integrations and the
Azure deployment remain unverified.

## 0.1.0 — original baseline

Version declared by the repository before the integration work. No release date
is inferred from that declaration.

- FastAPI investigation endpoint and sample observability collectors.
- Fixed demo hypotheses, example dashboard and optional model wrapper.

Baseline reviewed: `be3bbb626f58b85ee38bf58940f8503e62dd32b4`.
