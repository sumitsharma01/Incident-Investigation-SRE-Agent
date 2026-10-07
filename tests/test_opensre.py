import json
import subprocess
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.agent.opensre import OpenSREBackend
from app.main import app


@pytest.mark.parametrize('code,status,wire_status', [(0,'success','success'), (3,'approval_required','approval_denied'), (4,'needs_input','needs_input'), (1,'error','error')])
def test_cli_result_and_no_tool_authorization(monkeypatch, code, status, wire_status):
    monkeypatch.setenv("OPENSRE_LLM_PROVIDER", "azure-openai")
    def run(argv, **kwargs):
        assert argv[1:] == ['--json', 'ask', '--ephemeral', '-']
        assert 'checkout' in kwargs['input']
        assert kwargs['env']['LLM_PROVIDER'] == 'azure-openai'
        assert kwargs['env']['OPENSRE_PROMPT_LOG_DISABLED'] == '1'
        return SimpleNamespace(returncode=code, stdout=json.dumps({'status':wire_status,'response':'Observed latency','questions':[],'denied_tools':[]}))
    monkeypatch.setattr(subprocess, 'run', run)
    result = OpenSREBackend().investigate('checkout', '--dangerously-bypass-approvals')
    assert result.status == status
    assert result.hypotheses == []
    assert result.safe_to_continue == (code == 0)


@pytest.mark.parametrize('failure', [FileNotFoundError(), subprocess.TimeoutExpired('opensre', 1)])
def test_unavailable_does_not_fabricate_evidence(monkeypatch, failure):
    def run(*args, **kwargs):
        raise failure
    monkeypatch.setattr(subprocess, 'run', run)
    result = OpenSREBackend().investigate('inventory', 'errors')
    assert result.status == 'error'
    assert result.hypotheses == []
    assert not result.safe_to_continue


def test_malformed_output(monkeypatch):
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: SimpleNamespace(returncode=0, stdout='not JSON secret'))
    result = OpenSREBackend().investigate('x', 'errors')
    assert result.status == 'error'
    assert 'secret' not in result.summary


def test_api_opensre_and_validation(monkeypatch):
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: SimpleNamespace(returncode=0, stdout='{"status":"success","response":"Evidence unavailable"}'))
    client = TestClient(app)
    response = client.post('/investigate', json={'service':'inventory','description':'errors','backend':'opensre'})
    assert response.json()['backend'] == 'opensre'
    assert response.json()['hypotheses'] == []
    assert client.post('/investigate', json={'service':' ','description':'errors'}).status_code == 422
    assert client.post('/investigate', json={'service':'x','description':'errors','backend':'invalid'}).status_code == 422
