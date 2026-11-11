"""Cameras: a real one through OpenCV, and a simulated arena for building without hardware.

The simulator is a robot, an arena and a renderer in one: SimBlaster moves the robot the
way the real one moves (forward: straight; reverse: back and to the left), and SimCamera
draws what an overhead camera would see, markers included. The tracker then runs on those
frames exactly as it does on real ones. Simulated device ids start with "fake-".
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from typing import Protocol

import cv2
import numpy as np

from .config import Arena


class Camera(Protocol):
    def read(self) -> np.ndarray | None:
        """One BGR frame, or None if the camera gave nothing."""
        ...

    def close(self) -> None: ...


class OpenCVCamera:
    """A webcam. macOS asks once for camera permission for the app running this."""

    def __init__(self, index: int, width: int = 1280, height: int = 720) -> None:
        self.cap = cv2.VideoCapture(index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        if not self.cap.isOpened():
            raise RuntimeError(
                f"camera {index} did not open (try `exp001 cameras`; check camera permission)"
            )

    def read(self) -> np.ndarray | None:
        ok, frame = self.cap.read()
        return frame if ok else None

    def close(self) -> None:
        self.cap.release()


def list_cameras(max_index: int = 5) -> list[tuple[int, int, int]]:
    """(index, width, height) for each camera index that opens and returns a frame."""
    found = []
    for i in range(max_index + 1):
        cap = cv2.VideoCapture(i)
        try:
            ok, frame = cap.read() if cap.isOpened() else (False, None)
            if ok and frame is not None:
                found.append((i, frame.shape[1], frame.shape[0]))
        finally:
            cap.release()
    return found


# ------------------------------------------------------------------ simulation

SIM_ARENA = Arena(
    width_cm=100,
    height_cm=70,
    # mild perspective, as if the camera were a little off-centre
    corners_px=[(80, 420), (570, 430), (540, 60), (110, 50)],
)


@dataclass
class SimRobot:
    """Rough model of the exp000 toy robot; numbers to be replaced by measurement."""

    x_cm: float = 50.0
    y_cm: float = 35.0
    heading_deg: float = 0.0
    forward_cm_s: float = 18.0
    reverse_cm_s: float = 12.0
    reverse_turn_deg_s: float = 35.0  # left (positive) while reversing
    noise: float = 0.05  # relative speed noise per move
    rng: random.Random = field(default_factory=lambda: random.Random(0))

    def drive(self, code: str, seconds: float) -> None:
        k = 1 + self.rng.gauss(0, self.noise)
        steps = max(1, int(seconds * 50))
        dt = seconds / steps
        for _ in range(steps):
            if code == "robot_forward":
                v, turn = self.forward_cm_s * k, 0.0
            elif code == "robot_reverse":
                v, turn = -self.reverse_cm_s * k, self.reverse_turn_deg_s * k
            else:
                return
            self.heading_deg += turn * dt
            a = math.radians(self.heading_deg)
            self.x_cm += v * dt * math.cos(a)
            self.y_cm += v * dt * math.sin(a)


@dataclass
class SimBlaster:
    """Stands in for the RM4: hold() moves the simulated robot instead of sending IR."""

    robot: SimRobot
    realtime: bool = False
    id: str = "fake-sim-rm4"
    sent: list[str] = field(default_factory=list)

    def send(self, code_name: str) -> None:
        self.sent.append(code_name)

    def hold(self, code_name: str, seconds: float) -> int:
        self.sent.append(code_name)
        self.robot.drive(code_name, seconds)
        if self.realtime:
            time.sleep(seconds)
        return max(1, round(seconds / 0.127))


@dataclass
class SimCamera:
    """Renders the arena and robot from above, through the arena's perspective."""

    robot: SimRobot
    arena: Arena = field(default_factory=lambda: SIM_ARENA)
    size: tuple[int, int] = (640, 480)
    #: Set False to simulate the robot being covered or out of view.
    visible: bool = True

    def __post_init__(self) -> None:
        w, h = self.arena.width_cm, self.arena.height_cm
        src = np.array([(0, 0), (w, 0), (w, h), (0, h)], np.float32)
        self._m = cv2.getPerspectiveTransform(src, np.array(self.arena.corners_px, np.float32))

    def _px(self, x: float, y: float) -> tuple[int, int]:
        p = cv2.perspectiveTransform(np.array([[[x, y]]], np.float32), self._m)
        return int(round(p[0, 0, 0])), int(round(p[0, 0, 1]))

    def read(self) -> np.ndarray | None:
        img = np.full((self.size[1], self.size[0], 3), 70, np.uint8)
        floor = np.array([self._px(*c) for c in self._corners_cm()], np.int32)
        cv2.fillPoly(img, [floor], (150, 150, 150))
        for c in floor:
            cv2.circle(img, tuple(int(v) for v in c), 6, (0, 200, 255), -1)  # tape corners
        if self.visible:
            r = self.robot
            a = math.radians(r.heading_deg)
            ux, uy = math.cos(a), math.sin(a)
            cv2.circle(img, self._px(r.x_cm, r.y_cm), 18, (40, 40, 40), -1)  # body
            cv2.circle(img, self._px(r.x_cm + 4 * ux, r.y_cm + 4 * uy), 7, (40, 255, 60), -1)
            cv2.circle(img, self._px(r.x_cm - 4 * ux, r.y_cm - 4 * uy), 7, (180, 60, 255), -1)
        return img

    def _corners_cm(self) -> list[tuple[float, float]]:
        w, h = self.arena.width_cm, self.arena.height_cm
        return [(0, 0), (w, 0), (w, h), (0, h)]

    def close(self) -> None:
        pass
