from typing import Optional
from intent_manager import Intent


class SafetyDecision:
    def __init__(self, safe: bool, reason: Optional[str] = None):
        self.safe = safe
        self.reason = reason


class SafetyGate:
    """
    Enforces hard safety invariants.
    Safety may block execution but cannot modify intent or state.
    """

    def __init__(self):
        # Absolute safety limits (example values)
        self.max_position = 10.0
        self.min_position = -10.0

    def evaluate(self, intent: Intent, system_state) -> SafetyDecision:
        """
        Evaluate intent against live system state.
        """

        if intent.command == "adjust_orbit":
            delta_v = intent.parameters["delta_v"]
            projected_position = system_state.position + delta_v

            if projected_position > self.max_position:
                return SafetyDecision(
                    safe=False,
                    reason="Projected position exceeds maximum safe limit"
                )

            if projected_position < self.min_position:
                return SafetyDecision(
                    safe=False,
                    reason="Projected position exceeds minimum safe limit"
                )

        return SafetyDecision(safe=True)
