from dataclasses import dataclass, field

from app.tools.deployments import get_recent_deployments
from app.tools.incidents import search_similar_incidents
from app.tools.logs import get_logs
from app.tools.metrics import get_metrics
from app.tools.traces import get_traces


@dataclass
class IncidentContext:
    service: str
    description: str
    logs: list[dict] = field(default_factory=list)
    metrics: list[dict] = field(default_factory=list)
    traces: list[dict] = field(default_factory=list)
    deployments: list[dict] = field(default_factory=list)
    incidents: list[dict] = field(default_factory=list)


def aggregate_context(service: str, description: str) -> IncidentContext:
    return IncidentContext(
        service=service,
        description=description,
        logs=get_logs(service, "1h"),
        metrics=get_metrics(service),
        traces=get_traces(service),
        deployments=get_recent_deployments(service),
        incidents=search_similar_incidents(description),
    )
