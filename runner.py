import threading
import time


class OrchestrationRunner:
    """
    Runs the orchestrator in a background loop.
    """

    def __init__(self, orchestrator, interval_seconds=2.0):
        self.orchestrator = orchestrator
        self.interval = interval_seconds
        self._running = False
        self._thread = None

    def start(self):
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _loop(self):
        while self._running:
            self.orchestrator.run(cycles=1)
            time.sleep(self.interval)