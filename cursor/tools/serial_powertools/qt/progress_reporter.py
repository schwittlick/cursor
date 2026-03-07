#!/usr/bin/env python3
"""
progress_reporter.py — drop this into your Python jobs on lyrik.local

Usage:
    reporter = ProgressReporter(job_id="render-001", label="Render pass 1")
    reporter.start()

    for i, item in enumerate(my_items):
        do_work(item)
        reporter.report((i + 1) / len(my_items))

    reporter.finish()

The reporter runs a background thread and buffers updates so your main loop
is never blocked by network issues. If the server is unreachable it just
silently drops updates and keeps retrying in the background.
"""

import json
import socket
import threading
import time
import uuid


class ProgressReporter:
    def __init__(
        self,
        label: str,
        job_id: str | None = None,
        host: str = "lyrik.local",
        port: int = 9876,
        min_interval: float = 1.0,  # minimum seconds between updates
    ):
        self.job_id = job_id or str(uuid.uuid4())[:8]
        self.label = label
        self.host = host
        self.port = port
        self.min_interval = min_interval

        self._progress = 0.0
        self._done = False
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._stop = threading.Event()
        self._dirty = threading.Event()

    def start(self):
        """Call once before your work loop begins."""
        self._thread.start()
        self.report(0.0)
        return self

    def report(self, progress: float):
        """Call with a value 0.0–1.0 whenever progress changes."""
        with self._lock:
            self._progress = max(0.0, min(1.0, progress))
        self._dirty.set()

    def finish(self):
        """Call when the job is complete."""
        with self._lock:
            self._progress = 1.0
            self._done = True
        self._dirty.set()
        self._stop.set()
        self._thread.join(timeout=5)

    # ------------------------------------------------------------------
    # internal

    def _build_msg(self) -> bytes:
        with self._lock:
            payload = {
                "type": "report",
                "id": self.job_id,
                "label": self.label,
                "progress": self._progress,
                "done": self._done,
            }
        return (json.dumps(payload) + "\n").encode()

    def _send(self, data: bytes) -> bool:
        try:
            with socket.create_connection((self.host, self.port), timeout=3) as s:
                s.sendall(data)
            return True
        except OSError:
            return False

    def _run(self):
        last_sent = 0.0
        while not self._stop.is_set():
            self._dirty.wait(timeout=self.min_interval)
            self._dirty.clear()
            now = time.monotonic()
            if now - last_sent >= self.min_interval:
                msg = self._build_msg()
                if self._send(msg):
                    last_sent = now
        # final send to ensure done=true reaches server
        self._send(self._build_msg())


# ----------------------------------------------------------------------
# Example usage — remove when integrating into your real app
if __name__ == "__main__":
    import random

    reporter = ProgressReporter(label="Test job")
    reporter.start()

    steps = 50
    for i in range(steps):
        time.sleep(random.uniform(0.05, 0.2))
        reporter.report((i + 1) / steps)
        print(f"  step {i + 1}/{steps}  ({(i + 1) / steps * 100:.1f}%)")

    reporter.finish()
    print("Done.")
