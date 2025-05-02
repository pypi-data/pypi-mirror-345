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
    'ListCompositeMap',
    'CompositeMap'
]


class ListCompositeMap(Map):
    r""" Construct the composite map :math:`T_1 \circ T_2 \circ \cdots \circ T_n`
    """
    @required_kwargs('map_list')
    def __init__(self, **kwargs):
        r"""
        Args:
          map_list (list): list of maps :math:`[T_1,\ldots,T_n]`
        """
        self.map_list = kwargs['map_list']
        kwargs['dim_in'] = self.map_list[-1].dim_in
        kwargs['dim_out'] = self.map_list[0].dim_out
        super(ListCompositeMap, self).__init__(**kwargs)

    @property
    def map_list(self):
        try:
            return self._map_list
        except AttributeError:
            # Backward compatibility v < 3.0
            return self.tm_list

    @map_list.setter
    def map_list(self, map_list):
        if len(map_list)==0:
            raise ValueError("There should be at least a map in the list")
        dim_in = map_list[-1].dim_in
        dim_out_old = map_list[-1].dim_out
        for tm in reversed(map_list[:-1]):
            if tm.dim_in != dim_out_old:
                raise ValueError("The maps must have consistent dimensions!")
            dim_out_old = tm.dim_out
        self._map_list = map_list

    @property
    def dim_in(self):
        return self.map_list[-1].dim_in

    @property
    def dim_out(self):
        return self.map_list[0].dim_out
            
    def append(self, mp):
        r""" Append one map to the composition.
        """
        if self.map_list[-1].dim_in != mp.dim_out:
            raise ValueError(
                "The output dimension of the new map must " + \
                "match the input dimension of the last map in the composition."
            )
        self._map_list.append( mp )
        
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
        super(ListCompositeMap, self).update_ncalls_tree(obj)
        for i, (tm, obj_tm) in enumerate(zip(self.map_list, obj.map_list)):
            tm.update_ncalls_tree(obj_tm)

    def update_nevals_tree(self, obj):
        super(ListCompositeMap, self).update_nevals_tree(obj)
        for i, (tm, obj_tm) in enumerate(zip(self.map_list, obj.map_list)):
            tm.update_nevals_tree(obj_tm)

    def update_teval_tree(self, obj):
        super(ListCompositeMap, self).update_teval_tree(obj)
        for i, (tm, obj_tm) in enumerate(zip(self.map_list, obj.map_list)):
            tm.update_teval_tree(obj_tm)
        
    def reset_counters(self):
        super(ListCompositeMap, self).reset_counters()
        for tm in self.map_list:
            tm.reset_counters()
        
    @property
    def n_maps(self):
        return len(self.map_list)

    @cached([('map_list',"n_maps")], False)
    @counted
    def evaluate(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate the transport map at the points :math:`{\bf x} \in \mathbb{R}^{m \times d}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- transformed points

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        Xcp = x.copy()
        for tm, tm_cache in zip(reversed(self.map_list),reversed(map_list_cache)):
            Xcp = tm.evaluate(Xcp, idxs_slice=idxs_slice, cache=tm_cache)

        return Xcp

    @cached([('map_list',"n_maps")], False)
    @counted
    def grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute :math:`\nabla_{\bf x} T({\bf x})`.

        Apply chain rule.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           gradient matrices for every evaluation point.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))

        if self.dim_in > self.dim_out:
            # Expand gradient left to right (instead of right to left)
            ev_list = [x]
            for i in range(len(self.map_list)-1,0,-1):
                ev_list.insert(
                    0, self.map_list[i].evaluate(
                        ev_list[0], idxs_slice=idxs_slice, cache=map_list_cache[i]
                    )
                )
            ev_list.insert(0, None) # We don't need the last one if we are not evaluating
            gx_next = self.map_list[0].grad_x(
                ev_list[1], idxs_slice=idxs_slice, cache=map_list_cache[0])
            for i in range(1, len(self.map_list)):
                ev = ev_list[i+1]
                mp = self.map_list[i]
                mp_cache = map_list_cache[i]
                try:
                    gx_next = mp.action_adjoint_grad_x(
                        ev, gx_next, idxs_slice=idxs_slice, cache=mp_cache
                    )
                except NotImplementedError:
                    gx = mp.grad_x(ev, idxs_slice=idxs_slice, cache=mp_cache)
                    gx_next = np.einsum('...ji,...ik->...jk', gx_next, gx)
        else:
            # Expand gradient right to left (slower if number of input > number of outputs)
            gx_next = self.map_list[-1].grad_x(
                x, idxs_slice=idxs_slice, cache=map_list_cache[-1])
            if len(self.map_list) > 1:
                ev_next = self.map_list[-1].evaluate(
                    x, idxs_slice=idxs_slice, cache=map_list_cache[-1])
            for i in range(len(self.map_list)-2,-1,-1):
                tm = self.map_list[i]
                tm_cache = map_list_cache[i]
                try:
                    gx_next = tm.action_grad_x(ev_next, gx_next, idxs_slice=idxs_slice, cache=tm_cache)
                except NotImplementedError:
                    gx = tm.grad_x(ev_next, idxs_slice=idxs_slice, cache=tm_cache)
                    gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
                if i > 0:
                    # Update ev_next
                    ev_next = tm.evaluate( ev_next, idxs_slice=idxs_slice, cache=tm_cache )
        return gx_next

    @cached([('map_list',"n_maps")], False)
    @counted
    def action_adjoint_grad_x(self, x, dx, precomp=None, idxs_slice=slice(None), cache=None):
        r""" [Abstract] Evaluate the action of the gradient :math:`\langle\delta{\bf x},\nabla_{\bf x}T({\bf x})\rangle` at the points :math:`{\bf x} \in \mathbb{R}^{m \times d_x}` on the vector :math:`\delta{\bf x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x,...`]): vector :math:`\delta{\bf x}`
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y,...`]) -- transformed points
        """
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        # Expand gradient left to right
        ev_list = [x]
        for i in range(len(self.map_list)-1,0,-1):
            if i > 0:
                ev_list.insert(
                    0, self.map_list[i].evaluate(
                        ev_list[0], idxs_slice=idxs_slice, cache=map_list_cache[i]
                    )
                )
        ev_list.insert(0, None) # We don't need the last one if we are not evaluating
        try:
            gx_next = self.map_list[0].action_adjoint_grad_x(
                ev_list[1], dx, idxs_slice=idxs_slice, cache=map_list_cache[0])
        except NotImplementedError:
            gx = self.map_list[0].grad_x(
                ev_list[1], idxs_slice=idxs_slice, cache=map_list_cache[0])
            gx_next  = np.einsum('...i,...ij->...j', dx, gx)
        for i in range(1, len(self.map_list)):
            ev = ev_list[i+1]
            mp = self.map_list[i]
            mp_cache = map_list_cache[i]
            try:
                gx_next = mp.action_adjoint_grad_x(
                    ev, gx_next, idxs_slice=idxs_slice, cache=mp_cache
                )
            except NotImplementedError:
                gx = mp.grad_x(ev, idxs_slice=idxs_slice, cache=mp_cache)
                gx_next = np.einsum('...i,...ik->...k', gx_next, gx)
        return gx_next
    
    @cached_tuple(['evaluate','grad_x'],[('map_list',"n_maps")], False)
    @counted
    def tuple_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate the function and gradient.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`tuple`) -- function and gradient evaluation
        """
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        ev_next, gx_next = self.map_list[-1].tuple_grad_x(
            x, idxs_slice=idxs_slice, cache=map_list_cache[-1])
        for i in range(len(self.map_list)-2,-1,-1):
            tm = self.map_list[i]
            tm_cache = map_list_cache[i]
            try:
                ev_next, gx_next = tm.action_tuple_grad_x(
                    ev_next, gx_next, idxs_slice=idxs_slice, cache=tm_cache)
            except NotImplementedError:
                ev_next, gx = tm.tuple_grad_x(ev_next, idxs_slice=idxs_slice, cache=tm_cache)
                gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
        return ev_next, gx_next

    @cached([('map_list',"n_maps")],False)
    @counted
    def hess_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute :math:`\nabla^2_{\bf x} T({\bf x})`.

        Apply chain rule.
        
        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d,d`]) --
           Hessian matrices for every evaluation point and every dimension.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        hx_next = self.map_list[-1].hess_x(
            x, idxs_slice=idxs_slice, cache=map_list_cache[-1])
        if len(self.map_list) > 1:
            ev_next = self.map_list[-1].evaluate(
                x, idxs_slice=idxs_slice, cache=map_list_cache[-1])
            gx_next = self.map_list[-1].grad_x(
                x, idxs_slice=idxs_slice, cache=map_list_cache[-1] )
        for i in range(len(self.map_list)-2,-1,-1):
            tm = self.map_list[i]
            tm_cache = map_list_cache[i]
            hx = tm.hess_x(ev_next, idxs_slice=idxs_slice, cache=tm_cache) # m x d x d x d
            gx = tm.grad_x(ev_next, idxs_slice=idxs_slice, cache=tm_cache) # m x d x d
            hx_next = np.einsum('...ij,...jkl->...ikl', gx, hx_next)
            tmp = np.einsum('...ijk,...jl->...ikl', hx, gx_next)
            hx_next += np.einsum('...ikl,...km->...ilm', tmp, gx_next)
            if i > 0:
                # Update gx_next
                gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
                ev_next = tm.evaluate( ev_next, idxs_slice=idxs_slice, cache=tm_cache )
        return hx_next

    @cached([('map_list',"n_maps")],False)
    @counted
    def action_hess_x(self, x, dx, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute :math:`\langle\nabla^2_{\bf x} T({\bf x}), \delta{\bf x}\rangle`.

        Apply chain rule.
        
        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): direction
            on which to evaluate the Hessian
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           action of the Hessian matrices for every evaluation point and every dimension.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        ahx_next = self.map_list[-1].action_hess_x(
            x, dx, idxs_slice=idxs_slice, cache=map_list_cache[-1]) # m x d x d
        if len(self.map_list) > 1:
            ev_next = self.map_list[-1].evaluate(
                x, idxs_slice=idxs_slice, cache=map_list_cache[-1] )
            gx_next = self.map_list[-1].grad_x(
                x, idxs_slice=idxs_slice, cache=map_list_cache[-1] )
        for i in range(len(self.map_list)-2,-1,-1):
            tm = self.map_list[i]
            tm_cache = map_list_cache[i]
            gx = tm.grad_x(ev_next, idxs_slice=idxs_slice, cache=tm_cache) # m x d x d
            ahx_next = np.einsum('...ij,...jk->...ik', gx, ahx_next) # m x d x d
            tmp = np.einsum('...jl,...l->...j', gx_next, dx) # m x d
            tmp = tm.action_hess_x(
                ev_next, tmp, idxs_slice=idxs_slice, cache=tm_cache) # m x d x d
            ahx_next += np.einsum('...jl,...ij->...il', gx_next, tmp) # m x d x d
            if i > 0:
                # Update gx_next
                gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
                ev_next = tm.evaluate( ev_next, idxs_slice=idxs_slice, cache=tm_cache )
        return ahx_next

    @counted
    def inverse(self, x, *args, **kwargs):
        r""" Compute: :math:`T^{\dagger}({\bf y})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`T^{-1}({\bf y})` for every evaluation point
        """
        inv = x
        for tm in self.map_list:
            inv = tm.inverse(inv)
        return inv
    
    @counted
    def grad_x_inverse(self, x, *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf x} T^{\dagger}({\bf x})`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           gradient matrices for every evaluation point.
        """
        gx_next = self.map_list[0].grad_x_inverse( x )
        if len(self.map_list) > 1:
            ev_next = self.map_list[0].inverse(x)
        for i in range(1, len(self.map_list)):
            tm = self.map_list[i]
            gx = tm.grad_x_inverse(ev_next)
            gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
            if i > 0:
                # Update ev_next
                ev_next = tm.inverse( ev_next )
        return gx_next
    
    @counted
    def hess_x_inverse(self, x, *args, **kwargs):
        r""" Compute :math:`\nabla^2_{\bf x} T^{\dagger}({\bf x})`.
        
        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d,d`]) --
           Hessian matrices for every evaluation point and every dimension.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        hx_next = self.map_list[0].hess_x_inverse(x)
        if len(self.map_list) > 1:
            ev_next = self.map_list[0].inverse( x )
            gx_next = self.map_list[0].grad_x_inverse( x )
        for i in range(1,len(self.map_list)):
            tm = self.map_list[i]
            hx = tm.hess_x_inverse(ev_next) # m x d x d x d
            gx = tm.grad_x_inverse(ev_next) # m x d x d
            hx_next = np.einsum('...ij,...jkl->...ikl', gx, hx_next)
            tmp = np.einsum('...ijk,...jl->...ikl', hx, gx_next)
            hx_next += np.einsum('...ikl,...km->...ilm', tmp, gx_next)
            if i > 0:
                # Update gx_next
                gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
                # update ev_next
                ev_next = tm.inverse( ev_next )
        return hx_next

    @counted
    def action_hess_x_inverse(self, x, dx, *args, **kwargs):
        r""" Compute :math:`\langle\nabla^2_{\bf x} T^{\dagger}({\bf x}), \delta{\bf x}\rangle`.
        
        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): direction
            on which to evaluate the Hessian
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d,d`]) --
           action of the Hessian matrices for every evaluation point and every dimension.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        ahx_next = self.map_list[0].action_hess_x_inverse(x, dx)
        if len(self.map_list) > 1:
            ev_next = self.map_list[0].inverse( x )
            gx_next = self.map_list[0].grad_x_inverse( x )
        for i in range(1,len(self.map_list)):
            tm = self.map_list[i]
            gx = tm.grad_x_inverse(ev_next) # m x d x d
            ahx_next = np.einsum('...ij,...jk->...ik', gx, ahx_next)
            tmp = np.einsum('...jl,...l->...j', gx_next, dx) # m x d
            tmp = tm.action_hess_x_inverse(ev_next, tmp) # m x d x d
            ahx_next += np.einsum('...jl,...ij->...il', gx_next, tmp)
            if i > 0:
                # Update gx_next
                gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
                # update ev_next
                ev_next = tm.inverse( ev_next )
        return ahx_next

class CompositeMap(ListCompositeMap):
    r""" Given maps :math:`T_1,T_2`, define map :math:`T=T_1 \circ T_2`.

    Args:
      t1 (:class:`Map`): map :math:`T_1`
      t2 (:class:`Map`): map :math:`T_2`
    """
    def __init__(self, t1, t2):
        super(CompositeMap, self).__init__(
            map_list = [t1, t2]
        )
        self.t1 = self.map_list[0]
        self.t2 = self.map_list[1]
