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

from .ParametricMonotoneFunctionalBase import ParametricMonotoneFunctional

__all__ = ['IdentityParametricMonotoneFunctional']

class IdentityParametricMonotoneFunctional(ParametricMonotoneFunctional):
    r""" Identity functional :math:`\mathbb{R}\rightarrow\mathbb{R}`.
    """
    def __init__(self):
        super(IdentityParametricMonotoneFunctional, self).__init__(1)

    @property
    def n_coeffs(self):
        return 0

    @property
    def coeffs(self):
        return np.zeros(0)

    @coeffs.setter
    def coeffs(self, coeffs):
        pass

    def precomp_evaluate(self, *args, **kwargs):
        pass

    def precomp_Vandermonde_evaluate(self, *args, **kwargs):
        pass

    def precomp_grad_x(self, *args, **kwargs):
        pass

    def precomp_Vandermonde_grad_x(self, *args, **kwargs):
        pass

    def precomp_hess_x(self, *args, **kwargs):
        pass

    def precomp_Vandermonde_hess_x(self, *args, **kwargs):
        pass

    def precomp_partial_xd(self, *args, **kwargs):
        pass

    def precomp_Vandermonde_partial_xd(self, *args, **kwargs):
        pass

    def precomp_grad_x_partial_xd(self, *args, **kwargs):
        pass

    def precomp_Vandermonde_grad_x_partial_xd(self, *args, **kwargs):
        pass

    def precomp_hess_x_partial_xd(self, *args, **kwargs):
        pass

    def precomp_Vandermonde_hess_x_partial_xd(self, *args, **kwargs):
        pass

    def precomp_partial2_xd(self, *args, **kwargs):
        pass

    def precomp_Vandermonde_partial2_xd(self, *args, **kwargs):
        pass

    def evaluate(self, x, *args, **kwargs):
        return x

    def grad_x(self, x, *args, **kwargs):
        return np.ones((x.shape[0],1,1))

    def hess_x(self, x, *args, **kwargs):
        return np.zeros((x.shape[0],1,1,1))

    def action_hess_x(self, x, dx, *args, **kwargs):
        return np.zeros((x.shape[0],1,1))

    def partial_xd(self, x, *args, **kwargs):
        return self.grad_x(x, *args, **kwargs)[:,:,0]

    def grad_x_partial_xd(self, x, *args, **kwargs):
        return self.hess_x(x, *args, **kwargs)[:,:,:,0]

    def hess_x_partial_xd(self, x, *args, **kwargs):
        return self.hess_x(x, *args, **kwargs)

    def grad_a(self, x, *args, **kwargs):
        return np.zeros((x.shape[0],1,0))

    def hess_a(self, x, *args, **kwargs):
        return np.zeros((x.shape[0],1,0,0))

    def action_hess_a(self, x, *args, **kwargs):
        return np.zeros((x.shape[0],1,0))

    def grad_a_partial_xd(self, x, *args, **kwargs):
        return np.zeros((x.shape[0],1,0))

    def hess_a_partial_xd(self, x, *args, **kwargs):
        return np.zeros((x.shape[0],1,0,0))
