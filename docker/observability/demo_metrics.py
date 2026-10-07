"""Synthetic checkout metrics, generated for the local observability lab."""
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

started = time.monotonic()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/metrics':
            self.send_error(404)
            return
        elapsed = time.monotonic() - started
        body = f'''# HELP sre_demo_requests_total Synthetic checkout requests.
# TYPE sre_demo_requests_total counter
sre_demo_requests_total{{service="checkout",status="200"}} {int(elapsed * 45)}
sre_demo_requests_total{{service="checkout",status="500"}} {int(elapsed * 2)}
# HELP sre_demo_latency_seconds Synthetic checkout p95 latency.
# TYPE sre_demo_latency_seconds gauge
sre_demo_latency_seconds{{service="checkout",quantile="0.95"}} 0.42
'''.encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; version=0.0.4')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


HTTPServer(('0.0.0.0', 9101), Handler).serve_forever()
