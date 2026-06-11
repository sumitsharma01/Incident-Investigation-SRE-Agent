from app.core.aggregator import aggregate_context
from app.core.reasoning import generate_hypotheses


def test_generate_hypotheses_returns_ranked_results():
    context = aggregate_context("checkout", "Checkout service latency increased significantly")

    hypotheses = generate_hypotheses(context)

    assert len(hypotheses) >= 1
    assert hypotheses[0].rank == 1
    assert hypotheses[0].confidence >= 0.0
