"""All five fastener tools; run from an installed bd-buildabolt checkout."""
from build123d import Box, BuildPart, Locations
from bd_buildabolt import (
    BoltHole, CounterBoreBoltHole, CounterSinkBoltHole,
    NutcatchParallel, NutcatchSidecut,
)

with BuildPart() as model:
    Box(60, 20, 10)
    with Locations((-20, 0, 5)):
        BoltHole("M3")
    with Locations((-10, 0, 5)):
        CounterBoreBoltHole("M3")
    with Locations((0, 0, 5)):
        CounterSinkBoltHole("M3")
    with Locations((10, 0, 5)):
        NutcatchParallel("M3")
    with Locations((20, 0, 0)):
        NutcatchSidecut("M3")

result = model.part
