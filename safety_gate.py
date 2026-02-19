from typing import List, Optional
from intent_manager import Intent


class SafetyDecision:
    """
    Pure evaluation result.

    blocked:
        Whether execution must be blocked this cycle.

    reason:
        Optional explanation.

    critical_domains:
        Domains that crossed CRITICAL thresholds.
        Used by orchestrator for override logic.
    """

    def __init__(
        self,
        blocked: bool,
        reason: Optional[str] = None,
        critical_domains: Optional[List[str]] = None
    ):
        self.blocked = blocked
        self.reason = reason
        self.critical_domains = critical_domains or []


class SafetyGate:
    """
    Reflexive invariant enforcement layer.

    Responsibilities:
    - Detect SAFE violations
    - Detect CRITICAL violations
    - Block unsafe intent execution
    - Report critical domains

    Does NOT:
    - Change mode
    - Inject intents
    - Override policy
    - Mutate state
    """

    # SAFE thresholds
    SAFE_ENTRY_BATTERY = 10
    SAFE_ENTRY_TEMP = 120

    # CRITICAL thresholds
    CRITICAL_BATTERY = 5
    CRITICAL_TEMP = 140
    # Hard safety bounds
    MIN_BATTERY = 0.0
    MAX_TEMP = 150.0
    POSITION_MIN = -10.0
    POSITION_MAX = 10.0

    ENERGY_INTENSIVE_INTENTS = {
        "orbit_correction",
    }

    # Intent → affected domains
    INTENT_DOMAIN_MAP = {
        "orbit_correction": ["battery", "thermal"],
        "battery_recovery": ["battery"],
        "thermal_recovery": ["thermal"],
    }

    def evaluate(
        self,
        selected_intent: Optional[Intent],
        system_state
    ) -> SafetyDecision:

        critical_domains = []

        # ---- CRITICAL detection ----

        if system_state.battery_level <= self.CRITICAL_BATTERY:
            critical_domains.append("battery")

        if system_state.temperature >= self.CRITICAL_TEMP:
            critical_domains.append("thermal")

        # ---- Hard invariant detection ----

        if system_state.battery_level <= self.MIN_BATTERY:
            return SafetyDecision(
                blocked=True,
                reason="battery_depleted",
                critical_domains=critical_domains
            )

        if system_state.temperature >= self.MAX_TEMP:
            return SafetyDecision(
                blocked=True,
                reason="temperature_max_exceeded",
                critical_domains=critical_domains
            )

        if (
            system_state.position < self.POSITION_MIN
            or system_state.position > self.POSITION_MAX
        ):
            return SafetyDecision(
                blocked=True,
                reason="position_bounds_exceeded",
                critical_domains=critical_domains
            )

        # ---- SAFE violation detection ----

        violated_domains = []

        if system_state.battery_level <= self.SAFE_ENTRY_BATTERY:
            violated_domains.append("battery")

        if system_state.temperature >= self.SAFE_ENTRY_TEMP:
            violated_domains.append("thermal")

        # ---- No selected intent ----

        if selected_intent is None:
            return SafetyDecision(
                blocked=False,
                critical_domains=critical_domains
            )

        # ---- Mode restrictions ----

        if system_state.mode == "SAFE":
            if not selected_intent.intent_type.endswith("_recovery"):
                return SafetyDecision(
                    blocked=True,
                    reason="safe_mode_mission_blocked",
                    critical_domains=critical_domains
                )

        if system_state.mode == "LOW_POWER":
            if selected_intent.intent_type in self.ENERGY_INTENSIVE_INTENTS:
                return SafetyDecision(
                    blocked=True,
                    reason="low_power_energy_intensive_blocked",
                    critical_domains=critical_domains
                )

        # ---- Domain-aware blocking ----

        affected_domains = self.INTENT_DOMAIN_MAP.get(
            selected_intent.intent_type,
            []
        )

        # Block only if intent worsens a violated domain
        for domain in violated_domains:
            if domain in affected_domains:
                # Allow recovery for that domain
                if selected_intent.intent_type.endswith("_recovery"):
                    continue

                return SafetyDecision(
                    blocked=True,
                    reason=f"{domain}_unsafe_execution_blocked",
                    critical_domains=critical_domains
                )

        # ---- Allowed execution ----

        return SafetyDecision(
            blocked=False,
            critical_domains=critical_domains
        )
