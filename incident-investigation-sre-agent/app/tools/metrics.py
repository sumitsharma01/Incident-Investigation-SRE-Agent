def get_metrics(service: str) -> list[dict]:
    return [
        {"name": "p95_latency_ms", "value": 820, "service": service},
        {"name": "error_rate", "value": 0.03, "service": service},
        {"name": "requests_per_min", "value": 4500, "service": service},
    ]
