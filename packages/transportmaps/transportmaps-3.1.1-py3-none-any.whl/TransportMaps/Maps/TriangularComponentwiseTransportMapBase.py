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
import scipy.linalg as scila

from ..Misc import \
    required_kwargs, \
    deprecate, \
    counted, cached

from .TriangularComponentwiseMapBase import TriangularComponentwiseMap
from .ComponentwiseTransportMapBase import ComponentwiseTransportMap

__all__ = [
    'TriangularComponentwiseTransportMap',
    # Deprecated
    'TriangularTransportMap',
    'MonotonicTriangularTransportMap'
]

nax = np.newaxis

class TriangularComponentwiseTransportMap(
        TriangularComponentwiseMap,
        ComponentwiseTransportMap
):
    r""" Triangular transport map :math:`T({\bf x})=[T_1,T_2,\ldots,T_{d_x}]^\top`, where :math:`T_i(x_{1:i}):\mathbb{R}^i\rightarrow\mathbb{R}`.
    """
    @required_kwargs('active_vars', 'approx_list')
    def __init__(self, **kwargs):
        r"""
        Kwargs:
          active_vars (:class:`list<list>` [:math:`d_x`] of :class:`list<list>`): for
            each dimension lists the active variables.
          approx_list (:class:`list<list>` [:math:`d_x`] of :class:`MonotoneFunctional<TransportMaps.Maps.Functionals.MonotoneFunctional>`):
            list of monotone functionals for each dimension
        """
        super(TriangularComponentwiseTransportMap,self).__init__(**kwargs)

    @cached([('components','dim_out')])
    @counted
    def log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`\log \det \nabla_{\bf x} T({\bf x})`.

        Since the map is lower triangular,

        .. math::

           \log \det \nabla_{\bf x} T({\bf x}) = \sum_{k=1}^d \log \partial_{{\bf x}_k} T_k({\bf x}_{1:k})

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict<dict>`): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \det \nabla_{\bf x} T({\bf x})` at every
           evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        self.precomp_partial_xd(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        pxd = self.partial_xd(x, precomp=precomp, idxs_slice=idxs_slice, cache=cache)
        out = np.sum(np.log(pxd),axis=1)
        return out

    @counted
    def log_det_grad_x_inverse(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute: :math:`\log \det \nabla_{\bf x} T^{-1}({\bf x})`.

        Since the map is lower triangular,

        .. math::

           \log \det \nabla_{\bf y} T^{-1}({\bf x}) = \sum_{k=1}^d \log \partial_{{\bf x}_k} T^{-1}_k({\bf y}_{1:k})

        For :math:`{\bf x} = T^{-1}({\bf y})`,

        .. math::

           \log \det \nabla_{\bf y} T^{-1}({\bf x}) = - \sum_{k=1}^d \log \partial_{{\bf x}_k} T_k({\bf x}_{1:k})

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \det \nabla_{\bf x} T({\bf x})` at every
           evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        try:
            xinv = precomp['xinv']
        except (TypeError, KeyError):
            xinv = self.inverse(x, precomp)
        return - self.log_det_grad_x( xinv )

    @counted
    def grad_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None),
                              *args, **kwargs):
        r""" Compute: :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T({\bf x})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T({\bf x})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x`.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        self.precomp_grad_x_partial_xd(x, precomp)
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.dim))
        for k,(a,avar,p) in enumerate(zip(self.approx_list,self.active_vars,
                                          precomp['components'])):
            out[:,avar] += a.grad_x_partial_xd(x[:,avar], p)[:,0,:] / \
                           a.partial_xd(x[:,avar], p)[:,0,nax]
        return out

    @counted
    def hess_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None),
                              *args, **kwargs):
        r""" Compute: :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        self.precomp_hess_x_partial_xd(x, precomp)
        out = np.zeros((x.shape[0], self.dim, self.dim))
        for k,(a,avar,p) in enumerate(zip(self.approx_list, self.active_vars,
                                          precomp['components'])):
            # 2d numpy advanced indexing
            nvar = len(avar)
            rr,cc = np.meshgrid(avar,avar)
            rr = list( rr.flatten() )
            cc = list( cc.flatten() )
            idxs = (slice(None), rr, cc)
            # Compute hess_x_partial_xd
            dxk = a.partial_xd(x[:,avar], p)[:,0]
            out[idxs] += (
                a.hess_x_partial_xd(x[:,avar], p)[:,0,:,:] / \
                dxk[:,nax,nax]
            ).reshape((x.shape[0],nvar**2))
            dxdxkT = a.grad_x_partial_xd(x[:,avar], p)[:,0,:]
            dxdxkT2 = dxdxkT[:,:,nax] * dxdxkT[:,nax,:]
            out[idxs] -= (dxdxkT2 / (dxk**2.)[:,nax,nax]).reshape((x.shape[0],nvar**2))
        return out

    @counted
    def action_hess_x_log_det_grad_x(self, x, dx, precomp=None, idxs_slice=slice(None),
                                     *args, **kwargs):
        r""" Compute: :math:`\langle\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}), \delta{\bf x}\rangle`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): direction
            on which to evaluate the Hessian
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\langle\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}), \delta{\bf x}\rangle`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        self.precomp_hess_x_partial_xd(x, precomp)
        m = x.shape[0]
        out = np.zeros((m, self.dim))
        for k,(a,avar,p) in enumerate(zip(self.approx_list, self.active_vars,
                                          precomp['components'])):
            dxk = a.partial_xd(x[:,avar], p)[:,0] # m
            out[:,avar] += np.einsum(
                '...ij,...j->...i',
                a.hess_x_partial_xd(x[:,avar], p)[:,0,:,:],
                dx[:,avar]
            ) / dxk[:,nax]
            dxdxkT = a.grad_x_partial_xd(x[:,avar], p)[:,0,:] # m x navar
            tmp = np.einsum('ij,ij->i', dxdxkT, dx[:,avar])
            out[:,avar] -= dxdxkT * tmp[:,nax] / (dxk**2.)[:,nax]
        return out

    @counted
    def inverse(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Compute: :math:`T^{-1}({\bf y})`

        If the map has more input than outputs :math:`d_{\rm in} > d_{\rm out}`,
        it consider the first :math:`d_{\rm in} - d_{\rm out}` values in ``x``
        to be already inverted values and feed them to the following approximations
        to find the inverse.

        If ``x`` has :math:`d < d_{\rm in}`, performs the inversion only on
        the :math:`d` dimensional head of the map.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.


        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`T^{-1}({\bf y})` for every evaluation point

        Raises:
          ValueError: if :math:`d_{\rm in} < d_{\rm out}`
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {}
        # Evaluation
        d = x.shape[1]    
        if d > self.dim_in:
            raise ValueError("dimension mismatch")
        xout = np.zeros(x.shape)
        skip_dim = self.dim_in - self.dim_out
        if skip_dim < 0:
            raise ValueError("The map has more output than inputs")
        xout[:,:skip_dim] = x[:,:skip_dim]
        for i in range(x.shape[0]):
            for k, (a,avar) in enumerate(zip(self.approx_list,self.active_vars)):
                if avar[-1] == d: 
                    break # Terminate once d is reached
                xout[i,skip_dim+k] = a.inverse(xout[i,avar[:-1]], x[i,skip_dim+k])
        return xout

    @counted
    def grad_x_inverse(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf x} T^{-1}({\bf x})`.

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
           NotImplementedError: to be implemented in subclasses
        """
        try:
            xinv = precomp['xinv']
        except (TypeError, KeyError):
            xinv = self.inverse(x, precomp)
        gx = self.grad_x(xinv)
        gx_inv = np.zeros((xinv.shape[0], self.dim, self.dim))
        for i in range(xinv.shape[0]):
            gx_inv[i,:,:] = scila.solve_triangular(gx[i,:,:], np.eye(self.dim), lower=True)
        return gx_inv

##############
# DEPRECATED #
##############
    
class TriangularTransportMap(
        TriangularComponentwiseTransportMap
):
    @deprecate(
        'TriangularTransportMap',
        '3.0',
        'Use Maps.TriangularComponentwiseTransportMap instead'
    )
    def __init__(self, active_vars, approx_list):
        super(TriangularTransportMap, self).__init__(
            active_vars=active_vars,
            approx_list=approx_list
        )

class MonotonicTriangularTransportMap(
        TriangularComponentwiseTransportMap
):
    @deprecate(
        'MonotonicTriangularTransportMap',
        '3.0',
        'Use Maps.TriangularComponentwiseTransportMap instead'
    )
    def __init__(self, active_vars, approx_list):
        super(MonotonicTriangularTransportMap, self).__init__(
            active_vars=active_vars,
            approx_list=approx_list
        )
