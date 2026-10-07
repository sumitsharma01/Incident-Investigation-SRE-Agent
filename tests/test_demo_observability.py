from app.tools.demo_data import build_demo_context


def test_build_demo_context_includes_sli_slo_and_error_budget():
    context = build_demo_context("checkout")

    assert context["service"] == "checkout"
    assert context["sli"]
    assert context["slo"]
    assert context["error_budget_remaining_percent"] >= 0
    assert context["recommendations"]
