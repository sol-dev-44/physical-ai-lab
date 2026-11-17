# Measuring the wheel servo for the hub

The hub bolts to the round horn on an STS3215's output shaft. Eight numbers (A to H) go into
`servo.toml`. Use one of the two **spare** STS3215s, never a motor from an arm.

## Before you start

- Servo unplugged. Leave the horn and its centre screw on: measure the servo as it will run.
- Zero the caliper with the jaws closed. Read to 0.1 mm.
- Measure each number three times and write down the middle one.
- The horn is on the output side, the side with the spline under it. If both faces have a disc,
  use the one that turns when you twist the horn by hand (gently: it is geared).

## The numbers

| Key | `servo.toml` field | What it is | How |
|---|---|---|---|
| A | `od_mm` | Horn outside diameter | Outside jaws across the horn, at its widest. |
| B | `thickness_mm` | Horn disc thickness | Outside jaws on the edge of the disc, top face to bottom face. |
| C | `bolt_count` | Screw holes around the horn | Count them. Do not count the centre screw. |
| D | `bolt_circle_mm` | Distance across the holes, centre to centre | See "Bolt circle" below. |
| E | `bolt_size` | Screw that fits the holes | See "Hole size" below. `"M2"`, `"M2.5"` or `"M3"`. |
| F | `center_head_mm` | Centre screw head diameter | Outside jaws across the head. |
| G | `center_head_height_mm` | How far that head stands above the horn face | Depth rod (see below). `0` if flush or sunk. |
| H | `shaft_height_mm` | Horn top face down to the servo case | Depth rod (see below). |

### Bolt circle (D)

**Even number of holes (4, 6, 8).** Pick two holes straight across from each other.
1. Outside jaws: measure from the **far outer edge** of one hole to the **far outer edge** of the other.
2. Inside jaws: measure one hole's diameter.
3. D = step 1 minus step 2.

**Odd number of holes.** Measure two neighbouring holes the same way (far edge to far edge,
minus one hole diameter) to get the spacing `s`, then D = s / sin(180° / C).
For 3 holes that is s × 1.155; for 5 holes, s × 1.701.

### Hole size (E)

Take an M2, an M2.5 and an M3 screw from the assortment. The right one threads in by hand
with light, even resistance for at least two turns. Do not force a bigger one: a stripped horn
has to be replaced. If none threads in and the holes are plain (not tapped), write down the hole
diameter instead and tell Claude; the hub then needs a different screw plan.

### The depth rod (G and H)

The thin rod that slides out of the end of the caliper measures depth.

- **H, shaft height.** Stand the servo on the bench, horn up. Rest the end of the caliper beam
  flat on the horn's top face, near its edge, and slide the rod down until it touches the servo
  case beside the horn. Read it.
- **G, centre screw head.** Rest the beam end flat on the centre screw head and slide the rod down
  to the horn face beside it. If the head is level with the face or below it, G = 0.

### Optional photo

A photo of the horn, straight down, with the caliper's jaws open across it helps catch mistakes.
Drop it into the chat with your numbers.

## After measuring

1. Put the numbers in `servo.toml` and set `measured = true`.
2. Build (see `README.md`). The build refuses impossible numbers and says which one to re-measure.
3. Print `hub_coupon.step` and check the fit (see `README.md`, "Coupon check").
