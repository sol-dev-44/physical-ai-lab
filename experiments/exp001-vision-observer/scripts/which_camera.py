"""Which index is which camera? Prints each camera's average brightness every second for
20 s. Cover one lens with your hand: its number drops. Frames are never saved."""

import time

import cv2

caps = {i: cv2.VideoCapture(i) for i in (0, 1)}
try:
    for _ in range(20):
        row = []
        for i, cap in caps.items():
            ok, frame = cap.read()
            row.append(f"camera {i}: {frame.mean():5.1f}" if ok else f"camera {i}:  n/a")
            del frame
        print("   ".join(row), flush=True)
        time.sleep(1)
finally:
    for cap in caps.values():
        cap.release()
