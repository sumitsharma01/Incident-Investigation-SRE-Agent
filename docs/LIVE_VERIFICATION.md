# Live verification — 7 October 2026

Verified locally against Azure deployment `gpt-5.4` and OpenSRE binary `v2026.10.6`.
No OpenSRE hosted account was used. No production observability tools were queried.

| Check | Result |
| --- | --- |
| Azure Responses target with API version `2025-04-01-preview` | HTTP 200, completed response with output text |
| OpenSRE headless CLI using Azure OpenAI | Exit 0, status `success`, response `OK` |
| Agent API, demo backend with Azure reasoning | HTTP 200, status `success`, `llm_mode=azure`, summary returned |
| Agent API, OpenSRE backend | HTTP 200, status `success`, investigation narrative returned |

The OpenSRE API check reported that no diagnostic tools were configured. Model
connectivity and the adapter work; a real incident investigation still needs
configured observability sources and a separate end-to-end check.

## Local configuration

The application uses `LLM_PROVIDER=azure`; OpenSRE uses `azure-openai`.
Set `OPENSRE_LLM_PROVIDER=azure-openai` so the adapter overrides only the child
process's provider. Set `OPENSRE_LLM_TRANSPORT=litellm`, the Azure resource URL
in `AZURE_OPENAI_BASE_URL`, API version in `AZURE_OPENAI_API_VERSION`, and
deployment name in each `AZURE_OPENAI_*_MODEL` setting. See `.env.example`.
Both paths can use the locally saved `AZURE_OPENAI_API_KEY`. The ignored `.env`
contains the configured values; no credential is committed.

OpenSRE sign-in is optional for this headless provider configuration. The
installed binary, model credentials and observability setup remain local;
cloning the repository does not reproduce those credentials or installations.
