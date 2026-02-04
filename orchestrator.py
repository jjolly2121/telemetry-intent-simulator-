from typing import Dict

from intent_manager import IntentManager, IntentStatus, Intent
from policy_gate import PolicyGate, PolicyDecision
from state_engine import StateEngine
from telemetry import TelemetryBus


class Orchestrator:
    """
    Central execution coordinator.

    Responsibilities:
    - Pull pending intents
    - Evaluate policy decisions
    - Apply state transitions
    - Emit telemetry events

    The orchestrator does NOT:
    - Define policy
    - Enforce safety
    - Mutate intent state directly (delegates)
    """

    def __init__(
        self,
        intent_manager: IntentManager,
        policy_gate: PolicyGate,
        state_engine: StateEngine,
        telemetry: TelemetryBus
    ):
        self.intent_manager = intent_manager
        self.policy_gate = policy_gate
        self.state_engine = state_engine
        self.telemetry = telemetry

    def step(self):
        """
        Executes one orchestration cycle.
        """
        pending_intents = self.intent_manager.get_pending_intents()

        for intent in pending_intents:
            self._process_intent(intent)

    def _process_intent(self, intent: Intent):
        """
        Processes a single intent through the system.
        """
        # --- Telemetry: intent observed ---
        self.telemetry.record(
            event_type="INTENT_RECEIVED",
            intent=intent
        )

        # --- Policy evaluation ---
        decision, reason = self.policy_gate.evaluate(intent)

        self.telemetry.record(
            event_type="POLICY_EVALUATED",
            intent=intent,
            data={
                "decision": decision.value,
                "reason": reason
            }
        )

        if decision == PolicyDecision.DENY:
            self.intent_manager.update_status(
                intent.intent_id,
                IntentStatus.DENIED,
                reason
            )

            self.telemetry.record(
                event_type="INTENT_DENIED",
                intent=intent,
                data={"reason": reason}
            )
            return

        # --- State transition ---
        try:
            result: Dict = self.state_engine.apply(intent)

            self.intent_manager.update_status(
                intent.intent_id,
                IntentStatus.EXECUTED,
                "State transition applied"
            )

            self.telemetry.record(
                event_type="STATE_APPLIED",
                intent=intent,
                data=result
            )

        except Exception as e:
            self.intent_manager.update_status(
                intent.intent_id,
                IntentStatus.FAILED,
                str(e)
            )

            self.telemetry.record(
                event_type="EXECUTION_FAILED",
                intent=intent,
                data={"error": str(e)}
            )
