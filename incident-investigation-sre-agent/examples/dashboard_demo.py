import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.tools.demo_data import build_demo_context


def render_dashboard(context: dict) -> str:
    """Create a simple text-based dashboard for demo and presentation use."""
    lines = [
        "=== Incident Investigation SRE Agent Dashboard ===",
        f"Service: {context['service']}",
        f"SLO: {context['slo']['name']} -> {context['slo']['target']}",
        f"Error budget remaining: {context['error_budget_remaining_percent']}%",
        f"Toil risk: {context['toil_risk']}",
        "",
        "SLI snapshot:",
        f"  - {context['sli']['definition']}",
        f"  - Current signal: {context['sli']['current']}",
        "",
        "Top recommendations:",
    ]
    for item in context["recommendations"]:
        lines.append(f"  • {item}")

    lines.extend([
        "",
        "Evidence summary:",
        f"  - Logs: {len(context['logs'])}",
        f"  - Metrics: {len(context['metrics'])}",
        f"  - Traces: {len(context['traces'])}",
        f"  - Deployments: {len(context['deployments'])}",
        f"  - Similar incidents: {len(context['incidents'])}",
    ])
    return "\n".join(lines)


if __name__ == "__main__":
    context = build_demo_context("checkout")
    print(render_dashboard(context))
    Path("examples/dashboard_demo_output.txt").write_text(render_dashboard(context), encoding="utf-8")
    print("\nSaved dashboard preview to examples/dashboard_demo_output.txt")
