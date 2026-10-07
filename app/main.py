from fastapi import FastAPI

from app import __version__
from app.api.routes import router

app = FastAPI(title="Incident Investigation SRE Agent", version=__version__)
app.include_router(router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "incident-investigation-sre-agent", "version": __version__}
