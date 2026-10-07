from fastapi import APIRouter

from app.agent.schemas import InvestigationRequest, InvestigationResponse
from app.api.incident_controller import IncidentController

router = APIRouter()
controller = IncidentController()


@router.post("/investigate", response_model=InvestigationResponse)
def investigate(request: InvestigationRequest) -> InvestigationResponse:
    return controller.investigate(request)
