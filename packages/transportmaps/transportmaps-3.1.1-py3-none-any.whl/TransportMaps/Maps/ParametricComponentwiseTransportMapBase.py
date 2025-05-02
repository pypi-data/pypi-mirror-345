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

from .ParametricComponentwiseMapBase import ParametricComponentwiseMap
from .ComponentwiseTransportMapBase import ComponentwiseTransportMap
from .ParametricTransportMapBase import ParametricTransportMap

__all__ = [
    'ParametricComponentwiseTransportMap',
]


class ParametricComponentwiseTransportMap(
        ParametricComponentwiseMap,
        ComponentwiseTransportMap,
        ParametricTransportMap
):
    r"""Map :math:`T[{\bf a}_{1:d_x}]({\bf x})= [T_1[{\bf a}_1]({\bf x}),\ldots,T_{d_x}[{\bf a}_{d_x}]({\bf x})]^\top`, where :math:`T_i[{\bf a}_i]({\bf x}):\mathbb{R}^{n_i}\times\mathbb{R}^{d_x}\rightarrow\mathbb{R}`.

    Args:
       active_vars (:class:`list<list>` [:math:`d`] of :class:`list<list>`): for
         each dimension lists the active variables.
       approx_list (:class:`list<list>` [:math:`d`] of :class:`FunctionalApproximations.MonotonicFunctionApproximation`):
         list of monotonic functional approximations for each dimension
    """
    @required_kwargs('active_vars', 'approx_list')
    def __init__(self, **kwargs):
        kwargs['dim'] = len(kwargs['active_vars'])
        super(ParametricComponentwiseTransportMap, self).__init__(**kwargs)
