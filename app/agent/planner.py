from app.agent.prompts import build_prompt


class Planner:
    """Simple planner that outlines the investigation path without external LLM dependencies."""

    def plan(self, service: str, description: str, backend: str = "demo") -> list[str]:
        if backend == "opensre":
            return [
                "Query configured read-only observability tools for the stated service and time window",
                "Compare incoming traffic, tail latency, errors and saturation signals",
                "Separate observed signals from causes that still need logs, traces or deployment evidence",
                "Return evidence, uncertainties and proposed checks for human review",
            ]
        prompt = build_prompt(service, description)
        return [
            "Collect latest logs for the service",
            "Collect metrics and trace summaries",
            "Inspect recent deployments",
            "Search for similar incidents",
            "Rank hypotheses using evidence and confidence",
            prompt,
        ]
