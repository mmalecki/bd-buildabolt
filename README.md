# bd-buildabolt

Standard bolt holes, counterbores, countersinks, and nut pockets for
[build123d](https://build123d.readthedocs.io/), using fastener dimensions from BOLTS.
All dimensions and clearances are in millimetres. No CadQuery dependency or
Workplane monkey-patching is needed.

## Installation

Requires Python 3.11+ and build123d 0.13.

```sh
uv add bd-buildabolt
# or, to use a local checkout:
uv add --editable /path/to/bd-buildabolt
```

## Builder mode

```python
from build123d import Axis, Box, BuildPart, Locations
from bd_buildabolt import BoltHole, NutcatchParallel

with BuildPart() as model:
    Box(25, 10, 10)
    with Locations(model.faces().sort_by(Axis.Z)[0]):
        NutcatchParallel("M3")
    with Locations(model.faces().sort_by(Axis.Z)[-1]):
        BoltHole("M3")

result = model.part
```

Objects respect active workplanes and `Locations`, including multiple locations.
All default to `mode=Mode.SUBTRACT`; `Mode.PRIVATE` constructs a tool without
modifying the builder.

## Algebra mode

```python
from build123d import Box, Pos
from bd_buildabolt import CounterBoreBoltHole

result = Box(25, 10, 10) - Pos(0, 0, 5) * CounterBoreBoltHole("M3", depth=10)
```

Like native build123d holes, holes start at the local origin and cut along
local **-Z**. Supply an explicit `depth` outside a `BuildPart`. In a populated
builder, `depth=None` selects a through hole using build123d's native sizing.
Counterbores and countersinks include native build123d tool extensions above
the entry plane; their bounding boxes are not the physical fastener dimensions.

See [examples/simple.py](examples/simple.py) for all five objects.

## Dataclass queries

```python
from bd_buildabolt import BoltData, NutData, bolt_data, nut_data, BoltHole

bolt = bolt_data("M3", "socket_head")
print(bolt.diameter, bolt.head_diameter, bolt.head_length)
nut = nut_data("M3", "hexagon")
print(nut.width, nut.thickness)

# Custom dimensions use the same dataclasses:
tool = BoltHole(BoltData(diameter=3.2), depth=12)
```

`BoltData` and `NutData` are frozen dataclasses:

| Dataclass | Fields |
| --- | --- |
| `BoltData` | `diameter`, `head_diameter=None`, `head_length=None` |
| `NutData` | `thickness`, `width` (across flats), `nut_thickness=None` |

`bolt_data()` and `nut_data()` return fresh `size -> kind -> dataclass` catalogues.
A named query returns one dataclass, and passing a dataclass returns it unchanged.
Unknown sizes or kinds raise `KeyError`; raw dictionaries are not accepted.
Not all sizes have every kind. Bolt kinds are `headless` (default), `socket_head`,
and `countersunk`; nut kinds are `hexagon` (default), `hexagon_thin`, and
`hexagon_lock`. `nut_thickness` retains the optional dataset field; pockets use
`thickness`, matching the original package.

## Objects

All objects accept a size string or the corresponding dimensions dataclass.

| Object | Parameters (in addition to `mode=Mode.SUBTRACT`) |
| --- | --- |
| `BoltHole` | `bolt, depth=None, clearance=0.0` |
| `CounterBoreBoltHole` | `bolt, depth=None, clearance=0.0, head_clearance=0.1, counter_bore_depth=None` |
| `CounterSinkBoltHole` | `bolt, depth=None, clearance=0.0` |
| `NutcatchParallel` | `nut, kind="hexagon", height_clearance=0.0` |
| `NutcatchSidecut` | `nut, kind="hexagon", height_clearance=0.0, depth=None` |

- **BoltHole**: shaft diameter plus `clearance` (a diametral, not radial, allowance).
- **CounterBoreBoltHole**: queries `socket_head`. Counterbore diameter is
  `head_diameter + clearance + head_clearance`; counterbore depth defaults to
  `head_length`.
- **CounterSinkBoltHole**: queries `countersunk`, with a 90° included angle.
  Clearance affects only the shaft; the head diameter is unchanged.
- **NutcatchParallel**: hexagonal pocket of depth `thickness + height_clearance`
  along local -Z, with a vertex on +X.
- **NutcatchSidecut**: side-entry pocket opening toward local **+Y**, extruded
  along **+Z** by `thickness + height_clearance`, preserving the original
  sidecut orientation. `depth` controls the +Y entry length, not thickness.
  If omitted it uses the enclosing part's maximum dimension; explicit depth
  is required in algebra mode. Place it at the intended nut level.

Clearances must be finite and nonnegative; explicit depths and dimensions must
be finite and positive. Headed holes require both head dimensions in custom
`BoltData` values.

## Migration from cq-queryabolt

| CadQuery Workplane method | build123d object |
| --- | --- |
| `boltHole` | `BoltHole` |
| `cboreBoltHole` | `CounterBoreBoltHole` |
| `cskBoltHole` | `CounterSinkBoltHole` |
| `nutcatchParallel` | `NutcatchParallel` |
| `nutcatchSidecut` | `NutcatchSidecut` |

Use `Locations(face)` instead of `.faces(...).workplane()`. Parameters use
snake_case (`head_clearance`, `height_clearance`, `counter_bore_depth`). Replace
query subscripts such as `data["diameter"]` with `data.diameter`.

## Development

```sh
uv sync
uv run pytest
uv build
```

Datasets are bundled inside `bd_buildabolt/`, so installed wheels do not depend
on the working directory. To regenerate them from BOLTS, run
`./scripts/build` (requires Node.js and `yaml`). The generator writes directly
to `bd_buildabolt/`, the single source of dataset files. Its BOLTS reference
checkout under `vendor/` is ignored by Git.

## Licensing

This is a mixed-license distribution:

- The Python code, generator scripts, and original documentation retain the
  [MIT license](LICENSE).
- `bd_buildabolt/bolts.json` and `bd_buildabolt/nuts.json` are modified extracts
  of BOLTS tables, licensed **LGPL-2.1-or-later**.

See [the data license and attribution notice](bd_buildabolt/DATA-LICENSE.md)
and [the LGPL text](LICENSES/LGPL-2.1-or-later.txt). These notices and license
texts are included in both wheels and source distributions.

The distribution's SPDX expression is `MIT AND LGPL-2.1-or-later`: both licenses
apply to their respective components, not a choice to use the BOLTS data under
MIT. Using the library does not, by itself, place generated CAD designs under
LGPL; the license of particular output depends on what it contains.

## Acknowledgements and prior work

The Python implementation is derived from [cq-queryabolt](https://github.com/mmalecki/cq-queryabolt)
by Maciej Małecki and retains its MIT license and attribution. The BOLTS-derived
data has the separate licensing described above.

- The [authors](https://github.com/boltsparts/boltsparts/graphs/contributors) of
  [BOLTS](https://github.com/boltsparts/boltsparts)
- [cqparts_fasteners](https://cqparts.github.io/cqparts/doc/cqparts_fasteners/)
- [cq_warehouse](https://cq-warehouse.readthedocs.io/en/latest/fastener.html)
