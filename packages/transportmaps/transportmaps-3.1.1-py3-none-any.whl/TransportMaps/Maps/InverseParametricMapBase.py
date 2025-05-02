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

from ..Misc import \
    required_kwargs, \
    counted

from .InverseMapBase import InverseMap
from .ParametricMapBase import ParametricMap

__all__ = [
    'InverseParametricMap'
]


class InverseParametricMap(
        InverseMap,
        ParametricMap
):
    r""" Defines the parametric map :math:`S[{\bf a}] := T[{\bf a}]^{\dagger}`
    """
    @required_kwargs('base_map')
    def __init__(self, **kwargs):
        r"""
        Kwargs:
          base_map (:class:`ParametricMap`): map :math:`T`
        """
        base_map = kwargs['base_map']
        if not isinstance(base_map, ParametricMap):
            raise ValueError(
                "The provided base_map is not a ParametricMap"
            )
        kwargs['dim_in']  = base_map.dim_out
        kwargs['dim_out'] = base_map.dim_in
        super(InverseParametricMap, self).__init__(**kwargs)

    @property
    def n_coeffs(self):
        return self.base_map.n_coeffs

    @property
    def coeffs(self):
        return self.base_map.coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        self.base_map.coeffs = coeffs
        
    @counted
    def grad_a(self, x, *args, **kwargs):
        return self.base_map.grad_a_inverse(x)

    @counted
    def grad_a_inverse(self, x, *args, **kwargs):
        return self.base_map.grad_a(x)
