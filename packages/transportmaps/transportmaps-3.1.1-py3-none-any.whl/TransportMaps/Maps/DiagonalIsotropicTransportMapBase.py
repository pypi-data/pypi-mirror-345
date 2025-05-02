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
    counted

from .DiagonalComponentwiseTransportMapBase import DiagonalComponentwiseTransportMap

__all__ = [
    'DiagonalIsotropicTransportMap'
]

nax = np.newaxis


class DiagonalIsotropicTransportMap(DiagonalComponentwiseTransportMap):
    r""" Diagonal transport map :math:`T({\bf x})=[T_1,T_2,\ldots,T_{d_x}]^\top` where :math:`T_i(x_{i})=F(x_i):\mathbb{R}\rightarrow\mathbb{R}`.
    """
    @required_kwargs('dim', 'approx')
    def __init__(self, **kwargs):
        r"""
        Kwargs:
          dim (int): dimension :math:`d`
          approx (:class:`MonotoneFunctional<TransportMaps.Maps.Functionals.MonotoneFunctional>`):
            monotone functional :math:`F`
        """
        approx = kwargs['approx']
        dim    = kwargs['dim']
        kwargs['approx_list'] = [approx] * dim
        
        self.approx = approx
        super(DiagonalIsotropicTransportMap, self).__init__(**kwargs)

    @counted
    def evaluate(self, x, 
                 *args, **kwargs
             ):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        xout = self.approx.evaluate(
            x.reshape(x.shape[0]*x.shape[1],1)
        ).reshape(x.shape)
        return xout

    @counted
    def grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        xout = np.zeros( (x.shape[0], self.dim, self.dim) )
        gx = self.approx.grad_x(
            x.reshape(x.shape[0]*x.shape[1],1),
            # *args, **kwargs
        ).reshape(x.shape)
        for i in range(self.dim):
            xout[:,i,i] = gx[:,i]
        return xout

    @counted
    def hess_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        xout = np.zeros( (x.shape[0], self.dim, self.dim, self.dim) )
        hx = self.approx.hess_x(
            x.reshape(x.shape[0]*x.shape[1],1),
            # *args, **kwargs
        ).reshape(x.shape)
        for i in range(self.dim):
            xout[:,i,i,i] = hx[:,i]
        return xout

    @counted
    def log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        pxd = self.approx.partial_xd(
            x.reshape(x.shape[0]*x.shape[1],1),
            # *args, **kwargs
        ).reshape(x.shape)
        out = np.sum(np.log(pxd), axis=1)
        return out

    @counted
    def grad_x_log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        pxd = self.approx.partial_xd(
            x.reshape(x.shape[0]*x.shape[1],1),
            # *args, **kwargs
        ).reshape(x.shape)
        gxpxd = self.approx.grad_x_partial_xd(
            x.reshape(x.shape[0]*x.shape[1],1),
            # *args, **kwargs
        ).reshape(x.shape)
        out = gxpxd/pxd
        return out

    @counted
    def hess_x_log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        pxd = self.approx.partial_xd(
            x.reshape(x.shape[0]*x.shape[1],1),
            # *args, **kwargs
        ).reshape(x.shape)
        gxpxd = self.approx.grad_x_partial_xd(
            x.reshape(x.shape[0]*x.shape[1],1),
            # *args, **kwargs
        ).reshape(x.shape)
        hxpxd = self.approx.hess_x_partial_xd(
            x.reshape(x.shape[0]*x.shape[1],1),
            # *args, **kwargs
        ).reshape(x.shape)
        out = np.zeros((x.shape[0], self.dim, self.dim))
        for i in range(self.dim):
            out[:,i,i] = hxpxd[:,i] / pxd[:,i] - gxpxd[:,i]**2 / pxd[:,i]**2
        return out
