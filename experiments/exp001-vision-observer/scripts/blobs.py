"""List every region that differs from the empty arena, with marker pixels in each.
Nothing is saved."""

import cv2
import numpy as np
from exp001_vision_observer.camera import OpenCVCamera
from exp001_vision_observer.config import Arena
from exp001_vision_observer.tracker import make_tracker, mask

a = Arena.load()
tr = make_tracker(a)
cam = OpenCVCamera(a.camera_index, zoom=a.zoom)
for _ in range(10):
    f = cam.read()
cam.close()
m = tr.robot_mask(f)
hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
cs = sorted(cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0],
            key=cv2.contourArea, reverse=True)  # fmt: skip
for c in cs[:6]:
    x, y, w, h = cv2.boundingRect(c)
    only = np.zeros_like(m)
    cv2.drawContours(only, [c], -1, 255, -1)
    g = cv2.countNonZero(cv2.bitwise_and(mask(hsv, a.markers.head), only))
    o = cv2.countNonZero(cv2.bitwise_and(mask(hsv, a.markers.tail), only))
    cx, cy = tr.to_cm(x + w / 2, y + h / 2)
    print(
        f"area {cv2.contourArea(c):7.0f}px  box x{x}-{x + w} y{y}-{y + h}  ~({cx:.0f},{cy:.0f})cm"
        f"  green {g}px orange {o}px"
    )
fix = tr.find(f)
print("tracker:", fix and f"({fix.x_cm:.1f}, {fix.y_cm:.1f}) cm {fix.heading_deg:.0f} deg")
