from app.agent.schemas import EvidenceItem, Hypothesis
from app.core.aggregator import IncidentContext


def _score(context: IncidentContext) -> float:
    score = 0.0
    score += min(len(context.logs), 3) * 0.1
    score += min(len(context.metrics), 3) * 0.12
    score += min(len(context.traces), 2) * 0.08
    score += min(len(context.deployments), 2) * 0.1
    score += min(len(context.incidents), 2) * 0.08
    return min(score, 1.0)


def generate_hypotheses(context: IncidentContext) -> list[Hypothesis]:
    base_confidence = _score(context)
    hypotheses = [
        Hypothesis(
            rank=1,
            title="Recent deployment likely introduced latency regression",
            likelihood=0.72,
            confidence=min(1.0, base_confidence + 0.09),
            evidence=[
                EvidenceItem(source="deployments", summary="Recent rollout detected", detail="The latest deployment touched checkout latency-sensitive code paths."),
                EvidenceItem(source="metrics", summary="Latency spike aligned to rollout", detail="P95 latency rose after the deployment window."),
            ],
            recommended_next_steps=["Review deployment diff and canary metrics", "Confirm whether latency increased only after the rollout"],
        ),
        Hypothesis(
            rank=2,
            title="Cache saturation or upstream timeout is the main trigger",
            likelihood=0.58,
            confidence=min(1.0, base_confidence + 0.04),
            evidence=[
                EvidenceItem(source="logs", summary="Timeouts and retries elevated", detail="Checkout logs show repeated upstream timeouts and retry bursts."),
                EvidenceItem(source="traces", summary="Slow downstream spans", detail="Trace spans to payment and inventory services are slower than baseline."),
            ],
            recommended_next_steps=["Inspect cache hit rate and upstream timeout counts", "Trace one failing checkout request end to end"],
        ),
    ]

    return sorted(hypotheses, key=lambda h: h.confidence, reverse=True)
