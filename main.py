from intent_manager import IntentManager
from policy_gate import PolicyGate
from state_engine import StateEngine
from telemetry import TelemetryBus
from orchestrator import Orchestrator


def main():
    # --- Initialize core systems ---
    intent_manager = IntentManager()
    policy_gate = PolicyGate()
    state_engine = StateEngine()
    telemetry = TelemetryBus()

    orchestrator = Orchestrator(
        intent_manager=intent_manager,
        policy_gate=policy_gate,
        state_engine=state_engine,
        telemetry=telemetry
    )

    # --- Submit a test intent ---
    intent = intent_manager.submit_intent(
        intent_type="ADJUST_ORBIT",
        payload={
            "delta_v": 0.5,
            "target_altitude_km": 420
        },
        source="ground_control"
    )

    print(f"\nSubmitted intent: {intent.intent_id}\n")

    # --- Run one orchestration cycle ---
    orchestrator.step()

    # --- Dump telemetry for inspection ---
    print("\n--- TELEMETRY LOG ---")
    for event in telemetry.get_events():
        print(event)

    # --- Final intent state ---
    final_intent = intent_manager.get_intent(intent.intent_id)
    print("\n--- FINAL INTENT STATE ---")
    print(final_intent)


if __name__ == "__main__":
    main()
