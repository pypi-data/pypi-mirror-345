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
import scipy.sparse as scisp

from ..Misc import \
    required_kwargs, \
    deprecate, counted

from .ParametricMapBase import ParametricMap

__all__ = [
    'AffineMap',
    # Deprecated
    'LinearMap',
]


class AffineMap(ParametricMap):
    r""" Affine map :math:`T[{\bf c},{\bf L}]({\bf x})={\bf c} + {\bf L}{\bf x}`
    """
    @required_kwargs('c','L')
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
            raise ValueError("Inconsistent dimensions")
        if Linv is not None and Linv.shape != L.shape[::-1]:
            raise ValueError(
                "The Moore-Penrose inverse Linv must have the transpose shape of L")
        kwargs['dim_in']  = L.shape[1]
        kwargs['dim_out'] = L.shape[0]
        super(AffineMap, self).__init__(**kwargs)
        self.c = c
        self.L = L
        self.Linv = Linv

    @property
    def Linv(self):
        return self._Linv

    @Linv.setter
    def Linv(self, Linv):
        if Linv is not None and Linv.shape != self.L.shape[::-1]:
            raise ValueError(
                "The Moore-Penrose inverse Linv must have the transpose shape of L")
        if Linv is not None and not np.allclose(
                np.dot(np.dot(self.L, Linv), self.L), self.L):
            raise ValueError(
                "The provided Linv seem not to be the Moore-Penrose inverse of L")
        self._Linv = Linv
        
    @property
    def c(self):
        r""" The constant term :math:`{\bf c}`
        """
        return self.constantTerm

    @c.setter
    def c(self, value):
        if value.ndim != 1 or value.shape[0] != self.dim_out:
            raise ValueError("Inconsistent dimensions")
        self.constantTerm = value
        
    @property
    def L(self):
        r""" The linear term :math:`{\bf L}`
        """
        return self.linearTerm

    @L.setter
    def L(self, value):
        if value.ndim != 2 or self.dim_out != value.shape[0] or self.dim_in != value.shape[1]:
            raise ValueError("Inconsistent dimensions")
        self.linearTerm = value
        self.Linv = None

    @property
    def coeffs(self):
        r""" Returns the constant and linear term of the linear map.

        Returns:
          (:class:`ndarray<numpy.ndarray>`) --
            flattened array of coefficients
        """
        return np.hstack( (
            self.constantTerm.flatten(),
            self.linearTerm.flatten())
                      )

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the constant and linear term of the linear map.

        Args:
           coeffs (:class:`ndarray<numpy.ndarray>`): coefficients

        Raises:
           ValueError: if the shape of linear and constant term are inconsistent.
        """
        if self.constantTerm.size() + self.linearTerm.size() != len(coeffs):
            raise ValueError("Inconsistent dimensions")
        self.c = coeffs[:self.dim_out]
        self.L = coeffs[self.dim_out:].reshape((self.dim_out, self.dim_in))

    @counted
    def evaluate(self, x, *args, **kwargs):
        r""" Evaluate the map at the points :math:`{\bf x} \in \mathbb{R}^{m \times d_{\text{in}}}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_{\text{in}}`]): evaluation points

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d_{\text{out}}`]) -- transformed points

        Raises:
           ValueError: if :math:`d_{\text{in}}` does not match the dimension of the transport map.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = np.transpose( self.linearTerm.dot( x.transpose() ) ) + self.constantTerm 
        return out

    @counted
    def grad_x(self, x, *args, **kwargs):
        r""" Evaluate the gradient (constant for linear maps)

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_{\text{in}}`]): evaluation points

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m, d_{\text{out}},d_{\text{in}}`]) --
             gradient matrix (constant at every evaluation point).

        Raises:
           ValueError: if :math:`d_{\text{in}}` does not match the dimension of the transport map.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        if scisp.issparse(self.linearTerm):
            grad = self.linearTerm.toarray()
        else:
            grad = self.linearTerm
        return grad[np.newaxis,:,:]

    @counted
    def tuple_grad_x(self, x, *args, **kwargs):
        r""" Evaluate the function and gradient (constant for linear maps)

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_{\text{in}}`]): evaluation points

        Returns:
           (:class:`tuple`) --
             function and gradient matrices .

        Raises:
           ValueError: if :math:`d_{\text{in}}` does not match the dimension of the transport map.
        """
        return (self.evaluate(x, *args, **kwargs), self.grad_x(x, *args, **kwargs))
        
    @counted
    def hess_x(self, x, *args, **kwargs):
        r""" Evaluate the Hessian for the linear map (zero)

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_{\text{in}}`]): evaluation points
        
        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d_{\text{out},d_{\text{in}},d_{\text{in}}`]) -- Hessian matrix (zero everywhere).

        Raises:
          ValueError: if :math:`d_{\text{in}}` does not match the dimension of the transport map.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        return np.zeros((1, self.dim_out, self.dim_in, self.dim_in))

    @counted
    def action_hess_x(self, x, dx, *args, **kwargs):
        r""" Evaluate the action of the Hessian for the linear map (zero)
        
        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_{\text{in}}`]): evaluation points
          dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d_{\text{in}}`]): direction
            on which to evaluate the Hessian

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d_{\text{out}},d_{\text{in}}`]) --
            action of the Hessian matrix (zero everywhere).

        Raises:
          ValueError: if :math:`d_{\text{in}}` does not match the dimension of the transport map.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        return np.zeros((1, self.dim_out, self.dim_in))

    @counted
    def inverse(self, y, *args, **kwargs):
        r""" Compute the pseudoinverse map :math:`\hat{T}^{-1}({\bf y},{\bf a})`

        Args:
           y (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\hat{T}^{-1}({\bf y},{\bf a})` for every evaluation point
        """
        if y.shape[1] != self.dim_out:
            raise ValueError("dimension mismatch")
        b = (y - self.c)
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
        gxi = self.Linv.copy()
        return gxi[np.newaxis,:,:]

    @counted
    def hess_x_inverse(self, x, *args, **kwargs):
        r""" Compute :math:`\nabla^2_{\bf x} \hat{T}^{-1}({\bf x},{\bf a})`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`d,d,d`]) --
           Hessian matrix (zero everywhere).

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        return np.zeros((1,self.dim_in, self.dim_out, self.dim_out))

    @counted
    def action_hess_x_inverse(self, x, dx, *args, **kwargs):
        r""" Compute :math:`\langle\nabla^2_{\bf x} \hat{T}^{-1}({\bf x},{\bf a}), \delta{\bf x}\rangle`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): direction
            on which to evaluate the Hessian

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]) --
           action of Hessian matrix (zero everywhere).

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        return np.zeros((1,self.dim_in, self.dim_out))

class LinearMap(AffineMap):
    @deprecate(
        'LinearMap',
        '3.0',
        'Use Maps.AffineMap instead'
    )
    def __init__(self, c, L, Linv=None):
        super(LinearMap, self).__init__(c=c, L=L, Linv=Linv)
