from app.agent.orchestrator import Orchestrator
from app.agent.schemas import InvestigationRequest, InvestigationResponse


class IncidentController:
    def __init__(self) -> None:
        self.orchestrator = Orchestrator()

    def investigate(self, request: InvestigationRequest) -> InvestigationResponse:
        return self.orchestrator.investigate(request.service, request.description)
