import json
from urllib.parse import urlsplit

import httpx

from app.config import settings


class LLMReasoner:
    """Optional LLM-backed reasoning wrapper with compact prompt and token-budget controls."""

    def __init__(self) -> None:
        self.enabled = settings.llm_provider not in ("mock", "", None)
        self.provider = settings.llm_provider
        self.model = settings.llm_model

    def _trim_text(self, text: str, max_chars: int) -> str:
        return text if len(text) <= max_chars else text[:max_chars] + "..."

    def _compact_context(self, context: dict) -> dict:
        compact = {
            "service": context.get("service", "unknown"),
            "description": self._trim_text(str(context.get("description", "")), 220),
            "logs": self._trim_text(json.dumps(context.get("context", {}).logs[:3] if hasattr(context.get("context"), "logs") else []), 400),
            "metrics": self._trim_text(json.dumps(context.get("context", {}).metrics[:3] if hasattr(context.get("context"), "metrics") else []), 400),
            "traces": self._trim_text(json.dumps(context.get("context", {}).traces[:2] if hasattr(context.get("context"), "traces") else []), 400),
            "deployments": self._trim_text(json.dumps(context.get("context", {}).deployments[:2] if hasattr(context.get("context"), "deployments") else []), 300),
            "incidents": self._trim_text(json.dumps(context.get("context", {}).incidents[:2] if hasattr(context.get("context"), "incidents") else []), 300),
        }
        return compact

    def _prompt(self, compact_context: dict) -> str:
        return (
            "You are an evidence-based SRE incident assistant. "
            "Provide 3 short hypotheses and safe debugging steps without remediation. "
            "Use only the compact evidence provided below. "
            f"Context: {json.dumps(compact_context, separators=(',', ':'))}"
        )

    def summarize(self, context: dict) -> dict:
        compact_context = self._compact_context(context)

        if not self.enabled or not settings.llm_api_key:
            return {
                "mode": "mock",
                "summary": "Demo mode: synthetic evidence and fixed illustrative hypotheses; LLM integration is disabled.",
                "cost_controls": [
                    "Use compact model names",
                    "Limit input tokens to 1200",
                    "Compact evidence before calls",
                    "Prefer mock mode for demos",
                ],
                "compact_context": compact_context,
            }

        try:
            if self.provider == "azure":
                url = settings.azure_responses_url
                if not url:
                    raise ValueError("AZURE_OPENAI_RESPONSES_URL is required")
                parsed = urlsplit(url)
                if parsed.scheme != "https" or parsed.username or parsed.password or parsed.fragment:
                    raise ValueError("Azure URL must be HTTPS")
                payload = {"model": self.model, "input": self._prompt(compact_context),
                           "max_output_tokens": 2000, "store": False}
                # GPT-5 reasoning deployments do not accept the legacy temperature setting.
                response = httpx.post(url, headers={"api-key": settings.llm_api_key},
                                      json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()
                text = "\n".join(part["text"] for item in data.get("output", [])
                                 for part in item.get("content", [])
                                 if part.get("type") == "output_text")
                if not text:
                    raise ValueError("No model text returned")
                return {"mode": "azure", "summary": text, "compact_context": compact_context,
                        "cost_controls": ["Bounded evidence", "Bounded output", "No response storage"]}
            from openai import OpenAI

            client_kwargs = {"api_key": settings.llm_api_key}
            if settings.llm_base_url:
                client_kwargs["base_url"] = settings.llm_base_url
            client = OpenAI(**client_kwargs)
            response = client.responses.create(
                model=settings.llm_model,
                input=self._prompt(compact_context),
                temperature=settings.llm_temperature,
            )
            text = getattr(response, "output_text", "") or ""
            return {
                "mode": self.provider,
                "summary": text if text else "LLM response generated successfully.",
                "cost_controls": [
                    "Use gpt-4o-mini or Azure Foundry compact models",
                    "Reduce token count by summarizing evidence before prompt assembly",
                    "Use bounded evidence summaries",
                    "Clip the context to the configured token budget",
                ],
                "compact_context": compact_context,
            }
        except Exception:
            return {
                "mode": "mock",
                "summary": "LLM call failed; falling back to deterministic reasoning with synthetic demo evidence.",
                "cost_controls": [
                    "Use compact model names",
                    "Limit input tokens to 1200",
                    "Fallback safely to mock mode on provider errors",
                ],
                "compact_context": compact_context,
            }
