from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
import time
import uuid


# -------------------------------------------------
# Intent Status Enum
# -------------------------------------------------

class IntentStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    DENIED = "denied"


# -------------------------------------------------
# Intent Model
# -------------------------------------------------

@dataclass
class Intent:
    """
    Durable, outcome-oriented intent owned by the satellite.

    Intent describes *what condition should become true*,
    not *how it is achieved*.
    """

    # Identity
    intent_id: str
    intent_type: str
    created_at: float

    # Outcome definition
    goal_target: Optional[str] = None
    goal_reference: Optional[Any] = None
    goal_metric: Optional[str] = None
    goal_tolerance: Optional[Any] = None

    # Lifecycle
    status: IntentStatus = IntentStatus.PENDING
    last_updated: float = field(default_factory=time.time)

    # Evaluation Tracking
    evaluation_cycles: int = 0
    safety_block_cycles: int = 0
    consecutive_selected_cycles: int = 0
    stable_nominal_cycles: int = 0

    # Observability
    block_reason: Optional[str] = None


# -------------------------------------------------
# Intent Manager
# -------------------------------------------------

class IntentManager:
    """
    Owns storage and lifecycle of intents.

    Responsibilities:
    - Store durable intents
    - Track active vs archived
    - Provide filtered queries
    - Archive completed/denied intents

    Does NOT:
    - Score intents
    - Enforce safety
    - Apply physics
    """

    def __init__(self):
        self._intents: Dict[str, Intent] = {}

    # ---------------------------------------------
    # Submit
    # ---------------------------------------------

    def submit_intent(
        self,
        intent_type: str,
        goal_target: Optional[str] = None,
        goal_reference: Optional[Any] = None,
        goal_metric: Optional[str] = None,
        goal_tolerance: Optional[Any] = None
    ) -> Intent:

        intent_id = str(uuid.uuid4())

        intent = Intent(
            intent_id=intent_id,
            intent_type=intent_type,
            created_at=time.time(),
            goal_target=goal_target,
            goal_reference=goal_reference,
            goal_metric=goal_metric,
            goal_tolerance=goal_tolerance
        )

        self._intents[intent_id] = intent

        return intent

    # ---------------------------------------------
    # Active Queries
    # ---------------------------------------------

    def list_active(self):
        """
        Return all non-archived active intents.
        """
        return [
            intent
            for intent in self._intents.values()
            if intent.status in (IntentStatus.PENDING, IntentStatus.ACTIVE)
        ]

    def get_active_by_type(self, intent_type: str) -> Optional[Intent]:
        """
        Return active intent of given type if exists.
        """
        for intent in self._intents.values():
            if (
                intent.intent_type == intent_type and
                intent.status in (IntentStatus.PENDING, IntentStatus.ACTIVE)
            ):
                return intent

        return None

    # ---------------------------------------------
    # Lifecycle Updates
    # ---------------------------------------------

    def mark_active(self, intent: Intent):
        intent.status = IntentStatus.ACTIVE
        intent.last_updated = time.time()

    def mark_completed(self, intent: Intent):
        intent.status = IntentStatus.COMPLETED
        intent.last_updated = time.time()

    def mark_denied(self, intent: Intent, reason: str):
        intent.status = IntentStatus.DENIED
        intent.block_reason = reason
        intent.last_updated = time.time()

    # ---------------------------------------------
    # Archival
    # ---------------------------------------------

    def archive_completed(self):
        """
        Remove completed or denied intents
        from active storage.
        """
        to_remove = []

        for intent_id, intent in self._intents.items():
            if intent.status in (
                IntentStatus.COMPLETED,
                IntentStatus.DENIED
            ):
                to_remove.append(intent_id)

        for intent_id in to_remove:
            del self._intents[intent_id]
