"""Checks on the hub's derived numbers. No CadQuery needed, so these run in the lab's suite."""

from dataclasses import replace
from pathlib import Path

import pytest
from exp003_cad.params import Case, Horn, HubParams, Screws, derive, load, load_case

# Plausible STS3215 values, used only to test the arithmetic.
HORN = Horn(
    od_mm=20.0,
    thickness_mm=2.5,
    bolt_count=4,
    bolt_circle_mm=14.0,
    bolt_size="M2",
    center_head_mm=5.0,
    center_head_height_mm=0.0,
    shaft_height_mm=4.0,
    raised_case_mm=4.0,  # a flat case top
)


def params(**horn_changes) -> HubParams:
    return HubParams(horn=replace(HORN, **horn_changes), measured=True)


def test_hub_sits_flat_on_the_horn_when_the_case_is_low_enough():
    d = derive(params())
    assert d.relief_mm == 0.0
    assert d.pad_diameter_mm == pytest.approx(20.0)
    assert d.case_gap_mm == pytest.approx(4.0)


def test_underside_steps_up_to_keep_two_mm_over_a_raised_case():
    d = derive(params(raised_case_mm=1.2))
    assert d.relief_mm == pytest.approx(0.8)
    assert d.case_gap_mm == pytest.approx(2.0)
    # The step must not eat into the material under the screw heads.
    assert d.web_mm - d.counterbore_depth_mm - d.relief_mm >= 2.0


def test_web_keeps_two_mm_under_m3_socket_heads():
    d = derive(params(bolt_size="M3", bolt_circle_mm=14.0))
    assert d.counterbore_depth_mm == pytest.approx(3.3)
    assert d.web_mm - d.counterbore_depth_mm >= 2.0


def test_screw_length_reaches_into_the_horn_but_not_the_case():
    d = derive(params())
    # 3.7 mm of hub to clamp (6.0 web - 2.3 counterbore), then at least 2.0 mm of thread in the
    # horn; the tip stops 2.3 mm below the horn top and the case is 4.0 mm down.
    assert d.screw_length_mm == 6
    assert d.screw == "M2 x 6"


def test_center_pocket_locates_on_the_center_screw_head():
    assert derive(params()).center_pocket_depth_mm == 0.0
    proud = derive(params(center_head_height_mm=1.2))
    assert proud.center_pocket_depth_mm == pytest.approx(1.2 + 0.5)
    assert proud.center_pocket_diameter_mm == pytest.approx(5.0 + 2 * 0.2)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"shaft_height_mm": 1.5, "raised_case_mm": 1.5}, "servo case"),
        ({"raised_case_mm": 4.5}, "deeper than shaft_height"),
        ({"raised_case_mm": -1.5}, "step up"),
        ({"bolt_circle_mm": 19.0}, "outside the horn"),
        ({"center_head_mm": 11.0}, "centre screw"),
        ({"bolt_size": "M4"}, "bolt_size"),
        ({"bolt_count": 1}, "bolt_count"),
        ({"thickness_mm": 0.8}, "too thin"),
    ],
)
def test_impossible_measurements_are_rejected(change, message):
    with pytest.raises(ValueError, match=message):
        derive(params(**change))


def test_counterbores_stay_above_a_deep_centre_pocket():
    # The measured horn (2026-11-17): M3 holes and a centre screw standing 2 mm proud. The pocket
    # (2.0 + 0.5 = 2.5 mm deep) must stop below the counterbore floors, with material between.
    d = derive(params(bolt_size="M3", bolt_circle_mm=13.6, center_head_height_mm=2.0))
    counterbore_floor = d.web_mm - d.counterbore_depth_mm
    assert counterbore_floor - d.center_pocket_depth_mm == pytest.approx(0.8)


MEASURED_HORN = Horn(19.9, 2.08, 4, 13.6, "M3", 5.0, 2.0, 4.0, 2.0)
KIT = Screws(head="button", lengths_mm=(8, 12, 16, 20))  # the lab's Mywish M2-M5 kit


def test_web_thickens_so_the_shortest_kit_screw_stops_short_of_the_case():
    d = derive(HubParams(horn=MEASURED_HORN, measured=True, screws=KIT))
    assert d.screw == "M3 x 8"
    assert d.counterbore_depth_mm == pytest.approx(1.95)  # 1.65 mm button head + 0.3
    assert d.counterbore_diameter_mm == pytest.approx(6.3)  # 5.7 mm head + 0.6
    clamp = d.web_mm - d.counterbore_depth_mm
    tip_below_horn_top = 8 - clamp
    assert tip_below_horn_top == pytest.approx(4.0 - 0.5)  # stops 0.5 mm above the case
    assert d.web_mm == pytest.approx(6.45)


def test_measured_servo_clears_its_raised_case_by_two_mm():
    # 2026-11-18: the first coupon (1.5 mm recess round the horn) cleared the raised block beside
    # the horn by only about 0.2 mm. Sitting flat on the horn gives the full 2.0 mm.
    d = derive(HubParams(horn=MEASURED_HORN, measured=True, screws=KIT))
    assert d.relief_mm == 0.0
    assert d.case_gap_mm == pytest.approx(2.0)


def test_no_screw_on_hand_fits():
    with pytest.raises(ValueError, match="on hand"):
        derive(HubParams(horn=MEASURED_HORN, measured=True, screws=Screws(lengths_mm=(3,))))


