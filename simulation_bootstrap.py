from intent_manager import IntentManager
from state_engine import StateEngine, SystemState
from telemetry import TelemetryBus
from orchestrator import Orchestrator
from policy_gate import PolicyGate
from safety_gate import SafetyGate


def build_simulation():
    """
    Single source of truth for simulation wiring and initial conditions.
    Edit initial state or intents here to affect both main.py and mission_control.py.
    """
    system_state = SystemState()
    # main.py
    system_state.battery_level = 24.0

    # Example: set initial conditions here if needed
    # system_state.battery_level = 4.0

    intent_manager = IntentManager()
    state_engine = StateEngine(system_state)
    telemetry_bus = TelemetryBus()
    policy_gate = PolicyGate()
    safety_gate = SafetyGate()

    orchestrator = Orchestrator(
        intent_manager=intent_manager,
        state_engine=state_engine,
        telemetry=telemetry_bus,
        policy_gate=policy_gate,
        safety_gate=safety_gate,
    )

    # Initial mission intent
    intent_manager.submit_intent(
        intent_type="orbit_correction",
        goal_target="orbital_deviation",
        goal_reference=3.0,
        goal_metric="position",
        goal_tolerance=0.1,
    )

    return system_state, intent_manager, telemetry_bus, orchestrator
