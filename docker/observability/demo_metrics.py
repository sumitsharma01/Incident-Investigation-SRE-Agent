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


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/metrics':
            self.send_error(404)
            return
        successes, errors, latency, peak = sample(time.monotonic() - started, os.getenv('SRE_DEMO_TRAFFIC_SCENARIO', 'steady'))
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
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; version=0.0.4')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    HTTPServer(('0.0.0.0', 9101), Handler).serve_forever()
