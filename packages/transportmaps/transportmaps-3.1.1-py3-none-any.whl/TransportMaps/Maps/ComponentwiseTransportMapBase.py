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

from .ComponentwiseMapBase import ComponentwiseMap
from .TransportMapBase import TransportMap

__all__ = [
    'ComponentwiseTransportMap',
]


class ComponentwiseTransportMap(ComponentwiseMap, TransportMap):
    r"""Map :math:`T({\bf x}) := [T_1({\bf x}_{{\bf j}_{1}}),\ldots,T_{d_x}({\bf x}_{{\bf j}_{d_x}})]^\top`, where :math:`T_i({\bf x}_{{\bf j}_{i}}): \mathbb{R}^{\text{dim}({\bf j}_{i})} \rightarrow \mathbb{R}`.

    Args:
       active_vars (:class:`list<list>` [:math:`d_x`] of :class:`list<list>`): for
         each dimension lists the active variables.
       approx_list (:class:`list<list>` [:math:`d_x`] of :class:`Functional<TransportMaps.Maps.Functionals.Functional>`):
         list of functionals for each dimension
    """
    @required_kwargs('active_vars', 'approx_list')
    def __init__(self, **kwargs):
        active_vars = kwargs['active_vars']
        approx_list = kwargs['approx_list']
        kwargs['dim_in'] = max([ max(avars) for avars in active_vars ]) + 1
        kwargs['dim_out'] = len(active_vars)
        super(ComponentwiseTransportMap, self).__init__(**kwargs)
