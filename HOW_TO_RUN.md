# Running the Telemetry Intent Execution Simulator

This simulator runs as a local web application that exposes an intent-driven execution system with policy enforcement, safety validation, deterministic state mutation, and telemetry reporting.

To run the simulator locally, clone the repository, create a Python virtual environment, install dependencies, and start the web server.

Clone the repository and move into the project directory:

```bash
git clone https://github.com/<your-username>/telemetry-intent-execution-simulator.git
cd telemetry-intent-execution-simulator
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install required dependencies:

```bash
pip install -r requirements.txt
```

Start the simulator:

```bash
python ui_server.py
```

Once the server is running, open a browser and navigate to:

```
http://localhost:5000
```

The web interface allows intents to be submitted and inspected. Each intent flows through policy and safety gates before being eligible for execution. At most one state mutation is applied per execution cycle. Telemetry events are emitted to reflect observed outcomes and system behavior.

All system state, intents, and telemetry are held in memory and reset when the application restarts. To stop the simulator, press Ctrl+C in the terminal.
