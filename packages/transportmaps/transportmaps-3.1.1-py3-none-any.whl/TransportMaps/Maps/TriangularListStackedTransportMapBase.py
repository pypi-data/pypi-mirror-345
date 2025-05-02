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
from .ListStackedTransportMapBase import ListStackedTransportMap

__all__ = [
    'TriangularListStackedTransportMap'
]


class TriangularListStackedTransportMap(ListStackedTransportMap):
    @cached([('map_list',"n_maps")], False)
    @counted
    def log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        ldet = np.zeros(x.shape[0])
        for tm, avars, tm_cache in zip(self.map_list, self.active_vars, map_list_cache):
            ldet += tm.log_det_grad_x(x[:,avars], idxs_slice=idxs_slice, cache=tm_cache)
        return ldet

    @cached([('map_list',"n_maps")], False)
    @counted
    def grad_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        gx_ldet = np.zeros((x.shape[0],self.dim))
        for tm, avars, tm_cache in zip(self.map_list, self.active_vars, map_list_cache):
            gx_ldet[:,avars] += tm.grad_x_log_det_grad_x(x[:,avars], idxs_slice=idxs_slice, cache=tm_cache)
        return gx_ldet

    @cached([('map_list',"n_maps")], False)
    @counted
    def hess_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        hx_ldet = np.zeros((x.shape[0],self.dim,self.dim))
        for tm, avars, tm_cache in zip(self.map_list, self.active_vars, map_list_cache):
            # 2d numpy advanced indexing
            nvar = len(avars)
            rr,cc = np.meshgrid(avars, avars)
            rr = list( rr.flatten() )
            cc = list( cc.flatten() )
            idxs = (slice(None), rr, cc)
            # Evaluate
            hx_ldet[idxs] += tm.hess_x_log_det_grad_x(x[:,avars], idxs_slice=idxs_slice, cache=tm_cache)
        return hx_ldet

    @cached([('map_list',"n_maps")], False)
    @counted
    def action_hess_x_log_det_grad_x(self, x, dx, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        ahx_ldet = np.zeros((x.shape[0],self.dim))
        for tm, avars, tm_cache in zip(self.map_list, self.active_vars, map_list_cache):
            # Evaluate
            ahx_ldet[:,avars] += tm.action_hess_x_log_det_grad_x(
                x[:,avars], dx[:,avars], idxs_slice=idxs_slice, cache=tm_cache)
        return ahx_ldet

    @counted
    def log_det_grad_x_inverse(self, x, dx, precomp=None, idxs_slice=slice(None), cache=None):
        try:
            xinv = precomp['xinv']
        except (TypeError, KeyError):
            xinv = self.inverse(x, precomp)
        return - self.log_det_grad_x( xinv )
