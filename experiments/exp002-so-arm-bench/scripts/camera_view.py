"""Live view of one camera for aiming it. Press q in the window to quit.

Opens the camera at the recording size (640x480) so the view matches what the policy sees.
Draws a center cross and a rule-of-thirds grid. Writes nothing to disk.
Run it in a terminal, not a background shell. Usage: python camera_view.py [index]
"""

import sys

import cv2

index = int(sys.argv[1]) if len(sys.argv) > 1 else 0
cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
if not cap.isOpened():
    print(f"camera {index}: not opened", flush=True)
    sys.exit(1)

window = f"camera {index} (q to quit)"
print(f"camera {index} open, press q in the window to quit", flush=True)
while True:
    ok, frame = cap.read()
    if not ok:
        print(f"camera {index}: no frame", flush=True)
        break
    h, w = frame.shape[:2]
    for i in (1, 2):
        cv2.line(frame, (w * i // 3, 0), (w * i // 3, h), (200, 200, 200), 1)
        cv2.line(frame, (0, h * i // 3), (w, h * i // 3), (200, 200, 200), 1)
    cv2.drawMarker(frame, (w // 2, h // 2), (0, 255, 255), cv2.MARKER_CROSS, 30, 2)
    cv2.imshow(window, frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("camera closed", flush=True)
