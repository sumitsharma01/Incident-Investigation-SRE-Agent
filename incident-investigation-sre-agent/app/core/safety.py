from app.core.aggregator import IncidentContext


class SafetyGuard:
    """Enforces human-in-the-loop and non-destructive investigation behavior."""

    def validate_request(self, service: str, description: str) -> None:
        if not service or not description:
            raise ValueError("service and description are required")

    def allow_investigation(self, context: IncidentContext) -> bool:
        return bool(context.service and context.description)
