# SPDX-License-Identifier: AGPL-3.0-or-later OR GPL-2.0-or-later OR CERN-OHL-S-2.0+ OR Apache-2.0
from pathlib import Path

from pdkmaster.io.spice import SpicePrimsParamSpec, PySpiceFactory

from .pdkmaster import tech as _tech
from .spice import prims_spiceparams as _params

__all__ = ["pyspicefab"]


_file = Path(__file__)
_libfile = _file.parent.joinpath("models", "all.spice")
pyspicefab = PySpiceFactory(
    libfile=str(_libfile),
    corners=(
        "init",
        "typical", "ff", "ss", "fs", "sf",
    ),
    conflicts={
        "typical": ("ff", "ss", "fs", "sf"),
        "ff": ("typical", "ss", "fs", "sf"),
        "ss": ("typical", "ff", "fs", "sf"),
        "fs": ("typical", "ff", "ss", "sf"),
        "sf": ("typical", "ff", "ss", "fs"),
    },
    prims_params=_params,
)
