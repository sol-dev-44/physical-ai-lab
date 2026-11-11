"""Print what the background tracker sees in one live frame: blob size, box, markers,
and the heading from markers vs from the body's box edges. Nothing is saved."""

import math

import cv2
import numpy as np
from exp001_vision_observer.camera import grab_by_name
from exp001_vision_observer.config import Arena
from exp001_vision_observer.tracker import make_tracker, mask

a = Arena.load()
tr = make_tracker(a)
f = grab_by_name(a.camera_name or "HD Pro Webcam C920", a.zoom)
m = tr.robot_mask(f)
cs = sorted(cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0], key=cv2.contourArea)
print("blobs (largest last):", [int(cv2.contourArea(c)) for c in cs[-4:]])
body = cs[-1]
(cx, cy), (w, h), ang = cv2.minAreaRect(body)
print(f"body box centre ({cx:.0f},{cy:.0f}) px, {w:.0f}x{h:.0f} px, angle {ang:.1f}")
x, y, bw, bh = cv2.boundingRect(body)
print(f"bounding box x {x}-{x + bw}, y {y}-{y + bh}")
hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
only = np.zeros_like(m)
cv2.drawContours(only, [body], -1, 255, -1)
for name, r in (("front", a.markers.head), ("back", a.markers.tail)):
    mk = cv2.bitwise_and(mask(hsv, r), only)
    n = cv2.countNonZero(mk)
    if n:
        mo = cv2.moments(mk, binaryImage=True)
        print(f"{name}: {n} px at ({mo['m10'] / mo['m00']:.0f},{mo['m01'] / mo['m00']:.0f})")
    else:
        print(f"{name}: none")
fix = tr.find(f)
print("tracker:", fix and f"({fix.x_cm:.1f}, {fix.y_cm:.1f}) cm, {fix.heading_deg:.0f} deg")


def arena_dir(dx: float, dy: float) -> float:
    p0, p1 = tr.to_cm(cx, cy), tr.to_cm(cx + dx, cy + dy)
    return math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))


r = math.radians(ang)
dirs = [round(arena_dir(30 * math.cos(r + k * math.pi / 2), 30 * math.sin(r + k * math.pi / 2)))
        for k in range(4)]  # fmt: skip
print("box edge directions (deg):", dirs)
