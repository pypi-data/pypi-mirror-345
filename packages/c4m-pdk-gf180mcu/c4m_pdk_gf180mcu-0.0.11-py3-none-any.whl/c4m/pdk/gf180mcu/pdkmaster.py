# SPDX-License-Identifier: AGPL-3.0-or-later OR GPL-2.0-or-later OR CERN-OHL-S-2.0+ OR Apache-2.0
from pdkmaster.typing import GDSLayerSpecDict
from pdkmaster.technology import (
    property_ as _prp, primitive as _prm, technology_ as _tch,
)
from pdkmaster.technology.primitive import _derived as _prmderv
from pdkmaster.design import circuit as _ckt, layout as _lay


__all__ = [
    "tech", "layoutfab", "cktfab", "gds_layers",
]


class _GF180MCU(_tch.Technology):
    @property
    def name(self) -> str:
        return "GF180MCU"
    @property
    def grid(self) -> float:
        return 0.005

    def __init__(self):
        base = _prm.Base(type_=_prm.pBase)

        nwell = _prm.Well(
            name="Nwell",
            min_width=0.86, # NW.1a
            min_space=1.7, # NW.2b, TODO: 1.4µm for 3.3V Nwell
            type_=_prm.nImpl,
            # min_space_samenet=0.74, # NW.2a, TODO 0.6µm for 3.3V
        )
        nplus = _prm.Implant(
            name="Nplus",
            min_width=0.4, # NP.1
            min_space=0.4, # NP.2
            min_area=0.35, # NP.8a
            #min_hole_area=0.35, # NP.8b
            type_=_prm.nImpl,
        )
        pplus = _prm.Implant(
            name="Pplus",
            min_width=0.4, # PP.1
            min_space=0.4, # PP.2
            min_area=0.35, # PP.8a
            #min_hole_area=0.35, # PP.8b
            type_=_prm.pImpl,
        )
        dualgate = _prm.Insulator(
            name="Dualgate",
            min_width=0.7, # DV.5
            min_space=0.44, # DV.2
        )
        v5_xtor = _prm.Marker(
            name="V5_XTOR",
        )

        comp = _prm.WaferWire(
            name="COMP",
            # min_width=0.22, # DF.1a, 5V below
            min_width=0.30, # Needed for sff1(r)_x4
            min_space=0.28, # DF.3a, 5V below
            min_area=0.2025, #
            # min_hole_area=0.26, # DF.10
            implant=(nplus, pplus),
            min_implant_enclosure=_prp.Enclosure(0.16), # NP.5bcd
            implant_abut="all",
            allow_contactless_implant=False,
            well=nwell,
            min_well_enclosure=_prp.Enclosure(0.43), # DF.4c
            min_well_enclosure4oxide={
                dualgate: _prp.Enclosure(0.6), # DF.4c
            },
            min_well_enclosure_same_type=_prp.Enclosure(0.16), # DF.4d, TODO: 0.12 for 3.3V
            allow_in_substrate=True,
            min_substrate_enclosure=_prp.Enclosure(0.43), # DF.16
            min_substrate_enclosure4oxide={
                dualgate: _prp.Enclosure(0.6), # DF.16
            },
            min_substrate_enclosure_same_type=_prp.Enclosure(0.16), # DF.17, TODO: 0.12 for 3.3V
            oxide=dualgate,
            min_oxide_enclosure=_prp.Enclosure(0.24), # DV.6
            allow_well_crossing=False,
        )
        comp5_width = _prm.MinWidth(prim=comp.in_(dualgate), min_width=0.3)
        comp5_space = _prm.Spacing(primitives1=comp.in_(dualgate), min_space=0.36) # DF.3a
        poly2 = _prm.GateWire(
            name="Poly2",
            # min_width= 0.18, # PL.1
            min_width=0.28, # Same as min_l of 3.3V transistor
            min_space=0.24, # PL.3a
        )
        poly2_width = _prm.MinWidth(
            # TODO: remove use of internal PDKMaster class
            prim=_prmderv._Intersect(prims=(poly2, dualgate)),
            min_width=0.20, # PL.1
        )
        comp_poly2_space = _prm.Spacing(
            primitives1=comp, primitives2=poly2,
            min_space=0.3, # PL.5a & PL.5b, TODO: 0.1µm for 3.3V
        )
        metal_pins = (
            *(
                _prm.Marker(name=f"Metal{n + 1}_Label")
                for n in range(5)
            ),
            _prm.Marker(name="MetalTop_Label"),
        )
        metals = (
            *(
                _prm.MetalWire(
                    name=f"Metal{n + 1}",
                    pin=metal_pins[n],
                    min_width=(0.23 if n == 0 else 0.28), # Mn.1
                    min_space=(0.23 if n == 0 else 0.28), # Mn.2a
                    space_table=((10.0, 0.3),), # Mn.2b
                    min_area=0.1444, # Mn.3
                    min_density=0.30, # Mn.4
                ) for n in range(5)
            ),
            _prm.MetalWire(
                name="MetalTop", # Use thick top metal
                pin=metal_pins[-1],
                min_width=0.44, # MT.1
                min_space=0.436, # MT.2a
                space_table=((10.0, 0.60),), # MT.2b
                min_area=0.5625, #MT.4
                min_density=0.30, # MT.3
            )
        )

        vias = (
            _prm.Via(
                name="Contact",
                width=0.22, # CO.1
                min_space=0.28, # CO.2b, TODO: allow CO.2a
                bottom=(comp, poly2),
                min_bottom_enclosure=_prp.Enclosure(0.07), # CO.3 & CO.4
                top=metals[0],
                min_top_enclosure=_prp.Enclosure((0.06, 0.005)), # CO.6
            ),
            *(
                _prm.Via(
                    name=f"Via{n + 1}",
                    width=0.26, # Vn.1
                    min_space=0.36, # Vn.2b, TODO: allow Vn.2a
                    bottom=metals[n],
                    min_bottom_enclosure=_prp.Enclosure((0.06, 0.00 if n == 0 else 0.01)),
                    top=metals[n + 1],
                    min_top_enclosure=_prp.Enclosure((0.06, 0.01)),
                ) for n in range(5)
            ),
        )

        fet33gate = _prm.MOSFETGate(
            name="fet33gate",
            active=comp, poly=poly2,
            min_l=0.28, # PL.2
            min_w=0.22, # DF.2a
            # min_sd_width=0.24, # DF.6
            min_sd_width=0.30, # Join COMP in standard cells
            min_polyactive_extension=0.22, # PL.4
            contact=vias[0],
            min_contactgate_space=0.15, # CO.7
        )
        nfet_03v3 = _prm.MOSFET(
            name="nfet_03v3", gate=fet33gate, implant=nplus,
            min_gateimplant_enclosure=_prp.Enclosure(0.23), # NP.5a
        )
        pfet_03v3 = _prm.MOSFET(
            name="pfet_03v3", gate=fet33gate, implant=pplus, well=nwell,
            min_gateimplant_enclosure=_prp.Enclosure(0.23), # PP.5a
        )

        fet5gate = _prm.MOSFETGate(
            name="fet5gate",
            active=comp, poly=poly2, oxide=dualgate, inside=v5_xtor,
            min_l=0.5, # PL.2 for PMOS, need higher min_l for 5V NMOS
            min_sd_width=0.40, # DF.6
            min_polyactive_extension=0.22, # PL.4
            contact=vias[0],
            min_contactgate_space=0.15, # CO.7
        )
        nfet_05v0 = _prm.MOSFET(
            name="nfet_05v0", gate=fet5gate, implant=nplus,
            min_l=0.6, # PL.2
            min_gateimplant_enclosure=_prp.Enclosure(0.23), # NP.5a
        )
        pfet_05v0 = _prm.MOSFET(
            name="pfet_05v0", gate=fet5gate, implant=pplus, well=nwell,
            min_gateimplant_enclosure=_prp.Enclosure(0.23), # PP.5a
        )

        super().__init__(primitives=_prm.Primitives((
            base, nwell, nplus, pplus, dualgate, v5_xtor,
            comp, comp5_width, comp5_space,
            poly2, poly2_width, comp_poly2_space,
            *metal_pins, *metals, *vias,
            fet33gate, nfet_03v3, pfet_03v3,
            fet5gate, nfet_05v0, pfet_05v0,
        )))

tech = _GF180MCU()
cktfab = _ckt.CircuitFactory(tech=tech)
layoutfab = _lay.LayoutFactory(tech=tech)
gds_layers: GDSLayerSpecDict = {
    "Nwell": (21, 0),
    "Nplus": (32, 0),
    "Pplus": (31, 0),
    "Dualgate": (55, 0),
    "V5_XTOR": (112, 1),
    "COMP": (22, 0),
    "Poly2": (30, 0),
    "Contact": (33, 0),
    "Metal1_Label": (34, 10),
    "Metal1": (34, 0),
    "Via1": (35, 0),
    "Metal1_Label": (34, 10),
    "Metal1": (34, 0),
    "Via1": (35, 0),
    "Metal2_Label": (36, 10),
    "Metal2": (36, 0),
    "Via2": (38, 0),
    "Metal3_Label": (42, 10),
    "Metal3": (42, 0),
    "Via3": (40, 0),
    "Metal4_Label": (46, 10),
    "Metal4": (46, 0),
    "Via4": (41, 0),
    "Metal5_Label": (81, 10),
    "Metal5": (81, 0),
    "Via5": (82, 0),
    "MetalTop_Label": (53, 10),
    "MetalTop": (53, 0),
}