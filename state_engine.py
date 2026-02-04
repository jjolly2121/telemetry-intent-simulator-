from typing import Dict, Optional
from intent_manager import Intent, IntentStatus


class SystemState:
    def __init__(self):
        self.position = 0.0

    def snapshot(self) -> Dict:
        return {"position": self.position}


class StateEngine:
    """
    Applies exactly one mutation per cycle.
    """

    def __init__(self, system_state: SystemState):
        self.system_state = system_state

    def apply(self, intent: Intent) -> Optional[Dict]:
        if intent.status != IntentStatus.AUTHORIZED:
            return None

        result = None

        if intent.command == "adjust_orbit":
            delta_v = intent.parameters["delta_v"]
            self.system_state.position += delta_v

            result = {
                "command": "adjust_orbit",
                "delta_v": delta_v,
                "new_position": self.system_state.position
            }

        intent.status = IntentStatus.EXECUTED
        return result