def test_unknown_head_style_is_rejected():
    with pytest.raises(ValueError, match="head"):
        derive(HubParams(horn=MEASURED_HORN, measured=True, screws=Screws(head="pan")))


def test_checked_in_servo_file_is_the_measured_horn_and_kit():
    p = load(Path(__file__).resolve().parents[1] / "servo.toml")
    assert p.measured is True
    assert p.horn == MEASURED_HORN
    assert p.screws == KIT
    assert derive(p).screw == "M3 x 8"


def test_load_reads_every_field(tmp_path):
    f = tmp_path / "servo.toml"
    f.write_text(
        "measured = true\n"
        "[horn]\n"
        "od_mm = 21.0\nthickness_mm = 2.0\nbolt_count = 4\nbolt_circle_mm = 14.5\n"
        'bolt_size = "M2.5"\ncenter_head_mm = 5.5\ncenter_head_height_mm = 0.4\n'
        "shaft_height_mm = 4.5\nraised_case_mm = 3.0\n"
        "[screws]\n"
        'head = "button"\nlengths_mm = [6, 10]\n'
    )
    p = load(f)
    assert p.measured is True
    assert p.horn == Horn(21.0, 2.0, 4, 14.5, "M2.5", 5.5, 0.4, 4.5, 3.0)
    assert p.screws == Screws("button", (6, 10))


def test_load_defaults_to_standard_socket_screws_without_a_screws_table(tmp_path):
    f = tmp_path / "servo.toml"
    f.write_text(
        "measured = false\n[horn]\nod_mm = 20.0\nthickness_mm = 2.5\nbolt_count = 4\n"
        'bolt_circle_mm = 14.0\nbolt_size = "M2"\ncenter_head_mm = 5.0\n'
        "center_head_height_mm = 0.0\nshaft_height_mm = 4.0\nraised_case_mm = 4.0\n"
    )
    assert load(f).screws == Screws()


SERVO_TOML = Path(__file__).resolve().parents[1] / "servo.toml"


def test_checked_in_case_has_the_caliper_confirmed_body():
    # 2026-11-19: length, width and mounting-hole spacing checked on a spare against the model;
    # the bottom disc measured 4.1 mm proud of the case bottom round the shaft.
    c = load_case(SERVO_TOML)
    assert (c.length_mm, c.width_mm) == (45.4, 24.8)
    assert (c.holes_along_mm, c.holes_across_mm) == (20.7, 20.4)
    assert c.holes_near_offset_mm + c.holes_along_mm == pytest.approx(29.0)
    assert c.bottom_disc_proud_mm == pytest.approx(4.1)
    # The bottom has its own four holes, longer-spaced, sharing the near pair's position.
    assert (c.bottom_holes_along_mm, c.bottom_holes_across_mm) == (24.5, 20.5)
    assert (c.mount_screw_length_mm, c.max_screw_depth_mm) == (6, 4.1)


def test_hub_loader_ignores_the_case_table():
    assert load(SERVO_TOML).horn == MEASURED_HORN


CASE_FIELDS = {
    "length_mm": 45.4,
    "width_mm": 24.8,
    "shaft_to_near_end_mm": 10.2,
    "holes_along_mm": 20.7,
    "holes_across_mm": 20.4,
    "holes_near_offset_mm": 8.3,
    "bottom_holes_along_mm": 24.5,
    "bottom_holes_across_mm": 20.5,
    "height_shaft_end_mm": 28.8,
    "height_far_end_mm": 32.9,
    "bottom_disc_od_mm": 20.0,
    "bottom_disc_proud_mm": 4.1,
    "bottom_step_mm": 1.5,
    "bottom_step_from_mm": 5.3,
    "bottom_keepout_from_mm": 11.55,
    "bottom_keepout_to_mm": 29.9,
    "bottom_keepout_half_width_mm": 10.1,
    "bottom_keepout_proud_mm": 3.5,
    "mount_screw_length_mm": 6,
    "max_screw_depth_mm": 4.1,
}


def write_case(tmp_path, **changes):
    f = tmp_path / "servo.toml"
    fields = {**CASE_FIELDS, **changes}
    f.write_text("[case]\n" + "".join(f"{k} = {v}\n" for k, v in fields.items()))
    return f


def test_load_case_reads_every_field(tmp_path):
    assert load_case(write_case(tmp_path)) == Case(**CASE_FIELDS)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"width_mm": 46.0}, "not less than length"),
        ({"shaft_to_near_end_mm": 30.0}, "near half"),
        ({"holes_across_mm": 25.0}, "inside the case width"),
        ({"holes_along_mm": 30.0}, "past the end"),
        ({"bottom_holes_across_mm": 25.0}, "bottom mounting holes across"),
        ({"bottom_holes_along_mm": 30.0}, "bottom mounting holes falls past"),
        ({"height_far_end_mm": 20.0}, "the larger"),
        ({"bottom_disc_od_mm": 30.0}, "wider than the case"),
        ({"max_screw_depth_mm": 6.5}, "shorter than the mounting screw"),
        ({"bottom_step_from_mm": 9.0}, "on the bottom step"),
        ({"bottom_keepout_to_mm": 10.0}, "before bottom_keepout_to"),
    ],
)
def test_impossible_case_numbers_are_rejected(tmp_path, change, message):
    with pytest.raises(ValueError, match=message):
        load_case(write_case(tmp_path, **change))
