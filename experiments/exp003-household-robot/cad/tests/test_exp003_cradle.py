"""Checks on the servo cradle's sizing. No CadQuery needed."""

from dataclasses import replace
from pathlib import Path

import pytest
from exp003_cad.params import Cradle, derive_cradle, load, load_case

SERVO = Path(__file__).resolve().parents[1] / "servo.toml"
CASE = load_case(SERVO)
HORN = load(SERVO).horn


def test_supplied_screws_bite_without_going_past_the_known_depth():
    d = derive_cradle(CASE, HORN, Cradle())
    # 2.0 mm wall + 0.5 mm pad under the head: an M2 x 6 goes 3.5 mm into the case (SO-101: 4.1).
    assert d.screw_depth_mm == pytest.approx(3.5)


def test_holes_match_the_bottom_pattern():
    d = derive_cradle(CASE, HORN, Cradle())
    assert sorted(d.holes) == [(8.3, -10.25), (8.3, 10.25), (32.8, -10.25), (32.8, 10.25)]
    assert d.hole_diameter_mm == pytest.approx(2.4)


def test_disc_opening_clears_the_disc_and_spares_the_near_pads():
    d = derive_cradle(CASE, HORN, Cradle())
    assert d.disc_opening_radius_mm == pytest.approx(11.0)
    assert d.near_pad_gap_mm >= 0


def test_window_clears_connectors_and_pad_but_not_the_pads():
    d = derive_cradle(CASE, HORN, Cradle())
    a_from, a_to, half = d.window
    assert a_from <= CASE.bottom_keepout_from_mm - 0.4 + 1e-9
    assert a_to >= CASE.bottom_keepout_to_mm + 0.4 - 1e-9
    assert half >= CASE.bottom_keepout_half_width_mm + 0.4 - 1e-9


def test_throat_joins_the_openings_clear_of_the_near_pads():
    d = derive_cradle(CASE, HORN, Cradle())
    assert d.throat_half_width_mm == pytest.approx(10.25 - 4.3 / 2 - 1.0)


def test_cheeks_hug_the_case_and_stay_clear_of_the_hub():
    d = derive_cradle(CASE, HORN, Cradle())
    assert d.b_inner_mm == pytest.approx(12.6)  # 24.8 case + 0.2 a side
    assert (d.a_min_mm, d.a_max_mm) == (pytest.approx(-10.2), pytest.approx(35.2))
    assert d.hub_face_c_mm == pytest.approx(1.5 + 28.8 + 4.0)
    assert d.axle_above_foot_mm == pytest.approx(15.6)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"wall_mm": 1.0}, "past the 4.1 mm"),
        ({"wall_mm": 3.5}, "bite only"),
        ({"pad_diameter_mm": 6.0}, "near pads"),
        ({"disc_clearance_mm": 2.5}, "near"),
        ({"keepout_margin_mm": 2.5}, "connector window"),
        ({"cheek_height_mm": 33.0}, "spinning hub"),
    ],
)
def test_unworkable_cradles_are_rejected(change, message):
    with pytest.raises(ValueError, match=message):
        derive_cradle(CASE, HORN, replace(Cradle(), **change))
