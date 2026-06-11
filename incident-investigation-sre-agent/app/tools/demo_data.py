def build_demo_context(service: str) -> dict:
    """Create a realistic demo observability context for testing the SRE agent."""
    error_budget_remaining_percent = 98.6
    sli = {
        "name": "Checkout request success and latency",
        "definition": "95% of checkout requests complete in < 500 ms with no 5xx errors",
        "current": "p95 latency 420 ms, 5xx rate 0.2%",
    }
    slo = {
        "name": "Availability SLO",
        "target": "99.9% monthly availability",
        "window": "30 days",
    }
    recommendations = [
        "Review recent deployment and canary changes before touching production traffic.",
        "Inspect retry amplification and upstream timeout rates to reduce toil during the incident.",
        "Prioritize a non-destructive investigation of cache hit rate and dependency latency.",
    ]

    return {
        "service": service,
        "sli": sli,
        "slo": slo,
        "error_budget_remaining_percent": error_budget_remaining_percent,
        "toil_risk": "medium",
        "logs": [
            {"timestamp": "2026-06-11T10:05:00Z", "level": "warn", "message": "checkout p95 latency breach detected"},
            {"timestamp": "2026-06-11T10:08:00Z", "level": "error", "message": "inventory timeout retry storm observed"},
        ],
        "metrics": [
            {"name": "p95_latency_ms", "value": 420, "service": service},
            {"name": "error_rate", "value": 0.002, "service": service},
            {"name": "requests_per_min", "value": 4500, "service": service},
        ],
        "traces": [
            {"trace_id": "demo-trace-001", "service": service, "status": "slow", "duration_ms": 460},
            {"trace_id": "demo-trace-002", "service": service, "status": "timeout", "duration_ms": 720},
        ],
        "deployments": [
            {"version": "demo-2026.06.11.1", "service": service, "rolled_out_at": "2026-06-11T09:45:00Z", "change": "cache config update"},
        ],
        "incidents": [
            {"title": "checkout latency regression after cache rollover", "match": 0.88, "summary": "Similar incident with elevated retries and dependency latency"},
        ],
        "recommendations": recommendations,
    }
