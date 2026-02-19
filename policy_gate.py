from typing import List, Dict, Optional
from intent_manager import Intent


class PolicyResult:
    """
    Pure scoring and selection result.
    """

    def __init__(
        self,
        selected_intent: Optional[Intent],
        scores: Dict[str, float],
        reason: str
    ):
        self.selected_intent = selected_intent
        self.scores = scores
        self.reason = reason


class PolicyGate:
    """
    Intent scoring and selection logic.

    Responsibilities:
    - Score intents
    - Select highest scoring intent
    - Apply SAFE dominance
    - Apply LOW_POWER bias
    - Apply NOMINAL downgrade
    - Apply lightweight history penalty

    Does NOT:
    - Detect CRITICAL
    - Inject intents
    - Override selection
    - Mutate state
    """

    RECOVERY_SCALE = 1000.0
    LOW_POWER_BIAS = 50.0
    NOMINAL_RECOVERY_PENALTY = -200.0

    HISTORY_PENALTY_FACTOR = 0.5

    def evaluate(
        self,
        intents: List[Intent],
        system_state
    ) -> PolicyResult:

        if not intents:
            return PolicyResult(None, {}, "no_active_intents")

        scores = {}

        for intent in intents:
            score = 0.0

            # ---- Recovery Scoring ----

            if intent.intent_type == "battery_recovery":
                severity = max(
                    0.0,
                    (system_state.SAFE_EXIT_BATTERY - system_state.battery_level)
                    / system_state.SAFE_EXIT_BATTERY
                )
                score += severity * self.RECOVERY_SCALE

            elif intent.intent_type == "thermal_recovery":
                severity = max(
                    0.0,
                    (system_state.temperature - system_state.SAFE_EXIT_TEMP)
                    / system_state.SAFE_EXIT_TEMP
                )
                score += severity * self.RECOVERY_SCALE

            # ---- Mission Intent Base Score ----

            elif intent.intent_type == "orbit_correction":
                score += 100.0

            # ---- Mode Bias Adjustments ----

            if system_state.mode == "LOW_POWER":
                if intent.intent_type.endswith("_recovery"):
                    score += self.LOW_POWER_BIAS

            if system_state.mode == "NOMINAL":
                if intent.intent_type.endswith("_recovery"):
                    score += self.NOMINAL_RECOVERY_PENALTY

            # ---- History Penalty ----

            score -= intent.safety_block_cycles * self.HISTORY_PENALTY_FACTOR

            scores[intent.intent_id] = score

        # ---- Selection ----

        selected_id = max(scores, key=scores.get)
        selected_intent = next(i for i in intents if i.intent_id == selected_id)

        return PolicyResult(
            selected_intent=selected_intent,
            scores=scores,
            reason="highest_score_selected"
        )