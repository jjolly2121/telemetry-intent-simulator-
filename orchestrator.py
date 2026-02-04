from intent_manager import IntentStatus


class Orchestrator:
    """
    Coordinates intent → policy → safety → execution → telemetry.
    """

    def __init__(
        self,
        intent_manager,
        state_engine,
        telemetry,
        policy_gate,
        safety_gate
    ):
        self.intent_manager = intent_manager
        self.state_engine = state_engine
        self.telemetry = telemetry
        self.policy_gate = policy_gate
        self.safety_gate = safety_gate

    def run(self, cycles=1):
        for cycle in range(cycles):
            print(f"\n--- Cycle {cycle + 1} ---")

            intents = self.intent_manager.list_intents()
            pending = next(
                (i for i in intents.values() if i.status == IntentStatus.PENDING),
                None
            )

            if not pending:
                print("No pending intents.")
                continue

            print(f"Evaluating intent {pending.intent_id}: {pending.command}")

            # POLICY CHECK
            policy_decision = self.policy_gate.evaluate(pending)
            if not policy_decision.authorized:
                self.intent_manager.mark_blocked(
                    pending.intent_id,
                    policy_decision.reason
                )
                print(f"Blocked by policy: {policy_decision.reason}")
                continue

            self.intent_manager.mark_authorized(pending.intent_id)

            # SAFETY CHECK (state-aware)
            safety_decision = self.safety_gate.evaluate(
                pending,
                self.state_engine.system_state
            )

            if not safety_decision.safe:
                self.intent_manager.mark_blocked(
                    pending.intent_id,
                    safety_decision.reason
                )
                print(f"Blocked by safety: {safety_decision.reason}")
                continue

            # EXECUTION (exactly one mutation)
            result = self.state_engine.apply(pending)

            if result:
                self.telemetry.publish(result)
