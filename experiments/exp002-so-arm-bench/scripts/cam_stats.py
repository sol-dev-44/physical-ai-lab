"""Numbers-only check of one camera's light and focus. Writes nothing to disk.

Opens the camera at the recording size (640x480), waits 3 s for exposure to settle, then
reads frames for 5 s and prints brightness, clipping, sharpness and drift.
Run it in a terminal, not a background shell. Usage: python cam_stats.py [index]
"""

import sys
import time

import cv2
import numpy as np

index = int(sys.argv[1]) if len(sys.argv) > 1 else 1
cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
if not cap.isOpened():
    print(f"camera {index}: not opened", flush=True)
    sys.exit(1)

end_warmup = time.time() + 3
while time.time() < end_warmup:
    cap.read()

means, sharps, highs, lows, bgr = [], [], [], [], []
end = time.time() + 5
while time.time() < end:
    ok, frame = cap.read()
    if not ok:
        continue
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    means.append(float(gray.mean()))
    sharps.append(float(cv2.Laplacian(gray, cv2.CV_64F).var()))
    highs.append(float((gray >= 250).mean() * 100))
    lows.append(float((gray <= 5).mean() * 100))
    bgr.append(frame.reshape(-1, 3).mean(axis=0))
cap.release()

if not means:
    print(f"camera {index}: no frames", flush=True)
    sys.exit(1)

h, w = frame.shape[:2]
b, g, r = np.mean(bgr, axis=0)
print(f"camera {index}: {len(means)} frames at {w}x{h}", flush=True)
print(f"brightness mean {np.mean(means):.0f} (aim 80 to 180)", flush=True)
print(f"brightness drift {np.std(means):.1f} (under 2 is steady)", flush=True)
print(f"blown out {np.mean(highs):.2f}% (under 1% is good)", flush=True)
print(f"crushed dark {np.mean(lows):.2f}% (under 1% is good)", flush=True)
print(f"sharpness {np.mean(sharps):.0f} (over 100 is usually in focus)", flush=True)
print(f"sharpness drift {np.std(sharps):.0f} (large means focus is hunting)", flush=True)
print(f"color mean R {r:.0f} G {g:.0f} B {b:.0f}", flush=True)
