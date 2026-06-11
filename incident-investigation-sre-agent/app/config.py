import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Incident Investigation SRE Agent"
    human_in_the_loop: bool = True
    max_hypotheses: int = 5
    confidence_threshold: float = 0.65
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    llm_api_key: str | None = os.getenv("OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
    llm_base_url: str | None = os.getenv("OPENAI_BASE_URL") or os.getenv("AZURE_OPENAI_ENDPOINT")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    use_reasoning_cache: bool = os.getenv("USE_REASONING_CACHE", "true").lower() == "true"
    max_input_tokens: int = int(os.getenv("MAX_INPUT_TOKENS", "1200"))


settings = Settings()
