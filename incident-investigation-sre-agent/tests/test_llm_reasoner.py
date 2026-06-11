from app.agent.llm_reasoner import LLMReasoner


def test_llm_reasoner_defaults_to_mock_mode():
    reasoner = LLMReasoner()

    response = reasoner.summarize({"service": "checkout"})

    assert response["mode"] == "mock"
    assert "cost_controls" in response
