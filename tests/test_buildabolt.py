from dataclasses import FrozenInstanceError, is_dataclass
import math

import pytest
from build123d import Axis, Box, BuildPart, Locations, Mode, Plane, Pos
from bd_buildabolt import (
    BoltData, NutData, bolt_data, nut_data, BoltHole, CounterBoreBoltHole,
    CounterSinkBoltHole, NutcatchParallel, NutcatchSidecut,
)


def test_queries():
    assert bolt_data("M3") == BoltData(3)
    assert nut_data("M3").width == 5.5
    assert bolt_data(BoltData(3.1)) == BoltData(3.1)
    assert nut_data(NutData(2.5, 5.6)) == NutData(2.5, 5.6)
    for query in (bolt_data, nut_data):
        for size, kinds in query().items():
            for kind, data in kinds.items():
                assert is_dataclass(data)
                assert query(size, kind) == data
        with pytest.raises(KeyError):
            query("unknown")
        with pytest.raises(KeyError):
            query("M3", "unknown")
        with pytest.raises(TypeError):
            query({"diameter": 3})
    with pytest.raises(FrozenInstanceError):
        bolt_data("M3").diameter = 4
    catalogue = bolt_data()
    catalogue["M3"].clear()
    assert bolt_data("M3").diameter == 3


@pytest.mark.parametrize("cls", [BoltHole, CounterBoreBoltHole, CounterSinkBoltHole])
def test_holes_builder_and_algebra(cls):
    with BuildPart() as builder:
        Box(20, 20, 10)
        with Locations(builder.faces().sort_by(Axis.Z)[-1]):
            cls("M3", depth=10)
    algebra = Box(20, 20, 10) - Pos(0, 0, 5) * cls("M3", depth=10)
    assert builder.part.is_valid
    assert algebra.is_valid
    assert builder.part.volume == pytest.approx(algebra.volume)
    assert builder.part.volume < 4000


@pytest.mark.parametrize("cls", [BoltHole, CounterBoreBoltHole, CounterSinkBoltHole])
def test_through_holes_and_multiple_locations(cls):
    with BuildPart() as builder:
        Box(20, 20, 10)
        with Locations(Plane(origin=(0, 0, 5))):
            with Locations((-5, 0), (5, 0)):
                cls("M3")
    with BuildPart() as explicit:
        Box(20, 20, 10)
        with Locations(Plane(origin=(0, 0, 5))):
            with Locations((-5, 0), (5, 0)):
                cls("M3", depth=10)
    assert builder.part.is_valid
    assert builder.part.volume == pytest.approx(explicit.part.volume)


def test_bolt_clearance_and_blind_depth():
    part = Box(20, 20, 10) - Pos(0, 0, 5) * BoltHole("M3", depth=4, clearance=0.2)
    assert part.volume == pytest.approx(4000 - math.pi * 1.6**2 * 4)


def test_counterbore_dimensions():
    data = bolt_data("M3", "socket_head")
    hole = CounterBoreBoltHole("M3", depth=10, clearance=0.2,
                              head_clearance=0.3, counter_bore_depth=2)
    part = Box(20, 20, 10) - Pos(0, 0, 5) * hole
    removed = math.pi * ((data.head_diameter + 0.5) / 2)**2 * 2 + math.pi * 1.6**2 * 8
    assert part.volume == pytest.approx(4000 - removed)


def test_countersink_dimensions():
    data = bolt_data("M3", "countersunk")
    r, R = data.diameter / 2, data.head_diameter / 2
    h = R - r
    removed = math.pi * r**2 * (10 - h) + math.pi * h / 3 * (R**2 + R*r + r**2)
    part = Box(20, 20, 10) - Pos(0, 0, 5) * CounterSinkBoltHole("M3", depth=10)
    assert part.volume == pytest.approx(4000 - removed)


def test_parallel_nutcatch():
    data = nut_data("M3")
    pocket = NutcatchParallel("M3", height_clearance=0.2)
    assert pocket.volume == pytest.approx(math.sqrt(3) / 2 * data.width**2 * (data.thickness + 0.2))
    assert pocket.bounding_box().max.Z == pytest.approx(0)
    with BuildPart() as builder:
        Box(20, 20, 10)
        with Locations((0, 0, 5)):
            NutcatchParallel("M3", height_clearance=0.2)
    assert builder.part.volume == pytest.approx(4000 - pocket.volume)


def test_sidecut():
    data = nut_data("M3")
    pocket = NutcatchSidecut("M3", depth=12)
    bounds = pocket.bounding_box()
    assert bounds.max.Y == pytest.approx(12)
    assert bounds.min.Y == pytest.approx(-data.width / math.sqrt(3))
    assert bounds.min.Z == pytest.approx(0)
    assert bounds.max.Z == pytest.approx(data.thickness)
    with BuildPart() as builder:
        Box(20, 20, 10)
        NutcatchSidecut("M3")
    expected = Box(20, 20, 10) - pocket
    assert builder.part.is_valid
    assert builder.part.volume == pytest.approx(expected.volume)
    with pytest.raises(ValueError, match="depth"):
        NutcatchSidecut("M3")


def test_rotated_workplane_and_private_mode():
    with BuildPart() as builder:
        Box(20, 20, 10)
        with Locations(Plane(origin=(10, 0, 0), z_dir=(1, 0, 0))):
            BoltHole("M3", depth=20)
        NutcatchParallel("M3", mode=Mode.PRIVATE)
    assert builder.part.volume == pytest.approx(4000 - math.pi * 1.5**2 * 20)


@pytest.mark.parametrize("cls", [BoltHole, CounterBoreBoltHole, CounterSinkBoltHole])
def test_invalid_holes(cls):
    with pytest.raises(ValueError):
        cls("M3", depth=0)
    with pytest.raises(ValueError):
        cls("M3", depth=10, clearance=-0.1)
    if cls is not BoltHole:
        with pytest.raises(ValueError, match="headed bolt"):
            cls(BoltData(3), depth=10)


@pytest.mark.parametrize("cls", [NutcatchParallel, NutcatchSidecut])
def test_invalid_nuts(cls):
    with pytest.raises(ValueError):
        cls("M3", height_clearance=-0.1)
