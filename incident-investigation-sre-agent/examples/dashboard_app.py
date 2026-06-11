import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.tools.demo_data import build_demo_context

app = FastAPI(title="SRE Agent Dashboard")


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
      </style>
    </head>
    <body>
      <div class=\"page\">
        <div class=\"hero\">
          <div>
            <span class=\"badge\">Interactive SRE Demo</span>
            <h1>Incident Investigation SRE Agent</h1>
            <p>Evidence-driven investigation dashboard for logs, metrics, traces, deployments, and incident history — with human-in-the-loop guidance.</p>
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
            <h2 style=\"margin-top: 0; font-size: 18px;\">Signal posture</h2>
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
            <h2 style=\"margin-top: 0; font-size: 18px;\">Recommended next steps</h2>
            <ul class="list">{recommendations_html}</ul>
          </section>

          <section class=\"card span-4\">
            <h2 style=\"margin-top: 0; font-size: 18px;\">Evidence coverage</h2>
            <div class=\"pill\">Logs: {len(context['logs'])}</div>
            <div class=\"pill\">Metrics: {len(context['metrics'])}</div>
            <div class=\"pill\">Traces: {len(context['traces'])}</div>
            <div class=\"pill\">Deployments: {len(context['deployments'])}</div>
            <div class=\"pill\">Similar incidents: {len(context['incidents'])}</div>
          </section>
        </div>
      </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("examples.dashboard_app:app", host="127.0.0.1", port=8001, reload=False)
