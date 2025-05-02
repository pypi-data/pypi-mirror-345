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
    required_kwargs, \
    cached, counted, get_sub_cache
from .MapBase import Map

__all__ = [
    'ComponentwiseMap',
]


class ComponentwiseMap(Map):
    r"""Map :math:`T({\bf x}) := [T_1({\bf x}_{{\bf j}_1}), \ldots, T_{d_y}({\bf x}_{{\bf j}_{d_y}})]^\top`, where :math:`T_i({\bf x}_{{\bf j}_i}):\mathbb{R}^{\text{dim}({\bf j}_i)}\rightarrow\mathbb{R}`.
    """
    @required_kwargs('active_vars', 'approx_list')
    def __init__(self, **kwargs):
        r"""
        Kwargs:
          active_vars (:class:`list<list>` [:math:`d_y`] of :class:`list<list>`): for
            each dimension lists the active variables.
          approx_list (:class:`list<list>` [:math:`d_y`] of :class:`Functional<TransportMaps.Maps.Functionals.Functional>`):
            list of functionals for each dimension
        """
        active_vars = kwargs['active_vars']
        approx_list = kwargs['approx_list']
        if len(active_vars) != len(approx_list):
            raise ValueError("Inconsistent dimensions")
        for i,(vs,approx) in enumerate(zip(active_vars,approx_list)):
            if len(vs) != approx.dim_in:
                raise ValueError(
                    "The number of active variables for the " + \
                    "%d-th functional " % i +
                    "does not match the input dimension of the functional."
                )
        kwargs['dim_in'] = max([ max(avars) for avars in active_vars ]) + 1
        kwargs['dim_out'] = len(active_vars)
        super(ComponentwiseMap, self).__init__(**kwargs)
        self.approx_list = approx_list
        self.active_vars = active_vars

    def get_ncalls_tree(self, indent=""):
        out = super(ComponentwiseMap, self).get_ncalls_tree(indent)
        for i, a in enumerate(self.approx_list):
            out += a.get_ncalls_tree(indent + " T%d - " % i)
        return out

    def get_nevals_tree(self, indent=""):
        out = super(ComponentwiseMap, self).get_nevals_tree(indent)
        for i, a in enumerate(self.approx_list):
            out += a.get_nevals_tree(indent + " T%d - " % i)
        return out

    def get_teval_tree(self, indent=""):
        out = super(ComponentwiseMap, self).get_teval_tree(indent)
        for i, a in enumerate(self.approx_list):
            out += a.get_teval_tree(indent + " T%d - " % i)
        return out

    def update_ncalls_tree(self, obj):
        super(ComponentwiseMap, self).update_ncalls_tree( obj )
        for a, obj_a in zip(self.approx_list, obj.approx_list):
            a.update_ncalls_tree( obj_a )

    def update_nevals_tree(self, obj):
        super(ComponentwiseMap, self).update_nevals_tree( obj )
        for a, obj_a in zip(self.approx_list, obj.approx_list):
            a.update_nevals_tree( obj_a )

    def update_teval_tree(self, obj):
        super(ComponentwiseMap, self).update_teval_tree( obj )
        for a, obj_a in zip(self.approx_list, obj.approx_list):
            a.update_teval_tree( obj_a )

    def reset_counters(self):
        super(ComponentwiseMap, self).reset_counters()
        for a in self.approx_list:
            a.reset_counters()
        
    def precomp_evaluate(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`T({\bf x})`

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
            precomp = {'components': [{} for i in range(self.dim_out)]}
        for a,avar,p in zip(self.approx_list, self.active_vars, precomp['components']):
            if precomp_type == 'uni':
                a.precomp_evaluate(x[:,avar], p)
            elif precomp_type == 'multi':
                a.precomp_Vandermonde_evaluate(x[:,avar], p)
            else: raise ValueError("Unrecognized precomp_type")
        return precomp

    @cached([('components','dim_out')])
    @counted
    def evaluate(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate the transport map at the points :math:`{\bf x} \in \mathbb{R}^{m \times d}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict<dict>`): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- transformed points

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        # Init sub-cache if necessary
        comp_cache = get_sub_cache(cache, ('components',self.dim_out))
        # Evaluation
        self.precomp_evaluate(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        xout = np.zeros((x.shape[0], self.dim_out))
        for i,(a,avar,p, c) in enumerate(zip(self.approx_list,self.active_vars,
                                             precomp['components'], comp_cache)):
            xout[:,i] = a.evaluate( x[:,avar], p,
                                    idxs_slice=idxs_slice, cache=c )[:,0]
        return xout

    def precomp_grad_x(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`\nabla_{\bf x}T({\bf x},{\bf a})`

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
            precomp = {'components': [{} for i in range(self.dim_out)]}
        for a,avar,p in zip(self.approx_list, self.active_vars,
                            precomp['components']):
            if precomp_type == 'uni':
                a.precomp_grad_x(x[:,avar], p)
            elif precomp_type == 'multi':
                a.precomp_Vandermonde_grad_x(x[:,avar], p)
            else: raise ValueError("Unrecognized precomp_type")
        return precomp

    @cached([('components','dim_out')])
    @counted
    def grad_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf x} T({\bf x})`.

        This is
        
        .. math::
            :nowrap:

            \nabla_{\bf x} T({\bf x},{\bf a}) =
                 \begin{bmatrix}
                 \nabla_{\bf x}  T_1({\bf x})  \\
                 \nabla_{\bf x}  T_2({\bf x})  \\
                 \vdots \\
                 \nabla_{\bf x}  T_d({\bf x})
                 \end{bmatrix}

        for every evaluation point.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           gradient matrices for every evaluation point.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        self.precomp_grad_x(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = np.zeros( (x.shape[0], self.dim_out, self.dim_in) )
        for k,(a,avar,p) in enumerate(zip(self.approx_list, self.active_vars,
                                          precomp['components'])):
            out[:,k,avar] = a.grad_x(x[:,avar], p, idxs_slice=idxs_slice)[:,0,:]
        return out

    def precomp_hess_x(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`\nabla^2_{\bf x}T({\bf x})`

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
            precomp = {'components': [{} for i in range(self.dim_out)]}
        for a,avar,p in zip(self.approx_list, self.active_vars,
                            precomp['components']):
            if precomp_type == 'uni':
                a.precomp_hess_x(x[:,avar], p)
            elif precomp_type == 'multi':
                a.precomp_Vandermonde_hess_x(x[:,avar], p)
            else: raise ValueError("Unrecognized precomp_type")
        return precomp

    @cached([('components','dim_out')],False)
    @counted
    def hess_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Compute :math:`\nabla^2_{\bf x} T({\bf x})`.

        This is the tensor

        .. math::

           \left[\nabla^2_{\bf x} T({\bf x})\right]_{i,k,:,:} = \nabla^2_{\bf x} T_k({\bf x}^{(i)})

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d,d`]) --
           Hessian matrices for every evaluation point and every dimension.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        self.precomp_hess_x(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = np.zeros( (x.shape[0], self.dim_out, self.dim_in, self.dim_in) )
        for k,(a,avar,p) in enumerate(zip(self.approx_list,
                                          self.active_vars,
                                          precomp['components'])):
            # 2d numpy advanced indexing
            nvar = len(avar)
            rr,cc = np.meshgrid(avar,avar)
            rr = list( rr.flatten() )
            cc = list( cc.flatten() )
            idxs = (slice(None), k, rr, cc)
            # Compute hess_x
            out[idxs] = a.hess_x(x[:,avar], p, idxs_slice=idxs_slice).reshape((x.shape[0],nvar**2))
        return out

    @cached([('components','dim_out')],False)
    @counted
    def action_hess_x(self, x, dx, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Compute :math:`\langle\nabla^2_{\bf x} T({\bf x}),\delta{\bf x}\rangle`.

        This is the tensor

        .. math::

           \left[\nabla^2_{\bf x} T({\bf x})\right]_{i,k,:i} = \langle \nabla^2_{\bf x} T_k({\bf x}^{(i)}), \delta{\bf x}\rangle

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): direction
            on which to evaluate the Hessian
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           Hessian matrices for every evaluation point and every dimension.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        self.precomp_hess_x(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = np.zeros( (x.shape[0], self.dim_out, self.dim_in) )
        for k,(a,avar,p) in enumerate(zip(self.approx_list,
                                          self.active_vars,
                                          precomp['components'])):
            # 2d numpy advanced indexing
            nvar = len(avar)
            idxs = (slice(None), k, avar)
            # Compute hess_x
            hxTk = a.hess_x(x[:,avar], p, idxs_slice=idxs_slice)[:,0,:,:]
            out[idxs] = np.einsum('...ij,...j->...i', hxTk, dx[:,avar])
        return out
