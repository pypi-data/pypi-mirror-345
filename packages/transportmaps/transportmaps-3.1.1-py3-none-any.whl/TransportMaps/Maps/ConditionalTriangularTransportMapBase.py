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

from .TriangularComponentwiseTransportMapBase import TriangularComponentwiseTransportMap

from ..Misc import \
    required_kwargs,\
    counted, \
    cached

from .SlicedTransportMapBase import SlicedTransportMap

__all__ = [
    'ConditionalTriangularTransportMap'
]

nax = np.newaxis


class ConditionalTriangularTransportMap(SlicedTransportMap):
    r""" Takes the transport map :math:`T({\bf x})` and construct the transport map :math:`S_{{\bf y}}({\bf x}) := [T({\bf y}, {\bf x})]_{d_y:}`.
    """
    @required_kwargs('base_map', 'y')
    def __init__(self, **kwargs):
        r"""
        Args:
          base_map (:class:`TriangularComponentwiseTransportMap`): map :math:`T`
          y (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): values of :math:`{\bf y}`
        """
        base_map = kwargs['base_map']
        y = kwargs['y']
        if not isinstance(base_map, TriangularComponentwiseTransportMap):
            raise ValueError(
                "The base_map must be a TriangularComponentwiseTransportMap"
            )
        dy = y.shape[0]
        kwargs['idxs_fix'] = list(range(dy))
        kwargs['idxs_out'] = list(range(dy, base_map.dim))
        super(ConditionalTriangularTransportMap, self).__init__(**kwargs)

    @cached()
    @counted
    def log_det_grad_x(self, x, *args, **kwargs):
        xin = self._xin(x)
        xout = np.zeros(x.shape[0])
        # FIXME: sliced_approx_list and sliced_active_vars seem not to be defined anywhere
        for i,(a, avar) in enumerate(zip(
                self.sliced_approx_list, self.sliced_active_vars)):
            xout += a.partial_xd( xin[:,avar] )
        return xout

    @cached()
    @counted
    def grad_x_log_det_grad_x(self, x, *args, **kwargs):
        xin = self._xin(x)
        xout = np.zeros(x.shape)
        leny = len(self.idxs_fix)
        for i,(a, avar) in enumerate(zip(
                self.sliced_approx_list, self.sliced_active_vars)):
            avarout = [ v for v in avar if v >= leny ]
            xout[:,avarout] += a.grad_x_partial_xd( xin[:,avar] )[:,leny:] / \
                               a.partial_xd( xin[:,avar] )[:, nax]
        return xout

    @cached()
    @counted
    def hess_x_log_det_grad_x(self, x, *args, **kwargs):
        xin = self._xin(x)
        xout = np.zeros((x.shape[0],self.dim,self.dim))
        leny = len(self.idxs_fix)
        for i,(a, avar) in enumerate(zip(
                self.sliced_approx_list, self.sliced_active_vars)):
            avarout = [ v for v in avar if v >= leny ]
            # 2d numpy advanced indexing
            nvar = len(avarout)
            rr,cc = np.meshgrid(avarout,avarout)
            rr = list( rr.flatten() )
            cc = list( cc.flatten() )
            idxs = (slice(None), rr, cc)
            # Evaluate
            dxk = a.partial_xd(x[:,avar], p)
            xout[idxs] += (a.hess_x_partial_xd( xin[:,avar] )[:,leny:,leny:] / \
                           dxk[:,nax,nax]).reshape((x.shape[0], nvar**2))
            dxdxkT = a.grad_x_partial_xd(x[:,avar], p)[:,leny:]
            dxdxkT2 = dxdxkT[:,:,nax] * dxdxkT[:,nax,:]
            xout[idxs] -= (dxdxkT2 / (dxk**2.)[:,nax,nax]).reshape((x.shape[0],nvar**2))
        return xout

    @counted
    def inverse(self, x, *args, **kwargs):
        xin = self._xin(x)
        xout = np.zeros(xin.shape)
        skip_dim = len(self.idxs_fix)
        xout[:,:skip_dim] = xin[:,:skip_dim]
        for i in range(x.shape[0]):
            for k, (a,avar) in enumerate(zip(
                    self.sliced_approx_list, self.sliced_active_vars)):
                xout[i,skip_dim+k] = a.inverse(xout[i,avar[:-1]], xin[i,skip_dim+k])
        return xout[:,skip_dim:]

    @counted
    def log_det_grad_x_inverse(self, x, precomp=None, idxs_slice=slice(None), **kwargs):
        try:
            xinv = precomp['xinv']
        except (TypeError, KeyError):
            xinv = self.inverse(x, precomp)
        return - self.log_det_grad_x( xinv )