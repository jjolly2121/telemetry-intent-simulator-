from intent_manager import IntentManager
from state_engine import StateEngine, SystemState
from telemetry import TelemetryBus
from orchestrator import Orchestrator
from policy_gate import PolicyGate
from safety_gate import SafetyGate


def main():

    # --------------------------------
    # System State
    # --------------------------------
    system_state = SystemState()
    system_state.battery_level = 4.0

    # --------------------------------
    # Core Components
    # --------------------------------
    intent_manager = IntentManager()
    state_engine = StateEngine(system_state)
    telemetry_bus = TelemetryBus()
    policy_gate = PolicyGate()
    safety_gate = SafetyGate()

    # --------------------------------
    # Orchestrator
    # --------------------------------
    orchestrator = Orchestrator(
        intent_manager=intent_manager,
        state_engine=state_engine,
        telemetry=telemetry_bus,  # ← FIXED
        policy_gate=policy_gate,
        safety_gate=safety_gate
    )

    # --------------------------------
    # Submit Outcome-Based Intent
    # --------------------------------
    intent_manager.submit_intent(
        intent_type="orbit_correction",
        goal_target="orbital_deviation",
        goal_reference=3.0,
        goal_metric="position",
        goal_tolerance=0.1
    )

    # --------------------------------
    # Run Simulation
    # --------------------------------
    orchestrator.run(cycles=10)

    # --------------------------------
    # Print Telemetry
    # --------------------------------
    for frame in telemetry_bus.get_frames():  # ← get_frames not get_events
        print(frame)


if __name__ == "__main__":
    main()