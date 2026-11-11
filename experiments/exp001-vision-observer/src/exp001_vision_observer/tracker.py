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
        heading = math.degrees(math.atan2(hy - ty, hx - tx))
        return Fix((hx + tx) / 2, (hy + ty) / 2, heading, head, tail)
