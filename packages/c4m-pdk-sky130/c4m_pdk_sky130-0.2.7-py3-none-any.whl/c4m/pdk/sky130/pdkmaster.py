# SPDX-License-Identifier: AGPL-3.0-or-later OR GPL-2.0-or-later OR CERN-OHL-S-2.0+ OR Apache-2.0
from typing import Dict

from pdkmaster.typing import GDSLayerSpecDict
from pdkmaster.technology import (
    property_ as prp, primitive as prm, technology_ as tch
)
from pdkmaster.design import layout as lay, circuit as ckt

__all__ = [
    "tech", "technology", "layoutfab", "layout_factory",
    "cktfab", "circuit_factory", "gds_layers",
    "plotter", # pyright: ignore
]


class _Sky130(tch.Technology):
    @property
    def name(self):
        return "Sky130"
    @property
    def grid(self):
        return 0.005

    def __init__(self):
        prims = prm.Primitives(prm.Base(type_=prm.pBase))

        # TODO: angle design rules

        pin_prims = {
            name: prm.Marker(name=f"{name}.pin")
            for name in (
                "difftap", "poly",
                "li", *(f"m{n + 1}" for n in range(5))
            )
        }
        prims += pin_prims.values()

        block_prims: Dict[str, prm.Marker] = {
            name: prm.Marker(name=f"{name}.block")
            for name in (
                "difftap", "poly",
                "licon", "mcon", "via", *(f"via{n + 1}" for n in range(1, 4)),
                "li", *(f"m{n + 1}" for n in range(5)),
            )
        }
        prims += block_prims.values()

        # single mask based primitives
        implants: Dict[str, prm.Implant] = {
            implant: prm.Implant(name=implant,
                type_=type_,
                min_width=0.38, # nsdm.1; psdm.1
                min_space=0.38, # n/psdm.2
                # n/ psd.10a+b, lvtn.13, hvtp.5
                # Website says 0.255 for psdm but klayout DRC says 0.265
                min_area=0.265, # n/psdm.10a; n/psdm.10b
                # TODO: implement min_hole_area
                # min_hole_area=0.265 # n/ psd.11, lvtn.14, hvtp.6
            ) for implant, type_ in (
                ("nsdm", prm.nImpl),
                ("psdm", prm.pImpl),
                ("lvtn", prm.adjImpl),
                ("hvtp", prm.adjImpl),
            )
        }
        nwm = prm.Well(name="nwm",
            type_=prm.nImpl,
            min_width=0.840, # nwell.1
            min_space=1.270, # nwell.2a
        )
        dnm = prm.DeepWell(name="dnm",
            well=nwm,
            min_width=3.000, # dnwell.2
            min_space=6.300, # dnwell.3
            min_well_overlap=1.030, #nwell.6
            min_well_enclosure=0.400, # nwell.5
        )
        hvi = prm.Insulator(name="hvi",
            min_width = 0.600, min_space = 0.700,
        )
        # Recognition layers
        diffres = prm.Marker(name="diffres")
        polyres = prm.Marker(name="polyres")
        areaid_diode = prm.Marker(name="areaid_diode")
        areaid_sc = prm.Marker(name="areaid_sc")
        pnp = prm.Marker(name="pnp")
        npn = prm.Marker(name="npn")
        prims += (
            *implants.values(), nwm, dnm, hvi, diffres, polyres, areaid_diode, areaid_sc,
            pnp, npn,
        )

        # layers diff and tap will be generated out of difftap
        difftap = prm.WaferWire(name="difftap",
            pin=pin_prims["difftap"], blockage=block_prims["difftap"],
            min_width=0.150, # difftap.1
            min_space=0.270, # difftap.3
            allow_in_substrate=True, well=nwm,
            implant=implants.values(),
            min_implant_enclosure=prp.Enclosure(0.125), # n/ psd.5a+b
            implant_abut="all", # n/ psd.6
            allow_contactless_implant=False,
            min_well_enclosure=prp.Enclosure(0.180), # difftap.8+10
            min_well_enclosure4oxide={
                hvi: prp.Enclosure(0.33), # hvdifftap.17+19
            },
            min_substrate_enclosure=prp.Enclosure(0.340), # difftap.9
            min_substrate_enclosure4oxide={
                hvi: prp.Enclosure(0.43), # hvdifftap.18+20
            },
            min_substrate_enclosure_same_type=prp.Enclosure(0.130), # difftap.11
            allow_well_crossing=False,
            oxide=hvi,
            min_oxide_enclosure=prp.Enclosure(0.180) # hvdifftap.21/22
        )
        poly = prm.GateWire(name="poly",
            pin=pin_prims["poly"], blockage=block_prims["poly"],
            min_width=0.150, # poly.1a
            min_space=0.210, # poly.2
        )
        # wires
        metals: Dict[str, prm.MetalWire] = {
            name: prm.MetalWire(name=name, **wire_args) for name, wire_args in (
                ("li", {
                    "pin": pin_prims["li"],
                    "blockage": block_prims["li"],
                    "min_width": 0.170, # li.1.-
                    "min_space": 0.170, # li.3.-
                }),
                *(
                    (metal, {
                        "pin": pin_prims[metal],
                        "blockage": block_prims[metal],
                        "min_width": 0.140, # m1.1, m2.1
                        # TODO: implement max_width
                        # "max_width": 4.000, # m1.11, m2.11
                        "min_space": 0.140, # m1.2, m2.2
                        "space_table": ((1.5, 0.280),), # m1.3a+b, m2.3a+b
                        "min_area": 0.083 if metal == "m1" else 0.0676, # m1.6, m2.6
                        # TODO: implement min_hole_area
                        # "min_hole_area": 0.14, # m1.7, m2.7
                    }) for metal in ('m1', "m2")
                ),
                *(
                    (metal, {
                        "pin": pin_prims[metal],
                        "blockage": block_prims[metal],
                        "min_width": 0.300, # m3.1, m4.1
                        # TODO: implement max_width
                        # m3.11, m4.11
                        # "max_width": 4.000 if metal == "m3" else 11.000,
                        "min_space": 0.300, # m3.2, m4.2
                        "space_table": ((1.5, 0.400),), # m3.3c+d, m4.3a+b
                        "min_area": 0.240, # m3.7, m4.7
                        # TODO: implement min_hole_area
                        # "min_hole_area": 0.200, # m3.7, m3.7
                    }) for metal in ("m3", "m4")
                ),
                ("m5", {
                    "pin": pin_prims["m5"],
                    "blockage": block_prims["m5"],
                    "min_width": 1.600, # m5.1
                    "min_space": 1.600, # m5.2
                    "min_area": 4.000, # m5.4
                }),
            )
        }
        capm = prm.MIMTop(
            name="capm",
            min_width=1.0, # capm.1
            min_space=0.84, # capm.2a
        )
        cap2m = prm.MIMTop(
            name="cap2m",
            min_width=1.0, # cap2m.1
            min_space=0.84, # cap2m.2a
        )
        # TODO: RDL option
        prims += (difftap, poly, *metals.values(), capm, cap2m)

        # vias
        vias: Dict[str, prm.Via] = {
            via_args["name"]: prm.Via(**via_args) for via_args in (
                {
                    "name": "licon",
                    "blockage": block_prims["licon"],
                    "width": 0.170, # licon.1
                    "min_space": 0.170, # licon.2
                    "bottom": (difftap, poly), # licon.4
                    "top": metals["li"], # licon.4
                    "min_bottom_enclosure": (
                        # See: https://gitlab.com/Chips4Makers/PDKMaster/-/issues/6
                        # prp.Enclosure((0.040, 0.060)), # licon.5a+c
                        prp.Enclosure((0.040, 0.120)), # licon.5a+7
                        prp.Enclosure((0.050, 0.080)), # licon.8+a
                    ),
                    "min_top_enclosure": prp.Enclosure((0.000, 0.080)), # li.5.-
                },
                {
                    "name": "mcon",
                    "blockage": block_prims["mcon"],
                    "width": 0.170, # ct.1
                    "min_space": 0.190, # ct.2
                    "bottom": metals["li"],
                    "top": metals["m1"],
                    "min_bottom_enclosure": prp.Enclosure(0.000), # ct.4
                    "min_top_enclosure": prp.Enclosure((0.030, 0.060)), # m1.4+5
                },
                {
                    "name": "via",
                    "blockage": block_prims["via"],
                    "width": 0.150, # via.1a
                    "min_space": 0.170, # via.2
                    "bottom": metals["m1"],
                    "top": metals["m2"],
                    "min_bottom_enclosure": prp.Enclosure((0.055, 0.085)), # via.4a+5a
                    "min_top_enclosure": prp.Enclosure((0.055, 0.085)), # m2.4+5
                },
                {
                    "name": "via2",
                    "blockage": block_prims["via2"],
                    "width": 0.200, # via2.1a
                    "min_space": 0.200, # via2.2
                    "bottom": metals["m2"],
                    "top": metals["m3"],
                    "min_bottom_enclosure": prp.Enclosure((0.040, 0.085)), # via2.4+5
                    "min_top_enclosure": prp.Enclosure(0.065), # m3.4
                },
                {
                    "name": "via3",
                    "blockage": block_prims["via3"],
                    "width": 0.200, # via3.1
                    "min_space": 0.200, # via3.2
                    "bottom": (metals["m3"], capm),
                    "top": metals["m4"],
                    "min_bottom_enclosure": prp.Enclosure((0.060, 0.090)), # via3.4+5
                    "min_top_enclosure": prp.Enclosure(0.065), # m4.3
                },
                {
                    "name": "via4",
                    "blockage": block_prims["via4"],
                    "width": 0.800, # via4.1
                    "min_space": 0.800, # via4.2
                    "bottom": (metals["m4"], cap2m),
                    "top": metals["m5"],
                    "min_bottom_enclosure": prp.Enclosure(0.190), # via4.4
                    "min_top_enclosure": prp.Enclosure(0.310), # m5.3
                },
            )
        }
        pad = prm.PadOpening(name="pad",
            # TODO: Can min_width be reduced ?
            min_width=40.000, # Own rule
            min_space=1.270, # pad.2
            bottom=metals["m5"],
            min_bottom_enclosure=prp.Enclosure(1.000), # Own rule
        )
        prims += (*vias.values(), pad)

        poly_licon = vias["licon"].in_(poly)

        # misc using wires
        prims += (
            # resistors
            *(
                prm.Resistor(name=name,
                    min_width=0.33, # poly.3
                    wire=wire,
                    indicator=marker,
                    implant=implant,
                    min_implant_enclosure=enc,
                    min_indicator_extension=self.grid, # Own rule
                    contact=vias["licon"],
                    min_contact_space=0.045, # own rule
                )
                for name, wire, marker, implant, enc in (
                    ("ndiff_res", difftap, diffres, implants["nsdm"], difftap.min_implant_enclosure[0]),
                    ("pdiff_res", difftap, diffres, implants["nsdm"], difftap.min_implant_enclosure[0]),
                    ("poly_res", poly, polyres, (), ()),
                )
            ),
            # capacitors
            prm.MIMCapacitor(
                name="MIM_m3_capm", bottom=metals["m3"], top=capm, via=vias["via3"],
                min_bottom_top_enclosure=prp.Enclosure(0.14), # capm.3_a
                min_bottomvia_top_space=0.14, # capm.2b
                min_top_via_enclosure=prp.Enclosure(0.14), # capm.4
                min_bottom_space=1.2, # capm.2b_a
                min_top2bottom_space=0.5, # capm.11
            ),
            prm.MIMCapacitor(
                name="MIM_m4_cap2m", bottom=metals["m4"], top=cap2m, via=vias["via4"],
                min_bottom_top_enclosure=prp.Enclosure(0.14), # capm.3_a
                min_bottomvia_top_space=0.14, # capm.2b
                min_top_via_enclosure=prp.Enclosure(0.14), # capm.4
                min_bottom_space=1.2, # capm.2b_a
                min_top2bottom_space=0.5, # capm.11
            ),
            # TODO: licon on top of unsilicided poly(/difftap?) is allowed
            # diodes
            prm.Diode(
                name="ndiode", wire=difftap, implant=implants["nsdm"],
                indicator=areaid_diode, min_indicator_enclosure=prp.Enclosure(self.grid),
            ),
            prm.Diode(
                name="pdiode", wire=difftap, implant=implants["psdm"], well=nwm,
                indicator=areaid_diode, min_indicator_enclosure=prp.Enclosure(self.grid),
            ),

            # extra width rules
            prm.MinWidth( # hvdifftap.14
                prim=difftap.in_(hvi), min_width=0.29,
            ),
            # extra space rules
            prm.Spacing( # poly.4
                primitives1=difftap, primitives2=poly, min_space=0.075,
            ),
            prm.Spacing( # licon.9
                primitives1=poly_licon, primitives2=implants["psdm"], min_space=0.110,
            ),
            # See: https://gitlab.com/Chips4Makers/PDKMaster/-/issues/6
            prm.Spacing( # licon.14
                primitives1=vias["licon"], primitives2=difftap, min_space=0.190,
            ),
            prm.Spacing( # hvdifftap.15a
                primitives1=difftap.in_(hvi), min_space=0.300,
            ),
            prm.Spacing( # hvdifftap.15b
                primitives1=difftap.in_((hvi, implants["nsdm"])),
                primitives2=difftap.in_((hvi, implants["psdm"])),
                min_space=0.370,
                allow_abut=True,
            ),
            prm.Spacing( # hvdifftap.23
                primitives1=difftap, primitives2=hvi, min_space=0.180,
            )
        )

        # transistors
        mosgate = prm.MOSFETGate(name="mosgate",
            active=difftap, poly=poly,
            # No need for overruling min_l
            min_w=0.420, # difftap.2
            min_sd_width=0.250, # poly.7
            min_polyactive_extension=0.130, # poly.8
            contact=vias["licon"], min_contactgate_space=0.055, # licon.11
        )
        # For logic NMOS a minimum w of 0.36 is allowed when drawing areaid.sc
        # layer on top of it.
        mosgate_sc = prm.MOSFETGate(name="mosgate_sc",
            active=difftap, poly=poly,
            inside=areaid_sc, min_gateinside_enclosure=prp.Enclosure(self.grid),
            # No need for overruling min_l
            min_w=0.360, # specific klayout rule
            min_sd_width=0.250, # poly.7
            min_polyactive_extension=0.130, # poly.8
            contact=vias["licon"], min_contactgate_space=0.055, # licon.11
        )
        hvmosgate = prm.MOSFETGate(name="hvmosgate",
            active=difftap, poly=poly, oxide=hvi,
            min_l=0.500, # hvpoly.13
            min_w=0.420, # difftap.2
            min_gateoxide_enclosure=prp.Enclosure(0.200),
            min_sd_width=0.250, # poly.7
            min_polyactive_extension=0.130, # poly.8
            contact=vias["licon"],
            min_contactgate_space=0.055, # licon.11
        )
        trans = {
            name: prm.MOSFET(name=name,
                gate=gate, implant=impl, well=well,
                min_gateimplant_enclosure=prp.Enclosure(0.070), # Implant.1
            )
            for name, gate, impl, well in (
                ("nfet_01v8", mosgate, implants["nsdm"], None),
                ("nfet_01v8_sc", mosgate_sc, implants["nsdm"], None),
                ("pfet_01v8", mosgate, implants["psdm"], nwm),
                ("nfet_01v8_lvt", mosgate, (implants["nsdm"], implants["lvtn"]), None),
                ("pfet_01v8_lvt", mosgate, (implants["psdm"], implants["lvtn"]), nwm),
                ("pfet_01v8_hvt", mosgate, (implants["psdm"], implants["hvtp"]), nwm),
                ("nfet_g5v0d10v5", hvmosgate, implants["nsdm"], None),
                ("pfet_g5v0d10v5", hvmosgate, implants["psdm"], nwm),
            )
        }
        prims += (mosgate, mosgate_sc, hvmosgate, *trans.values())

        bipolars =  tuple(
            prm.Bipolar(name=name, type_=type_, indicator=ind)
            for name, type_, ind in (
                ("npn_05v5_w1u00l1u00", prm.npnBipolar, npn),
                ("npn_05v5_w1u00l2u00", prm.npnBipolar, npn),
                ("pnp_05v5_w0u68l0u68", prm.pnpBipolar, pnp),
                ("pnp_05v5_w3u40l3u40", prm.pnpBipolar, pnp),
            )
        )
        prims += bipolars

        prims += prm.Auxiliary(name="prBoundary")

        super().__init__(primitives=prims)

