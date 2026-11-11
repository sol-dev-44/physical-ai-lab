import pytest
from lab_agent.devices import ir


def frame(bits: str) -> list[int]:
    """A toy frame: header, one pulse/space per bit, then a 104 ms gap."""
    out = [4300, 1050]
    for b in bits:
        out += [1050, 3150] if b == "1" else [3150, 1050]
    return out + [1050, 104_000]


def test_round_trip_within_one_tick():
    pulses = frame("0110") * 2
    back = ir.decode(ir.encode(pulses))
    assert len(back) == len(pulses)
    assert all(abs(a - b) <= ir.TICK_US for a, b in zip(back, pulses, strict=True))


def test_long_durations_use_the_three_byte_form():
    packet = ir.encode([500, 104_000])
    assert packet[4:] == bytes([15, 0, 0x0C, 0x5E])  # 104000 us = 3166 ticks


def test_one_frame_trims_a_held_button():
    held = ir.encode(frame("0110") * 49)  # ~6 s, like a button held while learning
    one = ir.one_frame(held)
    assert len(one) == len(frame("0110"))
    assert ir.duration_s(one) == pytest.approx(0.13, abs=0.01)


def test_one_frame_without_a_gap_keeps_everything():
    assert len(ir.one_frame(ir.encode([560, 560, 560]))) == 3


def test_repeat_byte_and_bounds():
    assert ir.encode([560, 30_000], repeat=7)[1] == 7
    with pytest.raises(ValueError):
        ir.encode([560], repeat=256)


def test_rejects_non_ir_packets():
    with pytest.raises(ValueError):
        ir.decode(b"\xb2\x00\x00\x00")


def test_one_frame_skips_a_glitched_first_frame():
    glitched = [4300, 1050, 1000, 1400, 300, 1500, 3150, 1050, 1050, 104_000]
    clean = frame("0110")
    one = ir.one_frame(ir.encode(glitched + clean * 5))
    assert len(one) == len(clean)
    assert all(abs(a - b) <= ir.TICK_US for a, b in zip(one, clean, strict=True))


def test_one_frame_takes_the_command_not_the_shared_hold_frame():
    command, held = frame("0110"), frame("1001")
    one = ir.one_frame(ir.encode(command * 4 + held * 13))  # like the robot remote
    assert len(one) == len(command)
    assert all(abs(a - b) <= ir.TICK_US for a, b in zip(one, command, strict=True))


def test_one_frame_refuses_when_nothing_repeats():
    with pytest.raises(ValueError, match="no frame repeats"):
        ir.one_frame(ir.encode(frame("0110") + frame("1001") + frame("1111")))
