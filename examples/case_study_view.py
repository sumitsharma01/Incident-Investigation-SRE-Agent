"""Read-only view of a recorded proof run, not a live production console."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'docs' / 'case-studies' / 'checkout-overload' / 'run.json'


def render_case_study() -> str:
    from app import __version__
    if not RUN.exists():
        return '<h1>No recorded case study yet</h1><p>Run examples/run_overload_proof.py first.</p>'
    data = json.loads(RUN.read_text())
    baseline, incident, recovery = [data[k]['values'] for k in ['baseline','incident','recovery']]
    names=[('Incoming requests/sec','incoming_rps',1),('Successful requests/sec','successful_rps',1),
           ('P95 latency (seconds)','p95_seconds',3),('Errors (%)','error_percent',2),
           ('Queued requests','queue_depth',0),('Worker utilization (%)','worker_utilization',1)]
    rows=''
    for label,key,decimals in names:
        values=[s[key]*(100 if key=='worker_utilization' else 1) for s in [baseline,incident,recovery]]
        rows+='<tr><td>'+label+'</td>'+''.join('<td>'+f'{v:,.{decimals}f}'+'</td>' for v in values)+'</tr>'
    agent=data['agent']
    status=html.escape(agent.get('status','unknown'))
    excerpt=html.escape(agent.get('summary','No summary returned')[:2400])
    excerpt=re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', excerpt)
    excerpt=re.sub(r'`([^`]+)`', r'<code>\1</code>', excerpt)
    plan=''.join('<li>'+html.escape(s)+'</li>' for s in agent.get('investigation_plan',[]))
    stamp=html.escape(data['incident']['time_berlin'])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Checkout overload — recorded investigation</title><style>
* {{box-sizing:border-box;}}body {{margin:0;background:#08111e;color:#eef3ff;font:16px/1.5 Arial,sans-serif;}}main {{max-width:1320px;margin:auto;padding:28px;}}
a {{color:#58c7ff;}}nav {{display:flex;gap:20px;flex-wrap:wrap;margin-bottom:22px;}}h1 {{font-size:34px;margin:8px 0;}}h2 {{font-size:21px;margin:0 0 12px;}}
.meta {{color:#91b6d8;font-size:13px;}}.note {{background:#30291b;border:1px solid #775b2c;border-radius:12px;padding:14px;color:#ffe4a5;margin:20px 0;}}
.grid {{display:grid;grid-template-columns:1fr 1fr;gap:18px;}}.card {{background:#112235;border:1px solid #29415c;border-radius:15px;padding:20px;}}
.full {{grid-column:1/-1;}}table {{width:100%;border-collapse:collapse;}}th,td {{padding:11px;border-bottom:1px solid #29415c;text-align:left;}}th {{color:#82d4ff;}}
td:nth-child(3) {{color:#ffb473;font-weight:bold;}}pre {{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.55 Arial,sans-serif;background:#0b1828;padding:16px;border-radius:8px;}}
li {{margin:8px 0;}}.stats {{display:flex;gap:18px;flex-wrap:wrap;margin:20px 0;}}.stat {{flex:1;min-width:180px;padding:16px;background:#15324c;border-radius:12px;}}
.stat strong {{display:block;font-size:29px;color:#ffb473;}}.foot {{color:#91b6d8;font-size:13px;}}@media(max-width:750px){{.grid {{grid-template-columns:1fr;}}main {{padding:16px;}}table {{font-size:12px;}}}}
</style></head><body><main>
<nav><a href="/">Demo dashboard</a><a href="/integration">Integration guide</a><a href="http://127.0.0.1:3000/d/sre-overload-proof">Grafana evidence</a><a href="http://127.0.0.1:9090/query">Prometheus queries</a><a href="http://127.0.0.1:8000/docs">Agent API</a><a href="/case-study/response">Full agent response</a><a href="https://github.com/sumitsharma01/Incident-Investigation-SRE-Agent/blob/main/docs/case-studies/checkout-overload/README.md">Written report</a></nav>
<div class="meta">VERSION {__version__} · RECORDED PROOF RUN · CHECKOUT</div>
<h1>Peak traffic and rising P95</h1>
<p>Prometheus → Grafana → OpenSRE → Azure → the agent API. Recorded incident sample: {stamp}.</p>
<div class="note">Synthetic local incident. Screenshots and API calls are real; workload values are generated. Recovery is scripted by the exporter. The agent did not execute a fix.</div>
<div class="stats"><div class="stat">Peak incoming traffic<strong>{incident['incoming_rps']:,.0f} req/s</strong></div><div class="stat">P95 latency<strong>{incident['p95_seconds']:.1f} seconds</strong></div><div class="stat">Failed requests<strong>{incident['error_percent']:.1f}%</strong></div><div class="stat">OpenSRE run<strong>{status}</strong></div></div>
<div class="grid">
<section class="card full"><h2>Baseline → incident → modeled recovery</h2><table><thead><tr><th>Observed signal</th><th>Baseline</th><th>Incident</th><th>Recovery</th></tr></thead><tbody>{rows}</tbody></table></section>
<section class="card"><h2>What the evidence supports</h2><p>Traffic, latency, failed requests and queue depth rose together. Worker utilization reached 95%. This is consistent with saturation; it does not identify a particular deployment or dependency.</p><p>Under the illustrative 99% success objective, a 20% error rate consumes budget at about 20× the allowed rate. Remaining monthly budget cannot be calculated from this run.</p></section>
<section class="card"><h2>Suggested checks and mitigations</h2><ol><li>Confirm service impact and preserve the incident window.</li><li>Check queue limits, worker occupancy, resource headroom and dependency latency before raising concurrency.</li><li>Review load shedding, retries and capacity. Test a bounded capacity increase only if downstream headroom is verified.</li><li>Review recent changes; roll back only if evidence links a change to the incident.</li><li>Validate errors, latency and queue recovery while incoming traffic stays high.</li></ol></section>
<section class="card full"><h2>Agent response · verbatim excerpt</h2><pre>{excerpt}</pre><p class="foot">Excerpt limited to 2,400 characters. The complete returned response and query snapshots are in docs/case-studies/checkout-overload/. No tool transcript is inferred from narrative.</p></section>
<section class="card"><h2>Investigation plan</h2><ol>{plan}</ol></section><section class="card"><h2>Limits of this proof</h2><p>Only metrics are configured for the live path. Logs, traces, deployment history and previous incidents remain sample collectors on the separate demo backend. This run validates integration and evidence handling, not production root-cause accuracy or autoscaling effectiveness.</p></section>
</div></main></body></html>'''
