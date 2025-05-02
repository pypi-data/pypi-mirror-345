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
    required_kwargs, \
    cached, counted, get_sub_cache

from .TransportMapBase import TransportMap
from .ListCompositeMapBase import ListCompositeMap

__all__ = [
    'CompositeTransportMap',
    'ListCompositeTransportMap'
]

nax = np.newaxis


class ListCompositeTransportMap(ListCompositeMap, TransportMap):
    r""" Composition of transport maps :math:`T({\bf x}) := T_1 \circ T_2 \circ \ldots \circ T_k({\bf x})`.
    """
    @required_kwargs('map_list')
    def __init__(self, **kwargs):
        r"""
        Args:
          map_list (list): list of :class:`TransportMap`s :math:`[T_1,\ldots,T_n]`
        """
        map_list = kwargs['map_list']
        if any( not isinstance(m, TransportMap) for m in map_list ):
            raise ValueError(
                "The map_list should contain only TransportMaps"
            )
        kwargs['dim'] = map_list[0].dim
        super(ListCompositeTransportMap, self).__init__(**kwargs)

    @counted
    def inverse(self, x, *args, **kwargs):
        r"""
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
        r""" Compute :math:`\nabla_{\bf x} T^{-1}({\bf x})`.

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
        r""" Compute :math:`\nabla^2_{\bf x} T^{-1}({\bf x})`.
        
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
        r""" Compute :math:`\langle\nabla^2_{\bf x} T^{-1}({\bf x}), \delta{\bf x}\rangle`.
        
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

    @cached([('map_list',"n_maps")], False)
    @counted
    def log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`\log \det \nabla_{\bf x} T({\bf x}, {\bf a})`.

        For the transport maps :math:`T_1,T_2`,

        .. math::

           \log \det \nabla_{\bf x} (T_1 \circ T_2)({\bf x}) = \log \det \nabla_{\bf x} T_1 ({\bf y}) + \log \det \nabla_{\bf x} T_2({\bf x})

        where :math:`{\bf y} = T_2({\bf x})`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \det \nabla_{\bf x} T({\bf x}, {\bf a})` at every
           evaluation point
        """
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))

        Xcp = x.copy()
        log_det = np.zeros( Xcp.shape[0] )

        for tm, tm_cache in zip(reversed(self.map_list),reversed(map_list_cache)):
            log_det += tm.log_det_grad_x(Xcp, idxs_slice=idxs_slice, cache=tm_cache)
            Xcp = tm.evaluate(Xcp, idxs_slice=idxs_slice, cache=tm_cache)

        return log_det

    @cached([('map_list',"n_maps")], False)
    @counted
    def grad_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x`.
        """
        map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
        # Expand gradient left to right (allows to use action_adjoint_grad_x)
        ev_list = [x]
        for i in range(len(self.map_list)-1,0,-1):
            ev_list.insert(
                0, self.map_list[i].evaluate(
                    ev_list[0], idxs_slice=idxs_slice, cache=map_list_cache[i]
                )
            )
        gx_ldet_gx_sum = np.zeros((x.shape[0],self.dim_in))
        for i in range(len(self.map_list)-1):
            gx_ldet_gx_sum += self.map_list[i].grad_x_log_det_grad_x(
                ev_list[i], idxs_slice=idxs_slice, cache=map_list_cache[i]
            )
            try:
                gx_ldet_gx_sum = self.map_list[i+1].action_adjoint_grad_x(
                    ev_list[i+1], gx_ldet_gx_sum, idxs_slice=idxs_slice, cache=map_list_cache[i+1]
                )
            except NotImplementedError:
                gx = self.map_list[i+1].grad_x(
                    ev_list[i+1], idxs_slice=idxs_slice, cache=map_list_cache[i+1]
                )
                gx_ldet_gx_sum = np.einsum('...i,...ij->...j', gx_ldet_gx_sum, gx)
        gx_ldet_gx_sum += self.map_list[-1].grad_x_log_det_grad_x(
            ev_list[-1], idxs_slice=idxs_slice, cache=map_list_cache[-1]
        )
        return gx_ldet_gx_sum
                    
        # gx_ldet_next = self.map_list[-1].grad_x_log_det_grad_x(
        #     x, idxs_slice=idxs_slice, cache=map_list_cache[-1])
        # if len(self.map_list) > 1:
        #     ev_next = self.map_list[-1].evaluate(
        #         x, idxs_slice=idxs_slice, cache=map_list_cache[-1])
        #     gx_next = self.map_list[-1].grad_x(
        #         x, idxs_slice=idxs_slice, cache=map_list_cache[-1])
        # for i in range(len(self.map_list)-2,-1,-1):
        #     tm = self.map_list[i]
        #     tm_cache = map_list_cache[i]
        #     gx_ldet = tm.grad_x_log_det_grad_x(
        #         ev_next, idxs_slice=idxs_slice, cache=tm_cache)
        #     gx_ldet_next += np.einsum('...i,...ik->...k', gx_ldet, gx_next)
        #     if i > 0:
        #         # Update gx_next
        #         gx = tm.grad_x( ev_next, idxs_slice=idxs_slice, cache=tm_cache )
        #         gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
        #         # Update ev_next
        #         ev_next = tm.evaluate( ev_next, idxs_slice=idxs_slice, cache=tm_cache )
        # return gx_ldet_next

    @counted
    def log_det_grad_x_inverse(self, x, precomp=None, *args, **kwargs):
        r""" Compute: :math:`\log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`.
        
        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})` at every
           evaluation point
        """
        ldet_next = self.map_list[0].log_det_grad_x_inverse(x)
        if len(self.map_list) > 1:
            ev_next = self.map_list[0].inverse(x)
        for i in range(1,len(self.map_list)):
            tm = self.map_list[i]
            ldet_next += tm.log_det_grad_x_inverse(ev_next)
            if i < len(self.map_list)-1:
                # Update ev_next
                ev_next = tm.inverse(ev_next)
        return ldet_next

    @counted
    def grad_x_log_det_grad_x_inverse(self, x, precomp=None, *args, **kwargs):
        r""" Compute: :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`.
        
        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})` at every
           evaluation point
        """
        gx_ldet_next = self.map_list[0].grad_x_log_det_grad_x_inverse(x)
        if len(self.map_list) > 1:
            ev_next = self.map_list[0].inverse(x)
            gx_next = self.map_list[0].grad_x_inverse(x)
        for i in range(1,len(self.map_list)):
            tm = self.map_list[i]
            gx_ldet = tm.grad_x_log_det_grad_x_inverse(ev_next)
            gx_ldet_next += np.einsum('...i,...ik->...k', gx_ldet, gx_next)
            if i < len(self.map_list)-1:
                # Update gx_next
                gx = tm.grad_x_inverse( ev_next )
                gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
                # Update ev_next
                ev_next = tm.inverse( ev_next )
        return gx_ldet_next
    
    # @cached([('map_list',"n_maps")])
    # @counted
    # def log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
    #     r""" Compute: :math:`\log \det \nabla_{\bf x} T({\bf x})`.

    #     For the transport maps :math:`T_1,T_2`,

    #     .. math::

    #        \log \det \nabla_{\bf x} (T_1 \circ T_2)({\bf x}) = \log \det \nabla_{\bf x} T_1 ({\bf y}) + \log \det \nabla_{\bf x} T_2({\bf x})

    #     where :math:`{\bf y} = T_2({\bf x})`.

    #     Args:
    #        x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
    #        precomp (:class:`dict<dict>`): dictionary of precomputed values

    #     Returns:
    #        (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
    #        :math:`\log \det \nabla_{\bf x} T({\bf x})` at every
    #        evaluation point
    #     """
    #     map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))

    #     Xcp = x.copy()
    #     log_det = np.zeros( Xcp.shape[0] )

    #     for tm, tm_cache in zip(reversed(self.map_list),reversed(map_list_cache)):
    #         log_det += tm.log_det_grad_x(Xcp, idxs_slice=idxs_slice, cache=tm_cache)
    #         Xcp = tm.evaluate(Xcp, idxs_slice=idxs_slice, cache=tm_cache)

    #     return log_det

    # @cached([('map_list',"n_maps")])
    # @counted
    # def grad_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
    #     r""" Compute: :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T({\bf x})`

    #     Args:
    #        x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
    #        precomp (:class:`dict<dict>`): dictionary of precomputed values

    #     Returns:
    #        (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
    #        :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T({\bf x})`
    #        at every evaluation point

    #     Raises:
    #        ValueError: if :math:`d` does not match the dimension of the transport map.

    #     .. seealso:: :func:`log_det_grad_x`.
    #     """
    #     map_list_cache = get_sub_cache(cache, ('map_list',self.n_maps))
    #     gx_ldet_next = np.zeros((x.shape))
    #     gx_ldet_next += self.map_list[-1].grad_x_log_det_grad_x(
    #         x, idxs_slice=idxs_slice, cache=map_list_cache[-1])
    #     if len(self.map_list) > 1:
    #         ev_next = self.map_list[-1].evaluate(
    #             x, idxs_slice=idxs_slice, cache=map_list_cache[-1])
    #         gx_next = self.map_list[-1].grad_x(
    #             x, idxs_slice=idxs_slice, cache=map_list_cache[-1])
    #     for i in range(len(self.map_list)-2,-1,-1):
    #         tm = self.map_list[i]
    #         tm_cache = map_list_cache[i]
    #         gx_ldet = tm.grad_x_log_det_grad_x(
    #             ev_next, idxs_slice=idxs_slice, cache=tm_cache)
    #         gx_ldet_next += np.einsum('...i,...ik->...k', gx_ldet, gx_next)
    #         if i > 0:
    #             # Update gx_next
    #             gx = tm.grad_x( ev_next, idxs_slice=idxs_slice, cache=tm_cache )
    #             gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
    #             # Update ev_next
    #             ev_next = tm.evaluate( ev_next, idxs_slice=idxs_slice, cache=tm_cache )
    #     return gx_ldet_next

    # @counted
    # def log_det_grad_x_inverse(self, x, precomp=None, *args, **kwargs):
    #     r""" Compute: :math:`\log \det \nabla_{\bf x} T^{\dagger}({\bf x})`.
        
    #     Args:
    #        x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
    #        precomp (:class:`dict<dict>`): dictionary of precomputed values

    #     Returns:
    #        (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
    #        :math:`\log \det \nabla_{\bf x} T^{-1}({\bf x})` at every
    #        evaluation point
    #     """
    #     ldet_next = self.map_list[0].log_det_grad_x_inverse(x)
    #     if len(self.map_list) > 1:
    #         ev_next = self.map_list[0].inverse(x)
    #     for i in range(1,len(self.map_list)):
    #         tm = self.map_list[i]
    #         ldet = tm.log_det_grad_x_inverse(ev_next)
    #         ldet_next = np.einsum('...,...->...', ldet_next, ldet)
    #         if i < len(self.map_list)-1:
    #             # Update ev_next
    #             ev_next = tm.inverse(ev_next)
    #     return ldet_next

    # @counted
    # def grad_x_log_det_grad_x_inverse(self, x, precomp=None, *args, **kwargs):
    #     r""" Compute: :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T^{\dagger}({\bf x})`.
        
    #     Args:
    #        x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
    #        precomp (:class:`dict<dict>`): dictionary of precomputed values

    #     Returns:
    #        (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
    #        :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x})` at every
    #        evaluation point
    #     """
    #     gx_ldet_next = np.zeros((x.shape))
    #     gx_ldet_next += self.map_list[0].grad_x_log_det_grad_x_inverse(x)
    #     if len(self.map_list) > 1:
    #         ev_next = self.map_list[0].inverse(x)
    #         gx_next = self.map_list[0].grad_x_inverse(x)
    #     for i in range(1,len(self.map_list)):
    #         tm = self.map_list[i]
    #         gx_ldet = tm.grad_x_log_det_grad_x_inverse(ev_next)
    #         gx_ldet_next += np.einsum('...i,...ik->...k', gx_ldet, gx_next)
    #         if i < len(self.map_list)-1:
    #             # Update gx_next
    #             gx = tm.grad_x_inverse( ev_next )
    #             gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
    #             # Update ev_next
    #             ev_next = tm.inverse( ev_next )
    #     return gx_ldet_next

