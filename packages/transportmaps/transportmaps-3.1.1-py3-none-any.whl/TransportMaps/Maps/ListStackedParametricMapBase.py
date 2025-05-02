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

from TransportMaps.Misc import \
    cached, counted, get_sub_cache
from .ParametricMapBase import ParametricMap
from .ListStackedMapBase import ListStackedMap

__all__ = [
    'ListStackedParametricMap'
]


class ListStackedParametricMap(ListStackedMap, ParametricMap):
    @property
    def n_coeffs(self):
        return sum( tm.n_coeffs for tm in self.map_list )

    @property
    def coeffs(self):
        return np.hstack( tm.coeffs for tm in self.map_list )

    @coeffs.setter
    def coeffs(self, coeffs):
        if len(coeffs) != self.n_coeffs:
            raise ValueError("Wrong number of coefficients provided")
        start = 0
        for tm in self.map_list:
            stop = start + tm.n_coeffs
            tm.coeffs = coeffs[start:stop]
            start = stop
    
    @cached([('map_list',"n_maps")], False)
    @counted
    def grad_a(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        ga = []
        for tm, avars, tm_cache in zip(self.map_list, self.active_vars, map_list_cache):
            ga += tm.grad_a(x[:,avars], idxs_slice=idxs_slice, cache=tm_cache)
        return ga

    @cached([('map_list',"n_maps")], False)
    @counted
    def hess_a(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        ha = []
        for tm, avars, tm_cache in zip(self.map_list, self.active_vars, map_list_cache):
            ha += tm.hess_a(x[:,avars], idxs_slice=idxs_slice, cache=tm_cache)
        return ha

    @cached([('map_list',"n_maps")], False)
    @counted
    def action_hess_a(self, x, da, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        ha = []
        start = 0
        for tm, avars, tm_cache in zip(self.map_list, self.active_vars, map_list_cache):
            stop = start + tm.n_coeffs
            ha += tm.action_hess_a(
                x[:,avars], da[start:stop],
                idxs_slice=idxs_slice, cache=tm_cache)
            start = stop
        return ha
