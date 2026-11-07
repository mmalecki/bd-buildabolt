"""Native build123d subtractive objects for standard fasteners."""
import math

from build123d import (
    BasePartObject, BuildPart, CounterBoreHole, CounterSinkHole, Face,
    Hole, Mode, Solid, Wire,
)

from .data import BoltSpec, NutSpec, bolt_data, nut_data, DEFAULT_NUT_KIND

DEFAULT_CLEARANCE = 0.0
DEFAULT_HEAD_DIAMETER_CLEARANCE = 0.1


def _positive(value, name):
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and greater than zero")
    return value


def _clearance(value, name):
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return value


def _depth(depth):
    if depth is not None:
        _positive(depth, "depth")


def _head(data):
    if data.head_diameter is None or data.head_length is None:
        raise ValueError("a headed bolt requires head_diameter and head_length")
    _positive(data.head_diameter, "head_diameter")
    _positive(data.head_length, "head_length")


class BoltHole(Hole):
    """Bolt hole along local -Z. Clearance is added to the diameter.

    With depth=None, use the enclosing BuildPart to make a through hole.
    Algebra mode requires an explicit depth, just like build123d.Hole.
    """

    def __init__(self, bolt: BoltSpec, depth: float | None = None,
                 clearance: float = DEFAULT_CLEARANCE, mode: Mode = Mode.SUBTRACT):
        self.bolt = bolt_data(bolt)
        _depth(depth)
        diameter = _positive(self.bolt.diameter, "diameter")
        super().__init__((diameter + _clearance(clearance, "clearance")) / 2,
                         depth=depth, mode=mode)


class CounterBoreBoltHole(CounterBoreHole):
    """Socket-head bolt hole using build123d's counterbore geometry.

    Head diameter receives both clearance and head_clearance. The default
    counter_bore_depth is the bolt's head_length.
    """

    def __init__(self, bolt: BoltSpec, depth: float | None = None,
                 clearance: float = DEFAULT_CLEARANCE,
                 head_clearance: float = DEFAULT_HEAD_DIAMETER_CLEARANCE,
                 counter_bore_depth: float | None = None,
                 mode: Mode = Mode.SUBTRACT):
        self.bolt = bolt_data(bolt, "socket_head")
        _head(self.bolt)
        _depth(depth)
        _clearance(clearance, "clearance")
        _clearance(head_clearance, "head_clearance")
        bore_depth = self.bolt.head_length if counter_bore_depth is None else counter_bore_depth
        super().__init__(
            radius=(_positive(self.bolt.diameter, "diameter") + clearance) / 2,
            counter_bore_radius=(self.bolt.head_diameter + clearance + head_clearance) / 2,
            counter_bore_depth=_positive(bore_depth, "counter_bore_depth"),
            depth=depth, mode=mode,
        )


class CounterSinkBoltHole(CounterSinkHole):
    """90-degree countersink for a countersunk bolt, along local -Z.

    Clearance increases only the shaft diameter, matching the original API.
    """

    def __init__(self, bolt: BoltSpec, depth: float | None = None,
                 clearance: float = DEFAULT_CLEARANCE, mode: Mode = Mode.SUBTRACT):
        self.bolt = bolt_data(bolt, "countersunk")
        _head(self.bolt)
        _depth(depth)
        super().__init__(
            radius=(_positive(self.bolt.diameter, "diameter") + _clearance(clearance, "clearance")) / 2,
            counter_sink_radius=self.bolt.head_diameter / 2,
            counter_sink_angle=90, depth=depth, mode=mode,
        )


def _nut_dimensions(nut, height_clearance):
    return (_positive(nut.width, "width"),
            _positive(nut.thickness, "thickness") + _clearance(height_clearance, "height_clearance"))


class NutcatchParallel(BasePartObject):
    """Hexagonal surface nut pocket extruded into local -Z.

    Width is measured across flats. Use Locations/Planes for placement and
    rotation, as for native build123d holes.
    """

    def __init__(self, nut: NutSpec, kind: str = DEFAULT_NUT_KIND,
                 height_clearance: float = 0.0, mode: Mode = Mode.SUBTRACT):
        self.nut = nut_data(nut, kind)
        width, height = _nut_dimensions(self.nut, height_clearance)
        radius = width / math.sqrt(3)
        vertices = [(radius * math.cos(i * math.pi / 3),
                     radius * math.sin(i * math.pi / 3), 0) for i in range(6)]
        solid = Solid.extrude(Face(Wire.make_polygon(vertices, close=True)), (0, 0, -height))
        super().__init__(solid, mode=mode)


class NutcatchSidecut(BasePartObject):
    """Side-entry nut slot opening toward local +Y, extruded along +Z.

    Matches the CadQuery sidecut orientation: depth is the +Y entry length,
    not the extrusion thickness. If omitted it uses BuildPart.max_dimension;
    outside a builder an explicit depth is required.
    """

    def __init__(self, nut: NutSpec, kind: str = DEFAULT_NUT_KIND,
                 height_clearance: float = 0.0, depth: float | None = None,
                 mode: Mode = Mode.SUBTRACT):
        self.nut = nut_data(nut, kind)
        width, height = _nut_dimensions(self.nut, height_clearance)
        if depth is None:
            context = BuildPart._get_context(self)
            if context is None or context.part is None:
                raise ValueError("depth is required outside a populated BuildPart")
            depth = context.max_dimension
        _positive(depth, "depth")
        e = -width * math.sqrt(3) / 6
        vertices = [(-width / 2, depth, 0), (-width / 2, e, 0),
                    (0, -width / math.sqrt(3), 0), (width / 2, e, 0),
                    (width / 2, depth, 0)]
        solid = Solid.extrude(Face(Wire.make_polygon(vertices, close=True)), (0, 0, height))
        super().__init__(solid, mode=mode)
