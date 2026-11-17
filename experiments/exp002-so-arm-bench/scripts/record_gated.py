"""lerobot-record with a motion gate: only frames worth training on are saved.

Episodes also end themselves.

Same arguments as lerobot-record. While an episode records:
  - frames before you start moving are held back, not saved; the 3 frames just before the first
    move are kept, so the policy still sees the start pose;
  - once the arm is folded back to rest (shoulder lift and elbow within 5 degrees of the start)
    and every joint has stayed within 2 degrees for 1 s, the episode ends on its own
    (no waiting for the episode timer). The reset phase then runs as usual.
  - if you never move, the episode keeps its last 3 frames, and audit.py will flag it.
Thresholds match trim_idle.py and audit.py. The reset phase (no dataset) is untouched.

Why: about 37% of exp002's first 125 episodes were the arm sitting still (median 3.2 s before the
first move, 7 s at rest after), and v4 learned to wait at rest from it (2026-11-17).

Usage: python record_gated.py <lerobot-record arguments>
"""

from collections import deque

import numpy as np

MOVE_DEG = 2.0
LEAD_FRAMES = 3
STILL_FRAMES = 30  # still = every joint stays within a MOVE_DEG range for this many frames (1 s)
REST_JOINTS = (1, 2)  # shoulder_lift and elbow_flex fold the arm; wrist and gripper settle anywhere
REST_TOL_DEG = 5.0  # back within this of the start pose on the REST_JOINTS
MIN_MOVING_FRAMES = 90  # never end in the first 3 s after the first move


class MotionGate:
    """Decides frame by frame what to keep.

    Pure logic, so it can be replayed on recorded episodes.
    """

    def __init__(self) -> None:
        self.first: np.ndarray | None = None
        self.prev: np.ndarray | None = None
        self.held: deque = deque(maxlen=LEAD_FRAMES)
        self.open = False
        self.kept = 0
        self.recent: deque = deque(maxlen=STILL_FRAMES)
        self.done = False

    def offer(self, action: np.ndarray, frame: object) -> list:
        """Return the frames to save now (possibly none)."""
        a = np.asarray(action, dtype=np.float64)
        if self.first is None:
            self.first = a
        self.prev = a
        if not self.open:
            if np.abs(a - self.first).max() > MOVE_DEG:
                self.open = True
                out = [*self.held, frame]
                self.held.clear()
                self.kept += len(out)
                return out
            self.held.append(frame)
            return []
        self.kept += 1
        self.recent.append(a)
        window = np.stack(self.recent)
        still = (
            len(self.recent) == STILL_FRAMES
            and (window.max(axis=0) - window.min(axis=0)).max() < MOVE_DEG
        )
        at_rest = np.abs(a - self.first)[list(REST_JOINTS)].max() < REST_TOL_DEG
        if self.kept >= MIN_MOVING_FRAMES and still and at_rest:
            self.done = True
        return [frame]

    def leftovers(self) -> list:
        """Frames to save if the gate never opened, so the episode is not empty."""
        return [] if self.open else list(self.held)


def install() -> None:
    import lerobot.scripts.lerobot_record as rec

    original_loop = rec.record_loop

    def gated_loop(robot, events, fps, *args, dataset=None, **kwargs):
        if dataset is None:
            return original_loop(robot, events, fps, *args, dataset=dataset, **kwargs)
        gate = MotionGate()
        real_add = dataset.add_frame

        def add_frame(frame: dict) -> None:
            for f in gate.offer(frame["action"], frame):
                real_add(f)
            if gate.done:
                events["exit_early"] = True

        dataset.add_frame = add_frame
        try:
            return original_loop(robot, events, fps, *args, dataset=dataset, **kwargs)
        finally:
            dataset.add_frame = real_add
            for f in gate.leftovers():
                real_add(f)
            how = "ended at rest" if gate.done else ("timer" if gate.open else "NO MOTION")
            print(
                f"[gate] episode kept {gate.kept + len(gate.leftovers())} frames ({how})",
                flush=True,
            )

    rec.record_loop = gated_loop


if __name__ == "__main__":
    install()
    import lerobot.scripts.lerobot_record as rec

    rec.main()
