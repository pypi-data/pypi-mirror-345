#!/usr/bin/env python

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
# Author: Transport Map Team
# Website: transportmaps.mit.edu
# Support: transportmaps.mit.edu/qa/
#

import numpy as np
import numpy.linalg as npla
import scipy.linalg as scila

from ..Misc import \
    required_kwargs, \
    deprecate, counted, cached, get_sub_cache
from .AffineMapBase import AffineMap
from .ParametricTransportMapBase import ParametricTransportMap

__all__ = [
    'AffineTransportMap',
    # DEPRECATED
    'LinearTransportMap'
]


class AffineTransportMap(AffineMap, ParametricTransportMap):
    r""" Linear map :math:`T({\bf x})={\bf c} + {\bf L}{\bf x}`

    .. note:: This class supports only regular matrices. Ad-hoc implemnetations for 
       sparse matrices should be implemented by the user.
    """
    @required_kwargs('c', 'L')
    def __init__(self, **kwargs):
        r""""
        Kwargs:
          c (:class:`ndarray<numpy.ndarray>` [:math:`d`]): term :math:`{\bf c}`
          L (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]): term :math:`{\bf L}`
        
        Optional Kwargs:
          Linv (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]):
            if provided, it contains the Moore-Penrose pseudoinverse :math:`{\bf L}^{\dagger}`
        """
        c    = kwargs['c']
        L    = kwargs['L']
        Linv = kwargs.get('Linv')
        
        if c.shape[0] != L.shape[0]:
            raise ValueError("Dimensions of the constant term and the linear term are inconsistent")
        if L.shape[0] != L.shape[1]:
            raise ValueError("The linear term must be square")
        if Linv is not None and L.shape != Linv.shape:
            raise ValueError("The inerse matrix Linv must have the same shape of L")

        kwargs['dim'] = c.shape[0]
        super(AffineTransportMap, self).__init__(**kwargs)

    @property
    def L(self):
        return self.linearTerm
        
    @L.setter
    def L(self, L):
        self.Linv = None
        self.linearTerm = L

        # Check monotoniticy and invertibility,
        # and construct an appropriate factorization
        factorization_set = False
        if np.all( L == np.tril(L) ) or np.all( L == np.triu(L) ):
            # The linear term is already in a triangular form so does not need to be factorized
            if np.all( L == np.tril(L) ):
                ftype = 'l'
                f = L
            else:
                ftype = 'u'
                f = L
            not_inv_flag = np.any( np.isclose(np.diag(f), 0., atol=1e-12) )
            logdet = np.sum( np.log( np.abs(np.diag(f)) ) )
            factorization_set = True
        if np.all( L == L.T ):
            # A Cholesky factorization of the linear term can be computed
            try:
                ftype = 'chol'
                f = scila.cholesky(L, lower=True)
                not_inv_flag = np.any( np.isclose(np.diag(f), 0., atol=1e-12) )
                logdet = 2. * np.sum( np.log( np.abs(np.diag(f)) ) )
                factorization_set = True
            except npla.LinAlgError:
                self.logger.warning(
                    "The symmetric linear term is not positive definite. " + \
                    "Using LU factorization instead of Cholesky.")
        if not factorization_set:
            # Perform an LU factorization
            ftype = 'lu'
            f = scila.lu(L)
            not_inv_flag = np.any( np.isclose(np.diag(f[2]), 0., atol=1e-12) )
            logdet = np.sum( np.log( np.abs(np.diag(f[2])) ) )
        if not_inv_flag:
            raise ValueError("The map might not be strictly monotone and therefore not invertible")

        self._fact_type = ftype
        self._fact = f
        self._logdet = logdet

    def solve_linear(self, y):
        r""" Solves the linear system :math:`{\bf L}{\bf x} = {\bf y}`
        """
        if self._fact_type == 'l' or self._fact_type == 'u':
            x = scila.solve_triangular(self._fact, y, lower=(self._fact_type=='l'))
        elif self._fact_type == 'chol':
            x = scila.solve_triangular(self._fact, y, lower=True)
            x = scila.solve_triangular(self._fact, x, lower=True, trans='T')
        else:
            x = np.dot(self._fact[0].T, y)
            x = scila.solve_triangular(self._fact[1], x, lower=True)
            x = scila.solve_triangular(self._fact[2], x, lower=False)
        return x

    def solve_linear_transpose(self, y):
        r""" Solves the linear system :math:`{\bf L}^{\top}{\bf x} = {\bf y}`
        """
        if self._fact_type == 'l' or self._fact_type == 'u':
            x = scila.solve_triangular(
                self._fact, y, lower=(self._fact_type=='l'), trans='T')
        elif self._fact_type == 'chol':
            x = scila.solve_triangular(self._fact, y, lower=True)
            x = scila.solve_triangular(self._fact, x, lower=True, trans='T')
        else:
            x = scila.solve_triangular(self._fact[2], y, lower=False, trans='T')
            x = scila.solve_triangular(self._fact[1], x, lower=True, trans='T')
            x = np.dot(self._fact[0], x)
        return x

    @staticmethod
    @deprecate("build_from_Gaussian", '3.0',
               "Use build_from_Normal instead")
    def build_from_Gaussian(pi, typeMap = 'sym'):
        return LinearTransportMap.build_from_Normal(pi, typeMap)
        
    @staticmethod
    def build_from_Normal(pi , typeMap = "sym"):
        r""" Build a linear transport map from a
        standard normal to a Gaussian distribution pi

        Args:
          pi (:class:`GaussianDistribution`):
            constant term of the linear map
          typeMap (str): the linear term :math:`L` is obtained as the square root of
            the covarinace :math:`\Sigma` or precision :math:`\Sigma^{-1}` matrix.
            For ``typeMap=='sym'``, :math:`L=U\Lambda^{\frac{1}{2}}U^T`
            where :math:`\Sigma = U\Lambda U^T` is the eigenvalue decomposition
            of :math:`\Sigma`.
            For ``typeMap=='tri'``, :maht:`L=C` where :math:`\Sigma=CC^T` is
            the Cholesky decomposition of :math:`\Sigma`.
            For ``typeMap=='kl'``, :math:`L=U\Lambda^{\frac{1}{2}}`
            where :math:`\Sigma = U\Lambda U^T` is the eigenvalue decomposition
            of :math:`\Sigma` (this corresponds to the Karuenen-Loeve expansion).
            The eigenvalues and eigenvectors are ordered with :math:`\lambda_i\geq\lambda_{i+1}`.
        Raises:
           ValueError: if the shape of linear and constant term are inconsistent.
        """
        from TransportMaps.Distributions.Deprecated import GaussianDistribution
        from TransportMaps.Distributions.FrozenDistributions import NormalDistribution
        if not ( issubclass(type(pi), GaussianDistribution) or \
                 issubclass(type(pi), NormalDistribution) ):
            raise ValueError("The input distribution should be a Gaussian")
        if typeMap == "sym":
            try:
                U, s, V = np.linalg.svd(pi.sigma)
                s_sr = np.sqrt(s)
                linearTerm_sr = np.dot( U , np.diag( np.sqrt(s_sr) ) )
                linearTerm = np.dot( linearTerm_sr, linearTerm_sr.transpose() )
            except AttributeError:
                U, s, V = np.linalg.svd(pi.inv_sigma)
                s_inv_sr = np.sqrt(1./s)
                linearTerm_sr = np.dot( U , np.diag( np.sqrt(s_inv_sr) ) )
                linearTerm = np.dot( linearTerm_sr, linearTerm_sr.transpose() )
        elif typeMap == "tri":
            try:
                linearTerm = np.linalg.cholesky(pi.sigma)
            except AttributeError:
                sigma = np.linalg.inv(pi.inv_sigma)
                linearTerm = np.linalg.cholesky(sigma)
        elif typeMap == "kl":
            try:
                lmb, V = npla.eigh(pi.sigma)
                linearTerm = V * np.sqrt(lmb)[np.newaxis,:]
            except AttributeError:
                lmb, V = npla.eigh(pi.inv_sigma)
                lmb = 1/lmb
                linearTerm = V * np.sqrt(lmb)[np.newaxis,:]
        elif typeMap == "lis":
            linearTerm = pi.square_root
        else:
            raise ValueError("Type of the map not supported yet")
        constantTerm = pi.mu
        return LinearTransportMap(constantTerm, linearTerm)

    @counted
    def log_det_grad_x(self, x, *args, **kwargs):
        r""" Compute: :math:`\log \det \nabla_{\bf x} \hat{T}({\bf x}, {\bf a})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (:class:`float`) --
           :math:`\log \det \nabla_{\bf x} \hat{T}({\bf x}, {\bf a})`
           (constant at every evaluation point)

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return self._logdet * np.ones(1)

    @counted
    def grad_x_log_det_grad_x(self, x, *args, **kwargs):
        r""" Compute: :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x`.
        """
        return np.zeros((1,self.dim))

    @counted
    def hess_x_log_det_grad_x(self, x, *args, **kwargs):
        r""" Compute: :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x`.
        """
        return np.zeros((1, self.dim, self.dim))

    @counted
    def action_hess_x_log_det_grad_x(self, x, dx, *args, **kwargs):
        r""" Compute: :math:`\langle\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a}),\delta{\bf x}\rangle`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x`.
        """
        return np.zeros((1, self.dim))

    @counted
    def inverse(self, y, *args, **kwargs):
        r""" Compute: :math:`\hat{T}^{-1}({\bf y},{\bf a})`

        Args:
           y (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\hat{T}^{-1}({\bf y},{\bf a})` for every evaluation point
        """
        if y.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        b = (y - self.c)
        if not hasattr(self, '_Linv') or self._Linv is None:
            out = self.solve_linear( b.T ).T
        else:
            out = np.dot(self._Linv, b.T).T
        return out
    
    @counted
    def grad_x_inverse(self, x, *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf x} \hat{T}^{-1}({\bf x},{\bf a})`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]) --
           gradient matrix (constant at every evaluation point).

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if not hasattr(self, '_Linv') or self._Linv is None:
            self.Linv = self.solve_linear( np.eye(self.dim) )
        gxi = self.Linv.copy()
        return gxi[np.newaxis,:,:]
    
    @counted
    def log_det_grad_x_inverse(self, x, *args, **kwargs):
        r""" Compute: :math:`\log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (float) --
           :math:`\log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`
           (constant at every evaluation point)
        """
        return - self._logdet

    @counted
    def grad_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        return np.zeros((1,self.dim))

    @counted
    def hess_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        return np.zeros((1,self.dim,self.dim))

    @counted
    def action_hess_x_log_det_grad_x_inverse(self, x, dx, *args, **kwargs):
        return np.zeros((1,self.dim))


class LinearTransportMap(AffineTransportMap):
    @deprecate(
        'LinearTransportMap',
        '3.0',
        'Use Maps.AffineTransportMap instead'
    )
    def __init__(self, c, L, Linv=None):
        super(LinearTransportMap, self).__init__(c=c, L=L, Linv=Linv)
