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
    required_kwargs, cached, counted, get_sub_cache

from .ParametricComponentwiseMapBase import ParametricComponentwiseMap
from .TriangularComponentwiseMapBase import TriangularComponentwiseMap

__all__ = [
    'ParametricTriangularComponentwiseMap',
]


class ParametricTriangularComponentwiseMap(ParametricComponentwiseMap, TriangularComponentwiseMap):
    r"""Map :math:`T[{\bf a}_{1:d_y}]({\bf x})= [T_1[{\bf a}_1],\ldots,T_{d_y}[{\bf a}_{d_y}]]^\top`, where :math:`T_i[{\bf a}_i](x_{1:i}):\mathbb{R}^{n_i}\times\mathbb{R}^{i}\rightarrow\mathbb{R}`.

    Args:
       active_vars (:class:`list<list>` [:math:`d`] of :class:`list<list>`): for
         each dimension lists the active variables.
       approx_list (:class:`list<list>` [:math:`d`] of :class:`FunctionalApproximations.MonotonicFunctionApproximation`):
         list of monotonic functional approximations for each dimension
    """
    @required_kwargs('active_vars', 'approx_list')
    def __init__(self, **kwargs):
        super(ParametricTriangularComponentwiseMap, self).__init__(**kwargs)

    @cached([('components','dim_out')])
    @counted
    def grad_a_partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`[\nabla_{\bf a}\partial_{{\bf x}_k} T_k]_k`

        This is

        .. math::

           \left[ \begin{array}{ccccc}
             \nabla_{{\bf a}_1}\partial_{{\bf x}_1}T_1 & 0 & \cdots & & 0 \\
             0 \nabla_{{\bf a}_2}\partial_{{\bf x}_2}T_2 & 0 & \cdots & 0 \\
             \vdots & \ddots & & & \\
             0 & & \cdots & 0 & \nabla_{{\bf a}_d}\partial_{{\bf x}_d}T_d
           \end{array} \right]
        
        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict<dict>`): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`[\partial_{{\bf x}_1}T_1({\bf x}_1,{\bf a}^{(1)}),\ldots,\partial_{{\bf x}_d}T_d({\bf x}_{1:d},{\bf a}^{(d)})]` at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        # Init sub-cache if necessary
        comp_cache = get_sub_cache(cache, ('components',self.dim_out))
        # Evaluate
        self.precomp_partial_xd(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.dim_out, self.n_coeffs))
        start = 0
        for k,(a,avar,p, c) in enumerate(zip(self.approx_list,self.active_vars,
                                             precomp['components'], comp_cache)):
            gapxd = a.grad_a_partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)
            stop = start + gapxd.shape[1]
            out[:,k,start:stop] = gapxd
            start = stop
        return out

