"""LivePose: the latest robot pose from a camera, for the gate's interlocks and the judge.

Each frame is tracked and dropped. Nothing but numbers is kept (ADR 0007): no frame is
written anywhere by this module.
"""

from __future__ import annotations

import math
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field

from lab_agent.interlocks import Pose

from .camera import Camera
from .tracker import Tracker

# The blaster's hold() returns when the RM4 has finished playing the move; after that the
# robot coasts and the webcam may hand out a buffered frame or two. Wait this long, then
# let settle() demand fresh, agreeing fixes.
COAST_S = 0.4


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
    #: Heading comes from movement, not the tracker: refresh() uses `heading` (NaN until
    #: the first move sets it with set_heading).
    motion_heading: bool = False
    heading: float = math.nan
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
            h = self.heading if self.motion_heading else fix.heading_deg
            self._pose = Pose(fix.x_cm, fix.y_cm, h, t)
            return self._pose

    def set_heading(self, heading_deg: float) -> None:
        """Heading learned from a move (motion_heading mode); also updates the last pose."""
        with self._lock:
            self.heading = heading_deg
            if self._pose is not None:
                p = self._pose
                self._pose = Pose(p.x_cm, p.y_cm, heading_deg, p.t)

    def latest(self) -> Pose | None:
        with self._lock:
            return self._pose

    def settle(
        self,
        frames: int = 3,
        *,
        after_s: float = 0.0,
        tol_cm: float = 0.7,
        timeout_s: float = 3.0,
    ) -> Pose | None:
        """Where the robot is once it has stopped: wait `after_s` (a hold is played by the
        device after the send returns), then until `frames` fresh fixes in a row agree
        within `tol_cm`. Returns the last of them, or None if that doesn't happen in
        `timeout_s` (lost, or still moving). Never returns an old pose: a frame that isn't
        tracked breaks the run of agreeing fixes. With the background thread running it
        waits for that thread's fixes instead of reading the camera itself."""
        if after_s > 0:
            time.sleep(after_s)
        need = max(1, frames)
        deadline = time.monotonic() + timeout_s
        recent: list[Pose] = []
        seen: tuple[int, int] | None = None  # (frames, fixes) already looked at
        while time.monotonic() < deadline:
            if self._thread is not None:
                time.sleep(0.03)
                with self._lock:
                    counts, pose = (self.stats.frames, self.stats.fixes), self._pose
                if seen is None or counts[0] == seen[0]:
                    seen = seen or counts
                    continue  # no new frame yet
                all_tracked = counts[1] - seen[1] == counts[0] - seen[0]
                seen = counts
                if not all_tracked or pose is None:
                    recent = []  # a frame went by without a fix
                    continue
            else:
                pose = self.refresh()
                if pose is None:
                    recent = []
                    continue
            recent = [*recent, pose][-need:]
            if len(recent) == need and all(
                abs(q.x_cm - pose.x_cm) <= tol_cm and abs(q.y_cm - pose.y_cm) <= tol_cm
                for q in recent
            ):
                return pose
        return None

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
