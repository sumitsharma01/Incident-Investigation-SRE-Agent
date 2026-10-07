"""Synthetic metrics only: no requests are sent to a real checkout service."""
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

started = time.monotonic()


def sample(elapsed: float, scenario: str = 'steady') -> tuple[float, float, float, int]:
    """Integrate counters across phases so changing rates never resets totals."""
    elapsed = max(elapsed, 0)
    if scenario != 'high-traffic':
        return elapsed * 45, elapsed * 2, 0.42, 0
    baseline = min(elapsed, 60)
    peak = min(max(elapsed - 60, 0), 90)
    recovery = max(elapsed - 150, 0)
    successes = baseline * 45 + peak * 1380 + recovery * 45
    errors = baseline * 2 + peak * 120 + recovery * 2
    active = 60 <= elapsed < 150
    return successes, errors, 1.8 if active else 0.42, int(active)


def incident_sample(elapsed: float) -> dict:
    """Overload scenario: peak traffic, rising latency and rejected requests."""
    elapsed = max(elapsed, 0)
    baseline = min(elapsed, 60)
    incident = min(max(elapsed - 60, 0), 240)
    recovery = max(elapsed - 300, 0)
    phase = 0 if elapsed < 60 else 1 if elapsed < 300 else 2
    return {
        'successes': baseline * 199 + incident * 1600 + recovery * 1990,
        'errors': baseline * 1 + incident * 400 + recovery * 10,
        'rejections': incident * 400,
        'all_p95': [0.42, 2.4, 0.45][phase],
        'success_p95': [0.42, 2.4, 0.45][phase],
        'queue_depth': [8, 850, 12][phase],
        'worker_utilization': [0.35, 0.95, 0.6][phase],
        'phase': phase,
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/metrics':
            self.send_error(404)
            return
        elapsed = time.monotonic() - started
        scenario = os.getenv('SRE_DEMO_TRAFFIC_SCENARIO', 'steady')
        incident = incident_sample(elapsed) if scenario == 'overload' else None
        successes, errors, latency, peak = sample(elapsed, scenario)
        if incident:
            successes, errors, latency, peak = incident['successes'], incident['errors'], incident['all_p95'], int(incident['phase'] == 1)
        body = f'''# HELP sre_demo_requests_total Synthetic checkout requests.
# TYPE sre_demo_requests_total counter
sre_demo_requests_total{{service="checkout",status="200"}} {int(successes)}
sre_demo_requests_total{{service="checkout",status="500"}} {int(errors)}
# HELP sre_demo_latency_seconds Synthetic checkout p95 latency.
# TYPE sre_demo_latency_seconds gauge
sre_demo_latency_seconds{{service="checkout",quantile="0.95"}} {latency}
# HELP sre_demo_peak_active Whether the synthetic peak phase is active.
# TYPE sre_demo_peak_active gauge
sre_demo_peak_active{{service="checkout"}} {peak}
'''.encode()
        if incident:
            body += f"""# HELP sre_demo_success_latency_seconds Synthetic p95 for successful requests only.
# TYPE sre_demo_success_latency_seconds gauge
sre_demo_success_latency_seconds{{service="checkout",quantile="0.95"}} {incident['success_p95']}
# HELP sre_demo_admission_rejections_total Synthetic requests rejected by modeled admission control.
# TYPE sre_demo_admission_rejections_total counter
sre_demo_admission_rejections_total{{service="checkout",reason="capacity_limit"}} {int(incident['rejections'])}
# HELP sre_demo_queue_depth Synthetic queued checkout requests.
# TYPE sre_demo_queue_depth gauge
sre_demo_queue_depth{{service="checkout"}} {incident['queue_depth']}
# HELP sre_demo_worker_utilization Synthetic worker utilization fraction.
# TYPE sre_demo_worker_utilization gauge
sre_demo_worker_utilization{{service="checkout"}} {incident['worker_utilization']}
# HELP sre_demo_incident_phase Phase: 0 baseline, 1 overload incident, 2 operator-modeled recovery.
# TYPE sre_demo_incident_phase gauge
sre_demo_incident_phase{{service="checkout"}} {incident['phase']}
""".encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; version=0.0.4')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    HTTPServer(('0.0.0.0', 9101), Handler).serve_forever()
