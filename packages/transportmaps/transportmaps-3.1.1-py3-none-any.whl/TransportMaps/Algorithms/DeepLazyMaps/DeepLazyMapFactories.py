#
# This file is part of TransportMaps.
#
# TransportMaps is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TransportMaps is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with TransportMaps.  If not, see <http://www.gnu.org/licenses/>.
#
# Transport Maps Library
# Copyright (C) 2015-2018 Massachusetts Institute of Technology
# Uncertainty Quantification group
# Department of Aeronautics and Astronautics
#
# Authors: Transport Map Team
# Website: transportmaps.mit.edu
# Support: transportmaps.mit.edu/qa/
#

import numpy as np

from ...Misc import deprecate, cmdinput

from ...Maps import ParametricTriangularComponentwiseTransportMap, MapFactory, \
    assemble_IsotropicIntegratedSquaredTriangularTransportMap, IdentityEmbeddedParametricTransportMap

__all__ = [
    'DeepLazyMapFactory',
    'FixedOrderDeepLazyMapFactory',
    'ManualDeepLazyMapFactory',
    'DeepLazyMapListFactory',

    'FixedOrderMapFactory',
    'ManualMapFactory',

    # Deprecated
    'LazyTransportMap',
]


class LazyTransportMap(ParametricTriangularComponentwiseTransportMap):
    @deprecate(
        'LazyTransportMap',
        '3.0',
        'Use Maps.IdentityEmbeddedParametricTransportMap instead'
    )
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail
        dim = head.dim + tail.dim
        super(LazyTransportMap, self).__init__(
            active_vars = head.active_vars + [ [d] for d in range(head.dim,dim) ],
            approx_list = head.approx_list + tail.approx_list
        )

    def get_identity_coeffs(self):
        return np.hstack([
            self.head.get_identity_coeffs(),
            self.tail.get_identity_coeffs()
        ])

    def get_default_init_values_minimize_kl_divergence(self):
        return self.get_identity_coeffs()


class DeepLazyMapFactory(MapFactory):
    def generate(self, dim, dim_k, order, *args, **kwargs):
        tm = assemble_IsotropicIntegratedSquaredTriangularTransportMap(
            dim_k, order=order )
        if dim_k < dim:
            tm = IdentityEmbeddedParametricTransportMap(
                tm=tm, idxs=list(range(dim_k)), dim=dim
            )
            # Id = MAPS.IdentityParametricTriangularComponentwiseTransportMap(dim=dim-dim_k)
            # tm = LazyTransportMap(tm, Id)
        return tm


class DeepLazyMapListFactory( DeepLazyMapFactory ):
    def generate(self, dim, dim_k, order, *args, **kwargs):
        tm_list = []
        for o in range(1, self.order+1):
            tm = assemble_IsotropicIntegratedSquaredTriangularTransportMap(
                dim_k, order=o )
            if dim_k < dim:
                tm = IdentityEmbeddedParametricTransportMap(
                    tm=tm, idxs=list(range(dim_k)), dim=dim
                )
                # Id = MAPS.IdentityParametricTriangularComponentwiseTransportMap(dim=dim-dim_k)
                # tm = LazyTransportMap(tm, Id)
            tm_list.append( tm )
        return tm_list


class FixedOrderDeepLazyMapFactory( DeepLazyMapFactory ):
    def __init__(self, order):
        super(FixedOrderDeepLazyMapFactory, self).__init__()
        self.order = order
    def generate(self, dim, dim_k, *args, **kwargs):
        return super(FixedOrderDeepLazyMapFactory, self).generate(
            dim, dim_k, self.order )


class ManualDeepLazyMapFactory( DeepLazyMapFactory ):
    def generate(self, dim, dim_k, *args, **kwargs):
        order = None
        while not isinstance(order, int):
            instr = cmdinput(
                "Select the order of the new lazy map [>0]: "
            )
            try:
                order = int(instr)
                if order < 1: order = None
            except ValueError:
                pass
        return super(ManualDeepLazyMapFactory, self).generate(
            dim, dim_k, order )


class FixedOrderMapFactory(MapFactory):
    def __init__(self, order):
        super(FixedOrderMapFactory, self).__init__()
        self.order = order
    def generate(self, dim_k, *args, **kwargs):
        tm = assemble_IsotropicIntegratedSquaredTriangularTransportMap(
            dim_k, order=self.order )
        return tm


class ManualMapFactory(MapFactory):
    def generate(self, dim_k, *args, **kwargs):
        order = None
        while not isinstance(order, int):
            instr = cmdinput(
                "Select the order of the new lazy map [>0]: "
            )
            try:
                order = int(instr)
                if order < 1: order = None
            except ValueError:
                pass
        tm = assemble_IsotropicIntegratedSquaredTriangularTransportMap(
            dim_k, order=order )
        return tm
