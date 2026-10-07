def get_traces(service: str) -> list[dict]:
    return [
        {"trace_id": "trace-001", "service": service, "status": "slow", "duration_ms": 980},
        {"trace_id": "trace-002", "service": service, "status": "timeout", "duration_ms": 1450},
    ]
