from fastapi import APIRouter

from app.agent.schemas import InvestigationRequest, InvestigationResponse
from app.api.incident_controller import IncidentController
from app.workspace.routes import run_incident

router = APIRouter()
controller = IncidentController()


@router.post("/investigate", response_model=InvestigationResponse)
def investigate(request: InvestigationRequest) -> InvestigationResponse:
    return run_incident(request, controller)
