from typing import List, Dict, Any
import time


class TelemetryBus:
    """
    Append-only telemetry event bus.

    Observational only.
    No authority.
    No mutation.
    """

    def __init__(self):
        self._frames: List[Dict[str, Any]] = []

    def publish_frame(self, frame: Dict[str, Any]):
        self._frames.append({
            "timestamp": time.time(),
            "type": "cycle_frame",
            "data": frame
        })

    def get_frames(self) -> List[Dict[str, Any]]:
        return list(self._frames)


class TelemetryBuilder:
    """
    Pure projection layer.

    Converts system state and decisions
    into structured, JSON-safe telemetry.
    """

    def build_frame(
        self,
        system_state,
        policy_result,
        executed_intent,
        safety_result,
        override_applied: bool,
        lock_applied: bool
    ) -> Dict[str, Any]:

        state_snapshot = system_state.snapshot()

        policy_selected = (
            policy_result.selected_intent.intent_id
            if policy_result.selected_intent else None
        )

        executed_id = (
            executed_intent.intent_id
            if executed_intent else None
        )

        return {
            "state": state_snapshot,
            "policy": {
                "selected_intent_id": policy_selected,
                "scores": policy_result.scores,
            },
            "execution": {
                "executed_intent_id": executed_id,
                "override_applied": override_applied,
                "lock_applied": lock_applied,
            },
            "safety": {
                "blocked": safety_result.blocked,
                "critical_domains": safety_result.critical_domains,
                "reason": safety_result.reason,
            }
        }