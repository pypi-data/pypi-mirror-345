# SPDX-License-Identifier: AGPL-3.0-or-later OR GPL-2.0-or-later OR CERN-OHL-S-2.0+ OR Apache-2.0
"""This contains simulation support classes. Planning is to upstream this
code to PDKMaster after making it more generic. After that this module should
be able to be removed.
So there is no backward compatibility guarantee for code in this module.
"""
from typing import Tuple, Optional
from matplotlib import pyplot as _plt

from PySpice.Unit import u_Degree  # type: ignore

from pdkmaster.technology import primitive as _prm
from pdkmaster.io.spice.typing import CornerSpec

from .pdkmaster import cktfab
from .pyspice import pyspicefab

__all__ = [
    "SimMOS", "SimPNP", "SimR", "sim_plot_mos_vgs_eq_vds",
]


def _reldiff(f1: float, f2: float):
    return abs(f1/f2 - 1)


class SimMOS:
    def __init__(self, *,
        mos: _prm.MOSFET, l: float, w: float,
    ):
        self.ckt = ckt = cktfab.new_circuit(name="mos_ckt")
        mos_inst = ckt.instantiate(mos, name="mos", l=l, w=w)
        ckt.new_net(name="s", external=True, childports=mos_inst.ports.sourcedrain1)
        ckt.new_net(name="d", external=True, childports=mos_inst.ports.sourcedrain2)
        ckt.new_net(name="g", external=True, childports=mos_inst.ports.gate)
        ckt.new_net(name="b", external=True, childports=mos_inst.ports.bulk)

    def Ids(self, *,
        Vgs: float, Vds: float, Vbs: float=0.0,
        corner: CornerSpec, temp: u_Degree=u_Degree(25),
        debug: bool=False,
        **simopts: float,
    ) -> float:
        tb = pyspicefab.new_pyspicecircuit(
            corner=corner, top=self.ckt, title="Id tb",
        )

        tb.V("gnd", "s", tb.gnd, 0.0)
        tb.V("g", "g", "s", Vgs)
        tb.V("d", "d", "s", Vds)
        tb.V("b", "b", "s", Vbs)

        self.last_sim = sim = tb.simulator(temperature=temp)
        if simopts:
            sim.options(**simopts)
        if debug:
            print("Circuit:")
            print(str(sim))
            print("\nSimulating...")
        self.last_op = op = sim.operating_point()
        if debug:
            print("Done.")

        return float(-op.Vd)

    @staticmethod
    def l_for_Ids(*,
        mos: _prm.MOSFET, w: float, l_min: Optional[float]=None, l_max: float,
        Vgs: float, Vds: float, Vbs: float=0.0,
        Ids: float, reltol=0.01, max_runs=100,
        corner: CornerSpec, temp: u_Degree=u_Degree(25),
        debug: bool=False,
        **simopts: float,
    ) -> float:
        if l_min is None:
            l_min = mos.computed.min_l
        Ids = abs(Ids)

        if debug:
            print("Simulating current for l_min and l_max...")
        sim = SimMOS(mos=mos, l=l_min, w=w)
        Ids_lmin = abs(sim.Ids(
            Vgs=Vgs, Vds=Vds, Vbs=Vbs, corner=corner, temp=temp,
            **simopts,
        ))
        if Ids_lmin < Ids:
            raise ValueError(
                f"Simulated current '{Ids_lmin}' too low (<'{Ids}') for l_min '{l_min}'")

        sim = SimMOS(mos=mos, l=l_max, w=w)
        Ids_lmax = abs(sim.Ids(
            Vgs=Vgs, Vds=Vds, Vbs=Vbs, corner=corner, temp=temp,
            **simopts,
        ))
        if Ids_lmax > Ids:
            raise ValueError(
                f"Simulated current '{Ids_lmax}' too high (>'{Ids}') for l_max '{l_max}'")
        if debug:
            print(f"Ids_lmin={Ids_lmin}, Ids_lmax={Ids_lmax}")

        # Do binary search for 1/l
        run = 1
        while True:
            l_next = 1/(0.5*(1/l_min + 1/l_max))

            if debug:
                print(f"Simulating next current ... (l_next={l_next})")
            sim = SimMOS(mos=mos, l=l_next, w=w)
            Ids_lnext = abs(sim.Ids(
                Vgs=Vgs, Vds=Vds, Vbs=Vbs, corner=corner, temp=temp,
                **simopts,
            ))
            if debug:
                print(f"Ids_lnext={Ids_lnext}")

            reldiff = _reldiff(Ids_lnext, Ids)
            if reldiff < reltol:
                if debug:
                    print("Convergence criteria met")
                return l_next
            elif Ids_lnext < Ids:
                l_max = l_next
            else:
                assert Ids_lnext > Ids
                l_min = l_next

            run += 1
            if run > max_runs:
                raise RuntimeError("Maximum iterations reached")


