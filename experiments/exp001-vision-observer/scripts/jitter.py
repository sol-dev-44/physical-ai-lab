"""Pose readings of a still robot: is the tracker steady? Frames are never saved."""

import time

from exp001_vision_observer.camera import OpenCVCamera
from exp001_vision_observer.config import Arena
from exp001_vision_observer.tracker import make_tracker

a = Arena.load()
tr = make_tracker(a)
cam = OpenCVCamera(a.camera_index, zoom=a.zoom)
for _ in range(10):
    cam.read()
for i in range(20):
    f = cam.read()
    fix = tr.find(f) if f is not None else None
    if fix:
        print(
            f"{i:2d} ({fix.x_cm:5.1f}, {fix.y_cm:5.1f}) {fix.heading_deg:6.1f} deg"
            f"  front {fix.head.area_px:.0f}px back {fix.tail.area_px:.0f}px",
            flush=True,
        )
    else:
        print(f"{i:2d} not tracked", flush=True)
    time.sleep(0.1)
cam.close()
