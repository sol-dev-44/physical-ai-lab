"""The electronics deck's layout (derive_deck): placement, grid holes, screws, collisions.
No CadQuery needed."""

import math
from dataclasses import replace
from pathlib import Path

import pytest
from exp003_cad.params import (
    JACK_THREAD_MM,
    M3_MIN_ENGAGE_MM,
    UCTRONICS_MM,
    BaseLayout,
    BasePlate,
    Caster,
    CasterCup,
    Cradle,
    Deck,
    derive_base_plate,
    derive_deck,
    kit_screw,
    load,
    load_case,
)

SERVO = Path(__file__).resolve().parents[1] / "servo.toml"
# The plate exactly as build.py's _plate() makes it.
PLATE = derive_base_plate(
    load_case(SERVO), load(SERVO).horn, Cradle(), Caster(), BaseLayout(), BasePlate(), CasterCup()
)
D = derive_deck(PLATE)


def boxes(name):
    return [b for b in D.boxes if b.name == name]


def deck(**kw):
    return derive_deck(PLATE, replace(Deck(), **kw))


def test_pi_sits_where_the_spec_puts_it_on_coupon_bosses():
    assert sorted(D.compute.bosses) == [
        (-140.5, 62.5),
        (-140.5, 120.5),
        (-91.5, 62.5),
        (-91.5, 120.5),
    ]
    (pi,) = boxes("Pi 5")
    assert (pi.x0, pi.x1, pi.y1) == (-144.0, -88.0, 124.0)
    # Coupon boss (7 mm) plus the 11 mm standoff, less 2 mm room for pins under the board.
    assert pi.z0 == pytest.approx(7.0 + 11.0 - 2.0)


def test_uctronics_cradle_uses_the_measured_board_and_the_coupon_width():
    (u,) = boxes("UCTRONICS")
    assert u.y1 - u.y0 == pytest.approx(UCTRONICS_MM[0]) == pytest.approx(63.5)
    assert u.x1 - u.x0 == pytest.approx(27.3)
    back, front = D.compute.walls
    assert front.x0 - back.x1 == pytest.approx(27.6)
    assert (u.x0, u.x1) == pytest.approx((-179.15, -151.85))
    assert len(D.compute.ties) == 2


def test_servo_board_is_centred_over_the_cup_above_its_nuts_and_tips():
    assert PLATE.caster_xy == (-158.0, 0.0)
    assert sorted(D.bridge.bosses) == [
        (-176.5, -14.0),
        (-176.5, 14.0),
        (-139.5, -14.0),
        (-139.5, 14.0),
    ]
    assert D.cup_reach_mm == pytest.approx(12.0)  # the cup's M3 x 16 tips
    assert D.bridge.boss_bottom_mm == pytest.approx(13.0)
    assert D.bridge.platform_z_mm[1] >= 15.0
    assert D.bridge.platform_z_mm == pytest.approx((17.0, 20.0))


def test_bridge_posts_stand_on_grid_holes_outside_the_cup():
    cx, cy = PLATE.caster_xy
    for x, y in D.bridge.posts:
        assert (x, y) in PLATE.grid_holes
        assert math.hypot(x - cx, y - cy) - D.bridge.post_mm / 2 >= 37.0


def test_power_tray_places_the_drok_switch_and_jack():
    (drok,) = boxes("DROK")
    assert (drok.y0 + drok.y1) / 2 == pytest.approx(-100.0)
    assert drok.x1 - drok.x0 == pytest.approx(57.0)
    front, back = D.power.pads
    # The slots cover ear holes 54 to 68 mm apart.
    for p in (front, back):
        cx = (p.slot[0] + p.slot[1]) / 2
        assert (p.slot[1] - p.slot[0]) - 3.4 == pytest.approx(7.0)
        assert abs(abs(cx - (-118.0)) - 30.5) < 1e-6
    assert D.power.panel.x0 == pytest.approx(-179.0)  # inset so the paddle stays on the plate
    assert D.power.panel.x1 - D.power.panel.x0 == pytest.approx(2.0)
    _, _, across, tall = D.power.rocker_cutout
    assert (across, tall) == pytest.approx((13.4, 19.4))  # the coupon's snug cutout, upright
    assert D.power.jack_hole[2] == pytest.approx(JACK_THREAD_MM + 1.0) == pytest.approx(12.4)


def test_each_part_bolts_down_with_its_own_grid_holes():
    holes = [*D.compute.holes, *D.bridge.posts, *D.power.holes]
    assert len(holes) == len(set(holes)) == 12
    assert all(h in PLATE.grid_holes for h in holes)
    assert sorted(D.compute.holes) == [
        (-135.0, 80.0),
        (-135.0, 100.0),
        (-95.0, 80.0),
        (-95.0, 100.0),
    ]
    # (-175, -100) would put its nut under the inset switch panel, so the power tray takes four
    # holes under and beside the DROK.
    assert sorted(D.power.holes) == [
        (-135.0, -100.0),
        (-135.0, -80.0),
        (-115.0, -100.0),
        (-95.0, -80.0),
    ]


