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

from ..Misc import \
    required_kwargs, \
    counted, cached, get_sub_cache

from .ParametricTransportMapBase import  ParametricTransportMap
from .IdentityEmbeddedTransportMapBase import IdentityEmbeddedTransportMap

__all__ = [
    'IdentityEmbeddedParametricTransportMap'
]


class IdentityEmbeddedParametricTransportMap(
        IdentityEmbeddedTransportMap,
        ParametricTransportMap
):
    @required_kwargs('tm', 'idxs', 'dim')
    def __init__(self, **kwargs):
        if not isinstance(kwargs['tm'], ParametricTransportMap):
            raise AttributeError("tm must be a ParametricTransportMap")
        super(IdentityEmbeddedParametricTransportMap, self).__init__(**kwargs)

    @property
    def n_coeffs(self):
        return self.tm.n_coeffs

    @property
    def coeffs(self):
        return self.tm.coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        self.tm.coeffs = coeffs

    def get_identity_coeffs(self):
        return self.tm.get_identity_coeffs()

    @cached([('tm', None)],False)
    @counted
    def grad_a(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        tm_cache = get_sub_cache(cache, ('tm', None))
        return self.tm.grad_a(
            x[:,self.idxs], precomp=precomp, idxs_slice=idxs_slice, cache=tm_cache)

    @cached([('tm', None)],False)
    @counted
    def tuple_grad_a(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        tm_cache = get_sub_cache(cache, ('tm', None))
        return self.tm.tuple_grad_a(
            x[:,self.idxs], precomp=precomp, idxs_slice=idxs_slice, cache=tm_cache)

    @cached([('tm', None)],False)
    @counted
    def hess_a(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        tm_cache = get_sub_cache(cache, ('tm', None))
        return self.tm.hess_a(
            x[:,self.idxs], precomp=precomp, idxs_slice=idxs_slice, cache=tm_cache)

    @cached([('tm', None)],False)
    @counted
    def action_hess_a(self, x, da, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        tm_cache = get_sub_cache(cache, ('tm', None))
        return self.tm.action_hess_a(
            x[:,self.idxs], da, precomp=precomp, idxs_slice=idxs_slice, cache=tm_cache)

    @cached([('tm', None)],False)
    @counted
    def grad_a_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        tm_cache = get_sub_cache(cache, ('tm', None))
        return self.tm.grad_a_log_det_grad_x(
            x[:,self.idxs], precomp=precomp, idxs_slice=idxs_slice, cache=tm_cache)

    @cached([('tm', None)],False)
    @counted
    def hess_a_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        tm_cache = get_sub_cache(cache, ('tm', None))
        return self.tm.hess_a_log_det_grad_x(
            x[:,self.idxs], precomp=precomp, idxs_slice=idxs_slice, cache=tm_cache)

    @cached([('tm', None)],False)
    @counted
    def action_hess_a_log_det_grad_x(self, x, da, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        tm_cache = get_sub_cache(cache, ('tm', None))
        return self.tm.action_hess_a_log_det_grad_x(
            x[:,self.idxs], da, precomp=precomp, idxs_slice=idxs_slice, cache=tm_cache)

    def precomp_minimize_kl_divergence(self, *args, **kwargs):
        self.tm.precomp_minimize_kl_divergence(*args, **kwargs)

    def allocate_cache_minimize_kl_divergence(self, *args, **kwargs):
        return self.tm.allocate_cache_minimize_kl_divergence(*args, **kwargs)

    def reset_cache_minimize_kl_divergence(self, *args, **kwargs):
        self.tm.reset_cache_minimize_kl_divergence(*args, **kwargs)

    def get_default_init_values_minimize_kl_divergence(self):
        return self.tm.get_default_init_values_minimize_kl_divergence()