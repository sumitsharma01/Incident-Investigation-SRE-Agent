import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import __version__
from app.tools.demo_data import build_demo_context

app = FastAPI(title="SRE Agent Dashboard", version=__version__)


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    context = build_demo_context("checkout")
    recommendations_html = "".join(f"<li>{item}</li>" for item in context["recommendations"])
    return f"""
    <!doctype html>
    <html lang=\"en\">
    <head>
      <meta charset=\"utf-8\" />
      <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
      <title>Incident Investigation SRE Agent Dashboard</title>
      <style>
        :root {{
          color-scheme: dark;
          --bg: #07111f;
          --panel: #0f172a;
          --card: #14263a;
          --accent: #38bdf8;
          --good: #4ade80;
          --warn: #fbbf24;
          --danger: #fb7185;
          --text: #edf2ff;
          --muted: #bfd4ff;
        }}
        * {{ box-sizing: border-box; font-family: Arial, Helvetica, sans-serif; }}
        body {{ margin: 0; background: radial-gradient(circle at top, #12253b 0%, var(--bg) 45%); color: var(--text); }}
        .page {{ max-width: 1300px; margin: 0 auto; padding: 24px; }}
        .hero {{ display: flex; justify-content: space-between; align-items: end; gap: 18px; margin-bottom: 18px; }}
        .badge {{ display: inline-block; padding: 6px 10px; background: rgba(56, 189, 248, 0.12); color: var(--accent); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 999px; font-size: 12px; text-transform: uppercase; letter-spacing: 0.18em; }}
        h1 {{ font-size: 34px; margin: 8px 0 4px; }}
        p {{ color: var(--muted); line-height: 1.4; }}
        .grid {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 18px; }}
        .card {{ background: linear-gradient(180deg, rgba(20,38,58,0.98), rgba(8,15,26,0.98)); border: 1px solid rgba(148,163,184,0.18); border-radius: 18px; padding: 18px; box-shadow: 0 18px 38px rgba(2,6,23,0.45); }}
        .span-4 {{ grid-column: span 4; }}
        .span-8 {{ grid-column: span 8; }}
        .metric {{ display: flex; flex-direction: column; gap: 5px; margin-bottom: 12px; }}
        .metric-label {{ text-transform: uppercase; letter-spacing: 0.18em; font-size: 11px; color: var(--muted); }}
        .metric-value {{ font-size: 28px; font-weight: 700; }}
        .chip {{ display: inline-flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 999px; background: rgba(74, 222, 128, 0.12); color: #d1fae5; border: 1px solid rgba(74, 222, 128, 0.25); }}
        .bar {{ height: 10px; border-radius: 999px; background: rgba(148,163,184,0.18); overflow: hidden; margin-top: 6px; }}
        .bar-fill {{ height: 100%; background: linear-gradient(90deg, var(--accent), #a78bfa); border-radius: inherit; }}
        .list {{ margin: 0; padding-left: 18px; color: var(--text); line-height: 1.45; }}
        .mini-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
        .pill {{ display: inline-block; padding: 8px 10px; border-radius: 999px; background: rgba(251,191,36,0.12); color: #fde68a; border: 1px solid rgba(251,191,36,0.25); font-size: 13px; margin-right: 8px; margin-bottom: 8px; }}
        .muted {{ color: var(--muted); }}
        .note {{ margin-top: 18px; padding: 18px; border: 1px solid rgba(56,189,248,.3); border-radius: 14px; background: rgba(56,189,248,.05); }}
        code {{ color: var(--accent); overflow-wrap: anywhere; }}
        @media (max-width: 720px) {{
          .page {{ padding: 16px; }}
          .hero {{ flex-direction: column; align-items: start; }}
          h1 {{ font-size: 27px; }}
          .span-4, .span-8 {{ grid-column: span 12; }}
          .mini-grid {{ grid-template-columns: 1fr; }}
          .metric-value {{ font-size: 24px; }}
        }}
      </style>
    </head>
    <body>
      <div class=\"page\">
        <div class=\"hero\">
          <div>
            <span class=\"badge\">Demo dashboard · v{__version__}</span>
            <h1>Incident Investigation SRE Agent</h1>
            <p>A checkout incident walkthrough using sample logs, metrics, traces, and deployment history. All values on this page are synthetic.</p>
          </div>
          <div class=\"chip\">Error budget remaining: {context['error_budget_remaining_percent']}%</div>
        </div>

        <div class=\"grid\">
          <section class=\"card span-4\">
            <div class=\"metric\"><span class=\"metric-label\">Service</span><span class=\"metric-value\">{context['service']}</span></div>
            <div class=\"metric\"><span class=\"metric-label\">Toil Risk</span><span class=\"metric-value\">{context['toil_risk']}</span></div>
            <div class=\"metric\"><span class=\"metric-label\">SLO</span><span class=\"metric-value\">{context['slo']['target']}</span></div>
            <div class=\"metric\"><span class=\"metric-label\">Current SLI</span><span class=\"metric-value\">{context['sli']['current']}</span></div>
          </section>

          <section class=\"card span-8\">
            <h2 style=\"margin-top: 0; font-size: 18px;\">Service health</h2>
            <div class=\"mini-grid\">
              <div>
                <div class=\"metric-label\">Availability</div>
                <div class=\"metric-value\">99.9% target</div>
                <div class=\"bar\"><div class=\"bar-fill\" style=\"width: 98%\"></div></div>
              </div>
              <div>
                <div class=\"metric-label\">Latency health</div>
                <div class=\"metric-value\">p95 420 ms</div>
                <div class=\"bar\"><div class=\"bar-fill\" style=\"width: 74%\"></div></div>
              </div>
            </div>
            <p class=\"muted\">{context['sli']['definition']}</p>
          </section>

          <section class=\"card span-8\">
            <h2 style=\"margin-top: 0; font-size: 18px;\">What to check next</h2>
            <ul class="list">{recommendations_html}</ul>
          </section>

          <section class=\"card span-4\">
            <h2 style=\"margin-top: 0; font-size: 18px;\">Sample evidence</h2>
            <div class=\"pill\">Logs: {len(context['logs'])}</div>
            <div class=\"pill\">Metrics: {len(context['metrics'])}</div>
            <div class=\"pill\">Traces: {len(context['traces'])}</div>
            <div class=\"pill\">Deployments: {len(context['deployments'])}</div>
            <div class=\"pill\">Similar incidents: {len(context['incidents'])}</div>
          </section>
        </div>
        <section class="note">
          <h2 style="margin: 0 0 8px; font-size: 18px;">Investigating a real incident</h2>
          <p style="margin: 0;">The API supports an optional OpenSRE backend. Send an investigation to
          <code>POST /investigate</code> with <code>backend: opensre</code> after configuring OpenSRE on the API host.
          This dashboard stays a demo; it does not display live OpenSRE results. <a href="/integration" style="color: var(--accent);">See what the integration adds</a>.</p>
        </section>
      </div>
    </body>
    </html>
    """


