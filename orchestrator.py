from telemetry import TelemetryBuilder


class Orchestrator:
    """
    Coordination layer.

    Responsibilities:
    - SAFE recovery injection
    - CRITICAL override handling
    - Recovery lock enforcement
    - Policy → Safety → State sequencing
    - Telemetry emission

    Does NOT:
    - Score intents
    - Mutate physics directly
    - Detect threshold violations
    """

    MIN_RECOVERY_LOCK_CYCLES = 3

    def __init__(
        self,
        intent_manager,
        state_engine,
        telemetry,
        policy_gate,
        safety_gate
    ):
        self.intent_manager = intent_manager
        self.state_engine = state_engine
        self.telemetry = telemetry
        self.policy_gate = policy_gate
        self.safety_gate = safety_gate

        self.telemetry_builder = TelemetryBuilder()

        self._last_selected_intent = None
        self._pending_safe_injections = set()

    # -------------------------------------------------
    # MAIN LOOP
    # -------------------------------------------------

    def run(self, cycles=1):

        for _ in range(cycles):

            system_state = self.state_engine.system_state

            # ---- SAFE Injection (apply pending from last cycle) ----
            self._apply_pending_safe_injections()

            # ---- SAFE Injection (schedule for next cycle) ----
            self._pending_safe_injections = self._compute_safe_injections(
                system_state
            )

            active_intents = self.intent_manager.list_active()

            # ---- Policy Selection ----
            policy_result = self.policy_gate.evaluate(
                active_intents,
                system_state
            )

            policy_selected = policy_result.selected_intent
            selected = policy_selected

            override_applied = False
            lock_applied = False
            executed_intent = None

            # ---- Safety Evaluation (policy-selected) ----
            safety_result = self.safety_gate.evaluate(
                selected,
                system_state
            )

            # ---- CRITICAL Override ----
            if safety_result.critical_domains:
                override_target = self._apply_critical_override(
                    safety_result.critical_domains,
                    active_intents
                )

                if override_target and override_target != selected:
                    selected = override_target
                    override_applied = True

            # ---- Recovery Lock ----
            locked_target = self._apply_recovery_lock(
                selected,
                active_intents,
                safety_result
            )

            if locked_target != selected:
                lock_applied = True

            selected = locked_target

            # ---- Safety Evaluation (final selected) ----
            safety_result = self.safety_gate.evaluate(
                selected,
                system_state
            )

            # ---- Blocked Execution ----
            if safety_result.blocked:
                if selected:
                    selected.safety_block_cycles += 1

                self._emit_frame(
                    policy_result,
                    safety_result,
                    executed_intent,
                    override_applied,
                    lock_applied
                )
                continue

            # ---- Apply State Mutation ----
            if selected:
                if self.state_engine.apply(selected):
                    executed_intent = selected

            # ---- Update Lock Tracking ----
            self._update_lock_tracking(selected)

            # ---- Archive Completed Intents ----
            self.intent_manager.archive_completed()

            # ---- Telemetry ----
            self._emit_frame(
                policy_result,
                safety_result,
                executed_intent,
                override_applied,
                lock_applied
            )

    # -------------------------------------------------
    # SAFE Injection
    # -------------------------------------------------

    def _compute_safe_injections(self, system_state):

        if system_state.mode != "SAFE":
            return set()

        to_inject = set()

        # Battery domain
        if system_state.battery_level <= system_state.SAFE_ENTRY_BATTERY:
            to_inject.add("battery_recovery")

        # Thermal domain
        if system_state.temperature >= system_state.SAFE_ENTRY_TEMP:
            to_inject.add("thermal_recovery")

        return to_inject

    def _apply_pending_safe_injections(self):

        if not self._pending_safe_injections:
            return

        for intent_type in self._pending_safe_injections:
            if not self.intent_manager.get_active_by_type(intent_type):
                self.intent_manager.submit_intent(intent_type)

    # -------------------------------------------------
    # CRITICAL Override
    # -------------------------------------------------

    def _apply_critical_override(self, critical_domains, active_intents):

        for domain in critical_domains:
            recovery_type = f"{domain}_recovery"

            for intent in active_intents:
                if intent.intent_type == recovery_type:
                    return intent

            # Force recovery if missing
            return self.intent_manager.submit_intent(recovery_type)

        return None

    # -------------------------------------------------
    # Recovery Lock
    # -------------------------------------------------

    def _apply_recovery_lock(self, selected, active_intents, safety_result):

        if not self._last_selected_intent:
            return selected

        last = self._last_selected_intent

        # Only lock recovery intents
        if not last.intent_type.endswith("_recovery"):
            return selected

        # CRITICAL breaks lock
        if safety_result.critical_domains:
            return selected

        # Enforce minimum cycles
        if last.consecutive_selected_cycles < self.MIN_RECOVERY_LOCK_CYCLES:
            return last

        return selected

    def _update_lock_tracking(self, selected):

        if not selected:
            self._last_selected_intent = None
            return

        if (
            self._last_selected_intent and
            selected.intent_id == self._last_selected_intent.intent_id
        ):
            selected.consecutive_selected_cycles += 1
        else:
            selected.consecutive_selected_cycles = 1

        self._last_selected_intent = selected

    # -------------------------------------------------
    # Telemetry
    # -------------------------------------------------

    def _emit_frame(
        self,
        policy_result,
        safety_result,
        executed_intent,
        override_applied,
        lock_applied
    ):

        frame = self.telemetry_builder.build_frame(
            system_state=self.state_engine.system_state,
            policy_result=policy_result,
            executed_intent=executed_intent,
            safety_result=safety_result,
            override_applied=override_applied,
            lock_applied=lock_applied
        )

        self.telemetry.publish_frame(frame)
