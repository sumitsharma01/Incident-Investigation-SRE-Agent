from app.agent.llm_reasoner import LLMReasoner


def test_llm_reasoner_defaults_to_mock_mode():
    reasoner = LLMReasoner()

    response = reasoner.summarize({"service": "checkout"})

    assert response["mode"] == "mock"
    assert "cost_controls" in response


def test_azure_exact_responses_uri_and_model_output(monkeypatch):
    from app.config import settings
    import httpx
    monkeypatch.setattr(settings, 'llm_provider', 'azure')
    monkeypatch.setattr(settings, 'llm_api_key', 'test-only-not-a-key')
    monkeypatch.setattr(settings, 'llm_model', 'gpt-5.4')
    target = 'https://example.cognitiveservices.azure.com/openai/responses?api-version=2025-04-01-preview'
    monkeypatch.setattr(settings, 'azure_responses_url', target)
    def post(url, **kwargs):
        assert url == target
        assert kwargs['headers'] == {'api-key': 'test-only-not-a-key'}
        assert kwargs['json']['model'] == 'gpt-5.4'
        assert 'temperature' not in kwargs['json']
        assert kwargs['json']['store'] is False
        return httpx.Response(200, json={'output':[{'content':[{'type':'output_text','text':'Review the actual evidence'}]}]}, request=httpx.Request('POST',url))
    monkeypatch.setattr(httpx, 'post', post)
    result = LLMReasoner().summarize({'service':'checkout'})
    assert result['mode'] == 'azure'
    assert result['summary'] == 'Review the actual evidence'


def test_azure_error_does_not_expose_credentials(monkeypatch):
    from app.config import settings
    import httpx
    monkeypatch.setattr(settings, 'llm_provider', 'azure')
    monkeypatch.setattr(settings, 'llm_api_key', 'test-only-not-a-key')
    monkeypatch.setattr(settings, 'azure_responses_url', 'https://example.com/openai/responses')
    def post(*a, **k):
        raise RuntimeError('secret error')
    monkeypatch.setattr(httpx, 'post', post)
    result = LLMReasoner().summarize({})
    assert result['mode'] == 'mock'
    assert 'secret' not in result['summary']
