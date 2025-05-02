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

from ..Misc import \
    required_kwargs

from .TriangularComponentwiseTransportMapBase import TriangularComponentwiseTransportMap

__all__ = [
    'DiagonalComponentwiseTransportMap'
]

nax = np.newaxis


class DiagonalComponentwiseTransportMap(
        TriangularComponentwiseTransportMap
):
    r""" Diagonal transport map :math:`T({\bf x})=[T_1,T_2,\ldots,T_{d_x}]^\top`, where :math:`T_i(x_{i}):\mathbb{R}\rightarrow\mathbb{R}`.
    """
    @required_kwargs('approx_list')
    def __init__(self, **kwargs):
        r"""
        Kwargs:
          active_vars (:class:`list<list>` [:math:`d_x`] of :class:`list<list>`): for
            each dimension lists the active variables.
          approx_list (:class:`list<list>` [:math:`d_x`] of :class:`MonotoneFunctional<TransportMaps.Maps.Functionals.MonotoneFunctional>`):
            list of monotone functionals for each dimension
        """
        approx_list = kwargs['approx_list']
        for a in approx_list:
            if a.dim_in != 1:
                raise ValueError(
                    "The list of functionals provided must be one dimensional."
                )
        kwargs['active_vars'] = [ [i] for i,_ in enumerate(approx_list) ]
        super(TriangularComponentwiseTransportMap,self).__init__(**kwargs)
