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
from .TransportMapBase import TransportMap
from .ListStackedMapBase import ListStackedMap

__all__ = [
    'ListStackedTransportMap'
]


class ListStackedTransportMap(ListStackedMap,TransportMap):
    r""" Defines the transport map :math:`T` obtained by stacking :math:`T_1, T_2, \ldots`.
    """
    @required_kwargs('map_list', 'active_vars')
    def __init__(self, **kwargs):
        r"""
        Args:
          map_list (:class:`list` of :class:`Map`): list of transport maps :math:`T_i`
          active_vars (:class:`list` of :class:`list` of :class:`int`): active variables for each map
        """
        kwargs['dim'] = max( max(avars) for avars in kwargs['active_vars'] ) + 1
        super(ListStackedTransportMap, self).__init__(**kwargs)
        if self.dim_in != self.dim_out:
            raise ValueError(
                "The obtained map should be squared and invertible."
            )