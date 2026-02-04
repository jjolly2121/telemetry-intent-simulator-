from intent_manager import IntentManager
from state_engine import StateEngine, SystemState
from telemetry import TelemetryBus
from orchestrator import Orchestrator
from policy_gate import PolicyGate
from safety_gate import SafetyGate


def main():
    system_state = SystemState()

    intent_manager = IntentManager()
    state_engine = StateEngine(system_state)
    telemetry = TelemetryBus()
    policy_gate = PolicyGate()
    safety_gate = SafetyGate()

    orchestrator = Orchestrator(
        intent_manager,
        state_engine,
        telemetry,
        policy_gate,
        safety_gate
    )

    intent_manager.submit_intent(
        command="adjust_orbit",
        parameters={"delta_v": 3.0}
    )

    orchestrator.run(cycles=3)


if __name__ == "__main__":
    main()
