from datetime import datetime
from typing import Dict, List, Optional
from intent_manager import Intent


class TelemetryEvent:
    """
    Immutable telemetry record.
    """

    def __init__(
        self,
        event_type: str,
        intent: Optional[Intent],
        data: Optional[Dict] = None
    ):
        self.timestamp = datetime.utcnow().isoformat()
        self.event_type = event_type
        self.intent_id = intent.intent_id if intent else None
        self.command = intent.command if intent else None
        self.status = intent.status.value if intent else None
        self.data = data or {}

    def serialize(self) -> Dict:
        """
        Converts telemetry event to structured dictionary.
        """
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "intent_id": self.intent_id,
            "command": self.command,
            "status": self.status,
            "data": self.data
        }


class TelemetryBus:
    """
    Central telemetry collection system.
    Read-only observer of system behavior.
    """

    def __init__(self):
        self._events: List[TelemetryEvent] = []

    def record(
        self,
        event_type: str,
        intent: Optional[Intent] = None,
        data: Optional[Dict] = None
    ):
        """
        Records a telemetry event.
        """
        event = TelemetryEvent(
            event_type=event_type,
            intent=intent,
            data=data
        )
        self._events.append(event)

    def dump(self) -> List[Dict]:
        """
        Returns all telemetry events as serialized dicts.
        """
        return [event.serialize() for event in self._events]

    def latest(self) -> Optional[Dict]:
        """
        Returns the most recent telemetry event.
        """
        if not self._events:
            return None
        return self._events[-1].serialize()
