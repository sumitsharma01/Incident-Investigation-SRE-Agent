from app.agent.llm_reasoner import LLMReasoner
from app.agent.opensre import OpenSREBackend
from app.agent.planner import Planner
from app.agent.schemas import InvestigationResponse
from app.core.aggregator import aggregate_context
from app.core.reasoning import generate_hypotheses
from app.core.safety import SafetyGuard
from app.core.memory import InvestigationMemory
from app.workspace.tenancy import profile


class Orchestrator:
    def __init__(self) -> None:
        self.planner = Planner()
        self.safety_guard = SafetyGuard()
        self.llm_reasoner = LLMReasoner()

    def investigate(self, service: str, description: str, backend: str = "demo") -> InvestigationResponse:
        self.safety_guard.validate_request(service, description)
        plan = self.planner.plan(service, description, backend)
        memory = InvestigationMemory(service, description)
        if backend == "opensre":
            result = OpenSREBackend().investigate(service, description)
            memory.add_observation(f"OpenSRE run status: {result.status}")
            memory.add_note("Read-only investigation. Proposed fixes require engineer review; no remediation was executed.")
            result.investigation_plan = plan
            result.investigation_notes = memory.observations + memory.notes
            return result
        memory.add_note("Sample collectors and fixed hypotheses are demo evidence, not live incident observations.")
        context = aggregate_context(service, description)
        llm_summary = ({"summary": "Sample investigation only; no live observations or model call.", "mode": "mock"} if profile.get() is not None else self.llm_reasoner.summarize({"service": service, "description": description, "context": context}))
        hypotheses = generate_hypotheses(context)

        return InvestigationResponse(
            service=service,
            summary=llm_summary["summary"],
            llm_mode=llm_summary["mode"],
            investigation_plan=plan,
            investigation_notes=memory.notes,
            warnings=["Demo evidence and fixed hypotheses are synthetic; confidence is not calibrated."],
            hypotheses=hypotheses,
            human_in_the_loop=True,
            safe_to_continue=self.safety_guard.allow_investigation(context),
        )
