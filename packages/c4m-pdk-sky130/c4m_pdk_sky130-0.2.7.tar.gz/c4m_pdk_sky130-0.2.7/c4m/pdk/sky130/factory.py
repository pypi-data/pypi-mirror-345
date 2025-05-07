# SPDX-License-Identifier: AGPL-3.0-or-later OR GPL-2.0-or-later OR CERN-OHL-S-2.0+ OR Apache-2.0
from typing import Optional, Any, cast

from pdkmaster.technology import (
    property_ as _prp, geometry as _geo, primitive as _prm, technology_ as _tch,
)
from pdkmaster.design import (
    circuit as _ckt, layout as _lay, cell as _cell, library as _lbry,
)

from .pdkmaster import tech, cktfab, layoutfab

_prims = tech.primitives


__all__ = ["macrolib"]


class _NPN_05v5_W1u00L1u00(_cell.Cell):
    def __init__(self, *,
        name: str,
        tech: _tch.Technology, cktfab: _ckt.CircuitFactory, layoutfab: _lay.LayoutFactory,
    ):
        super().__init__(name=name, tech=tech, cktfab=cktfab, layoutfab=layoutfab)

        dnm = cast(_prm.DeepWell, _prims["dnm"])
        nwm = cast(_prm.Well, _prims["nwm"])
        # dnwell = cast(_prm.Well, )
        difftap = cast(_prm.WaferWire, _prims["difftap"])
        nsdm = cast(_prm.Implant, _prims["nsdm"])
        psdm = cast(_prm.Implant, _prims["psdm"])
        licon = cast(_prm.Via, _prims["licon"])
        li = cast(_prm.MetalWire, _prims["li"])
        assert li.pin is not None
        lipin = li.pin
        mcon = cast(_prm.Via, _prims["mcon"])
        m1 = cast(_prm.MetalWire, _prims["m1"])
        assert m1.pin is not None
        m1pin = m1.pin
        npn = cast(_prm.Marker, _prims["npn"])
        bnd = cast(_prm.Auxiliary, _prims["prBoundary"])

        ckt = self.new_circuit()
        inst = ckt.instantiate(cast(_prm.Bipolar, _prims["npn_05v5_w1u00l1u00"]), name="npn")
        collector = ckt.new_net(
            name="collector", external=True, childports=inst.ports["collector"],
        )
        base = ckt.new_net(
            name="base", external=True, childports=inst.ports["base"],
        )
        emitter = ckt.new_net(
            name="emitter", external=True, childports=inst.ports["emitter"],
        )
        layouter = self.new_circuitlayouter()
        layout = layouter.layout

        # emitter
        layouter.add_wire(
            net=emitter, wire=licon, columns=3, rows=3,
            bottom=difftap, bottom_enclosure=_prp.Enclosure(0.075),
            bottom_implant=nsdm, bottom_implant_enclosure=_prp.Enclosure(0.67),
            top_enclosure=_prp.Enclosure(0.08),
        )
        l = layouter.add_wire(
            net=emitter, wire=mcon, columns=3, rows=3,
            top_enclosure=_prp.Enclosure(0.06),
        )
        m1bb = l.bounds(mask=m1.mask)
        layouter.add_wire(net=emitter, wire=m1, pin=m1pin, shape=m1bb)

        # base
        outer = _geo.Rect.from_size(width=3.42, height=3.42)
        shape = _geo.Ring(outer_bound=outer, ring_width=0.41)
        layouter.add_wire(wire=difftap, net=base, shape=shape)
        layouter.add_wire(net=base, wire=li, pin=lipin, shape=shape)
        outer = _geo.Rect.from_size(width=3.68, height=3.68)
        shape = _geo.Ring(outer_bound=outer, ring_width=0.67)
        layouter.add_portless(prim=psdm, shape=shape)

        # TODO: Imp[ement RingOfShapes
        p = licon.width + licon.min_space
        m = 1.505
        m2 = 1.02
        n = 7

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=-m, y=-m),
            rows=2, columns=2,
            pitch_y=2*m, pitch_x=2*m,
        )
        layout.add_shape(layer=licon, net=base, shape=shape)

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=-m2, y=-m),
            rows=1, columns=n,
            pitch_x=p,
        )
        layout.add_shape(layer=licon, net=base, shape=shape)

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=-m2, y=m),
            rows=1, columns=n,
            pitch_x=p,
        )
        layout.add_shape(layer=licon, net=base, shape=shape)

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=-m, y=-m2),
            rows=n, columns=1,
            pitch_y=p,
        )
        layout.add_shape(layer=licon, net=base, shape=shape)

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=m, y=-m2),
            rows=n, columns=1,
            pitch_y=p,
        )
        layout.add_shape(layer=licon, net=base, shape=shape)

        # collector
        outer = _geo.Rect.from_size(width=7.44, height=7.44)
        shape = _geo.Ring(outer_bound=outer, ring_width=0.41)
        layout.add_shape(layer=difftap, net=collector, shape=shape)
        layouter.add_wire(net=collector, wire=li, pin=lipin, shape=shape)
        outer = _geo.Rect.from_size(width=7.70, height=7.70)
        shape = _geo.Ring(outer_bound=outer, ring_width=0.67)
        layouter.add_portless(prim=nsdm, shape=shape)
        outer = _geo.Rect.from_size(width=8.62, height=8.62)
        shape = _geo.Ring(outer_bound=outer, ring_width=1.8)
        layouter.add_wire(net=collector, wire=nwm, shape=shape)
        shape = _geo.Rect.from_size(width=7.82, height=7.82)
        layout.add_shape(layer=dnm, net=collector, shape=shape)

        # TODO: Imp[ement RingOfShapes
        p = licon.width + licon.min_space
        m = 3.515
        m2 = 3.06
        n = 19

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=-m, y=-m),
            rows=2, columns=2,
            pitch_y=2*m, pitch_x=2*m,
        )
        layout.add_shape(layer=licon, net=collector, shape=shape)

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=-m2, y=-m),
            rows=1, columns=n,
            pitch_x=p,
        )
        layout.add_shape(layer=licon, net=collector, shape=shape)

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=-m2, y=m),
            rows=1, columns=n,
            pitch_x=p,
        )
        layout.add_shape(layer=licon, net=collector, shape=shape)

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=-m, y=-m2),
            rows=n, columns=1,
            pitch_y=p,
        )
        layout.add_shape(layer=licon, net=collector, shape=shape)

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=m, y=-m2),
            rows=n, columns=1,
            pitch_y=p,
        )
        layout.add_shape(layer=licon, net=collector, shape=shape)

        # npn marker
        shape = _geo.Rect.from_size(width=7.44, height=7.44)
        layouter.add_portless(prim=npn, shape=shape)

        # boundary
        shape = _geo.Rect.from_size(width=8.62, height=8.62)
        layout.boundary = shape
        layouter.add_portless(prim=bnd, shape=shape)


