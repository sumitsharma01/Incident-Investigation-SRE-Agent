from app.agent.llm_reasoner import LLMReasoner
from app.agent.opensre import OpenSREBackend
from app.agent.planner import Planner
from app.agent.schemas import InvestigationResponse
from app.core.aggregator import aggregate_context
from app.core.reasoning import generate_hypotheses
from app.core.safety import SafetyGuard


class Orchestrator:
    def __init__(self) -> None:
        self.planner = Planner()
        self.safety_guard = SafetyGuard()
        self.llm_reasoner = LLMReasoner()

    def investigate(self, service: str, description: str, backend: str = "demo") -> InvestigationResponse:
        self.safety_guard.validate_request(service, description)
        if backend == "opensre":
            return OpenSREBackend().investigate(service, description)
        self.planner.plan(service, description)
        context = aggregate_context(service, description)
        llm_summary = self.llm_reasoner.summarize({"service": service, "description": description, "context": context})
        hypotheses = generate_hypotheses(context)

        return InvestigationResponse(
            service=service,
            summary=llm_summary["summary"],
            llm_mode=llm_summary["mode"],
            warnings=["Demo evidence and fixed hypotheses are synthetic; confidence is not calibrated."],
            hypotheses=hypotheses,
            human_in_the_loop=True,
            safe_to_continue=self.safety_guard.allow_investigation(context),
        )
