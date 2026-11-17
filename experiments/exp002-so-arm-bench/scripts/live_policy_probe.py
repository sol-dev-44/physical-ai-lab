"""Feed v3 and v4 one live frame from each camera and print the actions they predict.

Moves nothing, writes nothing.

Uses the rest-pose state from a recorded episode start (it does not connect to the arm).
Run it in a terminal, not a background shell: python live_policy_probe.py
"""

import time

import cv2
import numpy as np
import torch
from lerobot.configs.policies import PreTrainedConfig
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.policies.act.modeling_act import ACTPolicy
from lerobot.policies.factory import make_pre_post_processors

OUT = "/Users/alancampbell/lerobot_outputs"
CAMS = {"box": 1, "wrist": 0}

ds = LeRobotDataset(
    "local/exp002-bowl-p32", root="/Users/alancampbell/lerobot_data/exp002-bowl-p32"
)
rest = ds[int(ds.meta.episodes["dataset_from_index"][100])]


def grab(index):
    cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    end = time.time() + 3
    while time.time() < end:
        cap.read()
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise SystemExit(f"camera {index}: no frame")
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return torch.from_numpy(rgb).permute(2, 0, 1).float() / 255


live = {f"observation.images.{k}": grab(i) for k, i in CAMS.items()}
for k in live:
    print(
        f"{k}: live mean {live[k].mean():.3f}  recorded ep100 start mean {rest[k].mean():.3f}",
        flush=True,
    )

torch.set_printoptions(precision=1, sci_mode=False)
print(f"state used {rest['observation.state']}", flush=True)
for name in ("v3", "v4"):
    path = f"{OUT}/exp002-bowl-act-50k-{name}/checkpoints/050000/pretrained_model"
    cfg = PreTrainedConfig.from_pretrained(path)
    cfg.device = "mps"
    pol = ACTPolicy.from_pretrained(path, config=cfg).to("mps").eval()
    pre, post = make_pre_post_processors(
        cfg, pretrained_path=path, preprocessor_overrides={"device_processor": {"device": "mps"}}
    )
    rec = {k: rest[k] for k in live}
    box, wrist = "observation.images.box", "observation.images.wrist"
    bright = {k: (live[k] * (rec[k].mean() / live[k].mean())).clamp(0, 1) for k in live}
    combos = (
        ("live", live),
        ("recorded", rec),
        ("live box + rec wrist", {box: live[box], wrist: rec[wrist]}),
        ("rec box + live wrist", {box: rec[box], wrist: live[wrist]}),
        ("live brightened", bright),
    )
    for label, images in combos:
        obs = {"observation.state": rest["observation.state"], **images, "task": rest["task"]}
        with torch.no_grad():
            chunk = pol.predict_action_chunk(pre(obs))
        steps = [post(chunk[:, s]).cpu().flatten() for s in (0, 50, 99)]
        moved = float(np.abs((steps[2] - rest["observation.state"]).numpy()).max())
        print(f"{name} {label:22s} max move {moved:3.0f} deg  step99 {steps[2]}", flush=True)
