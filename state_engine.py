from typing import Dict, Optional
from intent_manager import Intent, IntentStatus


class SystemState:
    """
    Represents the mutable system state.
    This state may only be updated by the StateEngine.
    """

    def __init__(self):
        # Example state variables (generic by design)
        self.position = 0.0
        self.health = "nominal"

    def snapshot(self) -> Dict:
        """
        Returns a read-only snapshot of current state.
        """
        return {
            "position": self.position,
            "health": self.health
        }


class StateEngine:
    """
    Applies exactly one state mutation per execution cycle.
    """

    def __init__(self, system_state: SystemState):
        self.system_state = system_state

    def apply(self, intent: Intent) -> Optional[Dict]:
        """
        Applies an authorized intent to the system state.

        Returns a result dict describing the mutation,
        or None if no mutation occurred.
        """

        # Enforce lifecycle rule
        if intent.status != IntentStatus.AUTHORIZED:
            return None

        result = None

        # Execute command
        if intent.command == "adjust_orbit":
            delta_v = intent.parameters.get("delta_v", 0.0)

            # Single, deterministic state mutation
            self.system_state.position += delta_v

            result = {
                "command": intent.command,
                "delta_v": delta_v,
                "new_position": self.system_state.position
            }

        elif intent.command == "set_health":
            new_health = intent.parameters.get("health", "unknown")
            self.system_state.health = new_health

            result = {
                "command": intent.command,
                "health": new_health
            }

        # Mark intent as executed only after mutation
        intent.status = IntentStatus.EXECUTED

        return result
