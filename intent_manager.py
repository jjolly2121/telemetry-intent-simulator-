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
    """

    def __init__(self):
        self._intents: Dict[str, Intent] = {}

    def submit_intent(self, command: str, parameters: Dict) -> Intent:
        intent_id = str(uuid.uuid4())
        intent = Intent(
            intent_id=intent_id,
            command=command,
            parameters=parameters,
            created_at=time.time()
        )
        self._intents[intent_id] = intent
        return intent

    def list_intents(self) -> Dict[str, Intent]:
        return self._intents

    def mark_authorized(self, intent_id: str):
        self._intents[intent_id].status = IntentStatus.AUTHORIZED

    def mark_blocked(self, intent_id: str, reason: str):
        intent = self._intents[intent_id]
        intent.status = IntentStatus.BLOCKED
        intent.block_reason = reason

    def mark_executed(self, intent_id: str):
        self._intents[intent_id].status = IntentStatus.EXECUTED
