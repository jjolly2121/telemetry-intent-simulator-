from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template
from flask_socketio import SocketIO

from intent_manager import IntentManager
from state_engine import StateEngine, SystemState
from telemetry import TelemetryBus
from orchestrator import Orchestrator
from policy_gate import PolicyGate
from safety_gate import SafetyGate
from runner import OrchestrationRunner


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="gevent")


# -----------------------------
# Core Simulation Wiring
# -----------------------------

system_state = SystemState()
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

# Initial mission intent (read-only UI; no user input)
intent_manager.submit_intent(
    intent_type="orbit_correction",
    goal_target="orbital_deviation",
    goal_reference=3.0,
    goal_metric="position",
    goal_tolerance=0.1,
)

runner = OrchestrationRunner(orchestrator, interval_seconds=1.0)


# -----------------------------
# Telemetry Streaming
# -----------------------------


def stream_telemetry():
    last_index = 0
    while True:
        frames = telemetry_bus.get_frames()
        if last_index < len(frames):
            for frame in frames[last_index:]:
                socketio.emit("telemetry", frame)
            last_index = len(frames)
        socketio.sleep(0.1)


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@socketio.on("connect")
def on_connect():
    # No state mutation; client is read-only
    pass


if __name__ == "__main__":
    runner.start()
    socketio.start_background_task(stream_telemetry)
    socketio.run(app, host="0.0.0.0", port=5050)
