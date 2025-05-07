# SPDX-License-Identifier: AGPL-3.0-or-later OR GPL-2.0-or-later OR CERN-OHL-S-2.0+ OR Apache-2.0
from typing import Dict, Any, cast

from pdkmaster.technology import primitive as _prm

from pdkmaster.io.spice import SpicePrimsParamSpec, SpiceNetlistFactory

from .pdkmaster import tech as _tech


__all__ = ["prims_spiceparams", "netlistfab"]


_prims = _tech.primitives
prims_spiceparams = SpicePrimsParamSpec()
params: Dict[str, Any]
for dev_name, params in (
    ("nfet_03v3", {}),
    ("pfet_03v3", {}),
    ("nfet_05v0", dict(model="nfet_06v0")),
    ("pfet_05v0", dict(model="pfet_06v0")),
):
    prims_spiceparams.add_device_params(
        prim=cast(_prm.MOSFET, _prims[dev_name]), **params,
    )
netlistfab = SpiceNetlistFactory(params=prims_spiceparams)
