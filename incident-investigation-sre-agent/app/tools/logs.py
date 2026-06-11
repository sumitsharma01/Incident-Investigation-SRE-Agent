def get_logs(service: str, time_window: str) -> list[dict]:
    return [
        {"timestamp": "2026-06-11T10:05:00Z", "level": "warn", "message": f"{service} latency elevated in checkout path"},
        {"timestamp": "2026-06-11T10:10:00Z", "level": "error", "message": "upstream timeout retry burst on cart service"},
    ]