class SimPNP:
    def __init__(self, *, pnp: _prm.Bipolar):
        assert pnp.type_ == _prm.pnpBipolar
        self.ckt = ckt = cktfab.new_circuit(name="pnp_ckt")
        pnp_inst = ckt.instantiate(pnp, name="pnp")
        ckt.new_net(name="c", external=True, childports=pnp_inst.ports.collector)
        ckt.new_net(name="e", external=True, childports=pnp_inst.ports.emitter)
        ckt.new_net(name="b", external=True, childports=pnp_inst.ports.base)

    def Vec_diode(self, *,
        Iec: float,
        corner: CornerSpec, temp: u_Degree=u_Degree(25),
        debug: bool=False,
        **simopts: float,
    ):
        tb = pyspicefab.new_pyspicecircuit(
            corner=corner, top=self.ckt, title="Vec_diode tb",
        )

        tb.V("gnd", "c", tb.gnd, 0.0)
        tb.I("ec", "e", "c", -Iec)
        tb.V("bc", "b", "c", 0.0)

        self.last_sim = sim = tb.simulator(temperature=temp)
        if simopts:
            sim.options(**simopts)
        if debug:
            print("Circuit:")
            print(str(sim))
            print("\nSimulating...")
        self.last_op = op = sim.operating_point()
        if debug:
            print("Done.")

        return float(op.e)


class SimR:
    def __init__(self, *, resistor: _prm.Resistor, height: float) -> None:
        self.resistor = resistor
        self.height = height

        self.ckt = ckt = cktfab.new_circuit(name="r_ckt")
        res_inst = ckt.instantiate(resistor, name="r", length=height)
        ckt.new_net(name="n1", external=True, childports=res_inst.ports.port1)
        ckt.new_net(name="n2", external=True, childports=res_inst.ports.port2)

    def R(self, *,
        Vsim: float=1.0,
        corner: CornerSpec, temp: u_Degree=u_Degree(25),
        debug: bool=False,
        **simopts: float,
    ) -> float:
        tb = pyspicefab.new_pyspicecircuit(
            corner=corner, top=self.ckt, title="R tb",
        )

        tb.V("gnd", "n1", tb.gnd, 0.0)
        tb.V("r", "n2", "n1", Vsim)

        self.last_sim = sim = tb.simulator(temperature=temp)
        if simopts:
            sim.options(**simopts)
        if debug:
            print("Circuit:")
            print(str(sim))
            print("\nSimulating...")
        self.last_op = op = sim.operating_point()
        if debug:
            print(f"Done, (V={Vsim}, Ir={float(-op.Vr)})")

        return Vsim/float(-op.Vr)

    @staticmethod
    def height_for_R(*,
        resistor: _prm.Resistor, start_height: float,
        R: float,
        Vsim: float=1.0, R_reldiff=0.001,
        corner: CornerSpec, temp: u_Degree=u_Degree(25),
        debug: bool=False,
        **simopts: float
    ) -> float:
        """Compute new height to get wanted R value.

        Will start from the height given during SimR object creation.
        """
        run = 1
        height = start_height
        prevreldiff: Optional[float] = None
        if debug:
            print("Starting first run")
        while True: # Run until we have converged
            sim = SimR(resistor=resistor, height=height)
            Rsim = sim.R(
                Vsim=Vsim, corner=corner, temp=temp, **simopts,
            )
            reldiff = _reldiff(Rsim, R)
            if debug:
                print(f"Run {run}: height={height}, Rsim={Rsim}, reldiff={reldiff}")
            if reldiff < R_reldiff:
                if debug:
                    print("Tolerance criteria met")
                return height

            if (prevreldiff is not None) and (prevreldiff < reldiff):
                # Resistance is assumed to be quite linear with height so we should
                # converge in each step.
                raise RuntimeError("Simulation not converging")
            prevreldiff = reldiff

            # Compute new height
            height = height*R/Rsim

            run += 1


