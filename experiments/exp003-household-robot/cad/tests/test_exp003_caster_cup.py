"""The caster cup's numbers. No CadQuery needed."""

from dataclasses import replace
from pathlib import Path

import pytest
from exp003_cad.params import (
    CASTER_CUP_TEST,
    Caster,
    CasterCup,
    Cradle,
    derive_caster_cup,
    derive_heights,
    load,
    load_case,
)

SERVO = Path(__file__).resolve().parents[1] / "servo.toml"
HEIGHTS = derive_heights(load_case(SERVO), load(SERVO).horn, Cradle(), Caster())


def test_cup_takes_the_caster_plate_with_clearance():
    d = derive_caster_cup(Caster(), HEIGHTS, CasterCup())
    assert d.inner_mm == pytest.approx((47.0, 39.25))
    assert d.outer_mm == pytest.approx((51.0, 43.25))


def test_cavity_clears_the_measured_fork_sweep():
    caster = Caster()
    assert caster.fork_radius_mm == pytest.approx(47 - 23)
    d = derive_caster_cup(caster, HEIGHTS, CasterCup())
    assert d.sweep_radius_mm == pytest.approx(24 + 1.5)
    # v1 had only the box: its short walls were 19.6 mm from the axis, so the 24 mm fork hit them.
    assert d.inner_mm[1] / 2 < caster.fork_radius_mm < d.sweep_radius_mm


def test_cup_depth_is_the_raised_pocket_so_its_open_end_is_the_plate_underside():
    d = derive_caster_cup(Caster(), HEIGHTS, CasterCup())
    assert d.depth_mm == pytest.approx(HEIGHTS.caster_mount_mm)
    assert d.height_mm == pytest.approx(9.6 + 3.0)


def test_screws_match_the_caster_hole_centres_and_come_from_the_kit():
    d = derive_caster_cup(Caster(), HEIGHTS, CasterCup())
    got = sorted((round(x, 3), round(y, 3)) for x, y in d.holes)
    assert got == sorted((x, y) for x in (-17.875, 17.875) for y in (-13.875, 13.875))
    assert d.screw == "M4 x 12 button head and nut"


def test_a_centre_hole_that_reaches_the_screw_holes_is_refused():
    with pytest.raises(ValueError, match="centre hole"):
        derive_caster_cup(Caster(), HEIGHTS, replace(CasterCup(), center_hole_mm=38.0))


def test_light_fit_test_version_keeps_the_fit_and_the_screw():
    d = derive_caster_cup(Caster(), HEIGHTS, CASTER_CUP_TEST)
    full = derive_caster_cup(Caster(), HEIGHTS, CasterCup())
    assert d.inner_mm == full.inner_mm and d.sweep_radius_mm == full.sweep_radius_mm
    assert d.depth_mm == full.depth_mm  # same height test
    assert d.screw == "M4 x 12 button head and nut"
