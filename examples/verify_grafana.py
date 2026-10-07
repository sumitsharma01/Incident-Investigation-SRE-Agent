"""Check Grafana and its Prometheus datasource without invoking a model."""
import json
import os
import ssl
from pathlib import Path
from urllib.parse import quote, urlsplit

import httpx
from dotenv import load_dotenv


def verify(client: httpx.Client, datasource_uid: str = "") -> dict:
    response = client.get("api/datasources")
    response.raise_for_status()
    datasources = response.json()
    candidates = [d for d in datasources if d.get("type") == "prometheus"]
    if datasource_uid:
        candidates = [d for d in candidates if d.get("uid") == datasource_uid]
    if not candidates:
        return {"status": "error", "reason": "No matching Prometheus datasource is readable."}
    if len(candidates) > 1:
        return {"status": "needs_input", "reason": "Set GRAFANA_MIMIR_DATASOURCE_UID to select a datasource.",
                "datasources": [{"name": d.get("name"), "uid": d.get("uid")} for d in candidates]}
    uid = candidates[0]["uid"]
    response = client.get(f"api/datasources/proxy/uid/{quote(uid, safe='')}/api/v1/query", params={"query": "up"})
    response.raise_for_status()
    data = response.json()
    if data.get("status") != "success":
        return {"status": "error", "reason": "Prometheus rejected the query."}
    results = data.get("data", {}).get("result", [])
    return {"status": "success", "datasource_uid": uid, "series_count": len(results),
            "note": "Grafana authentication and Prometheus query succeeded." if results else
                    "Query succeeded, but returned no up series; investigate scrape configuration."}


def main() -> int:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    url = os.getenv("GRAFANA_INSTANCE_URL", "").strip()
    token = os.getenv("GRAFANA_READ_TOKEN", "").strip()
    if not url or not token:
        print(json.dumps({"status": "not_configured", "reason": "Set GRAFANA_INSTANCE_URL and GRAFANA_READ_TOKEN in the ignored .env."}))
        return 2
    parsed = urlsplit(url)
    if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.scheme not in {"https", "http"}:
        print(json.dumps({"status": "error", "reason": "Use a Grafana base URL without embedded credentials or query parameters."}))
        return 1
    if parsed.scheme == "http" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        print(json.dumps({"status": "error", "reason": "Use HTTPS for remote Grafana."}))
        return 1
    try:
        ca = os.getenv("GRAFANA_CA_BUNDLE", "")
        tls = ssl.create_default_context(cafile=ca) if ca else True
        with httpx.Client(base_url=url.rstrip('/')+'/', headers={"Authorization": f"Bearer {token}"},
                          verify=tls, timeout=20, follow_redirects=False) as client:
            result = verify(client, os.getenv("GRAFANA_MIMIR_DATASOURCE_UID", ""))
        print(json.dumps(result))
        return 0 if result["status"] == "success" else 1
    except httpx.HTTPStatusError as error:
        print(json.dumps({"status": "error", "http_status": error.response.status_code,
                          "reason": "Check token permissions, datasource access and proxy configuration."}))
    except (httpx.HTTPError, ValueError, KeyError, OSError):
        print(json.dumps({"status": "error", "reason": "Connection, certificate or response validation failed."}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
