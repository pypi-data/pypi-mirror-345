# SPDX-License-Identifier: AGPL-3.0-or-later OR GPL-2.0-or-later OR CERN-OHL-S-2.0+ OR Apache-2.0
from typing import Optional, Any, cast

from pdkmaster.technology import primitive as _prm
from pdkmaster.design import library as _lbry

from c4m.flexcell import factory as _fab

from .pdkmaster import tech, cktfab, layoutfab

__all__ = [
    "StdCellFactory", "stdcellcanvas", "stdcelllib", "stdcellfab",
    "StdCell5V0Factory", "stdcell5v0canvas", "stdcell5v0lib", "stdcell5v0fab",
]

prims = tech.primitives

_nmos = cast(_prm.MOSFET, prims["nfet_01v8"])
_pmos = cast(_prm.MOSFET, prims["pfet_01v8"])
_ionmos = cast(_prm.MOSFET, prims["nfet_g5v0d10v5"])
_iopmos = cast(_prm.MOSFET, prims["pfet_g5v0d10v5"])
_difftao = cast(_prm.WaferWire, prims["difftap"])
assert _difftao.oxide # help static type analysis

stdcellcanvas = _fab.StdCellCanvas(
    tech=tech,
    nmos=_nmos, nmos_min_w=0.84,
    pmos=_pmos, pmos_min_w=0.84,
    cell_height=5.60, cell_horplacement_grid=0.76,
    m1_vssrail_width=0.95, m1_vddrail_width=0.95,
    well_edge_height=2.7,
)

class StdCellFactory(_fab.StdCellFactory):
    def __init__(self, *,
        lib: _lbry.RoutingGaugeLibrary, canvas: _fab.StdCellCanvas=stdcellcanvas,
        name_prefix: str = "", name_suffix: str = "",
    ):
        super().__init__(
            lib=lib, cktfab=cktfab, layoutfab=layoutfab,
            name_prefix=name_prefix, name_suffix=name_suffix,
            canvas=canvas,
        )
# stdcelllib is handled by __getattr__()


stdcell5v0canvas = _fab.StdCellCanvas(
    tech=tech,
    nmos=_ionmos, nmos_min_w=0.84,
    pmos=_iopmos, pmos_min_w=0.84,
    cell_height=6.0, cell_horplacement_grid=1.10,
    m1_vssrail_width=1.10, m1_vddrail_width=1.10,
    well_edge_height=2.9,
    inside=_difftao.oxide[0], inside_enclosure=_difftao.min_oxide_enclosure[0],
)

class StdCell5V0Factory(_fab.StdCellFactory):
    def __init__(self, *,
        lib: _lbry.RoutingGaugeLibrary,
        name_prefix: str = "", name_suffix: str = "",
    ):
        super().__init__(
            lib=lib, cktfab=cktfab, layoutfab=layoutfab,
            name_prefix=name_prefix, name_suffix=name_suffix,
            canvas=stdcell5v0canvas,
        )
# stdcell5v0lib is handled by __getattr__()


_stdcelllib: Optional[_lbry.RoutingGaugeLibrary] = None
stdcelllib: _lbry.RoutingGaugeLibrary
_stdcellfab: Optional[StdCellFactory] = None
stdcellfab: StdCellFactory
_stdcell5v0lib: Optional[_lbry.RoutingGaugeLibrary] = None
stdcell5v0lib: _lbry.RoutingGaugeLibrary
_stdcell5v0fab: Optional[StdCell5V0Factory] = None
stdcell5v0fab: StdCell5V0Factory
def __getattr__(name: str) -> Any:
    if name in ("stdcelllib", "stdcellfab"):
        global _stdcelllib, _stdcellfab
        if _stdcelllib is None:
            assert _stdcellfab is None, "Internal error"
            _stdcelllib = _lbry.RoutingGaugeLibrary(
                name="StdCellLib", tech=tech, routinggauge=stdcellcanvas.routinggauge,
            )
            _stdcellfab = StdCellFactory(lib=_stdcelllib)
            _stdcellfab.add_default()
        return _stdcelllib if name == "stdcelllib" else _stdcellfab
    elif name == "stdcell5v0lib":
        global _stdcell5v0lib, _stdcell5v0fab
        if _stdcell5v0lib is None:
            assert _stdcell5v0fab is None, "Internal error"
            _stdcell5v0lib = _lbry.RoutingGaugeLibrary(
                name="StdCell5V0Lib", tech=tech,
                routinggauge=stdcell5v0canvas.routinggauge,
            )
            _stdcell5v0fab = StdCell5V0Factory(lib=_stdcell5v0lib)
            _stdcell5v0fab.add_default()
        return _stdcell5v0lib if name == "stdcell5v0lib" else _stdcell5v0fab
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