class _NPN_05v5_W1u00L2u00(_cell.Cell):
    def __init__(self, *,
        name: str,
        tech: _tch.Technology, cktfab: _ckt.CircuitFactory, layoutfab: _lay.LayoutFactory,
    ):
        super().__init__(name=name, tech=tech, cktfab=cktfab, layoutfab=layoutfab)

        dnm = cast(_prm.DeepWell, _prims["dnm"])
        nwm = cast(_prm.Well, _prims["nwm"])
        difftap = cast(_prm.WaferWire, _prims["difftap"])
        nsdm = cast(_prm.Implant, _prims["nsdm"])
        psdm = cast(_prm.Implant, _prims["psdm"])
        licon = cast(_prm.Via, _prims["licon"])
        li = cast(_prm.MetalWire, _prims["li"])
        assert li.pin is not None
        lipin = li.pin
        mcon = cast(_prm.Via, _prims["mcon"])
        m1 = cast(_prm.MetalWire, _prims["m1"])
        assert m1.pin is not None
        m1pin = m1.pin
        npn = cast(_prm.Marker, _prims["npn"])
        bnd = cast(_prm.Auxiliary, _prims["prBoundary"])

        ckt = self.new_circuit()
        inst = ckt.instantiate(cast(_prm.Bipolar, _prims["npn_05v5_w1u00l2u00"]), name="npn")
        collector = ckt.new_net(
            name="collector", external=True, childports=inst.ports["collector"],
        )
        base = ckt.new_net(
            name="base", external=True, childports=inst.ports["base"],
        )
        emitter = ckt.new_net(
            name="emitter", external=True, childports=inst.ports["emitter"],
        )
        layouter = self.new_circuitlayouter()
        layout = layouter.layout

        # emitter
        layouter.add_wire(
            net=emitter, wire=licon, columns=3, rows=6,
            bottom=difftap, bottom_enclosure=_prp.Enclosure((0.075, 0.065)),
            bottom_implant=nsdm, bottom_implant_enclosure=_prp.Enclosure(0.67),
            top_enclosure=_prp.Enclosure(0.08),
        )
        l = layouter.add_wire(
            net=emitter, wire=mcon, columns=3, rows=5,
            top_enclosure=_prp.Enclosure(0.06),
        )
        m1bb = l.bounds(mask=m1.mask)
        layouter.add_wire(net=emitter, wire=m1, pin=m1pin, shape=m1bb)

        # base
        outer = _geo.Rect.from_size(width=3.42, height=4.42)
        shape = _geo.Ring(outer_bound=outer, ring_width=0.41)
        layouter.add_wire(wire=difftap, net=base, shape=shape)
        layouter.add_wire(net=base, wire=li, pin=lipin, shape=shape)
        outer = _geo.Rect.from_size(width=3.68, height=4.68)
        shape = _geo.Ring(outer_bound=outer, ring_width=0.67)
        layouter.add_portless(prim=psdm, shape=shape)

        # TODO: Imp[ement RingOfShapes
        p = licon.width + licon.min_space
        mx = 1.505
        my = 2.005
        m2x = 1.02
        m2y = 1.53
        nx = 7
        ny = 10

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=-mx, y=-my),
            rows=2, columns=2,
            pitch_y=2*my, pitch_x=2*mx,
        )
        layout.add_shape(layer=licon, net=base, shape=shape)

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=-m2x, y=-my),
            rows=1, columns=nx,
            pitch_x=p,
        )
        layout.add_shape(layer=licon, net=base, shape=shape)

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=-m2x, y=my),
            rows=1, columns=nx,
            pitch_x=p,
        )
        layout.add_shape(layer=licon, net=base, shape=shape)

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=-mx, y=-m2y),
            rows=ny, columns=1,
            pitch_y=p,
        )
        layout.add_shape(layer=licon, net=base, shape=shape)

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=mx, y=-m2y),
            rows=ny, columns=1,
            pitch_y=p,
        )
        layout.add_shape(layer=licon, net=base, shape=shape)

        # collector
        outer = _geo.Rect.from_size(width=7.44, height=8.44)
        shape = _geo.Ring(outer_bound=outer, ring_width=0.41)
        layout.add_shape(layer=difftap, net=collector, shape=shape)
        layouter.add_wire(net=collector, wire=li, pin=lipin, shape=shape)
        outer = _geo.Rect.from_size(width=7.70, height=8.70)
        shape = _geo.Ring(outer_bound=outer, ring_width=0.67)
        layouter.add_portless(prim=nsdm, shape=shape)
        outer = _geo.Rect.from_size(width=8.62, height=9.62)
        shape = _geo.Ring(outer_bound=outer, ring_width=1.8)
        layouter.add_wire(net=collector, wire=nwm, shape=shape)
        shape = _geo.Rect.from_size(width=7.82, height=8.82)
        layout.add_shape(layer=dnm, net=collector, shape=shape)

        # TODO: Imp[ement RingOfShapes
        p = licon.width + licon.min_space
        mx = 3.515
        my = 4.015
        m2x = 3.06
        m2y = 3.57
        nx = 19
        ny = 22

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=-mx, y=-my),
            rows=2, columns=2,
            pitch_y=2*my, pitch_x=2*mx,
        )
        layout.add_shape(layer=licon, net=collector, shape=shape)

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=-m2x, y=-my),
            rows=1, columns=nx,
            pitch_x=p,
        )
        layout.add_shape(layer=licon, net=collector, shape=shape)

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=-m2x, y=my),
            rows=1, columns=nx,
            pitch_x=p,
        )
        layout.add_shape(layer=licon, net=collector, shape=shape)

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=-mx, y=-m2y),
            rows=ny, columns=1,
            pitch_y=p,
        )
        layout.add_shape(layer=licon, net=collector, shape=shape)

        shape = _geo.ArrayShape(
            shape=_geo.Rect.from_size(width=licon.width, height=licon.width),
            offset0=_geo.Point(x=mx, y=-m2y),
            rows=ny, columns=1,
            pitch_y=p,
        )
        layout.add_shape(layer=licon, net=collector, shape=shape)

        # npn marker
        shape = _geo.Rect.from_size(width=7.44, height=8.44)
        layouter.add_portless(prim=npn, shape=shape)

        # boundary
        shape = _geo.Rect.from_size(width=8.62, height=9.62)
        layout.boundary = shape
        layouter.add_portless(prim=bnd, shape=shape)


