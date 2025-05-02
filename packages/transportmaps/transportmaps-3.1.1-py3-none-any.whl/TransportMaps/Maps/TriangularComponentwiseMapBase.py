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

from .ComponentwiseMapBase import ComponentwiseMap

__all__ = [
    'TriangularComponentwiseMap'
]

class TriangularComponentwiseMap(ComponentwiseMap):
    r""" Triangular map :math:`T({\bf x}):=[T_1,T_2,\ldots,T_{d_x}]^\top`, where :math:`T_i(x_{1:i}):\mathbb{R}^i\rightarrow\mathbb{R}`.

    Args:
       active_vars (:class:`list<list>` [:math:`d`] of :class:`list<list>`): for
         each dimension lists the active variables.
       approx_list (:class:`list<list>` [:math:`d`] of :class:`FunctionalApproximations.MonotonicFunctionApproximation`):
         list of monotonic functional approximations for each dimension
    """
    @required_kwargs('active_vars', 'approx_list')
    def __init__(self, **kwargs):
        active_vars = kwargs['active_vars']
        approx_list = kwargs['approx_list']
        # Check lower triangularity
        for i, avars in enumerate(active_vars):
            if avars[-1] != i:
                raise ValueError("The map is not lower triangular.")
        super(TriangularComponentwiseMap, self).__init__(**kwargs)

    def precomp_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`\partial_{x_k}T_k({\bf x})` for :math:`k=1,\ldots,d`

        Enriches the dictionaries in the ``precomp`` list if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): list of dictionaries of precomputed values
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'

        Returns:
           (:class:`dict<dict>` of :class:`list<list>` [:math:`d`]
             :class:`dict<dict>`) -- necessary structures
        """
        if precomp is None:
            precomp = {'components': [{} for i in range(self.dim)]}
        for a,avar,p in zip(self.approx_list,self.active_vars,precomp['components']):
            if precomp_type == 'uni':
                a.precomp_partial_xd(x[:,avar], p)
            elif precomp_type == 'multi':
                a.precomp_Vandermonde_partial_xd(x[:,avar], p)
            else: raise ValueError("Unrecognized precomp_type")
        return precomp

    @cached([('components','dim_out')])
    @counted
    def partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`[\partial_{{\bf x}_1}T_1({\bf x}_1),\ldots,\partial_{{\bf x}_d}T_d({\bf x}_{1:d})]`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict<dict>`): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`[\partial_{{\bf x}_1}T_1({\bf x}_1),\ldots,\partial_{{\bf x}_d}T_d({\bf x}_{1:d})]` at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        # Init sub-cache if necessary
        comp_cache = get_sub_cache(cache, ('components',self.dim_out))
        # Evaluation
        self.precomp_partial_xd(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0],self.dim_out))
        for k,(a,avar,p, c) in enumerate(zip(self.approx_list,self.active_vars,
                                             precomp['components'], comp_cache)):
            out[:,k] = a.partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)[:,0]
        return out

    def precomp_grad_x_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`\nabla_{\bf x}\partial_{x_k}T_k({\bf x})` for :math:`k=1,\ldots,d`

        Enriches the dictionaries in the ``precomp`` list if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): list of dictionaries of precomputed values
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'

        Returns:
           (:class:`dict<dict>` of :class:`list<list>` [:math:`d`]
             :class:`dict<dict>`) -- necessary structures
        """
        if precomp is None:
            precomp = {'components': [{} for i in range(self.dim)]}
        for a,avar,p in zip(self.approx_list, self.active_vars,
                            precomp['components']):
            if precomp_type == 'uni':
                a.precomp_grad_x_partial_xd(x[:,avar], p)
            elif precomp_type == 'multi':
                a.precomp_Vandermonde_grad_x_partial_xd(x[:,avar], p)
            else: raise ValueError("Unrecognized precomp_type")
        return precomp

    def precomp_hess_x_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`\nabla^2_{\bf x}\partial_{x_k}T_k({\bf x})` for :math:`k=1,\ldots,d`

        Enriches the dictionaries in the ``precomp`` list if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): list of dictionaries of precomputed values
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'

        Returns:
           (:class:`dict<dict>` of :class:`list<list>` [:math:`d`]
             :class:`dict<dict>`) -- necessary structures
        """
        if precomp is None:
            precomp = {'components': [{} for i in range(self.dim)]}
        for a,avar,p in zip(self.approx_list, self.active_vars,
                            precomp['components']):
            if precomp_type == 'uni':
                a.precomp_hess_x_partial_xd(x[:,avar], p)
            elif precomp_type == 'multi':
                a.precomp_Vandermonde_hess_x_partial_xd(x[:,avar], p)
            else: raise ValueError("Unrecognized precomp_type")
        return precomp