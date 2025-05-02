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
    required_kwargs

from .ParametricTransportMapBase import ParametricTransportMap
from .InverseParametricMapBase import InverseParametricMap
from .InverseTransportMapBase import InverseTransportMap

__all__ = [
    'InverseParametricTransportMap'
]


class InverseParametricTransportMap(
        InverseParametricMap,
        InverseTransportMap
):
    r""" Defines the parametric transport map :math:`S[{\bf a}] := T[{\bf a}]^{-1}`
    """
    @required_kwargs('base_map')
    def __init__(self, **kwargs):
        r"""
        Kwargs:
          base_map (:class:`ParametricTransportMap`): map :math:`T`
        """
        base_map = kwargs['base_map']
        if not isinstance(base_map, ParametricTransportMap):
            raise ValueError(
                "The provided base_map is not a ParametricTransportMap"
            )
        super(InverseParametricTransportMap, self).__init__(**kwargs)
