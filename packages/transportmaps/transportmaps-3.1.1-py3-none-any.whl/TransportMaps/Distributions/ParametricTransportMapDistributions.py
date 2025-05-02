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
import scipy.linalg as scila

from ..Misc import counted, cached, cached_tuple, get_sub_cache
from .ParametricTransportMapDistributionBase import ParametricTransportMapDistribution
from .TransportMapDistributions import \
    PullBackTransportMapDistribution, \
    PushForwardTransportMapDistribution
from .ProductDistributionBase import  ProductDistribution

__all__ = [
    'PushForwardParametricTransportMapDistribution',
    'PullBackParametricTransportMapDistribution'
]

nax = np.newaxis


class PushForwardParametricTransportMapDistribution(
        ParametricTransportMapDistribution,
        PushForwardTransportMapDistribution
):
    r""" Class for densities of the transport map type :math:`T_\sharp \pi`

    Args:
      transport_map (:class:`TransportMap<TransportMaps.Maps.ParametricTransportMap>`): transport map :math:`T`
      base_distribution (:class:`Distribution`): distribution :math:`\pi``

    .. seealso:: :class:`ParametricTransportMapDistribution`
    """

    @cached()
    @counted
    def grad_a_log_pdf(self, x, params=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla_{\bf a} \log T_\sharp \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of
            :math:`\nabla_{\bf a} \log T_\sharp \pi` at the ``x`` points.
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
        # Compute grad_a_log_pushforward
        xinv = self.transport_map.inverse(x, params_t, idxs_slice=idxs_slice)
        gx = self.transport_map.grad_x(xinv)  # Lower triangular
        ga_list = self.transport_map.grad_a(xinv)  # List of diagonal blocks
        out = np.zeros((x.shape[0], self.n_coeffs))
        # Solve linear system
        tmp = self.transport_map.grad_x_log_det_grad_x(xinv)
        tmp -= self.base_distribution.grad_x_log_pdf(xinv)
        for i in range(x.shape[0]):
            scila.solve_triangular(gx[i, :, :], tmp[i, :],
                                   lower=True, trans='T', overwrite_b=True)
        # Finish computing first term
        start = 0
        for d, ga in enumerate(ga_list):
            stop = start + ga.shape[1]
            out[:, start:stop] = ga * tmp[:, d, nax]
            start += ga.shape[1]
        # Add second term
        out -= self.transport_map.grad_a_log_det_grad_x(xinv)
        return out


class PullBackParametricTransportMapDistribution(
        ParametricTransportMapDistribution,
        PullBackTransportMapDistribution
):
    r""" Class for densities of the transport map type :math:`T^\sharp \pi`

    Args:
      transport_map (:class:`TransportMap<TransportMaps.Maps.ParametricTransportMap>`): transport map :math:`T`
      base_distribution (:class:`Distribution`): distribution :math:`\pi``

    .. seealso:: :class:`ParametricTransportMapDistribution`
    """

    @cached([('pi',None),('t',None)])
    @counted
    def grad_a_log_pdf(self, x, params=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla_{\bf a} \log T^\sharp \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,n`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache
          
        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,n`]) -- values of
            :math:`\nabla_{\bf a} \log T^\sharp \pi` at the ``x`` points.
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
        # Compute grad_a_log_pullback
        if x.shape[1] != self.transport_map.dim_in:
            raise ValueError("dimension mismatch")
        # Init sub-cache if necessary
        pi_cache, t_cache = get_sub_cache(cache, ('pi',None), ('t',None))
        ev = self.transport_map.evaluate(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        ga_list = self.transport_map.grad_a(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        gxlpdf = self.base_distribution.grad_x_log_pdf(
            ev, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache)
        galdgx = self.transport_map.grad_a_log_det_grad_x(
            x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        return self._evaluate_grad_a_log_pullback(gxlpdf, ga_list, galdgx)

    def grad_a_hess_x_log_pdf(self, x, params=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf a} \nabla^2_{\bf x} \log T^\sharp \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,n,d,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,n,d,d`]) -- values of
            :math:`\nabla_{\bf a} \nabla^2_{\bf x} \log T^\sharp \pi` at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            idxs_slice = slice(None)
            params_t = None
        # Compute grad_a_hess_x_log_pullback
        from TransportMaps.Distributions.ProductDistributionBase import ProductDistribution
        from TransportMaps.Maps.Functionals import ProductDistributionParametricPullbackComponentFunction
        if issubclass(type(self.base_distribution), ProductDistribution):
            n = x.shape[0]
            grad_a_hess_x_sum = np.zeros((n, self.transport_map.n_coeffs, self.transport_map.dim, self.transport_map.dim))
            # currently not using parallel implementation (batch_size_list, mpi_pool_list)
            # currently using params_t and params_pi assuming None
            start_j = 0
            for i, (a, avars) in enumerate(zip(self.transport_map.approx_list, self.transport_map.active_vars)):
                pi_i = self.base_distribution.get_component([i])
                pS_i = ProductDistributionParametricPullbackComponentFunction(a, pi_i)
                stop_j = start_j + a.n_coeffs
                grad_a_hess_x_sum[np.ix_(range(n), range(start_j, stop_j), avars, avars)] += pS_i.grad_a_hess_x(
                    x[:, avars])[:, 0, :, :, :]
                start_j = stop_j
            return grad_a_hess_x_sum
        else:
            raise NotImplementedError('not implemented yet')

    @cached_tuple(['log_pullback', 'grad_a_log_pullback'],[('pi',None),('t',None)])
    @counted
    def tuple_grad_a_log_pdf(self, x, params=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\left(\log T^\sharp \pi({\bf x}), \nabla_{\bf a} \log T^\sharp \pi({\bf x})\right)`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache
        
        Returns:
          (:class:`tuple`) --
            :math:`\left(\log T^\sharp \pi({\bf x}), \nabla_{\bf a} \log T^\sharp \pi({\bf x})\right)`
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
        # Compute tuple_grad_a_log_pullback
        if x.shape[1] != self.transport_map.dim_in:
            raise ValueError("dimension mismatch")
        # Init sub-cache if necessary
        pi_cache, t_cache = get_sub_cache(cache, ('pi',None), ('t',None))
        ev = self.transport_map.evaluate(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        ldgx = self.transport_map.log_det_grad_x(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        ga_list = self.transport_map.grad_a(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        galdgx = self.transport_map.grad_a_log_det_grad_x(
            x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        lpdf, gxlpdf = self.base_distribution.tuple_grad_x_log_pdf(
            ev, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache)
        return (
            self._evaluate_log_transport(lpdf, ldgx),
            self._evaluate_grad_a_log_pullback(gxlpdf, ga_list, galdgx)
        )

    @cached([('pi',None),('t',None)], caching=False)
    @counted
    def hess_a_log_pdf(self, x, params=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla^2_{\bf a} \log T^\sharp \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache
          
        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of
            :math:`\nabla^2_{\bf a} \log T^\sharp \pi` at the ``x`` points.
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
        # Compute hess_a_log_pullback
        if x.shape[1] != self.transport_map.dim_in:
            raise ValueError("dimension mismatch")
        if issubclass(type(self.base_distribution), ProductDistribution):
            from TransportMaps.Maps.Functionals import ProductDistributionParametricPullbackComponentFunction
            n = x.shape[0]
            hess_a_sum = np.zeros((n, self.transport_map.n_coeffs, self.transport_map.n_coeffs))
            # currently not using parallel implementation (batch_size_list, mpi_pool_list)
            # currently using params_t and params_pi assuming None
            start_j = 0
            for i, (a, avars) in enumerate(zip(self.transport_map.approx_list, self.transport_map.active_vars)):
                pi_i = self.base_distribution.get_component([i])
                pS_i = ProductDistributionParametricPullbackComponentFunction(a, pi_i)
                stop_j = start_j + a.n_coeffs
                hess_a_sum[np.ix_(range(n), range(start_j, stop_j), range(start_j, stop_j))] += pS_i.hess_a(
                    x[:, avars])[:, 0, :, :]
                start_j = stop_j
            return hess_a_sum
        else:
            # Init sub-cache if necessary
            pi_cache, t_cache = get_sub_cache(cache, ('pi', None), ('t', None))
            xval = self.transport_map.evaluate(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
            grad_list = self.transport_map.grad_a(x, precomp=params_t, idxs_slice=idxs_slice,
                                    cache=t_cache)  # List of d (n x m) arrays
            hess_list = self.transport_map.hess_a(x, precomp=params_t, idxs_slice=idxs_slice,
                                    cache=t_cache)  # List of d (n x m x m) arrays
            dxlogpull = self.base_distribution.grad_x_log_pdf(
                xval, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache)  # (n x d) array
            dx2logpull = self.base_distribution.hess_x_log_pdf(
                xval, params=params_pi,
                idxs_slice=idxs_slice, cache=pi_cache)  # (n x d x d) array
            out = np.empty((x.shape[0], self.transport_map.n_coeffs,
                            self.transport_map.n_coeffs))  # Initialized by first addend
            # First addend
            start_j = 0
            for j in range(self.transport_map.dim_out):
                g = grad_list[j]
                stop_j = start_j + g.shape[1]
                start_k = 0
                for k in range(self.transport_map.dim_out):
                    h = grad_list[k]
                    stop_k = start_k + h.shape[1]
                    tmp = dx2logpull[:, j, k, nax] * g
                    out[:, start_j:stop_j, start_k:stop_k] = tmp[:, :, nax] * h[:, nax, :]
                    start_k = stop_k
                start_j = stop_j
            # Second addend
            start = 0
            for k, hess in enumerate(hess_list):
                stop = start + hess.shape[1]
                out[:, start:stop, start:stop] += dxlogpull[:, k, nax, nax] * hess
                start = stop
            # Add Hessian of the log determinant term
            out += self.transport_map.hess_a_log_det_grad_x(
                x, precomp=params_t,
                idxs_slice=idxs_slice, cache=t_cache)
            return out

    @cached([('pi',None),('t',None)], caching=False)
    @counted
    def action_hess_a_log_pdf(self, x, da, params=None, idxs_slice=slice(None),
                              cache=None):
        r""" Evaluate :math:`\langle\nabla^2_{\bf a} \log T^\sharp \pi({\bf x}), \delta{\bf a}\rangle`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          da (:class:`ndarray<numpy.ndarray>` [:math:`N`]): direction
            on which to evaluate the Hessian
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache
          
        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of
            :math:`\langle\nabla^2_{\bf a} \log T^\sharp \pi({\bf x}), \delta{\bf a}\rangle`
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
        # Compute action_hess_a_log_pullback
        if x.shape[1] != self.transport_map.dim_in:
            raise ValueError("dimension mismatch")
        # Init sub-cache if necessary
        pi_cache, t_cache = get_sub_cache(cache, ('pi', None), ('t', None))
        m = x.shape[0]
        xval = self.transport_map.evaluate(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)

        # First addend
        grad_list = self.transport_map.grad_a(
            x, precomp=params_t, idxs_slice=idxs_slice,
            cache=t_cache)  # List of d (m x n) arrays
        dx = np.zeros((m, self.transport_map.dim_out))
        start = 0
        for j, g in enumerate(grad_list):
            stop = start + g.shape[1]
            dx[:, j] = np.dot(g, da[start:stop])
            start = stop
        ahxlpdf = self.base_distribution.action_hess_x_log_pdf(
            xval, dx, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache)  # m x d
        A = np.zeros((m, self.transport_map.n_coeffs))  # m x N
        start = 0
        for j, g in enumerate(grad_list):
            stop = start + g.shape[1]
            A[:, start:stop] = g * ahxlpdf[:, [j]]
            start = stop

        # Second addend
        action_hess_list = self.transport_map.action_hess_a(
            x, da, precomp=params_t, idxs_slice=idxs_slice,
            cache=t_cache)  # list d (m x n)
        dxlogpull = self.base_distribution.grad_x_log_pdf(
            xval, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache)  # (m x d) array
        B = np.zeros((m, self.transport_map.n_coeffs))
        start = 0
        for j, ah in enumerate(action_hess_list):
            stop = start + ah.shape[1]
            B[:, start:stop] = dxlogpull[:, [j]] * ah
            start = stop

        # Add Hessian of the log determinant term
        C = self.transport_map.action_hess_a_log_det_grad_x(
            x, da, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        return A + B + C
