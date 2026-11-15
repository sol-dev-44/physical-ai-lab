"""Read-only probe: try camera indexes 0 to 3 and report which return a frame.

Writes nothing to disk. Run it in a terminal, not a background shell.
"""

import cv2

for index in range(4):
    cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        print(f"index {index}: not opened", flush=True)
        cap.release()
        continue
    ok, frame = cap.read()
    if ok:
        h, w = frame.shape[:2]
        print(f"index {index}: frame {w}x{h}", flush=True)
    else:
        print(f"index {index}: opened but no frame", flush=True)
    cap.release()
print("probe done", flush=True)
