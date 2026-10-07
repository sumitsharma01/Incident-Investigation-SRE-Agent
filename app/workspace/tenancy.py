"""Optional API-key tenant identities; operator-owned profiles, never client IDs."""
from contextvars import ContextVar
import hmac
import json
import os
from pathlib import Path

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

current = ContextVar('workspace_tenant', default='local')
profile = ContextVar('workspace_profile', default=None)
MODEL_ENV = {'LLM_PROVIDER','LLM_MODEL','AZURE_OPENAI_API_KEY','AZURE_OPENAI_ENDPOINT',
             'AZURE_OPENAI_RESPONSES_URL','AZURE_OPENAI_API_VERSION','OPENAI_API_KEY','OPENAI_BASE_URL'}


def profiles():
    path = os.getenv('SRE_TENANTS_FILE')
    if not path:
        return {}
    data = json.loads(Path(path).read_text())
    if not isinstance(data, dict) or not data:
        raise ValueError('Tenant configuration must contain profiles')
    keys, homes = set(), set()
    for name, item in data.items():
        if name == 'local' or not isinstance(name,str) or not isinstance(item,dict):
            raise ValueError('Invalid tenant identity')
        key = item.get('api_key', '')
        if not isinstance(key,str) or len(key) < 32 or key in keys:
            raise ValueError('Tenant keys must be unique and at least 32 characters')
        keys.add(key)
        if not item.get('services') or not isinstance(item['services'],list) or any(not isinstance(s,str) or not s.strip() for s in item['services']):
            raise ValueError('Each tenant needs an allowed service list')
        home = item.get('opensre_home')
        if home:
            canonical = str(Path(home).resolve())
            if not Path(home).is_absolute() or any(Path(canonical).is_relative_to(Path(other)) or Path(other).is_relative_to(Path(canonical)) for other in homes):
                raise ValueError('OpenSRE homes must be unique absolute paths')
            homes.add(canonical)
        if not isinstance(item.get('model_env',{}),dict) or any(not isinstance(v,str) for v in item.get('model_env',{}).values()) or set(item.get('model_env',{})) - MODEL_ENV:
            raise ValueError('Unsupported tenant model environment variable')
    return data


def allowed_service(service):
    config = profile.get()
    if config is not None and service not in config['services']:
        raise HTTPException(403, 'Service is outside this tenant workspace')


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            tenants = profiles()
        except (ValueError,OSError):
            return JSONResponse({'detail':'Tenant configuration is invalid'},status_code=503)
        name, config = 'local', None
        if tenants and not request.url.path.startswith('/brand/') and request.url.path not in {'/health','/workspace','/docs','/openapi.json','/redoc'}:
            header=request.headers.get('authorization','')
            token=header[7:] if header.startswith('Bearer ') else ''
            for candidate, item in tenants.items():
                if hmac.compare_digest(token.encode(),item['api_key'].encode()):
                    name,config=candidate,item
                    break
            if config is None:
                return JSONResponse({'detail':'Valid tenant bearer key required'},status_code=401)
        identity=current.set(name);context=profile.set(config)
        try:
            return await call_next(request)
        finally:
            current.reset(identity);profile.reset(context)
