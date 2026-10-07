from app.agent.prompts import build_prompt


class Planner:
    """Simple planner that outlines the investigation path without external LLM dependencies."""

    def plan(self, service: str, description: str) -> list[str]:
        prompt = build_prompt(service, description)
        return [
            "Collect latest logs for the service",
            "Collect metrics and trace summaries",
            "Inspect recent deployments",
            "Search for similar incidents",
            "Rank hypotheses using evidence and confidence",
            prompt,
        ]
