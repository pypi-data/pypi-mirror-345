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

import warnings
import numpy as np

from ..Misc import counted, cached, cached_tuple, get_sub_cache
from ..MPI import mpi_map
from ..Maps import \
    CompositeMap,\
    InverseTransportMap
from .TransportMapDistributionBase import TransportMapDistribution

__all__ = [
    'PushForwardTransportMapDistribution',
    'PullBackTransportMapDistribution'
]


class PushForwardTransportMapDistribution(TransportMapDistribution):
    r""" Class for densities of the transport map type :math:`T_\sharp \pi`

    Args:
      transport_map (Maps.TriangularTransportMap): transport map :math:`T`
      base_distribution (Distributions.Distribution): distribution :math:`\pi`

    .. seealso:: :class:`TransportMapDistribution`
    """

    @counted
    def pdf(self, x, params=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`T_\sharp \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`T_\sharp \pi`
            at the ``x`` points.
        """
        return np.exp( self.log_pdf(x, params, idxs_slice=idxs_slice, cache=cache) )

    @cached()
    @counted
    def log_pdf(self, x, params=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\log T_\sharp \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\log T_\sharp\pi`
            at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            # idxs_slice = slice(None)
            params_t = None
        # Compute log-pushforward
        if x.shape[1] != self.transport_map.dim_in:
            raise ValueError("dimension mismatch")
        if params_t is None:
            params_t = {'components': [{} for i in range(self.transport_map.dim_out)]}
        xinv = self.transport_map.inverse(x, precomp=params_t, idxs_slice=idxs_slice)
        params_t['xinv'] = xinv
        ldgx = self.transport_map.log_det_grad_x_inverse(x, precomp=params_t, idxs_slice=idxs_slice)
        lpdf = self.base_distribution.log_pdf(xinv, params=params_pi)
        return TransportMapDistribution._evaluate_log_transport(lpdf, ldgx)

    @cached()
    @counted
    def grad_x_log_pdf(
            self, x, params=None, idxs_slice=slice(None), cache=None, *args, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf x} \log \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\nabla_x\log\pi` at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            # idxs_slice = slice(None)
            params_t = None
        # Compute grad_x_log_pushforward
        if x.shape[1] != self.transport_map.dim_in:
            raise ValueError("dimension mismatch")
        inv = self.transport_map.inverse(x)
        gxinv = self.transport_map.grad_x_inverse(x)
        gxldgxinv = self.transport_map.grad_x_log_det_grad_x_inverse(x, params_t)
        gxlpdfinv = self.base_distribution.grad_x_log_pdf(inv, params_pi)
        return TransportMapDistribution._evaluate_grad_x_log_transport(gxlpdfinv, gxinv, gxldgxinv)

    @cached_tuple(['log_pdf','grad_x_log_pdf'])
    @counted
    def tuple_grad_x_log_pdf(
            self, x, params=None, idxs_slice=slice(None), cache=None, *args, **kwargs):
        r""" Evaluate :math:`\left(\log \pi({\bf x}), \nabla_{\bf x} \log \pi({\bf x})\right)`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`tuple`) --
            :math:`\left(\log \pi({\bf x}), \nabla_{\bf x} \log \pi({\bf x})\right)`
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            # idxs_slice = slice(None)
            params_t = None
        # Compute tuple_grad_x_log_pushforward
        if x.shape[1] != self.transport_map.dim_in:
            raise ValueError("dimension mismatch")
        inv = self.transport_map.inverse(x)
        gxinv = self.transport_map.grad_x_inverse(x)
        ldgxinv = self.transport_map.log_det_grad_x_inverse(x, params_t)
        gxldgxinv = self.transport_map.grad_x_log_det_grad_x_inverse(x, params_t)
        lpdfinv, gxlpdfinv = self.base_distribution.tuple_grad_x_log_pdf(inv, params_pi)
        return (
            TransportMapDistribution._evaluate_log_transport(lpdfinv, ldgxinv),
            TransportMapDistribution._evaluate_grad_x_log_transport(gxlpdfinv, gxinv, gxldgxinv)
        )

    @cached(caching=False)
    @counted
    def hess_x_log_pdf(
            self, x, params=None, idxs_slice=slice(None), cache=None, *args, **kwargs):
        r""" Evaluate :math:`\nabla^2_{\bf x} \log \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) -- values of
            :math:`\nabla^2_x\log\pi` at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            # idxs_slice = slice(None)
            params_t = None
        # Compute hess_x_log_pushforward
        if x.shape[1] != self.transport_map.dim_in:
            raise ValueError("dimension mismatch")
        n = x.shape[0]
        inv = self.transport_map.inverse(x)
        dxT = self.transport_map.grad_x_inverse(x) # n x d x d
        dx2logpi = self.base_distribution.hess_x_log_pdf( inv, params_pi ) # n x d x d
        A = np.einsum('...ij,...ik->...jk', dx2logpi, dxT) # n x d x d
        A = np.einsum('...ij,...ik->...jk', A, dxT) # n x d x d
        dxlogpi = self.base_distribution.grad_x_log_pdf(inv, params_pi) # n x d
        dx2T = self.transport_map.hess_x_inverse(x) # n x d x d x d
        B = np.einsum('...i,...ijk->...jk', dxlogpi, dx2T)
        C = self.transport_map.hess_x_log_det_grad_x_inverse(x)
        return A + B + C

    @cached(caching=False)
    @counted
    def action_hess_x_log_pdf(
            self, x, dx, params=None, idxs_slice=slice(None,None,None),
            cache=None, *args, **kwargs):
        r""" Evaluate :math:`\langle \nabla^2_{\bf x} \log \pi({\bf x}), \delta{\bf x}\rangle`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): direction
            on which to evaluate the Hessian
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\langle \nabla^2_{\bf x} \log \pi({\bf x}), \delta{\bf x}\rangle`.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            # idxs_slice = slice(None)
            params_t = None
        # Compute action_hess_x_log_pushforward
        if x.shape[1] != self.transport_map.dim_in:
            raise ValueError("dimension mismatch")
        # n = x.shape[0]
        inv = self.transport_map.inverse(x)
        dxT = self.transport_map.grad_x_inverse(x) # n x d x d

        A = np.einsum('...ij,...j->...i', dxT, dx) # n x d
        A = self.base_distribution.action_hess_x_log_pdf(inv, A, params_pi) # n x d
        A = np.einsum('...ij,...i->...j', dxT, A)

        dxlogpi = self.base_distribution.grad_x_log_pdf(inv, params_pi) # n x d
        B = self.transport_map.action_hess_x_inverse(x, dx) # n x d x d
        B = np.einsum('...i,...ij->...j', dxlogpi, B)

        C = self.transport_map.action_hess_x_log_det_grad_x_inverse(x, dx)
        return A + B + C

    def map_function_base_to_target(self, f):
        r""" Given the map :math:`f` returns :math:`f\circ T`

        Args:
          f (:class:`TransportMaps.Maps.Map<Map>`): the map :math:`f`

        Returns:
          (:class:`TransportMaps.Maps.CompositeMap<CompositeMap>`) -- :math:`f \circ T`
        """
        return CompositeMap(f, self.transport_map)
        
    def map_samples_base_to_target(self, x, mpi_pool=None):
        r""" Map input samples (assumed to be from :math:`\pi`) to the corresponding samples from :math:`T_\sharp \pi`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): input samples
          mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processes

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- corresponding samples
        """
        scatter_tuple = (['x'], [x])
        out = mpi_map("evaluate", scatter_tuple=scatter_tuple, obj=self.transport_map,
                       mpi_pool=mpi_pool)
        return out

    def map_samples_target_to_base(self, x, mpi_pool=None):
        r""" Map input samples assumed to be from :math:`T_\sharp \pi` to the corresponding samples from :math:`\pi`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): input samples
          mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processes

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- corresponding samples
        """
        scatter_tuple = (['x'], [x])
        out = mpi_map("inverse", scatter_tuple=scatter_tuple, obj=self.transport_map,
                       mpi_pool=mpi_pool)
        return out


class PullBackTransportMapDistribution(TransportMapDistribution):
    r""" Class for densities of the transport map type :math:`T^\sharp \pi`

    Args:
      transport_map (Maps.TriangularTransportMap): transport map :math:`T`
      base_distribution (Distributions.Distribution): distribution :math:`\pi`

    .. seealso:: :class:`TransportMapDistribution`
    """

    @counted
    def pdf(self, x, params=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`T^\sharp \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`T^\sharp \pi`
            at the ``x`` points.
        """
        return np.exp( self.log_pdf(x, params, idxs_slice=idxs_slice,
                                    cache=cache))

    @cached([('pi',None),('t',None)])
    @counted
    def log_pdf(self, x, params=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\log T^\sharp \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\log T^\sharp \pi`
            at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            # idxs_slice = slice(None)
            params_t = None
        # Compute log-pullback
        if x.shape[1] != self.transport_map.dim_in:
            raise ValueError("dimension mismatch")
        # Init sub-cache if necessary
        pi_cache, t_cache = get_sub_cache(cache, ('pi',None), ('t',None))
        ev = self.transport_map.evaluate(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        ldgx = self.transport_map.log_det_grad_x(
            x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        lpdf = self.base_distribution.log_pdf(ev, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache)
        return TransportMapDistribution._evaluate_log_transport(lpdf, ldgx)

    @cached([('pi',None),('t',None)])
    @counted
    def grad_x_log_pdf(
            self, x, params=None, idxs_slice=slice(None), cache=None, *args, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf x} \log T^\sharp \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of
            :math:`\nabla_{\bf x} \log T^\sharp \pi` at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            # idxs_slice = slice(None)
            params_t = None
        # Compute grad_x_log_pullback
        if x.shape[1] != self.transport_map.dim_in:
            raise ValueError("dimension mismatch")
        pi_cache, t_cache = get_sub_cache(cache, ('pi',None), ('t',None))
        ev = self.transport_map.evaluate(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        # Try to evaluate left to right (to save memory)
        gxlpdf = self.base_distribution.grad_x_log_pdf(
            ev, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache)
        gxldgx = self.transport_map.grad_x_log_det_grad_x(
            x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        try:
            gx = self.transport_map.action_adjoint_grad_x(
                x, gxlpdf, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        except NotImplementedError:
            gx = self.transport_map.grad_x(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
            gx = TransportMapDistribution._evaluate_grad_x_log_transport(gxlpdf, gx, gxldgx)
        else:
            gx += gxldgx
        return gx

    @cached_tuple(['log_pullback', 'grad_x_log_pullback'], [('pi',None),('t',None)])
    @counted
    def tuple_grad_x_log_pdf(
            self, x, params=None, idxs_slice=slice(None), cache=None, *args, **kwargs):
        r""" Evaluate :math:`\left(\log T^\sharp \pi({\bf x}), \nabla_{\bf x} \log T^\sharp \pi({\bf x})\right)`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`tuple`) --
            :math:`\left(\log T^\sharp \pi({\bf x}), \nabla_{\bf x} \log T^\sharp \pi({\bf x})\right)`
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            # idxs_slice = slice(None)
            params_t = None
        # Compute tuple_grad_x_log_pullback
        if x.shape[1] != self.transport_map.dim_in:
            raise ValueError("dimension mismatch")
        pi_cache, t_cache = get_sub_cache(cache, ('pi',None), ('t',None))
        ev = self.transport_map.evaluate(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        ldgx = self.transport_map.log_det_grad_x(
            x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        gx = self.transport_map.grad_x(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        gxldgx = self.transport_map.grad_x_log_det_grad_x(
            x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        lpdf, gxlpdf = self.base_distribution.tuple_grad_x_log_pdf(
            ev, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache)
        return (
            TransportMapDistribution._evaluate_log_transport(lpdf, ldgx),
            TransportMapDistribution._evaluate_grad_x_log_transport(gxlpdf, gx, gxldgx)
        )

    @cached([('pi',None),('t',None)], caching=False)
    @counted
    def hess_x_log_pdf(
            self, x, params=None, idxs_slice=slice(None), cache=None, *args, **kwargs):
        r""" Evaluate :math:`\nabla^2_{\bf x} \log T^\sharp \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) -- values of
            :math:`\nabla^2_{\bf x} \log T^\sharp \pi` at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            # idxs_slice = slice(None)
            params_t = None
        # Compute hess_x_log_pullback
        if x.shape[1] != self.transport_map.dim_in:
            raise ValueError("dimension mismatch")
        pi_cache, t_cache = get_sub_cache(cache, ('pi',None), ('t',None))
        n = x.shape[0]
        xval = self.transport_map.evaluate(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        dxT = self.transport_map.grad_x(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        dx2logpi = self.base_distribution.hess_x_log_pdf(
            xval, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache)  # n x d x d
        A = np.einsum('...ij,...ik->...jk', dx2logpi, dxT)  # n x d x d
        A = np.einsum('...ij,...ik->...jk', A, dxT)  # n x d x d
        dxlogpi = self.base_distribution.grad_x_log_pdf(
            xval, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache)  # n x d
        dx2T = self.transport_map.hess_x(
            x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)  # n x d x d x d
        B = np.einsum('...i,...ijk->...jk', dxlogpi, dx2T)
        C = self.transport_map.hess_x_log_det_grad_x(
            x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        return A + B + C

    @cached([('pi',None),('t',None)], caching=False)
    @counted
    def action_hess_x_log_pdf(self, x, dx, params=None, idxs_slice=slice(None),
                              cache=None, *args, **kwargs):
        r""" Evaluate :math:`\langle\nabla^2_{\bf x} \log T^\sharp \pi({\bf x}),\delta{\bf x}\rangle`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): direction
            on which to evaluate the Hessian
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\langle\nabla^2_{\bf x} \log T^\sharp \pi({\bf x}),\delta{\bf x}\rangle`
            at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            # idxs_slice = slice(None)
            params_t = None
        # Compute action_hess_x_log_pullback
        if x.shape[1] != self.transport_map.dim_in:
            raise ValueError("dimension mismatch")
        pi_cache, t_cache = get_sub_cache(cache, ('pi', None), ('t', None))
        n = x.shape[0]
        xval = self.transport_map.evaluate(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        dxT = self.transport_map.grad_x(
            x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)  # n x d x d

        A = np.einsum('...ij,...j->...i', dxT, dx)  # n x d
        A = self.base_distribution.action_hess_x_log_pdf(
            xval, A, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache)  # n x d
        A = np.einsum('...ij,...i->...j', dxT, A)

        dxlogpi = self.base_distribution.grad_x_log_pdf(
            xval, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache)  # n x d
        B = self.transport_map.action_hess_x(
            x, dx, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)  # n x d x d
        B = np.einsum('...i,...ij->...j', dxlogpi, B)

        C = self.transport_map.action_hess_x_log_det_grad_x(
            x, dx, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)

        return A + B + C

    def map_function_base_to_target(self, f):
        r""" Given the map :math:`f` returns :math:`f\circ T^{-1}`

        Args:
          f (:class:`TransportMaps.Maps.Map<Map>`): the map :math:`f`

        Returns:
          (:class:`TransportMaps.Maps.CompositeMap<CompositeMap>`) -- :math:`f \circ T^{-1}`
        """
        return CompositeMap(f, InverseTransportMap(self.transport_map))

    def map_samples_base_to_target(self, x, mpi_pool=None):
        r""" Map input samples (assumed to be from :math:`\pi`) to the corresponding samples from :math:`T^\sharp \pi`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): input samples
          mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processes

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- corresponding samples
        """
        scatter_tuple = (['x'], [x])
        out = mpi_map("inverse", scatter_tuple=scatter_tuple, obj=self.transport_map,
                       mpi_pool=mpi_pool)
        return out

    def map_samples_target_to_base(self, x, mpi_pool=None):
        r""" Map input samples assumed to be from :math:`T^\sharp \pi` to the corresponding samples from :math:`\pi`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): input samples
          mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processes

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- corresponding samples
        """
        scatter_tuple = (['x'], [x])
        out = mpi_map("evaluate", scatter_tuple=scatter_tuple, obj=self.transport_map,
                       mpi_pool=mpi_pool)
        return out
