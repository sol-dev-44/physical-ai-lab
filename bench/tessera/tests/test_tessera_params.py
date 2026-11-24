"""Tessera's numbers. No CadQuery needed."""

import math

import pytest
from tessera_cad.params import (
    FIRST_PIECE_CUPS,
    TEST_KEY_CLEARANCES,
    Grid,
    Joint,
    body,
    boss_intrusion,
    boss_size,
    bowtie,
    cavity,
    half_width,
    module_height,
    sockets,
)

G, J = Grid(), Joint()


def test_modules_leave_half_a_millimetre_between_neighbours():
    a = body(G, 1, 1)
    b = body(G, 1, 1)
    # b sits one cell to the right of a
    assert (b[0] + G.unit_mm) - a[1] == pytest.approx(2 * G.gap_mm)
    assert a[1] - a[0] == pytest.approx(51.5)
    assert a[1] - a[0] >= 2 * 25.4  # owner: the smallest cup is at least 2 in square


def test_one_socket_per_outside_cell_edge():
    assert len(sockets(G, 1, 1)) == 4
    assert len(sockets(G, 2, 3)) == 2 * (2 + 3)
    for s in sockets(G, 2, 3):
        # every socket sits mid-cell, so any two modules' sockets face each other
        along = s.at[0] if s.normal[0] == 0 else s.at[1]
        assert (along / G.unit_mm) % 1 == pytest.approx(0.5)


def test_bowtie_neck_sits_on_the_joint_line_and_flares_out():
    pts = bowtie(J, G)
    assert max(abs(x) for x, _ in pts) == pytest.approx(G.gap_mm + J.depth_mm)
    assert half_width(J, G, 0) * 2 == pytest.approx(J.neck_mm)
    assert half_width(J, G, G.gap_mm + J.depth_mm) * 2 == pytest.approx(J.end_mm)
    flank = math.degrees(math.atan((J.end_mm - J.neck_mm) / 2 / (G.gap_mm + J.depth_mm)))
    assert 10 < flank < 20  # steep enough to lock, shallow enough to print and slide


def _flank_gap(key, sock):
    """Perpendicular distance between the key's flank and the socket's (right upper flank)."""
    (x0, y0), (x1, y1) = sock[4], sock[3]  # neck to end, upper right flank
    px, py = key[3]
    return abs((y1 - y0) * px - (x1 - x0) * py + x1 * y0 - y1 * x0) / math.hypot(x1 - x0, y1 - y0)


def test_key_is_smaller_than_the_socket_by_its_clearance_all_round():
    for c in TEST_KEY_CLEARANCES:
        k, s = bowtie(J, G, c), bowtie(J, G)
        assert abs(s[2][0]) - abs(k[2][0]) == pytest.approx(c)  # end faces
        assert _flank_gap(k, s) == pytest.approx(c)  # slanted flanks, square to the face


def test_key_bridges_the_gap_with_plenty_in_each_socket():
    reach = bowtie(J, G, J.key_clearance_mm)[2][0]
    in_socket = reach - G.gap_mm
    assert in_socket > 6.0


def test_bosses_leave_the_cup_usable():
    w, d = boss_size(G, J)
    assert w == pytest.approx(16.2)
    assert boss_intrusion(G, J) == pytest.approx(6.1)
    x0, x1, _, _ = cavity(G, 1, 1)
    assert (x1 - x0) - 2 * boss_intrusion(G, J) > 35  # clear between opposite bosses


def test_bosses_never_reach_the_corners():
    w, _ = boss_size(G, J)
    # boss edge to the cell corner on the outer face
    assert G.unit_mm / 2 - w / 2 - G.gap_mm > G.wall_mm + G.corner_r_mm


def test_heights_come_in_steps():
    assert module_height(G, 2) == 52
    with pytest.raises(ValueError):
        module_height(G, 6)


def test_first_piece_cups_have_labels_and_serials():
    assert [c.label for c in FIRST_PIECE_CUPS] == ["TIPS", "SPARE"]
    assert [c.serial for c in FIRST_PIECE_CUPS] == [1, 2]
