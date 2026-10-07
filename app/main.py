from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.workspace.routes import router as workspace_router
from app.workspace.store import Store
from app.workspace.tenancy import TenantMiddleware, profiles

from app import __version__
from app.api.routes import router

@asynccontextmanager
async def lifespan(app):
    profiles()
    Store().interrupt_running()
    yield


app = FastAPI(lifespan=lifespan, title="Incident Investigation SRE Agent", version=__version__)
app.add_middleware(TenantMiddleware)
app.include_router(router)
app.include_router(workspace_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "incident-investigation-sre-agent", "version": __version__}
