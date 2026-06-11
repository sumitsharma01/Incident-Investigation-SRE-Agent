from examples.dashboard_demo import render_dashboard
from app.tools.demo_data import build_demo_context


def test_render_dashboard_contains_summary_and_recommendations():
    context = build_demo_context("checkout")
    dashboard = render_dashboard(context)

    assert "Incident Investigation SRE Agent Dashboard" in dashboard
    assert "Error budget remaining" in dashboard
    assert "Top recommendations:" in dashboard
    assert "checkout" in dashboard
