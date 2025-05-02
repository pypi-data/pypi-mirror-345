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
    cached, counted, get_sub_cache
from .ListStackedParametricTransportMapBase import ListStackedParametricTransportMap
from .TriangularListStackedTransportMapBase import TriangularListStackedTransportMap

__all__ = [
    'TriangularListStackedParametricTransportMap'
]


class TriangularListStackedParametricTransportMap(
        TriangularListStackedTransportMap, ListStackedParametricTransportMap):
    @cached([('map_list',"n_maps")])
    @counted
    def grad_a_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        out = np.zeros((x.shape[0], self.n_coeffs))
        for tm, avars, tm_cache in zip(self.map_list, self.active_vars, map_list_cache):
            out[:,avars] = tm.grad_a_log_det_grad_x(
                x[:,avars], idxs_slice=idxs_slice, cache=tm_cache)
        return out

    @cached([('map_list',"n_maps")])
    @counted
    def hess_a_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        out = np.zeros((x.shape[0], self.n_coeffs, self.n_coeffs))
        for tm, avars, tm_cache in zip(self.map_list, self.active_vars, map_list_cache):
            # 2d numpy advanced indexing
            nvar = len(avars)
            rr, cc = np.meshgrid(avars,avars)
            rr = list( rr.flatten() )
            cc = list( cc.flatten() )
            idxs = (slice(None), rr, cc)
            # Evaluate
            out[idxs] = tm.hess_a_log_det_grad_x(
                x[:,avars], idxs_slice=idxs_slice, cache=tm_cache)
        return out

    @cached([('map_list', "n_maps")])
    @counted
    def action_hess_a_log_det_grad_x(self, x, da, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        out = np.zeros((x.shape[0], self.n_coeffs))
        start = 0
        for tm, avars, tm_cache in zip(self.map_list, self.active_vars, map_list_cache):
            stop = start + tm.n_coeffs
            # Evaluate
            out[:,avars] = tm.hess_a_log_det_grad_x(
                x[:,avars], da[start:stop], idxs_slice=idxs_slice, cache=tm_cache)
            start = stop
        return out
