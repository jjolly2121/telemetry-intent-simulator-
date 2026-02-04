from flask import Flask, render_template, request, redirect, url_for

from intent_manager import IntentManager
from orchestrator import Orchestrator
from state_engine import StateEngine, SystemState
from telemetry import TelemetryBus
from policy_gate import PolicyGate
from safety_gate import SafetyGate

app = Flask(__name__)

# --- Core system (single shared instance) ---
system_state = SystemState()
intent_manager = IntentManager()
telemetry = TelemetryBus()
policy_gate = PolicyGate()
safety_gate = SafetyGate()
state_engine = StateEngine(system_state)

orchestrator = Orchestrator(
    intent_manager=intent_manager,
    state_engine=state_engine,
    telemetry=telemetry,
    policy_gate=policy_gate,
    safety_gate=safety_gate
)

# --- Routes ---

@app.route("/", methods=["GET", "POST"])
def index():
    # Handle new intent submission
    if request.method == "POST":
        command = request.form.get("command")
        value = request.form.get("value")

        if command == "adjust_orbit" and value is not None:
            intent_manager.submit_intent(
                command="adjust_orbit",
                parameters={"delta_v": float(value)}
            )

        return redirect(url_for("index"))

    # Run one orchestration cycle per page load (manual stepping)
    orchestrator.run(cycles=1)

    # --- Prepare JSON-safe view models ---

    system_state_snapshot = system_state.snapshot()

    intents_view = [
        {
            "id": intent.intent_id,
            "command": intent.command,
            "parameters": intent.parameters,
            "status": intent.status.value,
            "block_reason": intent.block_reason
        }
        for intent in intent_manager.list_intents().values()
    ]

    telemetry_events = telemetry.get_events()

    return render_template(
        "index.html",
        system_state=system_state_snapshot,
        intents=intents_view,
        telemetry=telemetry_events
    )


if __name__ == "__main__":
    app.run(debug=True)
