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

from ..Misc import counted

from .TransportMapBase import TransportMap

__all__ = [
    'PermutationTransportMap',
]


class PermutationTransportMap(TransportMap): 
    r""" Map :math:`T({\bf x}) = [x_{p(0)}, \ldots, x_{p(d)}]^T`

    Args:
      p (list): permutation list :math:`p`
    """
    def __init__(self, p):
        if any([ i != pi for i,pi in enumerate(sorted(p))]):
            raise ValueError("The permutation is not complete or valid")
        self.p = np.asarray(p)
        self.inv_p = np.argsort(self.p)
        super(PermutationTransportMap, self).__init__(
            dim=len(p)
        )

    @property
    def permutation(self):
        return self.p

    @permutation.setter
    def permutation(self, p):
        if any([ i != pi for i,pi in enumerate(sorted(p))]):
            raise ValueError("The permutation is not complete or valid")
        if len(p) != self.dim:
            raise ValueError("The permutation is not of the same dimension")
        self.p = np.asarray(p)
        self.inv_p = np.argsort(self.p)

    @counted
    def evaluate(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return x[:,self.p]

    @counted
    def grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        gx = np.zeros((1, self.dim, self.dim))
        for i in range(self.dim):
            gx[:,i,self.p[i]] = 1.
        return gx

    @counted
    def hess_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((1, self.dim, self.dim, self.dim))

    @counted
    def inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return x[:, self.inv_p]

    @counted
    def grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        gx = np.zeros((1, self.dim, self.dim))
        for i in range(self.dim):
            gx[:,i,self.inv_p[i]] = 1.
        return gx

    @counted
    def hess_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((1, self.dim, self.dim, self.dim))

    @counted
    def log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros(1)

    @counted
    def grad_x_log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((1, self.dim))

    @counted
    def hess_x_log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((1, self.dim, self.dim))

    @counted
    def det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.ones(1)

    @counted
    def log_det_grad_x_inverse(self, x, *args, **kwargs):
        return self.log_det_grad_x(x, *args, **kwargs)

    @counted
    def det_grad_x_inverse(self, x, *args, **kwargs):
        return self.det_grad_x(x, *args, **kwargs)

    @counted
    def grad_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        return self.grad_x_log_det_grad_x(x, *args, **kwargs)

    @counted
    def hess_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        return self.hess_x_log_det_grad_x(x, *args, **kwargs)
