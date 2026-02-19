from simulation_bootstrap import build_simulation


def main():

    system_state, intent_manager, telemetry_bus, orchestrator = build_simulation()

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
