from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional
import time
import uuid


class IntentStatus(Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    BLOCKED = "blocked"
    EXECUTED = "executed"


@dataclass
class Intent:
    """
    Represents a durable command intent.
    Intent is not an action — it is a request awaiting validation and execution.
    """
    intent_id: str
    command: str
    parameters: Dict
    created_at: float
    status: IntentStatus = IntentStatus.PENDING
    last_updated: float = field(default_factory=time.time)
    block_reason: Optional[str] = None


class IntentManager:
    """
    Stores and manages durable intent.
    Intents persist independently of execution success or failure.
    """

    def __init__(self):
        self._intents: Dict[str, Intent] = {}

    def submit_intent(self, command: str, parameters: Dict) -> Intent:
        """
        Accepts a new command and stores it as durable intent.
        """
        intent_id = str(uuid.uuid4())
        intent = Intent(
            intent_id=intent_id,
            command=command,
            parameters=parameters,
            created_at=time.time()
        )

        self._intents[intent_id] = intent
        return intent

    def get_intent(self, intent_id: str) -> Optional[Intent]:
        """
        Retrieve an intent by ID.
        """
        return self._intents.get(intent_id)

    def list_intents(self) -> Dict[str, Intent]:
        """
        Returns all known intents.
        """
        return self._intents

    def mark_authorized(self, intent_id: str):
        """
        Marks intent as authorized for execution.
        """
        intent = self.get_intent(intent_id)
        if not intent:
            raise ValueError("Intent not found")

        intent.status = IntentStatus.AUTHORIZED
        intent.last_updated = time.time()

    def mark_blocked(self, intent_id: str, reason: str):
        """
        Blocks intent due to policy or safety violation.
        Intent is preserved with an explanation.
        """
        intent = self.get_intent(intent_id)
        if not intent:
            raise ValueError("Intent not found")

        intent.status = IntentStatus.BLOCKED
        intent.block_reason = reason
        intent.last_updated = time.time()

    def mark_executed(self, intent_id: str):
        """
        Marks intent as executed after successful state mutation.
        """
        intent = self.get_intent(intent_id)
        if not intent:
            raise ValueError("Intent not found")

        intent.status = IntentStatus.EXECUTED
        intent.last_updated = time.time()
