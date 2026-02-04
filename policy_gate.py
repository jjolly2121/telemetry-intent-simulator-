from typing import Optional
from intent_manager import Intent


class PolicyDecision:
    def __init__(self, authorized: bool, reason: Optional[str] = None):
        self.authorized = authorized
        self.reason = reason


class PolicyGate:
    """
    Evaluates intent against policy rules.
    """

    def __init__(self):
        self.max_delta_v = 5.0

    def evaluate(self, intent: Intent) -> PolicyDecision:
        if intent.command == "adjust_orbit":
            delta_v = intent.parameters.get("delta_v")

            if delta_v is None:
                return PolicyDecision(False, "Missing delta_v")

            if delta_v > self.max_delta_v:
                return PolicyDecision(
                    False,
                    f"delta_v {delta_v} exceeds max {self.max_delta_v}"
                )

        return PolicyDecision(True)
