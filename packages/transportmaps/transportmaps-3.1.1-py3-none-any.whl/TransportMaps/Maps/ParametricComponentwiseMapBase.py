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
    cached, cached_tuple, counted, get_sub_cache
from .ComponentwiseMapBase import ComponentwiseMap
from .ParametricMapBase import ParametricMap

__all__ = [
    'ParametricComponentwiseMap',
]

nax = np.newaxis


class ParametricComponentwiseMap(ComponentwiseMap, ParametricMap):
    r"""Map :math:`T[{\bf a}_{1:d_y}]({\bf x})= [T_1[{\bf a}_1]({\bf x}_{{\bf j}_{1}}),\ldots,T_{d_y}[{\bf a}_{d_y}]({\bf x}_{{\bf j}_{d_y}})]^\top`, where :math:`T_i[{\bf a}_i]({\bf x}_{{\bf j}_{i}}):\mathbb{R}^{n_i}\times\mathbb{R}^{\text{dim}({{\bf j}_{i}})}\rightarrow\mathbb{R}`.
    """
    @required_kwargs('active_vars', 'approx_list')
    def __init__(self, **kwargs):
        r"""
        Args:
          active_vars (:class:`list<list>` [:math:`d`] of :class:`list<list>`): for
            each dimension lists the active variables.
          approx_list (:class:`list<list>` [:math:`d`] of :class:`ParametricFunctional<TransportMaps.Maps.Functionals.ParametricFunctionals>`):
            list of functionals approximations for each dimension
        """
        active_vars = kwargs['active_vars']
        approx_list = kwargs['approx_list']
        kwargs['dim_in']  = max([ max(avars) for avars in active_vars ]) + 1
        kwargs['dim_out'] = len(active_vars)
        super(ParametricComponentwiseMap, self).__init__(**kwargs)

    @property
    def n_coeffs(self):
        r""" Returns the total number of coefficients.

        Returns:
           total number :math:`N` of coefficients characterizing the transport map.
        """
        return np.sum([ a.n_coeffs for a in self.approx_list ])

    @property
    def coeffs(self):
        r""" Returns the actual value of the coefficients.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients.
        """
        out = np.zeros( self.n_coeffs )
        start = 0
        for a in self.approx_list:
            n_coeffs = np.sum( a.n_coeffs )
            out[start:start+n_coeffs] = a.coeffs
            start += n_coeffs
        return out

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients.

        Args:
           coeffs (:class:`ndarray<numpy.ndarray>` [:math:`N`]):
              coefficients for the various maps

        Raises:
           ValueError: if the number of input coefficients does not match the
              number of required coefficients :func:`n_coeffs`.
        """
        start = 0
        for a in self.approx_list:
            n_coeffs = a.n_coeffs
            a.coeffs = coeffs[start:start+n_coeffs]
            start += n_coeffs

    def get_identity_coeffs(self):
        r""" [Abstract] Returns the coefficients corresponding to the identity map

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients

        Raises:
          NotImplementedError: must be implemented in subclasses.
        """
        raise NotImplementedError("Must be implemented in subclasses.")

        
    @cached([('components','dim_out')],False)
    @counted
    def grad_a(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute :math:`\nabla_{\bf a} T[{\bf a}]({\bf x})`

        By the definition of the transport map :math:`T[{\bf a}]({\bf x})`,
        the components :math:`T_1[{\bf a}^{(1)}] ({\bf x}_1)`,
        :math:`T_2[{\bf a}^{(2)}] ({\bf x}_{1:2})`, ...
        are defined by different sets of parameters :math:`{\bf a}^{(1)}`,
        :math:`{\bf a}^{(2)}`, etc.

        For this reason :math:`\nabla_{\bf a} T[{\bf a}]({\bf x})`
        is block diagonal:

        .. math::
           :nowrap:

           \nabla_a T[{\bf a}]({\bf x}) = \begin{bmatrix}
           \left[ \nabla_{{\bf a}^{(1)}} T_1[{\bf a}^{(1)}] ({\bf x}_1) \right]^T & {\bf 0} & \cdots \\
           {\bf 0} & \left[ \nabla_{{\bf a}^{(2)}} T_2[{\bf a}^{(2)}] ({\bf x}_{1:2}) \right]^T & \\
           \vdots & & \ddots
           \end{bmatrix}

        Consequentely this function will return only the diagonal blocks of the gradient.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dics<dict>`): cache
          
        Returns:
           (:class:`list<list>` of :class:`ndarray<numpy.ndarray>` [:math:`n_i`]) --
              list containing
              :math:`\nabla_{{\bf a}^{(1)}} T_1[{\bf a}^{(1)}] ({\bf x}_1)`,
              :math:`\nabla_{{\bf a}^{(2)}} T_2[{\bf a}^{(2)}] ({\bf x}_{1:2})`,
              etc.

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
        out = []
        for k,(a,avar,p,c) in enumerate(zip(self.approx_list,self.active_vars,
                                          precomp['components'], comp_cache)):
            ga = a.grad_a(x[:,avar], p, idxs_slice=idxs_slice, cache=c)[:,0,:]
            out.append( ga )
        return out

    @counted
    def grad_a_inverse(self, x, precomp=None, idxs_slice=slice(None)):
        r""" [Abstract] Compute :math:`\nabla_{\bf a} T^{-1}({\bf x},{\bf a})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,N`]) --
              :math:`\nabla_{\bf a} T^{-1}({\bf x},{\bf a})`

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        raise NotImplementedError("Abstract method")

    @cached([('components','dim_out')],False)
    @counted
    def hess_a(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute :math:`\nabla^2_{\bf a} T[{\bf a}]({\bf x})`.

        As in the case of :func:`grad_a`, the :math:`d \times N \times N`
        Hessian of T[{\bf a}]({\bf x}) is (hyper) block diagonal.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`list<list>` of :class:`ndarray<numpy.ndarray>` [:math:`n_i,n_i`]) --
              list containing
              :math:`\nabla^2_{{\bf a}^{(1)}} T_1[{\bf a}^{(1)}] ({\bf x}_1)`,
              :math:`\nabla^2_{{\bf a}^{(2)}} T_2[{\bf a}^{(2)}] ({\bf x}_{1:2})`,
              etc.

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
        return [ a.hess_a(x[:,avar], p, idxs_slice=idxs_slice, cache=c)[:,0,:,:]
                 for k,(a,avar,p,c)
                 in enumerate(zip(self.approx_list,self.active_vars,
                                  precomp['components'], comp_cache)) ]

    @cached([('components','dim_out')],False)
    @counted
    def action_hess_a(self, x, da, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute :math:`\langle\nabla^2_{\bf a} T[{\bf a}]({\bf x}), \delta{\bf a}\rangle`.

        As in the case of :func:`grad_a`, the :math:`d \times N `
        actions of the Hessian of T[{\bf a}]({\bf x}) is (hyper) block diagonal.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          da (:class:`ndarray<numpy.ndarray>` [:math:`N`]): direction
            on which to evaluate the Hessian
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
           (:class:`list<list>` of :class:`ndarray<numpy.ndarray>` [:math:`n_i,n_i`]) --
              list containing
              :math:`\langle\nabla^2_{{\bf a}^{(1)}} T_1[{\bf a}^{(1)}] ({\bf x}_1),\delta{\bf a}^{(1)}\rangle`,
              :math:`\langle\nabla^2_{{\bf a}^{(2)}} T_2[{\bf a}^{(2)}] ({\bf x}_{1:2}),\delta{\bf a}^{(2)}\rangle`,
              etc.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        self.precomp_evaluate(x, precomp)
        # Init sub-cache if necessary
        comp_cache = get_sub_cache(cache, ('components',self.dim_out))
        out = []
        start = 0
        for k, (a, avar, p, c) in enumerate(zip(self.approx_list,self.active_vars,
                                             precomp['components'], comp_cache)):
            stop = start + a.n_coeffs
            ha = a.hess_a(x[:,avar], p, idxs_slice=idxs_slice, cache=c)[:,0,:,:]
            out.append( np.einsum('...ij,j->...i', ha, da[start:stop]) )
            start = stop
        return out

    @cached([('components','dim_out')],False)
    @counted
    def grad_a_grad_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf a} \nabla_{\bf x} T[{\bf a}]({\bf x})`

        By the definition of the transport map :math:`T[{\bf a}]({\bf x})`,
        the components :math:`T_1[{\bf a}^{(1)}] ({\bf x}_1)`,
        :math:`T_2[{\bf a}^{(2)}] ({\bf x}_{1:2})`, ...
        are defined by different sets of parameters :math:`{\bf a}^{(1)}`,
        :math:`{\bf a}^{(2)}`, etc.

        For this reason :math:`\nabla_{\bf a} \nabla_{\bf x} T[{\bf a}]({\bf x})`
        is block diagonal:

        .. math::
           :nowrap:

           \nabla_a \nabla_{\bf x} T[{\bf a}]({\bf x}) = \begin{bmatrix}
           \left[ \nabla_{{\bf a}^{(1)}} \nabla_{\bf x}_1 T_1[{\bf a}^{(1)}] ({\bf x}_1) \right]^T & {\bf 0} & \cdots \\
           {\bf 0} & \left[ \nabla_{{\bf a}^{(2)}} \nabla_{\bf x}_{1:2} T_2[{\bf a}^{(2)}] ({\bf x}_{1:2}) \right]^T & \\
           \vdots & & \ddots
           \end{bmatrix}

        Consequentely this function will return only the diagonal blocks of the gradient.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          
        Returns:
           (:class:`list<list>` of :class:`ndarray<numpy.ndarray>` [:math:`n_i`]) --
              list containing
              :math:`\nabla_{{\bf a}^{(1)}} \nabla_{\bf x}_1 T_1[{\bf a}^{(1)}] ({\bf x}_1)`,
              :math:`\nabla_{{\bf a}^{(2)}} \nabla_{\bf x}_{1:2} T_2[{\bf a}^{(2)}] ({\bf x}_{1:2})`,
              etc.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        self.precomp_evaluate(x, precomp)
        self.precomp_grad_x(x, precomp)
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = []
        for k,(a,avar,p) in enumerate(zip(self.approx_list,self.active_vars,
                                          precomp['components'])):
            ga = a.grad_a_grad_x(x[:,avar], p, idxs_slice=idxs_slice)[:,0,:,:]
            out.append( ga )
        return out

    @cached([('components','dim_out')],False)
    @counted
    def grad_a_hess_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf a} \nabla^2_{\bf x} T[{\bf a}]({\bf x})`.

        By the definition of the transport map :math:`T[{\bf a}]({\bf x})`,
        the components :math:`T_1[{\bf a}^{(1)}] ({\bf x}_1)`,
        :math:`T_2[{\bf a}^{(2)}] ({\bf x}_{1:2})`, ...
        are defined by different sets of parameters :math:`{\bf a}^{(1)}`,
        :math:`{\bf a}^{(2)}`, etc.

        For this reason :math:`\nabla_{\bf a} \nabla^2_{\bf x} T[{\bf a}]({\bf x})`
        is block diagonal:

        .. math::
           :nowrap:

           \nabla_a \nabla^2_{\bf x} T[{\bf a}]({\bf x}) = \begin{bmatrix}
           \left[ \nabla_{{\bf a}^{(1)}} \nabla^2_{\bf x}_1 T_1[{\bf a}^{(1)}] ({\bf x}_1) \right]^T & {\bf 0} & \cdots \\
           {\bf 0} & \left[ \nabla_{{\bf a}^{(2)}} \nabla^2_{\bf x}_{1:2} T_2[{\bf a}^{(2)}] ({\bf x}_{1:2}) \right]^T & \\
           \vdots & & \ddots
           \end{bmatrix}

        Consequentely this function will return only the diagonal blocks of the hessian.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`list<list>` of :class:`ndarray<numpy.ndarray>` [:math:`n_i`]) --
              list containing
              :math:`\nabla_{{\bf a}^{(1)}} \nabla^2_{\bf x}_1 T_1[{\bf a}^{(1)}] ({\bf x}_1)`,
              :math:`\nabla_{{\bf a}^{(2)}} \nabla^2_{\bf x}_{1:2} T_2[{\bf a}^{(2)}] ({\bf x}_{1:2})`,
              etc.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """

        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        self.precomp_hess_x(x, precomp)
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = []
        for k,(a,avar,p) in enumerate(zip(self.approx_list,self.active_vars,
                                          precomp['components'])):
            ga = a.grad_a_hess_x(x[:,avar], p, idxs_slice=idxs_slice)[:,0,:,:,:]
            out.append( ga )
        return out
