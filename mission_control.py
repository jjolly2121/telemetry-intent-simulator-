from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template
from flask_socketio import SocketIO

from simulation_bootstrap import build_simulation
from runner import OrchestrationRunner


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="gevent")


# -----------------------------
# Core Simulation Wiring
# -----------------------------

system_state, intent_manager, telemetry_bus, orchestrator = build_simulation()

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
