"""Ask macOS for camera permission and wait for the answer, then list cameras.

OpenCV asks once and gives up immediately, so a first run from a new app always fails.
Run this from the app that will use the camera (e.g. Terminal), click Allow, and it
retries for a minute. Frames are read to check the camera works, and never saved.
"""

import time

import cv2

deadline = time.monotonic() + 60
print("Waiting for camera permission: click Allow if macOS asks...", flush=True)
while time.monotonic() < deadline:
    found = []
    for i in range(4):
        cap = cv2.VideoCapture(i)
        ok, frame = cap.read() if cap.isOpened() else (False, None)
        cap.release()
        if ok and frame is not None:
            found.append(f"camera {i}: {frame.shape[1]}x{frame.shape[0]}")
        del frame
    if found:
        print("\n".join(found))
        raise SystemExit(0)
    time.sleep(2)
print("No camera after 60 s. Check System Settings > Privacy & Security > Camera.")
raise SystemExit(1)