class _PNP_05v5_W0u68L0u68(_cell.Cell):
    def __init__(self, *,
        name: str,
        tech: _tch.Technology, cktfab: _ckt.CircuitFactory, layoutfab: _lay.LayoutFactory,
    ):
        super().__init__(name=name, tech=tech, cktfab=cktfab, layoutfab=layoutfab)

        nwm = cast(_prm.Well, _prims["nwm"])
        difftap = cast(_prm.WaferWire, _prims["difftap"])
        nsdm = cast(_prm.Implant, _prims["nsdm"])
        psdm = cast(_prm.Implant, _prims["psdm"])
        licon = cast(_prm.Via, _prims["licon"])
        li = cast(_prm.MetalWire, _prims["li"])
        assert li.pin is not None
        lipin = li.pin
        mcon = cast(_prm.Via, _prims["mcon"])
        m1 = cast(_prm.MetalWire, _prims["m1"])
        assert m1.pin is not None
        m1pin = m1.pin
        pnp = cast(_prm.Marker, _prims["pnp"])
        bnd = cast(_prm.Auxiliary, _prims["prBoundary"])

        ckt = self.new_circuit()
        inst = ckt.instantiate(cast(_prm.Bipolar, _prims["pnp_05v5_w0u68l0u68"]), name="pnp")
        collector = ckt.new_net(
            name="collector", external=True, childports=inst.ports["collector"],
        )
        base = ckt.new_net(
            name="base", external=True, childports=inst.ports["base"],
        )
        emitter = ckt.new_net(
            name="emitter", external=True, childports=inst.ports["emitter"],
        )

        layouter = self.new_circuitlayouter()
        layout = layouter.layout

        # emitter
        layouter.add_wire(
            net=emitter, wire=licon, columns=2, rows=2,
            bottom=difftap, bottom_enclosure=_prp.Enclosure(0.085),
            bottom_implant=psdm, bottom_implant_enclosure=_prp.Enclosure(0.13),
            top_enclosure=_prp.Enclosure(0.14),
        )
        l = layouter.add_wire(
            net=emitter, wire=mcon, columns=2, rows=2, space=0.33,
            top_enclosure=_prp.Enclosure(0.09),
        )
        m1bb = l.bounds(mask=m1.mask)
        layouter.add_wire(net=emitter, wire=m1, pin=m1pin, shape=m1bb)

        # base
        outer = _geo.Rect.from_size(width=2.09, height=2.09)
        shape = _geo.Ring(outer_bound=outer, ring_width=0.36)
        layouter.add_wire(wire=difftap, net=base, shape=shape)
        layouter.add_wire(net=base, wire=li, pin=lipin, shape=shape)
        outer = _geo.Rect.from_size(width=2.35, height=2.35)
        shape = _geo.Ring(outer_bound=outer, ring_width=0.62)
        layouter.add_portless(prim=nsdm, shape=shape)

        m = 0.84
        dx = _geo.Point(x=0.34, y=0.0)
        dy = _geo.Point(x=0.0, y=0.34)

        # bottom left
        o = _geo.Point(x=-m, y=-m)
        layouter.add_wire(
            net=base, wire=licon, origin=o,
            bottom=difftap, bottom_implant=nsdm, bottom_enclosure="wide",
            top_enclosure="wide",
        )
        layouter.add_wire(
            net=base, wire=licon, origin=(o + dx),
            bottom=difftap, bottom_implant=nsdm, bottom_enclosure="wide",
            top_enclosure="wide",
        )
        layouter.add_wire(
            net=base, wire=licon, origin=(o + dy),
            bottom=difftap, bottom_implant=nsdm, bottom_enclosure="tall",
            top_enclosure="tall",
        )

        # bottom right
        o = _geo.Point(x=m, y=-m)
        layouter.add_wire(
            net=base, wire=licon, origin=o,
            bottom=difftap, bottom_implant=nsdm, bottom_enclosure="wide",
            top_enclosure="wide",
        )
        layouter.add_wire(
            net=base, wire=licon, origin=(o - dx),
            bottom=difftap, bottom_implant=nsdm, bottom_enclosure="wide",
            top_enclosure="wide",
        )
        layouter.add_wire(
            net=base, wire=licon, origin=(o + dy),
            bottom=difftap, bottom_implant=nsdm, bottom_enclosure="tall",
            top_enclosure="tall",
        )

        # top left
        o = _geo.Point(x=-m, y=m)
        layouter.add_wire(
            net=base, wire=licon, origin=o,
            bottom=difftap, bottom_implant=nsdm, bottom_enclosure="wide",
            top_enclosure="wide",
        )
        layouter.add_wire(
            net=base, wire=licon, origin=(o + dx),
            bottom=difftap, bottom_implant=nsdm, bottom_enclosure="wide",
            top_enclosure="wide",
        )
        layouter.add_wire(
            net=base, wire=licon, origin=(o - dy),
            bottom=difftap, bottom_implant=nsdm, bottom_enclosure="tall",
            top_enclosure="tall",
        )

        # top right
        o = _geo.Point(x=m, y=m)
        layouter.add_wire(
            net=base, wire=licon, origin=o,
            bottom=difftap, bottom_implant=nsdm, bottom_enclosure="wide",
            top_enclosure="wide",
        )
        layouter.add_wire(
            net=base, wire=licon, origin=(o - dx),
            bottom=difftap, bottom_implant=nsdm, bottom_enclosure="wide",
            top_enclosure="wide",
        )
        layouter.add_wire(
            net=base, wire=licon, origin=(o - dy),
            bottom=difftap, bottom_implant=nsdm, bottom_enclosure="tall",
            top_enclosure="tall",
        )

        shape = _geo.Rect.from_size(width=2.45, height=2.45)
        layouter.add_wire(net=base, wire=nwm, shape=shape)

        # collector
        outer = _geo.Rect.from_size(width=3.72, height=3.72)
        shape = _geo.Ring(outer_bound=outer, ring_width=0.505)
        layout.add_shape(layer=difftap, net=collector, shape=shape)
        layouter.add_wire(net=collector, wire=li, pin=lipin, shape=shape)
        outer = _geo.Rect.from_size(width=3.98, height=3.98)
        shape = _geo.Ring(outer_bound=outer, ring_width=0.765)
        layouter.add_portless(prim=psdm, shape=shape)

        m = 1.605
        dx = _geo.Point(x=0.34, y=0.0)
        dy = _geo.Point(x=0.0, y=0.34)

        # bottom left
        o = _geo.Point(x=-m, y=-m)
        layouter.add_wire(
            net=collector, wire=licon, origin=o,
            bottom=difftap, bottom_implant=psdm, bottom_enclosure="wide",
            top_enclosure="wide",
        )
        for i in range(3):
            layouter.add_wire(
                net=collector, wire=licon, origin=(o + (i + 1)*dx),
                bottom=difftap, bottom_implant=psdm, bottom_enclosure="wide",
                top_enclosure="wide",
            )
            layouter.add_wire(
                net=collector, wire=licon, origin=(o + (i + 1)*dy),
                bottom=difftap, bottom_implant=psdm, bottom_enclosure="tall",
                top_enclosure="tall",
            )

        # bottom right
        o = _geo.Point(x=m, y=-m)
        layouter.add_wire(
            net=collector, wire=licon, origin=o,
            bottom=difftap, bottom_implant=psdm, bottom_enclosure="wide",
            top_enclosure="wide",
        )
        for i in range(3):
            layouter.add_wire(
                net=collector, wire=licon, origin=(o - (i + 1)*dx),
                bottom=difftap, bottom_implant=psdm, bottom_enclosure="wide",
                top_enclosure="wide",
            )
            layouter.add_wire(
                net=collector, wire=licon, origin=(o + (i + 1)*dy),
                bottom=difftap, bottom_implant=psdm, bottom_enclosure="tall",
                top_enclosure="tall",
            )

        # top left
        o = _geo.Point(x=-m, y=m)
        layouter.add_wire(
            net=collector, wire=licon, origin=o,
            bottom=difftap, bottom_implant=psdm, bottom_enclosure="wide",
            top_enclosure="wide",
        )
        for i in range(3):
            layouter.add_wire(
                net=collector, wire=licon, origin=(o + (i + 1)*dx),
                bottom=difftap, bottom_implant=psdm, bottom_enclosure="wide",
                top_enclosure="wide",
            )
            layouter.add_wire(
                net=collector, wire=licon, origin=(o - (i + 1)*dy),
                bottom=difftap, bottom_implant=psdm, bottom_enclosure="tall",
                top_enclosure="tall",
            )

        # top right
        o = _geo.Point(x=m, y=m)
        layouter.add_wire(
            net=collector, wire=licon, origin=o,
            bottom=difftap, bottom_implant=psdm, bottom_enclosure="wide",
            top_enclosure="wide",
        )
        for i in range(3):
            layouter.add_wire(
                net=collector, wire=licon, origin=(o - (i + 1)*dx),
                bottom=difftap, bottom_implant=psdm, bottom_enclosure="wide",
                top_enclosure="wide",
            )
            layouter.add_wire(
                net=collector, wire=licon, origin=(o - (i + 1)*dy),
                bottom=difftap, bottom_implant=psdm, bottom_enclosure="tall",
                top_enclosure="tall",
            )

        # pnp marker
        shape = _geo.Rect.from_size(width=3.71, height=3.71)
        layouter.add_portless(prim=pnp, shape=shape)

        # boundary
        shape = _geo.Rect.from_size(width=4.36, height=4.36)
        layout.boundary = shape
        layouter.add_portless(prim=bnd, shape=shape)


