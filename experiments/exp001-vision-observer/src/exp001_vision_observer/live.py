"""LivePose: the latest robot pose from a camera, for the gate's interlocks and the judge.

Each frame is tracked and dropped. Nothing but numbers is kept (ADR 0007): no frame is
written anywhere by this module.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field

from lab_agent.interlocks import Pose

from .camera import Camera
from .tracker import Tracker


@dataclass
class Stats:
    frames: int = 0
    fixes: int = 0

    @property
    def fix_rate(self) -> float:
        return self.fixes / self.frames if self.frames else 0.0


@dataclass
class LivePose:
    camera: Camera
    tracker: Tracker
    clock: Callable[[], float] = time.monotonic
    stats: Stats = field(default_factory=Stats)
    _pose: Pose | None = None
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _thread: threading.Thread | None = None
    _stop: threading.Event = field(default_factory=threading.Event)

    def refresh(self) -> Pose | None:
        """Read and track one frame now. Returns the new pose, or None if not found."""
        frame = self.camera.read()
        t = self.clock()
        fix = self.tracker.find(frame) if frame is not None else None
        del frame  # frames are never kept
        with self._lock:
            self.stats.frames += 1
            if fix is None:
                return None
            self.stats.fixes += 1
            self._pose = Pose(fix.x_cm, fix.y_cm, fix.heading_deg, t)
            return self._pose

    def latest(self) -> Pose | None:
        with self._lock:
            return self._pose

    def settle(self, frames: int = 5) -> Pose | None:
        """A few fresh frames, so a judgement uses where the robot ended up."""
        pose = None
        for _ in range(frames):
            pose = self.refresh() or pose
        return pose

    def start(self, hz: float = 15.0) -> None:
        """Track in the background so interlocks always see a recent fix."""
        if self._thread:
            return

        def loop() -> None:
            while not self._stop.is_set():
                self.refresh()
                self._stop.wait(1 / hz)

        self._thread = threading.Thread(target=loop, name="live-pose", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)
        self.camera.close()
