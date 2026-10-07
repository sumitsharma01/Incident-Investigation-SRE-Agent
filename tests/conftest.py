import pytest


@pytest.fixture(autouse=True)
def isolate_workspace_database(tmp_path, monkeypatch):
    """API tests must never write to an operator's persistent incident workspace."""
    monkeypatch.setenv('SRE_WORKSPACE_DB', str(tmp_path/'test-workspace.sqlite3'))
    monkeypatch.delenv('SRE_TENANTS_FILE', raising=False)
