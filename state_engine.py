from typing import Optional
from intent_manager import Intent, IntentStatus


class SystemState:
    """
    Physical system state.

    Owns:
    - Position
    - Battery
    - Temperature
    - Mode
    - Hysteresis thresholds
    """

    # SAFE thresholds
    SAFE_ENTRY_BATTERY = 10
    SAFE_EXIT_BATTERY = 20
    SAFE_EXIT_EPSILON = 0.5

    SAFE_ENTRY_TEMP = 120
    SAFE_EXIT_TEMP = 100
    SAFE_EXIT_TEMP_EPSILON = 1.0

    # LOW_POWER thresholds
    LOW_POWER_ENTRY = 25
    LOW_POWER_EXIT = 30
    # Hard safety bounds
    POSITION_MIN = -10.0
    POSITION_MAX = 10.0
    MAX_TEMP = 150.0
    MIN_BATTERY = 0.0

    def __init__(self):
        self.position = 0.0
        self.battery_level = 100.0
        self.temperature = 25.0
        self.mode = "NOMINAL"

    def snapshot(self):
        return {
            "position": self.position,
            "battery_level": self.battery_level,
            "temperature": self.temperature,
            "mode": self.mode,
        }


class StateEngine:
    """
    Applies exactly one mutation per cycle.

    Responsibilities:
    - Update mode (hysteresis)
    - Apply recovery physics
    - Apply mission physics
    - Complete intents based on physical outcome
    """

    def __init__(self, system_state: SystemState):
        self.system_state = system_state

    def apply(self, intent: Optional[Intent]):

        # ---- Mode update happens first ----
        self._update_mode()

        if intent is None:
            return False

        intent.evaluation_cycles += 1
        intent.status = IntentStatus.ACTIVE

        # ---- SAFE Recovery Physics ----

        if self.system_state.mode == "SAFE":
            self._apply_recovery_physics(intent)
            self._check_completion(intent)
            return True

        # ---- Mission Physics ----

        if intent.intent_type == "orbit_correction":
            self._apply_orbit_correction()

        # ---- Recovery in LOW_POWER or NOMINAL ----

        if intent.intent_type in ("battery_recovery", "thermal_recovery"):
            self._apply_recovery_physics(intent)

        # ---- Completion Logic ----

        self._check_completion(intent)
        return True

    # -----------------------------
    # Mode Management
    # -----------------------------

    def _update_mode(self):

        s = self.system_state

        # SAFE entry
        if (
            s.battery_level <= s.SAFE_ENTRY_BATTERY
            or s.temperature >= s.SAFE_ENTRY_TEMP
        ):
            s.mode = "SAFE"
            return

        # SAFE exit
        if s.mode == "SAFE":
            if (
                s.battery_level >= s.SAFE_EXIT_BATTERY - s.SAFE_EXIT_EPSILON
                and s.temperature <= s.SAFE_EXIT_TEMP + s.SAFE_EXIT_TEMP_EPSILON
            ):
                s.mode = "NOMINAL"
                return

        # LOW_POWER entry
        if s.battery_level <= s.LOW_POWER_ENTRY:
            s.mode = "LOW_POWER"
            return

        # LOW_POWER exit
        if s.mode == "LOW_POWER":
            if s.battery_level >= s.LOW_POWER_EXIT:
                s.mode = "NOMINAL"

    # -----------------------------
    # Physics
    # -----------------------------

    def _apply_orbit_correction(self):

        s = self.system_state

        step = 0.5
        battery_cost_per_unit = 2.0
        thermal_cost_per_unit = 4.0

        battery_cost = step * battery_cost_per_unit
        thermal_cost = step * thermal_cost_per_unit

        s.position += step
        s.battery_level -= battery_cost
        s.temperature += thermal_cost

    def _apply_recovery_physics(self, intent: Intent):

        s = self.system_state

        if intent.intent_type == "battery_recovery":
            if s.mode == "SAFE":
                target = s.SAFE_EXIT_BATTERY
            elif s.mode == "LOW_POWER":
                target = s.LOW_POWER_EXIT
            else:
                if s.battery_level < s.LOW_POWER_EXIT:
                    target = s.LOW_POWER_EXIT
                else:
                    target = s.SAFE_EXIT_BATTERY

            deficit = target - s.battery_level
            if deficit > 0:
                s.battery_level += 0.1 * deficit
                if s.battery_level > target:
                    s.battery_level = target

        if intent.intent_type == "thermal_recovery":
            excess = s.temperature - s.SAFE_EXIT_TEMP
            if excess > 0:
                s.temperature -= 0.1 * excess

    # -----------------------------
    # Completion Logic
    # -----------------------------

    def _check_completion(self, intent: Intent):

        s = self.system_state

        # Mission completion example
        if intent.intent_type == "orbit_correction":
            goal_value = 3.0
            if intent.goal_metric == "position" and intent.goal_reference is not None:
                goal_value = float(intent.goal_reference)

            if s.position >= goal_value:
                intent.status = IntentStatus.COMPLETED

        # Recovery completion logic
        if intent.intent_type == "battery_recovery":
            if s.mode == "SAFE":
                target = s.SAFE_EXIT_BATTERY
            elif s.mode == "LOW_POWER":
                target = s.LOW_POWER_EXIT
            else:
                if s.battery_level < s.LOW_POWER_EXIT:
                    target = s.LOW_POWER_EXIT
                else:
                    target = s.SAFE_EXIT_BATTERY

            if s.battery_level >= target:
                intent.status = IntentStatus.COMPLETED

        elif intent.intent_type == "thermal_recovery":
            if s.temperature <= s.SAFE_EXIT_TEMP + s.SAFE_EXIT_TEMP_EPSILON:
                intent.status = IntentStatus.COMPLETED
