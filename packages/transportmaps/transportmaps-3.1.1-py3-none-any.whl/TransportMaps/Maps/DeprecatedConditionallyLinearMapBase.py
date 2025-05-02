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

from ..Misc import deprecate, counted
from .MapBase import Map

__all__ = [
    'ConditionallyLinearMap',
]

nax = np.newaxis


class ConditionallyLinearMap(Map):
    r""" Map :math:`T:\mathbb{R}^{d_x}\times\mathbb{R}^{d_a}\rightarrow\mathbb{R}^{d_y}` defined by :math:`T({\bf x};{\bf a}) = {\bf c}({\bf a}) + {\bf T}({\bf a}) {\bf x}`

    Args:
      c (:class:`Map`): map :math:`{\bf c}:\mathbb{R}^{d_a}\rightarrow\mathbb{R}^{d_y}`
      T (:class:`Map`):
        map :math:`{\bf T}:\mathbb{R}^{d_a}\rightarrow\mathbb{R}^{d_y\times d_x}`
      coeffs (:class:`ndarray<numpy.ndarray>`): fixing the coefficients :math:`{\bf a}` defining
        :math:`{\bf c}({\bf a})` and :math:`{\bf T}({\bf a})`.
    """
    @deprecate(
        'ConditionallyLinearMap',
        '3.0',
        'This class was needed for the linear filtering/smoothing algorithm. ' + \
        'We need to figure out whether it is still needed.'
    )
    def __init__(self, c, T, coeffs=None):
        if c.dim_in != T.dim_in:
            raise ValueError("Input dimension mismatch between c and T")
        if T.dim_out % c.dim_out != 0:
            raise ValueError("Output dimension mismatch between c and T")
        self._n_coeffs = c.dim_in
        self._cMap = c
        self._TMap = T
        din = T.dim_out // c.dim_out
        dout = c.dim_out
        super(ConditionallyLinearMap,self).__init__(
            din + self.n_coeffs, dout)
        self._coeffs = None
        self.coeffs = coeffs
        
    @property
    def c(self):
        return self._c

    @property
    def T(self):
        return self._T
        
    @property
    def n_coeffs(self):
        return self._n_coeffs

    @property
    def dim_lin(self):
        return self.dim_in - self.n_coeffs

    @property
    def coeffs(self):
        r""" Returns the actual value of the coefficients.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients.
        """
        return self._coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients.

        Args:
           coeffs (:class:`ndarray<numpy.ndarray>` [:math:`N`]):
              coefficients for the various maps
        """
        if coeffs is None:
            self._coeffs = None
        elif self._coeffs is None or np.any(self._coeffs != coeffs):
            self._c = self._cMap.evaluate(coeffs[nax,:])[0,:]
            self._T = self._TMap.evaluate(coeffs[nax,:])[0,:,:]
            try:
                self._grad_a_c = self._cMap.grad_x(coeffs[nax,:])[0,:,:]
                self._grad_a_T = self._TMap.grad_x(coeffs[nax,:])[0,:,:,:]
            except NotImplementedError:
                self._grad_a_c = None
                self._grad_a_T = None
            try:
                self._hess_a_c = self._cMap.hess_x(coeffs[nax,:])[0,:,:,:]
                self._hess_a_T = self._TMap.hess_x(coeffs[nax,:])[0,:,:,:,:]
            except NotImplementedError:
                self._hess_a_c = None
                self._hess_a_T = None
            self._coeffs = coeffs

    @property
    def grad_a_c(self):
        return self._grad_a_c

    @property
    def grad_a_T(self):
        return self._grad_a_T

    @property
    def hess_a_c(self):
        return self._hess_a_c

    @property
    def hess_a_T(self):
        return self._hess_a_T

    @counted
    def evaluate(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate the map :math:`T` at the points :math:`{\bf x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]) -- transformed points
        """
        if self._coeffs is None:
            m = x.shape[0]
            out = np.zeros((m,self.dim_out))
            for i in range(m):
                cf = x[[i],self.dim_lin:]
                xx = x[i,:self.dim_lin]
                c = self._cMap.evaluate(cf)[0,:]
                T = self._TMap.evaluate(cf)[0,:,:]
                out[i,:] = c + np.dot(T, xx)
        else:
            xx = x[:,:self.dim_lin]
            out = self.c + np.dot(self.T, xx.T).T
        return out

    @counted
    def grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        if self._coeffs is None:
            m = x.shape[0]
            out = np.zeros((m,self.dim_out, self.dim_in))
            for i in range(m):
                cf = x[[i],self.dim_lin:]
                xx = x[i,:self.dim_lin]
                T = self._TMap.evaluate(cf)[0,:,:]
                gac = self._cMap.grad_x(cf)[0,:,:]
                gaT = self._TMap.grad_x(cf)[0,:,:,:]
                out[i,:,:self.dim_lin] = T
                out[i,:,self.dim_lin:] = gac + np.einsum('ijk,j->ik', gaT, xx)
        else:
            raise NotImplementedError("To be done")
        return out
