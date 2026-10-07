from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict

from app.agent.schemas import InvestigationRequest
from app.api.incident_controller import IncidentController
from app.workspace.metrics import MetricError, capture, compare
from app.workspace.store import Store, now
from app.workspace.tenancy import allowed_service, profile

router = APIRouter()


class ObservationRequest(BaseModel):
    label: Literal['before', 'after']


class RecoveryRequest(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    before_id: str
    after_id: str
    intervention: str = Field(min_length=3, max_length=2000, pattern=r".*\S.*")
    max_p95_seconds: float = Field(default=.5, gt=0)
    max_error_ratio: float = Field(default=.01, ge=0, le=1)
    max_queue_depth: float = Field(default=20, ge=0)
    minimum_traffic_rps: float = Field(default=1, gt=0)
    traffic_retention: float = Field(default=.8, gt=0, le=1)


def incident_or_404(identifier):
    try:
        return Store().get(identifier, 'incident')
    except KeyError:
        raise HTTPException(404, 'Incident not found') from None


def run_incident(request, controller=None):
    allowed_service(request.service)
    if profile.get() is not None and request.backend == 'opensre' and not profile.get().get('opensre_home'):
        raise HTTPException(503, 'This tenant needs an isolated OpenSRE home before live investigations')
    store = Store()
    record = store.create('incident', {'request': request.model_dump(), 'state': 'running', 'result': None})
    try:
        result = (controller or IncidentController()).investigate(request)
        result.incident_id = record['id']
        record.update(state=result.status, result=result.model_dump(), finished_at=now())
        store.update(record['id'], record)
        return result
    except Exception:
        record.update(state='error', finished_at=now(), error='Investigation failed; provider details withheld.')
        store.update(record['id'], record)
        raise


@router.get('/incidents')
def list_incidents():
    return Store().list('incident')


@router.get('/incidents/{identifier}')
def get_incident(identifier: str):
    incident = incident_or_404(identifier)
    incident['observations'] = Store().list('observation', identifier)
    incident['verifications'] = Store().list('verification', identifier)
    return incident


@router.post('/incidents/{identifier}/observations', status_code=201)
def observe(identifier: str, request: ObservationRequest):
    incident = incident_or_404(identifier)
    try:
        observation = capture(incident['request']['service'], request.label)
    except MetricError as exc:
        raise HTTPException(502, str(exc)) from None
    return Store().create('observation', observation, identifier)


@router.post('/incidents/{identifier}/recovery', status_code=201)
def recovery(identifier: str, request: RecoveryRequest):
    incident_or_404(identifier)
    snapshots = {row['id']: row for row in Store().list('observation', identifier)}
    if request.before_id not in snapshots or request.after_id not in snapshots:
        raise HTTPException(404, 'Snapshot not found in this incident')
    before, after = snapshots[request.before_id], snapshots[request.after_id]
    if before['label'] != 'before' or after['label'] != 'after':
        raise HTTPException(422, 'Select before and after observations in that order')
    try:
        result = compare(before, after, request)
    except MetricError as exc:
        raise HTTPException(422, str(exc)) from None
    result.update(before_id=request.before_id, after_id=request.after_id, intervention=request.intervention,
                  intervention_source='operator supplied; not independently attested')
    return Store().create('verification', result, identifier)


@router.get('/workspace', include_in_schema=False)
def workspace():
    return FileResponse(Path(__file__).with_name('workspace.html'))