tech = technology = _Sky130()
cktfab = circuit_factory = ckt.CircuitFactory(tech=tech)
layoutfab = layout_factory = lay.LayoutFactory(tech=tech)
gds_layers: GDSLayerSpecDict = {
    # For li/metal layer we fix datatype to 20
    # Custom layers:
    # There is descrepancy between klayout DRC script and magic tech file in layer
    # definition. Magic one used as reference.
    # - *.pin; datatype 16
    # - *.block; layer: 100, different datatype per layer; multiple of 10
    #   blockage not in magic tech file

    "nwm": (64, 20), # NWell
    "dnm": (64, 18), # Deep NWell
    "difftap": (65, 20), # We will generate diff and tap from difftap, fix to datatype 20
    "difftap.pin": (65, 16),
    "difftap.block": (100, 10),
    "diffres": (65, 13),
    "nsdm": (93, 44), # N+ implant
    "psdm": (94, 20), # P+ implant
    "areaid_diode": (81, 23), # Diode recognition layer
    "lvtn": (125, 44), # low-Vt adjust
    "hvtp": (78, 44), # pmos high-Vt adjust
    "hvi": (75, 20), # Thick oxide
    "poly": (66, 20),
    "poly.pin": (66, 16),
    "poly.block": (100, 20),
    "polyres": (66, 13),
    "areaid_sc": (81, 4),
    "licon": (66, 44),
    "licon.block": (100, 30),
    "li": (67, 20), # We fix it to datatype 20
    "li.pin": (67, 16),
    "li.block": (100, 40),
    "mcon": (67, 44),
    "mcon.block": (100, 50),
    "m1": (68, 20),
    "m1.pin": (68, 16),
    "m1.block": (100, 60),
    "via": (68, 44),
    "via.block": (100, 70),
    "m2": (69, 20),
    "m2.pin": (69, 16),
    "m2.block": (100, 80),
    "via2": (69, 44),
    "via2.block": (100, 90),
    "m3": (70, 20),
    "m3.pin": (70, 16),
    "m3.block": (100, 100),
    "capm": (89, 44),
    "via3": (70, 44),
    "via3.block": (100, 110),
    "m4": (71, 20),
    "m4.pin": (71, 16),
    "m4.block": (100, 120),
    "cap2m": (97, 44),
    "via4": (71, 44),
    "via4.block": (100, 130),
    "m5": (72, 20),
    "m5.pin": (72, 16),
    "m5.block": (100, 140),
    "pad": (76, 20),
    "prBoundary": (235, 4),
    "npn": (82, 20),
    "pnp": (82, 44),
    # Unhandled layers
    # "pwbm": (19, 44),
    # "pwde": (124, 20),
    # "natfet": (124, 21),
    # "hvtr": (18,20),
    # "ldntm": (11, 44),
    # "tunm": (80,20),
    # "hvntm": (125, 20),
    # "rpm": (86, 20),
    # "urpm": (79, 20),
    # "npc": (95, 20),
    # "nsm": (61, 20),
    # "vhvi": (74, 21),
    # "uhvi": (74, 22),
    # "inductor": (82, 24),
    # "vpp": (82, 64),
    # "lvs_prune": (84, 44),
    # "ncm": (92, 44),
    # "padcenter": (81, 20),
    # "mf": (76, 44),
    # "areaid_sl": (81, 1),
    # "areaid_ce": (81, 2),
    # "areaid_fe": (81, 3),
    # "areaid_sf": (81, 6),
    # "areaid_sw": (81, 7),
    # "areaid_sr": (81, 8),
    # "areaid_mt": (81, 10),
    # "areaid_dt": (81, 11),
    # "areaid_ft": (81, 12),
    # "areaid_ww": (81, 13),
    # "areaid_ld": (81, 14),
    # "areaid_ns": (81, 15),
    # "areaid_ij": (81, 17),
    # "areaid_zr": (81, 18),
    # "areaid_ed": (81, 19),
    # "areaid_de": (81, 23),
    # "areaid_rd": (81, 24),
    # "areaid_dn": (81, 50),
    # "areaid_cr": (81, 51),
    # "areaid_cd": (81, 52),
    # "areaid_st": (81, 53),
    # "areaid_op": (81, 54),
    # "areaid_en": (81, 57),
    # "areaid_en20": (81, 58),
    # "areaid_le": (81, 60),
    # "areaid_hl": (81, 63),
    # "areaid_sd": (81, 70),
    # "areaid_po": (81, 81),
    # "areaid_it": (81, 84),
    # "areaid_et": (81, 101),
    # "areaid_lvt": (81, 108),
    # "areaid_re": (81, 125),
    # "areaid_ag": (81, 79),
    # "poly_rs": (66, 13),
    # "diff_rs": (65, 13),
    # "pwell_rs": (64, 13),
    # "li_rs": (67, 13),
    # "cfom": (22, 20),
}