def sim_plot_mos_vgs_eq_vds(
    mos: _prm.MOSFET, corner: CornerSpec,
    lnom: float, ws: Tuple[float, ...],
    wnom: float, ls: Tuple[float, ...],
    vgs: slice, vzoom: Tuple[float, float], imax: Tuple[float, float, float, float],
    temp: u_Degree=u_Degree(25),
    debug: bool=False,
):
    is_n = mos.implant[0].type_ == _prm.nImpl

    n_ws = len(ws)
    n_ls = len(ls)
    ckt = cktfab.new_circuit(name="nmos_tb")
    sb = ckt.new_net(name=f"sb", external=True)

    for i, w in enumerate(ws):
        nmos_inst = ckt.instantiate(mos, name=f"nmos_w{i}", l=lnom, w=w)
        ckt.new_net(name=f"nmos_w{i}_gd", external=True, childports=(
            nmos_inst.ports.sourcedrain2, nmos_inst.ports.gate,
        ))
        sb.childports += (nmos_inst.ports.sourcedrain1, nmos_inst.ports.bulk)
    for i, l in enumerate(ls):
        nmos_inst = ckt.instantiate(mos, name=f"nmos_l{i}", l=l, w=wnom)
        ckt.new_net(name=f"nmos_l{i}_gd", external=True, childports=(
            nmos_inst.ports.sourcedrain2, nmos_inst.ports.gate,
        ))
        sb.childports += (nmos_inst.ports.sourcedrain1, nmos_inst.ports.bulk)

    tb = pyspicefab.new_pyspicecircuit(
        corner=corner, top=ckt, title="nmos_tb",
    )

    pos = "gd" if is_n else "sb"
    neg = "sb" if is_n else "gd"
    tb.V("gs", pos, neg, 1.8)
    tb.V("gnd", neg, tb.gnd, 0.0)

    for i in range(n_ws):
        # Current measurement
        tb.V(f"w{i}", "gd", f"nmos_w{i}_gd", 0.0)
    for i in range(n_ls):
        # Current measurement
        tb.V(f"l{i}", "gd", f"nmos_l{i}_gd", 0.0)

    sim = tb.simulator(temperature=temp)
    print("Simulating...")
    if debug:
        print(str(sim))
    dc = sim.dc(vgs=vgs)
    print("Done")

    _plt.figure(figsize=(16,14))

    _plt.subplot(2, 2, 1)
    for i, w in enumerate(ws):
        _plt.plot(dc.sweep, dc.branches[f"vw{i}"], label=f"w={round(ws[i], 3)}µm")
    cur = imax[0]
    _plt.axis((vgs.start, vgs.stop, min(0.0, cur), max(0.0, cur)))
    _plt.title(f"l={lnom}µm")
    _plt.xlabel("|Vgs|=|Vds| [V]")
    _plt.ylabel("Ids [A]")
    _plt.legend()
    _plt.grid(True)
    _plt.subplot(2, 2, 2)
    for i, w in enumerate(ws):
        _plt.plot(dc.sweep, dc.branches[f"vw{i}"], label=f"w={round(ws[i], 3)}µm")
    cur = imax[1]
    _plt.axis((*vzoom, min(0.0, cur), max(0.0, cur)))
    _plt.title(f"l={lnom}µm")
    _plt.xlabel("|Vgs|=|Vds| [V]")
    _plt.ylabel("Ids [A]")
    _plt.legend()
    _plt.grid(True)

    _plt.subplot(2, 2, 3)
    for i, l in enumerate(ls):
        _plt.plot(dc.sweep, dc.branches[f"vl{i}"], label=f"l={round(ls[i], 3)}µm")
    cur = imax[2]
    _plt.axis((vgs.start, vgs.stop, min(0.0, cur), max(0.0, cur)))
    _plt.title(f"w={wnom}µm")
    _plt.xlabel("|Vgs|=|Vds| [V]")
    _plt.ylabel("Ids [A]")
    _plt.legend()
    _plt.grid(True)
    _plt.subplot(2, 2, 4)
    for i, l in enumerate(ls):
        _plt.plot(dc.sweep, dc.branches[f"vl{i}"], label=f"l={round(ls[i], 3)}µm")
    cur = imax[3]
    _plt.axis((*vzoom, min(0.0, cur), max(0.0, cur)))
    _plt.title(f"w={wnom}µm")
    _plt.xlabel("|Vgs|=|Vds| [V]")
    _plt.ylabel("Ids [A]")
    _plt.legend()
    _plt.grid(True)
