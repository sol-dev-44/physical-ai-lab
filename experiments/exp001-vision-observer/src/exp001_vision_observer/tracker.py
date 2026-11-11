"""Find the robot in a frame: two coloured markers, mapped to arena centimetres.

Pure functions on numpy arrays. Frames are never stored; only the pose leaves here.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import cv2
import numpy as np

from .config import Arena, HsvRange


@dataclass(frozen=True)
class Blob:
    x_px: float
    y_px: float
    area_px: float


@dataclass(frozen=True)
class Fix:
    """Where the robot is in one frame. x, y: midpoint of the markers; heading: tail to head."""

    x_cm: float
    y_cm: float
    heading_deg: float
    head: Blob
    tail: Blob


def _wrap(deg: float) -> float:
    return (deg + 180) % 360 - 180


def mask(hsv: np.ndarray, r: HsvRange) -> np.ndarray:
    lo, hi = np.array(r.lo, np.uint8), np.array(r.hi, np.uint8)
    if r.lo[0] <= r.hi[0]:
        return cv2.inRange(hsv, lo, hi)
    # hue wraps around 0 (reds): two ranges
    a = cv2.inRange(hsv, lo, np.array((179, r.hi[1], r.hi[2]), np.uint8))
    b = cv2.inRange(hsv, np.array((0, r.lo[1], r.lo[2]), np.uint8), hi)
    return cv2.bitwise_or(a, b)


def find_blob(hsv: np.ndarray, r: HsvRange, min_area_px: int) -> Blob | None:
    """The largest blob of this colour, or None."""
    m = cv2.morphologyEx(mask(hsv, r), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    contours, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    c = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(c)
    if area < min_area_px:
        return None
    mo = cv2.moments(c)
    return Blob(mo["m10"] / mo["m00"], mo["m01"] / mo["m00"], area)


class Tracker:
    def __init__(self, arena: Arena) -> None:
        self.arena = arena
        src = np.array(arena.corners_px, np.float32)
        w, h = arena.width_cm, arena.height_cm
        dst = np.array([(0, 0), (w, 0), (w, h), (0, h)], np.float32)
        self.px_to_cm = cv2.getPerspectiveTransform(src, dst)
        self.cm_to_px = cv2.getPerspectiveTransform(dst, src)

    def to_cm(self, x_px: float, y_px: float) -> tuple[float, float]:
        p = cv2.perspectiveTransform(np.array([[[x_px, y_px]]], np.float32), self.px_to_cm)
        return float(p[0, 0, 0]), float(p[0, 0, 1])

    def to_px(self, x_cm: float, y_cm: float) -> tuple[float, float]:
        p = cv2.perspectiveTransform(np.array([[[x_cm, y_cm]]], np.float32), self.cm_to_px)
        return float(p[0, 0, 0]), float(p[0, 0, 1])

    def find(self, frame_bgr: np.ndarray) -> Fix | None:
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        mk = self.arena.markers
        head = find_blob(hsv, mk.head, mk.min_area_px)
        tail = find_blob(hsv, mk.tail, mk.min_area_px)
        if head is None or tail is None:
            return None
        hx, hy = self.to_cm(head.x_px, head.y_px)
        tx, ty = self.to_cm(tail.x_px, tail.y_px)
        heading = math.degrees(math.atan2(hy - ty, hx - tx)) + self.arena.heading_offset_deg
        return Fix((hx + tx) / 2, (hy + ty) / 2, _wrap(heading), head, tail)


class BackgroundTracker(Tracker):
    """The robot is the biggest region that differs from the empty arena; the front-marker
    colour *inside* that region gives the heading. The floor can share the marker's colour
    (it isn't searched), and static glare is part of the background."""

    def __init__(self, arena: Arena, background_bgr: np.ndarray) -> None:
        super().__init__(arena)
        self.cfg = arena.background
        self.bg = self._prep(background_bgr)
        h, w = background_bgr.shape[:2]
        self.inside = np.zeros((h, w), np.uint8)
        poly = np.array(arena.corners_px, np.int32)
        cv2.fillPoly(self.inside, [poly], 255)
        # the robot can overhang the edge a little; look slightly beyond the corners
        self.inside = cv2.dilate(self.inside, np.ones((31, 31), np.uint8))

    @staticmethod
    def _prep(frame_bgr: np.ndarray) -> np.ndarray:
        lab = cv2.cvtColor(cv2.GaussianBlur(frame_bgr, (7, 7), 0), cv2.COLOR_BGR2LAB)
        return lab.astype(np.int16)

    def robot_mask(self, frame_bgr: np.ndarray) -> np.ndarray:
        cur = self._prep(frame_bgr)
        # The webcam re-balances exposure and colour on its own (a dark robot entering view
        # shifts the whole picture). Measure that global shift as the median difference over
        # the arena, where the robot is a minority, and take it out before comparing.
        inside = self.inside > 0
        shift = np.median((cur - self.bg)[inside], axis=0).astype(np.int16)
        d = np.abs(cur - shift - self.bg)
        changed = (
            (d[:, :, 1] > self.cfg.chroma_threshold)
            | (d[:, :, 2] > self.cfg.chroma_threshold)
            | (d[:, :, 0] > self.cfg.light_threshold)
        )
        m = np.where(changed, 255, 0).astype(np.uint8)
        m = cv2.bitwise_and(m, self.inside)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))

    def find(self, frame_bgr: np.ndarray) -> Fix | None:
        if frame_bgr.shape[:2] != self.bg.shape[:2]:
            return None
        m = self.robot_mask(frame_bgr)
        contours, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        body = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(body)
        if not self.cfg.min_robot_px <= area <= self.cfg.max_robot_px:
            return None  # nothing there, or something that isn't the robot
        mo = cv2.moments(body)
        cx, cy = mo["m10"] / mo["m00"], mo["m01"] / mo["m00"]
        only_body = np.zeros_like(m)
        cv2.drawContours(only_body, [body], -1, 255, -1)
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        front = cv2.bitwise_and(mask(hsv, self.arena.markers.head), only_body)
        n = int(cv2.countNonZero(front))
        if n < self.cfg.min_front_px:
            return None  # can't tell front from back
        fm = cv2.moments(front, binaryImage=True)
        fx, fy = fm["m10"] / fm["m00"], fm["m01"] / fm["m00"]
        head = Blob(fx, fy, float(n))
        # Heading: back marker -> front marker when the back colour shows inside the body
        # (steady, even if the front marker sits near the middle); else centre -> front.
        back = cv2.bitwise_and(mask(hsv, self.arena.markers.tail), only_body)
        nb = int(cv2.countNonZero(back))
        if nb >= self.cfg.min_front_px:
            bm = cv2.moments(back, binaryImage=True)
            tail = Blob(bm["m10"] / bm["m00"], bm["m01"] / bm["m00"], float(nb))
        else:
            tail = Blob(2 * cx - fx, 2 * cy - fy, 0.0)  # mirrored through the body centre
        bx, by = self.to_cm(cx, cy)
        hx, hy = self.to_cm(fx, fy)
        tx, ty = self.to_cm(tail.x_px, tail.y_px)
        heading = math.degrees(math.atan2(hy - ty, hx - tx)) + self.arena.heading_offset_deg
        return Fix(bx, by, _wrap(heading), head, tail)


def make_tracker(arena: Arena) -> Tracker:
    """The tracker arena.json asks for."""
    if arena.tracking == "markers":
        return Tracker(arena)
    from .config import BACKGROUND

    if not BACKGROUND.exists():
        raise FileNotFoundError(
            f"tracking is 'background' but {BACKGROUND} is missing: run `exp001 background`"
        )
    bg = cv2.imread(str(BACKGROUND), cv2.IMREAD_COLOR)
    return BackgroundTracker(arena, bg)
