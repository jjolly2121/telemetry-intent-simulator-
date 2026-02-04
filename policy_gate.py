from typing import Tuple, Optional
from intent_manager import Intent, IntentStatus


class PolicyDecision:
    """
    Simple container for policy evaluation results.
    """
    def __init__(self, authorized: bool, reason: Optional[str] = None):
        self.authorized = authorized
        self.reason = reason


class PolicyGate:
    """
    Evaluates intent against policy and safety rules.

    This layer may block execution but must never destroy intent.
    """

    def __init__(self):
        # Example thresholds / rules (can be expanded later)
        self.max_delta_v = 5.0
        self.forbidden_commands = {"shutdown_system"}

    def evaluate(self, intent: Intent) -> PolicyDecision:
        """
        Evaluate an intent and return a PolicyDecision.
        """

        # Rule 1: forbidden commands
        if intent.command in self.forbidden_commands:
            return PolicyDecision(
                authorized=False,
                reason=f"Command '{intent.command}' is forbidden by policy"
            )

        # Rule 2: parameter safety check
        if intent.command == "adjust_orbit":
            delta_v = intent.parameters.get("delta_v")

            if delta_v is None:
                return PolicyDecision(
                    authorized=False,
                    reason="Missing required parameter: delta_v"
                )

            if delta_v > self.max_delta_v:
                return PolicyDecision(
                    authorized=False,
                    reason=f"delta_v {delta_v} exceeds max allowed {self.max_delta_v}"
                )

        # Passed all checks
        return PolicyDecision(authorized=True)
