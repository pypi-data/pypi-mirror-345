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
    counted, cached, get_sub_cache

from .TransportMapBase import TransportMap

__all__ = [
    'IdentityEmbeddedTransportMap',
]


class IdentityEmbeddedTransportMap(TransportMap):
    @required_kwargs('tm', 'idxs', 'dim')
    def __init__(self, **kwargs):
        tm = kwargs.pop('tm')
        idxs = kwargs.pop('idxs')
        if not isinstance(tm, TransportMap):
            raise AttributeError("tm must be a TransportMap.")
        if len(idxs) != tm.dim:
            raise ValueError(
                "The dimension of tm must match the number of idxs.")
        if kwargs['dim'] <= max(idxs):
            raise ValueError(
                "The dimension of the new map must be > than the " + \
                "maximum idxs.")
        self.tm = tm
        self.idxs = idxs
        super(IdentityEmbeddedTransportMap, self).__init__(
            **kwargs
        )

    @cached([('tm', None)])
    @counted
    def evaluate(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        tm_cache = get_sub_cache(cache, ('tm', None))
        out = x.copy()
        out[:,self.idxs] = self.tm.evaluate(
            x[:,self.idxs],  precomp, idxs_slice, cache=tm_cache)
        return out

    @counted
    def inverse(self, x, precomp=None, idxs_slice=slice(None)):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = x.copy()
        out[:,self.idxs] = self.tm.inverse(
            x[:,self.idxs],  precomp, idxs_slice)
        return out

    @cached([('tm', None)],False)
    @counted
    def grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        tm_cache = get_sub_cache(cache, ('tm', None))
        m = x.shape[0]
        out = np.zeros( (m, self.dim, self.dim) )
        out[:,range(self.dim),range(self.dim)] = 1.
        out[np.ix_(range(m),self.idxs, self.idxs)] = self.tm.grad_x(
            x[:,self.idxs],  precomp, idxs_slice, cache=tm_cache)
        return out

    @cached([('tm', None)],False)
    @counted
    def action_grad_x(self, x, dx, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        tm_cache = get_sub_cache(cache, ('tm', None))
        gx_tm = self.tm.grad_x(
            x[:,self.idxs],  precomp, idxs_slice, cache=tm_cache)
        out = dx.copy()
        idxs = tuple( [slice(None)]*(dx.ndim-1) + [self.idxs] )
        out[idxs] = np.einsum('...jk,...k->...j', gx_tm, dx[idxs])
        return out

    @cached([('tm', None)],False)
    @counted
    def action_adjoint_grad_x(self, x, dx, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        tm_cache = get_sub_cache(cache, ('tm', None))
        gx_tm = self.tm.grad_x(
            x[:,self.idxs],  precomp, idxs_slice, cache=tm_cache)
        out = dx.copy()
        idxs = tuple( [slice(None)]*(dx.ndim-1) + [self.idxs] )
        if dx.ndim == 2:
            expr = '...j,...jk->...k'
        else:
            expr = '...ij,...jk->...ik'
        out[idxs] = np.einsum(expr, dx[idxs], gx_tm)
        return out

    @cached([('tm', None)],False)
    @counted
    def tuple_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        ev = self.evaluate(x, precomp=precomp, idxs_slice=idxs_slice, cache=cache)
        gx = self.grad_x(x, precomp=precomp, idxs_slice=idxs_slice, cache=cache)
        return ev, gx

    @cached([('tm', None)],False)
    @counted
    def action_tuple_grad_x(self, x, dx, precomp=None, idxs_slice=slice(None), cache=None):
        ev = self.evaluate(x, precomp=precomp, idxs_slice=idxs_slice, cache=cache)
        agx = self.action_grad_x(x, dx, precomp=precomp, idxs_slice=idxs_slice, cache=cache)
        return ev, agx

    @cached([('tm', None)],False)
    @counted
    def hess_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        tm_cache = get_sub_cache(cache, ('tm', None))
        m = x.shape[0]
        out = np.zeros( (m, self.dim, self.dim, self.dim) )
        out[np.ix_(range(m),self.idxs, self.idxs,self.idxs)] = \
            self.tm.hess_x(
                x[:,self.idxs],  precomp, idxs_slice, cache=tm_cache)
        return out

    @cached([('tm',None)])
    @counted
    def log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        tm_cache = get_sub_cache(cache, ('tm', None))
        return self.tm.log_det_grad_x(x[:,self.idxs], precomp=precomp,
                                      idxs_slice=idxs_slice, cache=tm_cache)

    @cached([('tm',None)])
    @counted
    def grad_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        tm_cache = get_sub_cache(cache, ('tm', None))
        out = np.zeros((x.shape[0], self.dim))
        out[:,self.idxs] = self.tm.grad_x_log_det_grad_x(
            x[:,self.idxs], precomp=precomp,
            idxs_slice=idxs_slice, cache=tm_cache)
        return out

    @cached([('tm',None)],False)
    @counted
    def hess_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        tm_cache = get_sub_cache(cache, ('tm', None))
        m = x.shape[0]
        out = np.zeros((m, self.dim, self.dim))
        out[np.ix_(range(m),self.idxs, self.idxs)] = \
            self.tm.hess_x_log_det_grad_x(
                x[:,self.idxs], precomp=precomp,
                idxs_slice=idxs_slice, cache=tm_cache)
        return out

    @counted
    def log_det_grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        return self.tm.log_det_grad_x_inverse(x[:,self.idxs], *args, **kwargs)
