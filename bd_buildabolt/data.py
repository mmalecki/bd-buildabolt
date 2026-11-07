"""Fastener dimensions in millimetres, sourced from BOLTS."""
from dataclasses import dataclass
from importlib.resources import files
import json
from typing import overload

DEFAULT_NUT_KIND = "hexagon"
DEFAULT_BOLT_KIND = "headless"


@dataclass(frozen=True)
class BoltData:
    diameter: float
    head_diameter: float | None = None
    head_length: float | None = None


@dataclass(frozen=True)
class NutData:
    thickness: float
    width: float
    nut_thickness: float | None = None


def _load(name):
    return json.loads(files(__package__).joinpath(name).read_text(encoding="utf-8"))


_bolts = _load("bolts.json")
_nuts = _load("nuts.json")
BoltSpec = str | BoltData
NutSpec = str | NutData


@overload
def bolt_data(options: None = None, kind: str = DEFAULT_BOLT_KIND) -> dict[str, dict[str, BoltData]]: ...


@overload
def bolt_data(options: BoltSpec, kind: str = DEFAULT_BOLT_KIND) -> BoltData: ...


def bolt_data(options=None, kind=DEFAULT_BOLT_KIND):
    """Query a size/kind, pass through custom dimensions, or list all sizes.

    Unknown sizes/kinds raise KeyError. The full catalogue is a fresh nested
    mapping whose leaves are immutable dataclasses, never raw dimension dicts.
    """
    if options is None:
        return {size: {k: BoltData(**v) for k, v in kinds.items()}
                for size, kinds in _bolts.items()}
    if isinstance(options, str):
        return BoltData(**_bolts[options][kind])
    if isinstance(options, BoltData):
        return options
    raise TypeError("bolt must be a size string or BoltData")


@overload
def nut_data(options: None = None, kind: str = DEFAULT_NUT_KIND) -> dict[str, dict[str, NutData]]: ...


@overload
def nut_data(options: NutSpec, kind: str = DEFAULT_NUT_KIND) -> NutData: ...


def nut_data(options=None, kind=DEFAULT_NUT_KIND):
    """Query nut dimensions; see bolt_data for catalogue and error semantics."""
    if options is None:
        return {size: {k: NutData(**v) for k, v in kinds.items()
                       if isinstance(v, dict)} for size, kinds in _nuts.items()}
    if isinstance(options, str):
        return NutData(**_nuts[options][kind])
    if isinstance(options, NutData):
        return options
    raise TypeError("nut must be a size string or NutData")


# Query spelling retained for callers migrating from CadQuery.
boltData = bolt_data
nutData = nut_data