def test_screw_lengths_come_from_the_kit_with_three_threads_in_the_nut():
    assert kit_screw(4.0 + 3.0, "tray") == 12  # plate + floor: 8.5 needed
    assert kit_screw(4.0 + 2.0, "thin") == 8
    with pytest.raises(ValueError, match="longer than the kit"):
        kit_screw(19.0, "too long")
    assert D.compute.screw_mm == D.power.screw_mm == 12
    assert D.bridge.screw_mm == 12  # plate 4 + the post's 5 mm under the nut
    assert D.power.ear_screw_mm == 8
    for ear in (1.5, 3.5):  # the ears' thickness is unknown: 8 mm suits the whole range
        engaged = 8 - ear - 3.0
        assert engaged >= M3_MIN_ENGAGE_MM
        assert 9.0 + ear - 8 >= 0.5  # tip stays above the plate in the channel


def test_screw_tips_stay_under_whatever_sits_above():
    for b in D.boxes:
        if b.kind == "hardware":
            assert b.z1 == pytest.approx(8.0)  # M3 x 12 through 4 mm plate
    (drok,) = boxes("DROK")
    assert drok.z0 > 8.0


def test_fasteners_add_up():
    f = D.fasteners
    assert f["M3 x 12 (trays to plate)"] == 8
    assert f["M3 x 12 (bridge posts to plate)"] == 4
    assert f["M3 x 8 (DROK ears)"] == 2
    assert f["M3 nuts"] == 14
    assert f["M2.5 nuts"] == 8 and f["zip ties"] == 8


def test_every_part_fits_the_bed():
    for owner in ("compute tray", "servo bridge", "power tray"):
        bs = [b for b in D.boxes if b.owner == owner and b.kind == "part"]
        dx = max(b.x1 for b in bs) - min(b.x0 for b in bs)
        dy = max(b.y1 for b in bs) - min(b.y0 for b in bs)
        assert dx <= 300 and dy <= 320


def test_rocker_paddle_stays_inside_the_plates_back_edge():
    # Bezel and paddle up to 10 mm proud of the panel face: the tip keeps 1 mm of plate behind it.
    assert Deck().rocker_front_mm == 10.0
    assert D.power.panel.x0 - Deck().rocker_front_mm >= PLATE.x_back_mm + 1.0 - 1e-9
    assert D.rocker_inside_mm == pytest.approx(1.0)
    with pytest.raises(ValueError, match="paddle"):
        deck(panel_x_mm=-180.0)  # 1 mm further back: the paddle tip is on the edge


def test_a_part_moved_onto_the_cup_raises():
    floor = (*Deck().power_floor, (-150.0, -130.0, -34.0, -20.0))  # a tray reaching under
    with pytest.raises(ValueError, match="power tray floor 5 hits the caster cup"):
        deck(power_floor=floor)
    with pytest.raises(ValueError, match="hits the caster cup"):
        deck(cup_clearance_mm=-2.0)  # the bridge's bosses down among the cup's nuts


def test_bridge_posts_must_be_grid_holes():
    with pytest.raises(ValueError, match="not on a grid hole"):
        deck(posts=((-158.0, 30.0), (-175.0, -40.0), (-135.0, -40.0), (-115.0, 0.0)))


def test_the_specs_example_post_under_the_pi_raises():
    with pytest.raises(ValueError, match="collides"):
        deck(posts=((-175.0, 40.0), (-175.0, -40.0), (-135.0, -40.0), (-135.0, 40.0)))


def test_servo_board_on_short_standoffs_would_plug_into_the_pi():
    with pytest.raises(ValueError, match="Pi 5 collides with servo board USB-C"):
        deck(servo_standoff_mm=11.0)


def test_uctronics_moved_inboard_hits_a_bridge_post():
    with pytest.raises(ValueError, match="UCTRONICS input leads collides with bridge post"):
        deck(uct_y0_mm=50.0)


def test_uctronics_plug_off_the_plate_side_raises():
    with pytest.raises(ValueError, match="off the base plate"):
        deck(uct_y0_mm=56.0)


def test_drok_onto_the_ina226_raises():
    with pytest.raises(ValueError, match="collides|grid holes"):
        deck(drok_xy=(-140.0, -100.0))


def test_fuses_into_the_strap_slots_raise():
    with pytest.raises(ValueError, match="strap|deck's front"):
        deck(fuse_x_mm=(-120.0, -80.0))


def test_panel_off_the_plate_raises():
    with pytest.raises(ValueError, match="off the base plate"):
        deck(panel_x_mm=-189.5, rocker_front_mm=0.0)


def test_part_round_the_corner_radius_raises():
    floor = (*Deck().power_floor[:-1], (-179.0, -140.0, -130.5, -110.0))
    with pytest.raises(ValueError, match="off the base plate"):
        deck(power_floor=floor)


def test_a_tie_slot_under_a_gusset_raises():
    with pytest.raises(ValueError, match="zip-tie slot .* is under the panel gusset"):
        deck(gusset_mm=(2.0, 14.0))  # reaches over the INA226's back tie


def test_rocker_into_the_droks_back_ear_raises():
    with pytest.raises(ValueError, match="collides with rocker"):
        deck(rocker_crimp_mm=12.0)  # longer crimps reach the back pad and ear