@app.get("/integration", response_class=HTMLResponse)
def integration_dashboard() -> str:
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>OpenSRE integration guide</title><style>
* {{ box-sizing:border-box; }} body {{margin:0;background:#07111f;color:#edf2ff;font-family:Arial,sans-serif;line-height:1.5;}}
main {{max-width:1180px;margin:auto;padding:32px;}} a {{color:#38bdf8;}} h1 {{font-size:34px;margin:10px 0;}} h2 {{font-size:20px;margin:0 0 10px;}}
p {{color:#bfd4ff;}} .tag {{color:#38bdf8;font-size:13px;letter-spacing:2px;}} .grid {{display:grid;grid-template-columns:1fr 1fr;gap:18px;}}
.card {{background:#102033;border:1px solid #2a4058;border-radius:16px;padding:22px;}} .flow {{display:flex;gap:12px;margin:22px 0;}}
.step {{flex:1;background:#12304a;border:1px solid #2b638a;padding:16px;border-radius:12px;}} .step strong {{display:block;}}
.note {{background:#30271b;border:1px solid #7c6132;border-radius:12px;padding:16px;color:#fde68a;margin:22px 0;}}
code {{color:#7dd3fc;overflow-wrap:anywhere;}} li {{margin:7px 0;}} .footer {{font-size:13px;color:#bfd4ff;margin-top:24px;}}
@media(max-width:720px) {{main {{padding:16px;}} .grid {{grid-template-columns:1fr;}} .flow {{flex-direction:column;}} h1 {{font-size:27px;}}}}
</style></head><body><main>
<div class="tag">SRE AGENT · V{__version__} · INTEGRATION GUIDE</div>
<h1>What OpenSRE adds</h1>
<p>The original agent walks through a sample checkout incident. OpenSRE gives the API a second path: investigate through the observability tools you configure.</p>
<div class="note">Setup is required. This page explains the integration; it does not report live connector health or investigation results.</div>
<div class="flow">
<div class="step"><strong>1. Incident request</strong>Service, description and <code>backend: opensre</code></div>
<div class="step"><strong>2. OpenSRE CLI</strong>One ephemeral turn using configured tools</div>
<div class="step"><strong>3. Engineer review</strong>Summary, questions and denied tools returned by the API</div>
</div>
<div class="grid">
<section class="card"><h2>Why it was added</h2><p>The demo collectors return sample data, and the hypotheses are fixed examples. Useful real investigations need access to the actual service signals.</p><p>OpenSRE provides the tool integrations and investigation runtime. This agent keeps its small HTTP API and lets you choose the backend per request.</p></section>
<section class="card"><h2>What changed in 0.2.0</h2><ul><li>Optional OpenSRE investigation backend.</li><li>Explicit errors, missing context and denied tool requests.</li><li>No sample-data fallback when OpenSRE fails.</li><li>Azure Responses summaries now reach the API.</li><li>Demo evidence is clearly labeled.</li></ul></section>
<section class="card"><h2>Before the first real investigation</h2><ol><li>Install and authenticate OpenSRE on the API host.</li><li>Configure the observability sources you need.</li><li>Use read-only credentials and verify the CLI independently.</li><li>Submit an API request with <code>backend: opensre</code>.</li></ol><p>Azure settings for this agent do not configure OpenSRE's model provider.</p></section>
<section class="card"><h2>How to read the response</h2><ul><li><code>success</code>: review the summary and its evidence.</li><li><code>needs_input</code>: read the returned questions.</li><li><code>approval_required</code>: a tool request was denied.</li><li><code>error</code>: the run failed or timed out.</li></ul><p>Structured hypotheses stay empty for OpenSRE. The adapter does not invent confidence scores or grant additional tools.</p></section>
</div>
<p class="footer">Reference: OpenSRE source commit <code>288a824</code>. Contract tests use mocks; live OpenSRE and Azure access remain unverified.
<a href="https://github.com/Tracer-Cloud/opensre/blob/288a82456af27ce75487527b2b21c7ab1cbf5d6b/docs/guides/headless-cli.mdx">Upstream CLI reference</a> · <a href="/">Demo dashboard</a></p>
</main></body></html>'''


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("examples.dashboard_app:app", host="127.0.0.1", port=8001, reload=False)


