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
    counted, cached, cached_tuple, get_sub_cache
from .MapBase import Map

__all__ = [
    'ListStackedMap',
]

nax = np.newaxis


class ListStackedMap(Map):
    r""" Defines the map :math:`T` obtained by stacking :math:`T_1, T_2, \ldots`.

    .. math::

       T({\bf x}) = \left[
       \begin{array}{c}
       T_1({\bf x}_{0:d_1}) \\
       T_2({\bf x}_{0:d_2}) \\
       \vdots
       \end{array}
       \right]
    """
    @required_kwargs('map_list', 'active_vars')
    def __init__(self, **kwargs):
        r"""
        Args:
          map_list (:class:`list` of :class:`Map`): list of transport maps :math:`T_i`
          active_vars (:class:`list` of :class:`list` of :class:`int`): active variables for each map
        """
        map_list = kwargs['map_list']
        active_vars = kwargs['active_vars']
        
        if active_vars is None:
            dim_in = max( [ tm.dim_in for tm in map_list ] )
            self.active_vars = [ list(range(tm.dim_in)) for tm in map_list ]
        else:
            dim_in = max( [ max(avars) for avars in active_vars ] ) + 1
            self.active_vars = active_vars
        dim_out = sum( [tm.dim_out for tm in map_list] )
        self.map_list = map_list

        kwargs['dim_in'] = dim_in
        kwargs['dim_out'] = dim_out
        super(ListStackedMap, self).__init__(**kwargs)

    @property
    def map_list(self):
        try:
            return self._map_list
        except AttributeError:
            # Backward compatibility v < 3.0
            return self.tm_list

    @map_list.setter
    def map_list(self, map_list):
        self._map_list = map_list

    @property
    def active_vars(self):
        return self._active_vars

    @active_vars.setter
    def active_vars(self, avars):
        self._active_vars = avars
    
    def get_ncalls_tree(self, indent=""):
        out = Map.get_ncalls_tree(self, indent)
        for i, tm in enumerate(self.map_list):
            out += tm.get_ncalls_tree(indent + " T%d - " % i)
        return out

    def get_nevals_tree(self, indent=""):
        out = Map.get_nevals_tree(self, indent)
        for i, tm in enumerate(self.map_list):
            out += tm.get_nevals_tree(indent + " T%d - " % i)
        return out

    def get_teval_tree(self, indent=""):
        out = Map.get_teval_tree(self, indent)
        for i, tm in enumerate(self.map_list):
            out += tm.get_teval_tree(indent + " T%d - " % i)
        return out

    def update_ncalls_tree(self, obj):
        super(ListStackedMap, self).update_ncalls_tree(obj)
        for i, (tm, obj_tm) in enumerate(zip(self.map_list, obj.map_list)):
            tm.update_ncalls_tree(obj_tm)

    def update_nevals_tree(self, obj):
        super(ListStackedMap, self).update_nevals_tree(obj)
        for i, (tm, obj_tm) in enumerate(zip(self.map_list, obj.map_list)):
            tm.update_nevals_tree(obj_tm)

    def update_teval_tree(self, obj):
        super(ListStackedMap, self).update_teval_tree(obj)
        for i, (tm, obj_tm) in enumerate(zip(self.map_list, obj.map_list)):
            tm.update_teval_tree(obj_tm)
        
    def reset_counters(self):
        super(ListStackedMap, self).reset_counters()
        for tm in self.map_list:
            tm.reset_counters()
        
    @property
    def n_maps(self):
        return len(self.map_list)

    @cached([('map_list',"n_maps")], False)
    @counted
    def evaluate(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        out = np.zeros((x.shape[0], self.dim_out))
        start = 0
        for tm, avars, tm_cache in zip(self.map_list, self.active_vars, map_list_cache):
            stop = start + tm.dim_out
            out[:,start:stop] = tm.evaluate(
                x[:,avars], idxs_slice=idxs_slice, cache=tm_cache)
            start = stop
        return out

    @cached([('map_list',"n_maps")], False)
    @counted
    def grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        out = np.zeros((x.shape[0], self.dim_out, self.dim_in))
        start = 0
        for tm, avars, tm_cache in zip(self.map_list, self.active_vars, map_list_cache):
            stop = start + tm.dim_out
            out[:,start:stop,avars] = tm.grad_x(
                x[:,avars], idxs_slice=idxs_slice, cache=tm_cache)
            start = stop
        return out

    @cached_tuple(['evaluate','grad_x'],[('map_list',"n_maps")], False)
    @counted
    def tuple_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        ev = self.evaluate(x, *args, **kwargs)
        gx = self.grad_x(x, *args, **kwargs)
        return ev, gx

    @cached([('map_list',"n_maps")],False)
    @counted
    def hess_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        out = np.zeros((x.shape[0], self.dim_out, self.dim_in, self.dim_in))
        start = 0
        for tm, avars, tm_cache in zip(self.map_list, self.active_vars, map_list_cache):
            stop = start + tm.dim_out
            # 2d numpy advanced indexing
            nvar = len(avars)
            ll, rr, cc = np.meshgrid(range(start,stop),avars,avars)
            ll = list( ll.flatten() )
            rr = list( rr.flatten() )
            cc = list( cc.flatten() )
            idxs = (slice(None), ll, rr, cc)
            # Evaluate
            hx = tm.hess_x(x[:,avars], idxs_slice=idxs_slice, cache=tm_cache)
            if hx.ndim == 3:
                out[idxs] = hx.reshape((stop-start)*nvar**2)[nax,:]
            else:
                out[idxs] = hx.reshape(
                    (x.shape[0], (stop-start)*nvar**2) )
            start = stop
        return out

    @cached([('map_list',"n_maps")],False)
    @counted
    def action_hess_x(self, x, dx, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        out = np.zeros((x.shape[0], self.dim_out, self.dim_in))
        start = 0
        for tm, avars, tm_cache in zip(self.map_list, self.active_vars, map_list_cache):
            stop = start + tm.dim_out
            # 2d numpy advanced indexing
            nvar = len(avars)
            ll, rr = np.meshgrid(range(start,stop),avars)
            ll = list( ll.flatten() )
            rr = list( rr.flatten() )
            idxs = (slice(None), ll, rr)
            # Evaluate
            ahx = tm.action_hess_x(x[:,avars], dx[:,avars], idxs_slice=idxs_slice, cache=tm_cache)
            out[:,start:stop,avars] = ahx
            start = stop
        return out
