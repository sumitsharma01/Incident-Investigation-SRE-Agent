"""Capture server-defined queries; never infer recovery from model prose."""
import json
import math
import os
import re
import time

import httpx
from app.workspace.tenancy import profile, allowed_service


class MetricError(ValueError):
    pass


def capture(service, label):
    allowed_service(service)
    config = profile.get()
    if config is not None and not config.get('prometheus_url'):
        raise MetricError('No Prometheus endpoint configured for this tenant')
    url = os.getenv('SRE_PROMETHEUS_URL', 'http://127.0.0.1:9090').rstrip('/')
    if config is not None:
        url = config['prometheus_url'].rstrip('/')
    prefix = os.getenv('SRE_METRIC_PREFIX', 'sre_lab')
    if config is not None:
        prefix = config.get('metric_prefix', 'sre_lab')
    if not re.fullmatch(r'[a-zA-Z_:][a-zA-Z0-9_:]*', prefix):
        raise MetricError('Invalid server metric prefix')
    selector = '{service=' + json.dumps(service) + '}'
    all_requests = prefix + '_requests_total' + selector
    failed = prefix + '_requests_total{service=' + json.dumps(service) + ',status="500"}'
    queries = {
        'traffic_rps': f'sum(rate({all_requests}[30s]))',
        'p95_seconds': f'{prefix}_latency_seconds{{service={json.dumps(service)},quantile="0.95"}}',
        'error_ratio': f'sum(rate({failed}[30s])) / sum(rate({all_requests}[30s]))',
        'queue_depth': f'{prefix}_queue_depth' + selector,
        'sample_age_seconds': f'time() - timestamp({prefix}_latency_seconds{{service={json.dumps(service)},quantile="0.95"}})',
    }
    timestamp = time.time()
    observations = {}
    # URL and query templates are operator configuration, not request-supplied targets.
    token = config.get('prometheus_token') if config is not None else os.getenv('SRE_PROMETHEUS_TOKEN')
    headers = {'Authorization': 'Bearer '+token} if token else {}
    with httpx.Client(timeout=10, follow_redirects=False, headers=headers) as client:
        for signal, query in queries.items():
            try:
                response = client.get(url + '/api/v1/query', params={'query': query, 'time': timestamp})
                response.raise_for_status()
                raw = response.json()
                results = raw.get('data', {}).get('result', [])
                if raw.get('status') != 'success' or raw.get('data', {}).get('resultType') != 'vector' or len(results) != 1:
                    raise MetricError(f'{signal}: expected exactly one series')
                value = float(results[0]['value'][1])
                sample_time = float(results[0]['value'][0])
                if not math.isfinite(value) or value < 0 or timestamp - sample_time > 30 or (signal == 'sample_age_seconds' and value > 15):
                    raise MetricError(f'{signal}: missing, invalid or stale data')
                observations[signal] = {'query': query, 'evaluated_at': timestamp, 'sample_timestamp': sample_time, 'value': value, 'raw': raw}
            except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
                if isinstance(exc, MetricError):
                    raise
                raise MetricError(f'{signal}: query failed; inspect Prometheus configuration') from None
    return {'service': service, 'label': label, 'source': 'prometheus', 'window_seconds': 30,
            'evaluated_at': timestamp, 'signals': observations}


def compare(before, after, policy):
    reasons = []
    b = {key: item['value'] for key, item in before['signals'].items()}
    a = {key: item['value'] for key, item in after['signals'].items()}
    if {k: v['query'] for k,v in before['signals'].items()} != {k: v['query'] for k,v in after['signals'].items()}:
        raise MetricError('Snapshots must use the same metric queries')
    if before['service'] != after['service']:
        raise MetricError('Snapshots must describe the same service')
    if after['evaluated_at'] - before['evaluated_at'] < 30:
        reasons.append('Observation windows overlap; wait at least 30 seconds.')
    if b['traffic_rps'] < policy.minimum_traffic_rps:
        reasons.append('Before observation has insufficient traffic.')
    traffic_floor = max(policy.minimum_traffic_rps, b['traffic_rps'] * policy.traffic_retention)
    checks = {
        'traffic_retained': a['traffic_rps'] >= traffic_floor,
        'latency_within_target': a['p95_seconds'] <= policy.max_p95_seconds,
        'error_ratio_within_target': a['error_ratio'] <= policy.max_error_ratio,
        'queue_within_target': a['queue_depth'] <= policy.max_queue_depth,
        'latency_improved': a['p95_seconds'] < b['p95_seconds'],
    }
    if not checks['traffic_retained']:
        reasons.append('Insufficient comparable traffic; lower demand could explain the improvement.')
    status = 'inconclusive' if reasons else 'recovered' if all(checks.values()) else 'not_recovered'
    return {'status': status, 'checks': checks, 'before': b, 'after': a, 'traffic_floor_rps': traffic_floor,
            'policy': policy.model_dump(), 'reasons': reasons,
            'limitations': ['Two observation windows support a recovery check, not proof of causation or sustained recovery.',
                            'P95 is the configured exporter gauge; use a production histogram query for production services.']}