# Use __getattr__ for plotter so io.notebook is only imported when used.
_plotter = None
def __getattr__(name: str):
    if name == "plotter":
        global _plotter
        if _plotter is None:
            from pdkmaster.io import notebook as nb
            _plotter = nb.Plotter({
                # "pwell": {"fc": (1.0, 1.0, 0.0, 0.2), "ec": "orange", "zorder": 10},
                "nwm": {"fc": (0.0, 0.0, 0.0, 0.1), "ec": "grey", "zorder": 10},
                "difftap": {"fc": "lawngreen", "ec": "lawngreen", "zorder": 11},
                "poly": {"fc": "red", "ec": "red", "zorder": 12},
                "nsdm": {"fc": "purple", "ec": "purple", "alpha": 0.3, "zorder": 13},
                "psdm": {"fc": "blueviolet", "ec": "blueviolet", "alpha": 0.3, "zorder": 13},
                "lvtn": {"fc": (0.0, 0.0, 0.0, 0.0), "ec": "grey", "zorder": 13},
                "hvtp": {"fc": (1, 1, 1, 0.3), "ec": "whitesmoke", "zorder": 13},
                "licon": {"fc": "black", "ec": "black", "zorder": 14},
                "li": {"fc": (0.1, 0.1, 1, 0.4), "ec": "blue", "zorder": 15},
            })
        return _plotter
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
