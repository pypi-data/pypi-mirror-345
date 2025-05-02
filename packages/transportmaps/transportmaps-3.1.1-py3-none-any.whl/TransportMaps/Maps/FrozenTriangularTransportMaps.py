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

from ..Misc import counted

from .Functionals import \
    FrozenLinear, FrozenExponential, FrozenNormalToUniform

from .TransportMapBase import TransportMap
from .TriangularComponentwiseTransportMapBase import TriangularComponentwiseTransportMap

__all__ = [
    'FrozenLinearDiagonalTransportMap',
    'FrozenExponentialDiagonalTransportMap',
    'FrozenNormalToUniformDiagonalTransportMap',
    'FrozenGaussianToUniformDiagonalTransportMap',
    'FrozenBananaMap'
]

nax = np.newaxis


class FrozenLinearDiagonalTransportMap(TriangularComponentwiseTransportMap):
    r""" Linear diagonal transport map :math:`(x_1,\ldots,x_d) \rightarrow (a_1+b_1 x_1, \ldots, a_d + b_d x_d)`

    Args:
       a (:class:`ndarray<numpy.ndarray>` [:math:`d`]): coefficients
       b (:class:`ndarray<numpy.ndarray>` [:math:`d`]): coefficients

    .. note:: This map is frozen, meaning that optimizing the coefficients with
       respect to a certain cost function is not allowed.

    .. seealso:: :class:`TriangularTransportMap` for a description of the
       overridden methods and :class:`FunctionalApproximations.FrozenLinear`
       for a description of the linear approximation used for each component.
    """

    def __init__(self, a, b):
        if len(a) != len(b):
            raise ValueError("Dimension mismatch")
        dim = len(a)
        self.a = np.asarray(a)
        self.b = np.asarray(b)
        approx_list = []
        active_vars = []
        for d in range(dim):
            approx_list.append(FrozenLinear(1, a[d], b[d]))
            active_vars.append([d])
        super(FrozenLinearDiagonalTransportMap, self).__init__(
            active_vars=active_vars,
            approx_list=approx_list
        )

    def evaluate(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        xout = self.a[nax,:] + self.b[nax,:] * x
        return xout

    def inverse(self, x, *args, **kwargs):
        xout = (x - self.a[nax,:]) / self.b[nax,:]
        return xout

    def grad_x(self, x, *args, **kwargs):
        r""" This is a diagonal map """
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros( (x.shape[0], self.dim, self.dim) )
        diag_out = np.einsum('...ii->...i', out) # Read/write from Numpy 1.10
        diag_out[:] = self.b
        return out

    def grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros( (x.shape[0], self.dim, self.dim) )
        diag_out = np.einsum('...ii->...i', out) # Read/write from Numpy 1.10
        diag_out[:] = 1./self.b
        return out

    def det_grad_x(self, x, *args, **kwargs):
        return np.exp( self.log_deg_grad_x(x, *args, **kwargs) )

    def log_det_grad_x(self, x, *args, **kwargs):
        return np.sum( np.log(self.b) )

    def log_det_grad_x_inverse(self, x, *args, **kwargs):
        return - self.log_det_grad_x(x, *args, **kwargs)

    def grad_x_log_det_grad_x(self, x, *args, **kwargs):
        return np.zeros((x.shape[0], self.dim))

    def grad_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        return self.grad_x_log_det_grad_x(x, *args, **kwargs)
        
    def hess_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros( (x.shape[0], self.dim, self.dim, self.dim) )

    def hess_x_inverse(self, x, *args, **kwargs):
        return self.hess_x(x, *args, **kwargs)

    def action_hess_x(self, x, dx, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros( (x.shape[0], self.dim, self.dim) )

    def action_hess_x_inverse(self, x, dx, *args, **kwargs):
        return self.action_hess_x(x, dx, *args, **kwargs)
        
    def hess_x_log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((x.shape[0], self.dim, self.dim))

    def hess_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        return self.hess_x_log_det_grad_x(x, *args, **kwargs)
        
    def action_hess_x_log_det_grad_x(self, x, dx, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((x.shape[0], self.dim))

    def action_hess_x_log_det_grad_x_inverse(self, x, dx, *args, **kwargs):
        return self.action_hess_x_log_det_grad_x(x, dx, *args, **kwargs)


class FrozenExponentialDiagonalTransportMap(TriangularComponentwiseTransportMap):
    r""" Exponential diagonal transport map :math:`(x_1,\ldots,x_d) \rightarrow (\exp(x_1), \ldots, \exp(x_d))`

    Args:
       dim (int): dimension :math:`d` of the transport map

    .. note:: This map is frozen, meaning that optimizing the coefficients with
       respect to a certain cost function is not allowed.

    .. seealso:: :class:`TriangularTransportMap` for a description of the
       overridden methods and
       :class:`FunctionalApproximations.FrozenExponential`
       for a description of the exponential approximation used for each component.
    """
    
    def __init__(self, dim):
        approx_list = []
        active_vars = []
        for d in range(dim):
            approx_list.append( FrozenExponential(1) )
            active_vars.append( [d] )
        super(FrozenExponentialDiagonalTransportMap,self).__init__(
            active_vars=active_vars,
            approx_list=approx_list
        )

    def evaluate(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        xout = np.exp(x)
        return xout

    def grad_x(self, x, *args, **kwargs):
        r""" This is a diagonal map """
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros( (x.shape[0], self.dim, self.dim) )
        diag_out = np.einsum('...ii->...i', out) # Read/write from Numpy 1.10
        diag_out[:] = self.evaluate(x)
        return out

    def action_grad_x(self, x, dx, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        ev = self.evaluate(x)
        ixs = tuple( [slice(None), slice(None)] + [np.newaxis]*(dx.ndim-2) )
        out = ev[ixs] * dx
        return out

    def action_adjoint_grad_x(self, x, dx, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        ev = self.evaluate(x)
        ixs = tuple( [slice(None)] + [np.newaxis]*(dx.ndim-2) + [slice(None)] )
        out = dx * ev[ixs]
        return out

    def tuple_grad_x(self, x, *args, **kwargs):
        return self.evaluate(x), self.grad_x(x)

    def action_tuple_grad_x(self, x, dx, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        ev = self.evaluate(x)
        ixs = tuple( [slice(None), slice(None)] + [np.newaxis]*(dx.ndim-2) )
        out = ev[ixs] * dx
        return ev, out

    def det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.exp( self.log_det_grad_x(x, *args, **kwargs) )

    def log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.sum( x, axis=1 )

    def grad_x_log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.ones((self.dim))

    def hess_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros( (x.shape[0], self.dim, self.dim, self.dim) )
        diag_out = np.einsum('...iii->...i', out) # Read/write from Numpy 1.10
        diag_out[:] = self.evaluate(x)
        return out

    def action_hess_x(self, x, dx, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros( (x.shape[0], self.dim, self.dim) )
        diag_out = np.einsum('...ii->...i', out) # Read/write from Numpy 1.10
        diag_out[:] = self.evaluate(x) * dx
        return out

    def hess_x_log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((self.dim, self.dim))

    def action_hess_x_log_det_grad_x(self, x, dx, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((self.dim))

    def inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        xout = np.log(x)
        return xout

    def grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros( (x.shape[0], self.dim, self.dim) )
        diag_out = np.einsum('...ii->...i', out) # Read/write from Numpy 1.10
        diag_out[:] = 1/x
        return out

    def hess_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros( (x.shape[0], self.dim, self.dim, self.dim) )
        diag_out = np.einsum('...iii->...i', out) # Read/write from Numpy 1.10
        diag_out[:] = -1/x**2
        return out

    def action_hess_x_inverse(self, x, dx, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros( (x.shape[0], self.dim, self.dim) )
        diag_out = np.einsum('...ii->...i', out) # Read/write from Numpy 1.10
        diag_out[:] = -1/x**2 * dx
        return out

    def log_det_grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        xout = - np.sum( np.log(x), axis=1 )
        return xout

    def grad_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        xout = - 1./x
        return xout

    def hess_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros( (x.shape[0], self.dim, self.dim) )
        diag_out = np.einsum('...ii->...i', out) # Read/write from Numpy 1.10
        diag_out[:] = 1/x**2
        return out

    def action_hess_x_log_det_grad_x_inverse(self, x, dx, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = 1/x**2 * dx
        return out


class FrozenNormalToUniformDiagonalTransportMap(TriangularComponentwiseTransportMap):
    r""" Gaussian to Uniform diagonal transport map :math:`(x_1,\ldots,x_d) \rightarrow (\frac{1}{2}[1+{\rm erf}(x_1/\sqrt{2})], \ldots, \frac{1}{2}[1+{\rm erf}(x_d/\sqrt{2})])`

    Args:
       dim (int): dimension :math:`d` of the transport map

    .. note:: This map is frozen, meaning that optimizing the coefficients with
       respect to a certain cost function is not allowed.

    .. seealso:: :class:`TriangularTransportMap` for a description of the
       overridden methods and
       :class:`FunctionalApproximations.FrozenGaussianToUniform`
       for a description of the Gaussian to Uniform approximation used for
       each component.
    """
    
    def __init__(self, dim):
        approx_list = []
        active_vars = []
        for d in range(dim):
            approx_list.append( FrozenNormalToUniform(1) )
            active_vars.append( [d] )
        super(FrozenGaussianToUniformDiagonalTransportMap,self).__init__(
            active_vars=active_vars,
            approx_list=approx_list
        )


FrozenGaussianToUniformDiagonalTransportMap = FrozenNormalToUniformDiagonalTransportMap
        
# class FrozenBananaTransportMap(TriangularTransportMap):
#     def __init__(self, a, b, mu, sigma2):
#         self.dim = 2
#         self.a = a
#         self.b = b
#         self.mu = mu
#         self.sigma2 = sigma2
#         self.chol = scila.cholesky( sigma2, lower = True )
#         self.inv_chol = scila.solve_triangular( self.chol,
#                                             np.eye(self.dim),
#                                             lower=True )
#         self.inv_sigma2 = scila.cho_solve( (self.chol,True),
#                                            np.eye(self.dim) )
#     def Tb(self, x, *args, **kwargs):
#         return self.mu + np.dot( self.chol, x.T ).T
#     def Tb_inv(self, x, *args, **kwargs):
#         return scila.solve_triangular( self.chol, (x-self.mu).T, lower=True ).T
#     def Tt(self, x, *args, **kwargs):
#         a = self.a
#         b = self.b
#         y = np.zeros(x.shape)
#         y[:,0] = a * x[:,0]
#         # y[:,1] = x[:,1] / a - b * ((a*x[:,0])**2. + a**2.)
#         y[:,1] = x[:,1] / a - b * ((a*x[:,0])**2.)
#         return y
#     def Tt_inv(self, y, *args, **kwargs):
#         a = self.a
#         b = self.b
#         x = np.zeros(y.shape)
#         x[:,0] = y[:,0] / a
#         # x[:,1] = a * (y[:,1] + b * (y[:,0]**2. + a**2.))
#         x[:,1] = a * (y[:,1] + b * (y[:,0]**2.))
#         return x
#     def evaluate(self, x, *args, **kwargs):
#         return self.Tt( self.Tb(x, par), par )
#     def __call__(self, x):
#         return self.evaluate(x)
#     def inverse(self, x, *args, **kwargs):
#         return self.Tb_inv( self.Tt_inv(x, par), par )
#     def log_det_grad_x(self, x, *args, **kwargs):
#         return 2. * np.log(self.a)


class FrozenBananaMap(TransportMap):
    def __init__(self, a, b):
        self.a = a
        self.b = b
        super(FrozenBananaMap, self).__init__(
            dim_in=2,
            dim_out=2
        )

    @counted
    def evaluate(self, x, *args, **kwargs):
        a = self.a
        b = self.b
        y = np.zeros(x.shape)
        y[:,0] = a * x[:,0]
        y[:,1] = x[:,1] / a - b * ((a*x[:,0])**2. + a**2.)
        # y[:,1] = x[:,1] / a - b * ((a*x[:,0])**2.)
        return y

    @counted
    def inverse(self, y, *args, **kwargs):
        a = self.a
        b = self.b
        x = np.zeros(y.shape)
        x[:,0] = y[:,0] / a
        x[:,1] = a * (y[:,1] + b * (y[:,0]**2. + a**2.))
        # x[:,1] = a * (y[:,1] + b * (y[:,0]**2.))
        return x

    @counted
    def log_det_grad_x(self, x, *args, **kwargs):
        return np.ones(x.shape[0])

    @counted
    def log_det_grad_x_inverse(self, x, *args, **kwargs):
        return np.ones(x.shape[0])

    @counted
    def grad_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        return np.zeros(x.shape)

    @counted
    def hess_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        return np.zeros((x.shape[0],self.dim,self.dim))

    @counted
    def action_hess_x_log_det_grad_x_inverse(self, x, dx, *args, **kwargs):
        return np.zeros((x.shape[0],self.dim))

    @counted
    def grad_x(self, x, *args, **kwargs):
        out = np.zeros( (x.shape[0], self.dim, self.dim) )
        out[:,0,0] = self.a
        out[:,1,0] = - 2. * self.a**2. * self.b * x[:,0]
        out[:,1,1] = 1./self.a
        return out

    @counted
    def hess_x(self, x, *args, **kwargs):
        out = np.zeros( (x.shape[0], self.dim, self.dim, self.dim) )
        out[:,1,0,0] = - 2. * self.a**2. * self.b
        return out

    @counted
    def grad_x_inverse(self, x, *args, **kwargs):
        out = np.zeros( (x.shape[0], self.dim, self.dim) )
        out[:,0,0] = 1./self.a
        out[:,1,0] = 2. * self.a * self.b * x[:,0]
        out[:,1,1] = self.a
        return out

    @counted
    def hess_x_inverse(self, x, *args, **kwargs):
        out = np.zeros( (x.shape[0], self.dim, self.dim, self.dim) )
        out[:,1,0,0] = 2. * self.a * self.b
        return out

    @counted
    def action_hess_x_inverse(self, x, dx, *args, **kwargs):
        return np.einsum('...ijk,...k->...ij', self.hess_x_inverse(x), dx)
