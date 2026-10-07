# Model and provider configuration

[Project overview](../README.md) · [OpenSRE integration](OPENSRE_INTEGRATION.md) ·
[Grafana/Prometheus quickstart](GRAFANA_PROMETHEUS_QUICKSTART.md)

There are two independent model paths: this project's optional demo summary,
and the model provider used by OpenSRE. Configuring one does not automatically
configure the other.

## Optional Azure summary for the demo backend

Copy `.env.example` to an ignored `.env` if you do not already have one. Set:

```dotenv
LLM_PROVIDER=azure
LLM_MODEL=YOUR_DEPLOYMENT_NAME
AZURE_OPENAI_RESPONSES_URL=https://YOUR_RESOURCE.cognitiveservices.azure.com/openai/responses?api-version=2025-04-01-preview
AZURE_OPENAI_API_KEY=
```

Save the key locally or inject it through a secret manager. Start the API with
`uvicorn app.main:app --env-file .env`; plain `uvicorn` does not load the file.

The wrapper uses the full Responses target URI with `api-key` authentication.
The model field is the deployment name. Azure calls omit temperature, cap output
at 2,000 tokens, and request no response storage. Azure uses the existing `httpx`
dependency. Missing credentials or provider errors fall back to a labeled demo
summary. That fallback is separate from the OpenSRE backend, which does not
substitute demo evidence when a run fails.

This model sees a compact sample of the mock evidence. It does not turn the demo
collectors into live telemetry. `USE_REASONING_CACHE` and `MAX_INPUT_TOKENS` are
reserved settings; a reasoning cache and exact input token enforcement are not
implemented. Evidence is clipped by field.

## Optional OpenAI summary for the demo backend

Install the SDK extra:

```bash
pip install -e '.[llm]'
```

Set `LLM_PROVIDER=openai`, `LLM_MODEL`, and a locally stored `OPENAI_API_KEY`.
`OPENAI_BASE_URL` is available for an explicitly configured compatible endpoint.

## OpenSRE with Azure

Install OpenSRE on the API host. Its headless CLI supports your own model
provider without an OpenSRE account. For the Azure path:

```dotenv
OPENSRE_LLM_PROVIDER=azure-openai
OPENSRE_LLM_TRANSPORT=litellm
AZURE_OPENAI_BASE_URL=https://YOUR_RESOURCE.cognitiveservices.azure.com
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_API_VERSION=2025-04-01-preview
AZURE_OPENAI_REASONING_MODEL=YOUR_DEPLOYMENT_NAME
AZURE_OPENAI_TOOLCALL_MODEL=YOUR_DEPLOYMENT_NAME
AZURE_OPENAI_CLASSIFICATION_MODEL=YOUR_DEPLOYMENT_NAME
```

The application calls its own provider `azure`; OpenSRE uses `azure-openai`.
`OPENSRE_LLM_PROVIDER` overrides the child process's provider so both paths can
share the locally saved Azure key without a provider-name conflict.

| Setting | Default | Purpose |
| --- | --- | --- |
| `OPENSRE_BINARY` | `opensre` | Executable name or absolute path |
| `OPENSRE_TIMEOUT_SECONDS` | `120` | Process timeout; the recorded proof used `240` |
| `OPENSRE_LLM_PROVIDER` | Unset | Optional provider override for the OpenSRE child process |

The adapter disables OpenSRE telemetry and prompt logging for its calls. It does
not grant additional tools or bypass approvals. Tool declarations, configured
credentials, and runtime permissions remain the access boundary.

The supplied Azure `gpt-5.4` deployment and local OpenSRE model connection passed
live checks. See the [verification history](LIVE_VERIFICATION.md) and
[recorded overload case](case-studies/checkout-overload/README.md) for the scope.
Other resources, deployments, and API versions need their own validation.
