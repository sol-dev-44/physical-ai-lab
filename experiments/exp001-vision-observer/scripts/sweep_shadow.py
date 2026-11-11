"""Try shadow-tolerant difference settings on one live frame. Nothing is saved."""

import cv2
import numpy as np
from exp001_vision_observer.camera import grab_by_name
from exp001_vision_observer.config import BACKGROUND, Arena

a = Arena.load()
bg = cv2.imread(str(BACKGROUND))
f = grab_by_name(a.camera_name or "HD Pro Webcam C920", a.zoom)


def prep(x):
    return cv2.cvtColor(cv2.GaussianBlur(x, (7, 7), 0), cv2.COLOR_BGR2LAB).astype(np.int16)


d = np.abs(prep(f) - prep(bg))
inside = np.zeros(f.shape[:2], np.uint8)
cv2.fillPoly(inside, [np.array(a.corners_px, np.int32)], 255)
inside = cv2.dilate(inside, np.ones((31, 31), np.uint8))
for chroma_t, light_t in [(30, 30), (20, 60), (25, 70), (30, 80), (20, 255), (15, 255)]:
    m = ((d[:, :, 1] > chroma_t) | (d[:, :, 2] > chroma_t) | (d[:, :, 0] > light_t)) * 255
    m = cv2.bitwise_and(m.astype(np.uint8), inside)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    cs = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    c = max(cs, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)
    (cx, cy), (bw, bh), ang = cv2.minAreaRect(c)
    print(
        f"chroma>{chroma_t} or light>{light_t}: area {int(cv2.contourArea(c))}, "
        f"x {x}-{x + w}, y {y}-{y + h}, box {bw:.0f}x{bh:.0f} @ {ang:.1f}"
    )
