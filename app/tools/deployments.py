def get_recent_deployments(service: str) -> list[dict]:
    return [
        {"version": "2026.06.11.1", "service": service, "rolled_out_at": "2026-06-11T09:45:00Z", "change": "cache config update"},
        {"version": "2026.06.11.0", "service": service, "rolled_out_at": "2026-06-11T08:30:00Z", "change": "latency optimization patch"},
    ]
