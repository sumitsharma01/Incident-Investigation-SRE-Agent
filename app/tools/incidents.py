def search_similar_incidents(query: str) -> list[dict]:
    return [
        {"title": "checkout latency spike after cache config change", "match": 0.87, "summary": "Similar incident reported two weeks ago."},
        {"title": "inventory timeout cascade in checkout path", "match": 0.74, "summary": "Upstream delay caused retries and elevated p95 latency."},
    ]
