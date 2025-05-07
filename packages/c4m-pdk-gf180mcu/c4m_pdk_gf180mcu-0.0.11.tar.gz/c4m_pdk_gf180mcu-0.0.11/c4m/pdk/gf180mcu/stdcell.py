# SPDX-License-Identifier: AGPL-3.0-or-later OR GPL-2.0-or-later OR CERN-OHL-S-2.0+ OR Apache-2.0
from typing import Optional, Any, cast

from pdkmaster.technology import property_ as _prp, primitive as _prm
from pdkmaster.design import circuit as _ckt, layout as _lay, library as _lbry

from c4m.flexcell import factory as _fab

from .pdkmaster import tech, cktfab, layoutfab

__all__ = [
    "stdcellcanvas", "StdCellFactory", "stdcelllib",
    "stdcell5v0canvas", "StdCell5V0Factory", "stdcell5v0lib",
]

prims = tech.primitives


stdcellcanvas = _fab.StdCellCanvas(
    tech=tech,
    nmos=cast(_prm.MOSFET, prims["nfet_03v3"]), nmos_min_w=0.88,
    pmos=cast(_prm.MOSFET, prims["pfet_03v3"]), pmos_min_w=0.88,
    cell_height=7.00, cell_horplacement_grid=1.14,
    m1_vssrail_width=1.34, m1_vddrail_width=1.34,
    well_edge_height=3.40,
)


class StdCellFactory(_fab.StdCellFactory):
    def __init__(self, *,
        lib: _lbry.RoutingGaugeLibrary, name_prefix: str = "", name_suffix: str = "",
    ):
        super().__init__(
            lib=lib, cktfab=cktfab, layoutfab=layoutfab,
            name_prefix=name_prefix, name_suffix=name_suffix,
            canvas=stdcellcanvas,
        )
# stdcelllib is handled by __getattr__()


stdcell5v0canvas = _fab.StdCellCanvas(
    tech=tech,
    nmos=cast(_prm.MOSFET, prims["nfet_05v0"]), nmos_min_w=0.88,
    pmos=cast(_prm.MOSFET, prims["pfet_05v0"]), pmos_min_w=0.88,
    l=0.6,
    cell_height=7.00, cell_horplacement_grid=1.5,
    m1_vssrail_width=1.36, m1_vddrail_width=1.36,
    well_edge_height=3.42,
    inside=(cast(_prm.Insulator, prims["Dualgate"]), cast(_prm.Marker, prims["V5_XTOR"])),
    inside_enclosure=(_prp.Enclosure(0.4), _prp.Enclosure(0.005))
)


class StdCell5V0Factory(_fab.StdCellFactory):
    def __init__(self, *,
        lib: _lbry.RoutingGaugeLibrary, name_prefix: str = "", name_suffix: str = "",
    ):
        super().__init__(
            lib=lib, cktfab=cktfab, layoutfab=layoutfab,
            name_prefix=name_prefix, name_suffix=name_suffix,
            canvas=stdcell5v0canvas,
        )
# stdcell5v0lib is handled by __getattr__()


_stdcelllib: Optional[_lbry.RoutingGaugeLibrary] = None
stdcelllib: _lbry.RoutingGaugeLibrary
_stdcell5v0lib: Optional[_lbry.RoutingGaugeLibrary] = None
stdcell5v0lib: _lbry.RoutingGaugeLibrary
def __getattr__(name: str) -> Any:
    if name == "stdcelllib":
        global _stdcelllib
        if _stdcelllib is None:
            _stdcelllib = _lbry.RoutingGaugeLibrary(
                name="StdCellLib", tech=tech, routinggauge=stdcellcanvas.routinggauge,
            )
            StdCellFactory(lib=_stdcelllib).add_default()
        return _stdcelllib
    elif name == "stdcell5v0lib":
        global _stdcell5v0lib
        if _stdcell5v0lib is None:
            _stdcell5v0lib = _lbry.RoutingGaugeLibrary(
                name="StdCell5V0Lib", tech=tech, routinggauge=stdcell5v0canvas.routinggauge,
            )
            StdCell5V0Factory(lib=_stdcell5v0lib).add_default()
        return _stdcell5v0lib
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
