# SPDX-License-Identifier: AGPL-3.0-or-later OR GPL-2.0-or-later OR CERN-OHL-S-2.0+ OR Apache-2.0
from pdkmaster.io.spice import SpicePrimsParamSpec, SpiceNetlistFactory

from .pdkmaster import tech as _tech


__all__ = ["prims_spiceparams", "netlistfab"]


_prims = _tech.primitives
prims_spiceparams = SpicePrimsParamSpec()
for dev_name, params in (
    # sheet resistances are estimated from the model
    ("ndiff_res", dict(sheetres=120.0, model="sky130_fd_pr__res_generic_nd")),
    ("pdiff_res", dict(sheetres=197.0, model="sky130_fd_pr__res_generic_pd")),
    ("poly_res", dict(sheetres=48.2, model="sky130_fd_pr__res_generic_po")),
    ("MIM_m3_capm", dict(model="sky130_fd_pr__cap_mim_m3_1")),
    ("MIM_m4_cap2m", dict(model="sky130_fd_pr__cap_mim_m3_2")),
    ("ndiode", dict(model="sky130_fd_pr__diode_pw2nd_05v5")),
    ("pdiode", dict(model="sky130_fd_pr__diode_pd2nw_05v5")),
    ("nfet_01v8", dict(model="sky130_fd_pr__nfet_01v8__model")),
    ("nfet_01v8_sc", dict(model="sky130_fd_pr__nfet_01v8__model")),
    ("pfet_01v8", dict(model="sky130_fd_pr__pfet_01v8__model")),
    ("nfet_01v8_lvt", dict(model="sky130_fd_pr__nfet_01v8_lvt__model")),
    ("pfet_01v8_lvt", dict(model="sky130_fd_pr__pfet_01v8_lvt__model")),
    ("pfet_01v8_hvt", dict(model="sky130_fd_pr__pfet_01v8_hvt__model")),
    ("nfet_g5v0d10v5", dict(model="sky130_fd_pr__nfet_g5v0d10v5__model")),
    ("pfet_g5v0d10v5", dict(model="sky130_fd_pr__pfet_g5v0d10v5__model")),
    ("npn_05v5_w1u00l1u00", dict(
        model="sky130_fd_pr__npn_05v5_W1p00L1p00", is_subcircuit=True,
    )),
    ("npn_05v5_w1u00l2u00", dict(
        model="sky130_fd_pr__npn_05v5_W1p00L2p00", is_subcircuit=True,
    )),
    ("pnp_05v5_w0u68l0u68", dict(
        model="sky130_fd_pr__pnp_05v5_W0p68L0p68", is_subcircuit=True,
    )),
    ("pnp_05v5_w3u40l3u40", dict(
        model="sky130_fd_pr__pnp_05v5_W3p40L3p40", is_subcircuit=True,
    )),
):
    prims_spiceparams.add_device_params(prim=_prims[
        dev_name], **params, # type: ignore
    )
netlistfab = SpiceNetlistFactory(params=prims_spiceparams)