class CompositeTransportMap(ListCompositeTransportMap):
    r""" Composition of two transport maps :math:`T({\bf x}) := T_1 \circ T_2`.
    """
    def __init__(self, t1, t2):
        r"""
        Args:
          t1 (:class:`TransportMap`): :math:`T_1`
          t2 (:class:`TransportMap`): :math:`T_2`
        """
        super(CompositeTransportMap, self).__init__(
            map_list = [t1, t2]
        )
        self.t1 = self.map_list[0]
        self.t2 = self.map_list[1]

    @cached([('map_list',"n_maps")],False)
    @counted
    def hess_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x})`

        For the transport maps :math:`T_1,T_2`,

        .. math::

           \nabla^2_{\bf x} \log \det \nabla_{\bf x} (T_1 \circ T_2) = \left[ \nabla^2_{\bf x} \log \det (\nabla_{\bf x} T_1 \circ T_2) \cdot \nabla_{\bf x} T_2 + \nabla_{\bf x} \log \det \nabla_{\bf x} T_2 \right] \cdot (\nabla_{\bf x} T_2) + \nabla_{\bf x} \log \det (\nabla_{\bf x} T_1 \circ T_2) \cdot \nabla^2_{\bf x} T_2 + \nabla^2_{\bf x} \log \det \nabla_{\bf x} T_2

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        try:
            t1_cache = cache['map_list_cache'][0]
            t2_cache = cache['map_list_cache'][1]
        except TypeError:
            t1_cache = None
            t2_cache = None
        ev_t2 = self.t2.evaluate(x, cache=t2_cache) # m x d
        gx_t2 = self.t2.grad_x(x, cache=t2_cache)   # m x d x d
        hx_t2 = self.t2.hess_x(x, cache=t2_cache)   # m x d x d x d
        gx_ldet_gx_t1 = self.t1.grad_x_log_det_grad_x( ev_t2, cache=t1_cache ) # m x d
        hx_ldet_gx_t1 = self.t1.hess_x_log_det_grad_x( ev_t2, cache=t1_cache ) # m x d x d
        hx_ldet_gx_t2 = self.t2.hess_x_log_det_grad_x(x, cache=t2_cache) # m x d x d
        out = np.einsum('...ij,...jl->...il', hx_ldet_gx_t1, gx_t2)
        out = np.einsum('...ij,...il->...jl', gx_t2, out)
        out += np.einsum('...i,...ijk->...jk', gx_ldet_gx_t1, hx_t2)
        out += hx_ldet_gx_t2
        return out

    @cached([('map_list',"n_maps")],False)
    @counted
    def action_hess_x_log_det_grad_x(
            self, x, dx, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`\langle\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}), \delta{\bf x}\rangle`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): direction
            on which to evaluate the Hessian
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
             :math:`\langle\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}), \delta{\bf x}\rangle` at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`hess_x_log_det_grad_x`.
        """
        try:
            t1_cache = cache['map_list_cache'][0]
            t2_cache = cache['map_list_cache'][1]
        except TypeError:
            t1_cache = None
            t2_cache = None
        ev_t2 = self.t2.evaluate(x, cache=t2_cache) # m x d
        gx_t2 = self.t2.grad_x(x, cache=t2_cache)   # m x d x d
        A = np.einsum('...ij,...j->...i', gx_t2, dx) # m x d
        A = self.t1.action_hess_x_log_det_grad_x(ev_t2, A, cache=t1_cache) # m x d
        A = np.einsum('...ij,...i->...j', gx_t2, A) # m x d

        gx_ldet_gx_t1 = self.t1.grad_x_log_det_grad_x( ev_t2, cache=t1_cache ) # m x d
        B = self.t2.action_hess_x(x, dx, cache=t2_cache) # m x d x d
        B = np.einsum('...i,...ij->...j', gx_ldet_gx_t1, B) # m x d

        C = self.t2.action_hess_x_log_det_grad_x(x, dx, cache=t2_cache) # m x d

        return A + B + C

    @counted
    def hess_x_log_det_grad_x_inverse(self, x, precomp=None, *args, **kwargs):
        r""" Compute: :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        t1_inv = self.t1.inverse(x) # m x d
        gx_t1_inv = self.t1.grad_x_inverse(x)   # m x d x d
        hx_t1_inv = self.t1.hess_x_inverse(x)   # m x d x d x d
        gx_ldet_gx_t2_inv = self.t2.grad_x_log_det_grad_x_inverse( t1_inv ) # m x d
        hx_ldet_gx_t2_inv = self.t2.hess_x_log_det_grad_x_inverse( t1_inv ) # m x d x d
        hx_ldet_gx_t1_inv = self.t1.hess_x_log_det_grad_x_inverse(x) # m x d x d
        out = np.einsum('...ij,...jl->...il', hx_ldet_gx_t2_inv, gx_t1_inv)
        out = np.einsum('...ij,...il->...jl', gx_t1_inv, out)
        out += np.einsum('...i,...ijk->...jk', gx_ldet_gx_t2_inv, hx_t1_inv)
        out += hx_ldet_gx_t1_inv
        return out

    @counted
    def action_hess_x_log_det_grad_x_inverse(self, x, dx, precomp=None, *args, **kwargs):
        r""" Compute: :math:`\langle\nabla^2_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x}), \delta{\bf x}\rangle`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): direction
            on which to evaluate the Hessian
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           :math:`\langle\nabla^2_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x}), \delta{\bf x}\rangle` at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        t1_inv = self.t1.inverse(x) # m x d
        gx_t1_inv = self.t1.grad_x_inverse(x)   # m x d x d
        A = np.einsum('...ij,...j->...i', gx_t1_inv, dx) # m x d
        A = self.t2.action_hess_x_log_det_grad_x_inverse(t1_inv, A) # m x d
        A = np.einsum('...ij,...i->...j', gx_t1_inv, A) # m x d

        gx_ldet_gx_t2_inv = self.t2.grad_x_log_det_grad_x_inverse( t1_inv ) # m x d
        B = self.t1.action_hess_x_inverse(x, dx) # m x d x d
        B = np.einsum('...i,...ij->...j', gx_ldet_gx_t2_inv, B) # m x d

        C = self.t1.action_hess_x_log_det_grad_x_inverse(x, dx) # m x d

        return A + B + C
