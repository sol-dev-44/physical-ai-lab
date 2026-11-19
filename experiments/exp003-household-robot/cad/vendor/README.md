# Vendored models

## STS3215_03a.step

The Feetech STS3215 servo with its horn, from The Robot Studio's SO-ARM100 repository,
`STEP/SO100/STS3215_03a.step` at commit `d04fa975fb79c9870df5824cce7c7390d52cac85`
(Apache-2.0, https://github.com/TheRobotStudio/SO-ARM100). Unchanged; sha256
`cacd717c2f22bec856fdace2c3bc9fa58084d54b6e70378eae90562f34df93ef`.

Use it as the starting shape for brackets and the base plate. Where it disagrees with a caliper
reading of the lab's own servo, the reading wins: the hub's numbers in `servo.toml` are measured
and already proven by two prints.

### What the model says, and what the lab's servo says

The model's frame: x along the case length, y across it, z along the output shaft. The shaft is at
x = 12.5, y = 0, and the case runs x = -22.7 to 22.7. The working numbers are in the `[case]` table
of `../servo.toml`, each marked (lab) or (model).

Checked 2026-11-19 on a spare: the case and its mounting holes match the model exactly. The horn
and the case right round it differ by 0.3 to 0.5 mm, so the hub keeps its own measured numbers.

| What | Model | Lab measurement | Notes |
|---|---|---|---|
| Case length x width | 45.4 x 24.8 mm | 45.4 x 24.8 mm | Datasheet: 45.2 x 24.7 |
| Shaft centre to the near end of the case | 10.2 mm | not measured | |
| Top-face mounting holes, centre to centre | 20.7 mm along, 20.4 mm across | 20.7, 20.4 mm | Nearer pair 8.3 mm from the shaft, other pair 29.0 mm (model). Holes are 1.5 mm in the model; thread not checked yet |
| Horn diameter, thickness | 20.0, 2.5 mm | 19.9, 2.08 mm | |
| Horn bolt circle | 13.9 mm (4 holes) | 13.6 mm | |
| Centre screw head above the horn | 1.5 mm | 2.0 mm | |
| Horn top down to the case round the shaft | 4.3 mm | 4.0 mm (H) | |
| Horn top down to the raised block | 1.7 mm | 2.0 mm (I) | The block starts 8.9 mm from the shaft centre |
| Case height, shaft end / far end | 28.8 / 32.9 mm | not measured | Far end: 1.5 mm raised strips along both long sides on top, a 1.5 mm step on the bottom |
| Horn top to bottom of case | 34.6 mm | not measured | Datasheet height: 35 |
| Bottom disc, diameter | 20.0 mm | present, not measured | An idler disc on the shaft axis, like a second horn |
| Bottom disc, how far it stands proud | 3.3 mm to its face, 3.9 mm to a 6 mm centre nub | about 4.1 mm | Both from the lowest part of the bottom face, round the shaft axis. About 0.1 mm more than the horn stands on top |

How the bottom is built in the model, from the case bottom round the shaft (z = -14.4): a 6 mm boss
for 1.2 mm, the 20 mm disc 2.1 mm thick, then a 6 mm nub 0.6 mm proud. The far end of the bottom
steps 1.5 mm lower, so the disc stands only about 1.8 mm (model) past that step.

**For anything under the servo:** the base plate cannot sit flat against the bottom. Either give it
a pocket of at least 21 mm diameter and 4.6 mm deep (4.1 plus 0.5), or hold the servo by its
top-face holes or its sides and leave air below.
