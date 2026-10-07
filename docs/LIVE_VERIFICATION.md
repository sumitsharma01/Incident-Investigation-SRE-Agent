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

## Grafana / Prometheus lab follow-up

A loopback-only Grafana/Prometheus stack was added on 7 October 2026. Its
first Viewer-token query returned two Prometheus `up` series, but subsequent
Docker storage I/O errors, Grafana session failures and token HTTP 401 responses
prevented a reliable end-to-end OpenSRE metrics investigation. Model-only
verification above still stands; observability integration is not yet verified.
See [lab setup and diagnosis](GRAFANA_PROMETHEUS.md).

### Lab recovery and screenshot verification

An approved Docker Desktop restart restored the lab. Renewed Viewer-token
access returned two `up` series. Browser screenshots captured and visually
verified the Grafana panels and Prometheus tables, including scrape health 1,
request rate 47 and latency 0.42 seconds. Synthetic error percentage was about
4.26%. No existing Docker volumes were deleted. OpenSRE's complete metrics
investigation is assessed separately from these direct datasource checks.

### OpenSRE metrics investigation after recovery

The retried `/investigate` call completed with HTTP 200, `status=success` and
no denied tools. OpenSRE used the read-only Grafana metrics tool and reported
failed requests at `4.25531914893617%`. Its response also recorded initial
service-filter parameter errors followed by successful query results. The
returned report is saved in [grafana-demo-investigation.json](grafana-demo-investigation.json).
This verifies the local synthetic lab integration; production datasource
permissions and real incident accuracy have not been evaluated.
