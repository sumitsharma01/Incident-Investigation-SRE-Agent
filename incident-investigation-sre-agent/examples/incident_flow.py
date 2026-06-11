from app.agent.orchestrator import Orchestrator
from app.agent.schemas import InvestigationRequest


if __name__ == "__main__":
    controller = Orchestrator()
    result = controller.investigate(
        service="checkout",
        description="Checkout service latency increased significantly",
    )
    print(result.model_dump_json(indent=2))
