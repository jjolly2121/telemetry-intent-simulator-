from typing import List, Dict
import time


class TelemetryBus:
    """
    Append-only telemetry event bus.

    Telemetry is observational only:
    - No authority
    - No state mutation
    - JSON-safe output
    """

    def __init__(self):
        self._events: List[Dict] = []

    def publish(self, event: Dict):
        """
        Record a telemetry event.
        """
        if event is None:
            return

        self._events.append({
            "timestamp": time.time(),
            "event": event
        })

    def get_events(self) -> List[Dict]:
        """
        Return all telemetry events.
        Safe for UI / JSON serialization.
        """
        return list(self._events)
