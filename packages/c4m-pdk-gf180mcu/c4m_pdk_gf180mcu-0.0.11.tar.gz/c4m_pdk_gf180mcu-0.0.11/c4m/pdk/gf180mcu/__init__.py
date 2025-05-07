# SPDX-License-Identifier: AGPL-3.0-or-later OR GPL-2.0-or-later OR CERN-OHL-S-2.0+ OR Apache-2.0
from importlib import import_module
from typing import Iterable, Any

from pdkmaster.design import library as _lbry

from c4m.flexcell import factory as _stdfab

from .pdkmaster import *
from .spice import *
from .pyspice import *
from .klayout import register_primlib as pya_register_primlib


# This module uses lazy submodule importing using __getattr__() to avoid that all
# libraries are generated when this module is imported.


from .pdkmaster import __all__ as _pdkmaster_all
from .spice import __all__ as _spice_all
from .pyspice import __all__ as _pyspice_all
from .stdcell import __all__ as _stdcell_all

stdcellcanvas: _stdfab.StdCellCanvas
StdCellFactory: type
stdcelllib: _lbry.RoutingGaugeLibrary
stdcelllib: _lbry.RoutingGaugeLibrary
stdcell5v0canvas: _stdfab.StdCellCanvas
StdCell5V0Factory: type
stdcell5v0lib: _lbry.RoutingGaugeLibrary
libs: Iterable[_lbry.Library]
def __getattr__(name: str) -> Any:
    if name in _stdcell_all:
        stdcell = import_module(".stdcell", __name__)
        return getattr(stdcell, name)
    elif name == "libs":
        from .stdcell import (
            stdcelllib, stdcell5v0lib,
        )
        return [
            stdcelllib, stdcell5v0lib,
        ]
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    self = import_module(__name__)
    return sorted((
        *(name for name in self.__dict__.keys() if name.startswith("__")),
        *_pdkmaster_all, *_spice_all, *_pyspice_all,
        "pya_register_primlib",
        *_stdcell_all,
        "libs",
    ))