class _PNP_05v5_W3u40L3u40(_cell.Cell):
    def __init__(self, *,
        name: str,
        tech: _tch.Technology, cktfab: _ckt.CircuitFactory, layoutfab: _lay.LayoutFactory,
    ):
        super().__init__(name=name, tech=tech, cktfab=cktfab, layoutfab=layoutfab)

        nwm = cast(_prm.Well, _prims["nwm"])
        difftap = cast(_prm.WaferWire, _prims["difftap"])
        nsdm = cast(_prm.Implant, _prims["nsdm"])
        psdm = cast(_prm.Implant, _prims["psdm"])
        licon = cast(_prm.Via, _prims["licon"])
        li = cast(_prm.MetalWire, _prims["li"])
        assert li.pin is not None
        lipin = li.pin
        mcon = cast(_prm.Via, _prims["mcon"])
        m1 = cast(_prm.MetalWire, _prims["m1"])
        assert m1.pin is not None
        m1pin = m1.pin
        pnp = cast(_prm.Marker, _prims["pnp"])
        bnd = cast(_prm.Auxiliary, _prims["prBoundary"])

        ckt = self.new_circuit()
        inst = ckt.instantiate(cast(_prm.Bipolar, _prims["pnp_05v5_w3u40l3u40"]), name="pnp")
        collector = ckt.new_net(
            name="collector", external=True, childports=inst.ports["collector"],
        )
        base = ckt.new_net(
            name="base", external=True, childports=inst.ports["base"],
        )
        emitter = ckt.new_net(
            name="emitter", external=True, childports=inst.ports["emitter"],
        )

        layouter = self.new_circuitlayouter()
        layout = layouter.layout

        # emitter
        layouter.add_wire(
            net=emitter, wire=licon, columns=7, rows=7, space=0.28,
            bottom=difftap, bottom_enclosure=_prp.Enclosure(0.27),
            bottom_implant=psdm, bottom_implant_enclosure=_prp.Enclosure(0.13),
            top_enclosure=_prp.Enclosure(0.305),
        )
        l = layouter.add_wire(
            net=emitter, wire=mcon, columns=6, rows=6, space=0.33,
            top_enclosure=_prp.Enclosure(0.19),
        )
        m1bb = l.bounds(mask=m1.mask)
        layouter.add_wire(net=emitter, wire=m1, pin=m1pin, shape=m1bb)

        # base
        outer = _geo.Rect.from_size(width=4.81, height=4.81)
        shape = _geo.Ring(outer_bound=outer, ring_width=0.36)
        layouter.add_wire(wire=difftap, net=base, shape=shape)
        layouter.add_wire(net=base, wire=li, pin=lipin, shape=shape)
        outer = _geo.Rect.from_size(width=5.09, height=5.09)
        shape = _geo.Ring(outer_bound=outer, ring_width=0.63)
        layouter.add_portless(prim=nsdm, shape=shape)

        _l = layouter.wire_layout(
            net=base, wire=licon, columns=9, space=0.28,
            bottom=difftap, bottom_implant=nsdm, bottom_enclosure="wide",
            top_enclosure="wide",
        )
        layouter.place(_l, y=2.225)
        layouter.place(_l, y=-2.225)
        _l = layouter.wire_layout(
            net=base, wire=licon, rows=9, space=0.28,
            bottom=difftap, bottom_implant=nsdm, bottom_enclosure="tall",
            top_enclosure="tall",
        )
        layouter.place(_l, x=2.225)
        layouter.place(_l, x=-2.225)

        shape = _geo.Rect.from_size(width=5.17, height=5.17)
        layouter.add_wire(net=base, wire=nwm, shape=shape)

        # collector
        outer = _geo.Rect.from_size(width=6.44, height=6.44)
        shape = _geo.Ring(outer_bound=outer, ring_width=0.505)
        layout.add_shape(layer=difftap, net=collector, shape=shape)
        layouter.add_wire(net=collector, wire=li, pin=lipin, shape=shape)
        outer = _geo.Rect.from_size(width=6.7, height=6.7)
        shape = _geo.Ring(outer_bound=outer, ring_width=0.765)
        layouter.add_portless(prim=psdm, shape=shape)

        _l = layouter.wire_layout(
            net=collector, wire=licon, columns=12, space=0.28,
            bottom=difftap, bottom_implant=psdm, bottom_enclosure="wide",
            top_enclosure="wide",
        )
        layouter.place(_l, y=2.97)
        layouter.place(_l, y=-2.97)
        _l = layouter.wire_layout(
            net=collector, wire=licon, rows=13, space=0.28,
            bottom=difftap, bottom_implant=psdm, bottom_enclosure="tall",
            top_enclosure="tall",
        )
        layouter.place(_l, x=2.97)
        layouter.place(_l, x=-2.97)

        # pnp marker
        shape = _geo.Rect.from_size(width=6.43, height=6.43)
        layouter.add_portless(prim=pnp, shape=shape)

        # boundary
        shape = _geo.Rect.from_size(width=7.08, height=7.08)
        layout.boundary = shape
        layouter.add_portless(prim=bnd, shape=shape)


_macrolib: Optional[_lbry.Library] = None
macrolib: _lbry.Library
def __getattr__(name: str) -> Any:
    if name == "macrolib":
        global _macrolib
        if _macrolib is None:
            _macrolib = _lbry.Library(name="MacroLib", tech=tech)
            _macrolib.cells += (
                _NPN_05v5_W1u00L1u00(
                    name="NPN_05v5_W1u00L1u00",
                    tech=tech, cktfab=cktfab, layoutfab=layoutfab,
                ),
                _NPN_05v5_W1u00L2u00(
                    name="NPN_05v5_W1u00L2u00",
                    tech=tech, cktfab=cktfab, layoutfab=layoutfab,
                ),
                _PNP_05v5_W0u68L0u68(
                    name="PNP_05v5_W0u68L0u68",
                    tech=tech, cktfab=cktfab, layoutfab=layoutfab,
                ),
                _PNP_05v5_W3u40L3u40(
                    name="PNP_05v5_W3u40L3u40",
                    tech=tech, cktfab=cktfab, layoutfab=layoutfab,
                ),
            )
        return _macrolib
