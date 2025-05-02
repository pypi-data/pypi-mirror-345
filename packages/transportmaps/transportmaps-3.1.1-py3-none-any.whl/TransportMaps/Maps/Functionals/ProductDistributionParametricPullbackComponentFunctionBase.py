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

from TransportMaps.Misc import cached, counted, get_sub_cache
from .ParametricFunctionalBase import \
    ParametricFunctional

__all__ = ['ProductDistributionParametricPullbackComponentFunction']

nax = np.newaxis


class ProductDistributionParametricPullbackComponentFunction(
        ParametricFunctional
):
    r""" Parametric function :math:`f[{\bf a}](x_{1:k}) = \log\pi\circ T_k[{\bf a}](x_{1:k}) + \log\partial_{x_k}T_k[{\bf a}](x_{1:k})`

    Args:
      transport_map_component (MonotonicFunctionApproximation): component :math:`T_k`
        of monotone map :math:`T`
      base_distribution (Distribution): distribution :math:`\pi`
    """
    def __init__(self, transport_map_component, base_distribution):
        if base_distribution.dim != 1:
            raise AttributeError("The dimension of the distribution must be 1")
        super(ProductDistributionParametricPullbackComponentFunction,
              self).__init__(transport_map_component.dim_in)
        self.tmap_component = transport_map_component
        self.base_distribution = base_distribution

    @property
    def coeffs(self):
        r""" Get the coefficients :math:`{\bf a}` of the function

        .. seealso:: :func:`ParametricFunctionApproximation.coeffs`
        """
        return self.tmap_component.coeffs

    @property
    def n_coeffs(self):
        r""" Get the number :math:`N` of coefficients
        
        .. seealso:: :func:`ParametricFunctionApproximation.n_coeffs`
        """
        return self.tmap_component.n_coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients :math:`{\bf a}` of the distribution

        .. seealso:: :func:`ParametricFunctionApproximation.coeffs`
        """
        self.tmap_component.coeffs = coeffs

    @cached([('pi',None), ('ti',None)])
    @counted
    def evaluate(self, x, params={}, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`f[{\bf a}](x_{1:k})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,k`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cached values

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1`]) -- evaluations
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        params_pi = params.get('params_pi')
        params_ti = params.get('params_t')
        # Retrieve cache
        pi_cache, ti_cache = get_sub_cache(cache, ('pi',None), ('ti',None))
        # Evaluate
        ev = self.tmap_component.evaluate(
            x, params_ti, idxs_slice=idxs_slice,
            cache=ti_cache)[:,0]
        lpdf = self.base_distribution.log_pdf(ev[:,nax], params_pi, cache=pi_cache)
        lgxd = np.log( self.tmap_component.partial_xd(
            x, params_ti, idxs_slice=idxs_slice, cache=ti_cache)[:,0] )
        return (lpdf + lgxd)[:,nax]

    @cached([('pi',None), ('ti',None)])
    @counted
    def grad_a(self, x, params={}, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla_{\bf a}f[{\bf a}](x_{1:k})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,k`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cached values

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,n`]) -- evaluations
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        params_pi = params['params_pi']
        params_ti = params['params_t']
        # Retrieve cache
        pi_cache, ti_cache = get_sub_cache(cache, ('pi',None), ('ti',None))
        # Evaluate
        ev = self.tmap_component.evaluate(
            x, params_ti, idxs_slice=idxs_slice, cache=ti_cache)[:,0]
        gxlpdf = self.base_distribution.grad_x_log_pdf(
            ev[:,nax], params_pi, cache=pi_cache)[:,0]
        ga = self.tmap_component.grad_a(
            x, params_ti, idxs_slice=idxs_slice, cache=ti_cache)[:,0,:]
        gxd = self.tmap_component.partial_xd(
            x, params_ti, idxs_slice=idxs_slice, cache=ti_cache)[:,0]
        gagxd = self.tmap_component.grad_a_partial_xd(
            x, params_ti, idxs_slice=idxs_slice, cache=ti_cache)[:,0,:]
        out = gxlpdf[:,nax] * ga + gagxd / gxd[:,nax]
        return out[:,nax,:]

    @cached([('pi',None), ('ti',None)], False)
    @counted
    def hess_a(self, x, params={}, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla^2_{\bf a}f[{\bf a}](x_{1:k})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,k`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cached values

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,n,n`]) -- evaluations
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        params_pi = params.get('params_pi')
        params_ti = params.get('params_t')
        # Retrieve cache
        pi_cache, ti_cache = get_sub_cache(cache, ('pi',None), ('ti',None))
        # Evaluate
        # First term
        ev = self.tmap_component.evaluate(
            x, params_ti, idxs_slice=idxs_slice, cache=ti_cache)[:,0]
        hxlpdf = self.base_distribution.hess_x_log_pdf(
            ev[:,nax], params_pi, cache=pi_cache)[:,0,0]
        ga = self.tmap_component.grad_a(
            x, params_ti, idxs_slice=idxs_slice, cache=ti_cache)[:,0,:]
        t1 = ga[:,nax,:] * ga[:,:,nax]
        t1 *= hxlpdf[:,nax,nax]
        # Second term
        gxlpdf = self.base_distribution.grad_x_log_pdf(
            ev[:,nax], params_pi, cache=pi_cache)[:,0]
        ha = self.tmap_component.hess_a(
            x, params_ti, idxs_slice=idxs_slice, cache=ti_cache)[:,0,:,:]
        t2 = gxlpdf[:,nax,nax] * ha
        # Third term
        gxd = self.tmap_component.partial_xd(
            x, params_ti, idxs_slice=idxs_slice, cache=ti_cache)[:,0]
        hagxd = self.tmap_component.hess_a_partial_xd(
            x, params_ti, idxs_slice=idxs_slice, cache=ti_cache)[:,0,:,:]
        t3 = hagxd / gxd[:,nax,nax]
        # Fourth term
        gagxd = self.tmap_component.grad_a_partial_xd(
            x, params_ti, idxs_slice=idxs_slice, cache=ti_cache)[:,0,:]
        t4 = (gagxd[:,nax,:] * gagxd[:,:,nax]) / gxd[:,nax,nax]**2
        # Output
        out = t1 + t2 + t3 - t4
        return out[:,nax,:,:]

    def grad_x(self, x, params={}, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf x} \log T_{k}^\sharp \pi({\bf x_{1:k}})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,k`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,k`]) -- values of
            :math:`\nabla_{\bf x} \log T_{k}^\sharp \pi` at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_ti = params['params_t']
        except (KeyError,TypeError):
            idxs_slice = slice(None)
            params_ti = None
        ev = self.tmap_component.evaluate(x, params_ti, idxs_slice)[:,0]
        gxlpdf = self.base_distribution.grad_x_log_pdf(ev[:,nax], params_pi)[:,0]
        gx = self.tmap_component.grad_x(x, params_ti, idxs_slice)[:,0,:]
        gxd = self.tmap_component.partial_xd(x, params_ti, idxs_slice)[:,0]
        gxgxd = self.tmap_component.grad_x_partial_xd(x, params_ti, idxs_slice)[:,0,:]
        out = gxlpdf[:,nax] * gx + gxgxd / gxd[:,nax]
        return out[:,nax,:]

    def hess_x(self, x, params={}, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla^2_{\bf x} \log T_{k}^\sharp \pi({\bf x_{1:k}})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,k`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,k,k`]) -- values of
            :math:`\nabla^2_{\bf x} \log T_{k}^\sharp \pi` at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_ti = params['params_t']
        except (KeyError,TypeError):
            idxs_slice = slice(None)
            params_ti = None
        # First term
        ev = self.tmap_component.evaluate(x, params_ti, idxs_slice)[:,0]
        hxlpdf = self.base_distribution.hess_x_log_pdf(ev[:,nax], params_pi)[:,0,0]
        gx = self.tmap_component.grad_x(x, params_ti, idxs_slice)[:,0,:]
        t1 = gx[:,nax,:] * gx[:,:,nax]
        t1 *= hxlpdf[:,nax,nax]
        # Second term
        gxlpdf = self.base_distribution.grad_x_log_pdf(ev[:,nax], params_pi)[:,0]
        hx = self.tmap_component.hess_x(x, params_ti, idxs_slice)[:,0,:,:]
        t2 = gxlpdf[:,nax,nax] * hx
        # Third term
        gxd = self.tmap_component.partial_xd(x, params_ti, idxs_slice)[:,0]
        hxgxd = self.tmap_component.hess_x_partial_xd(x, params_ti, idxs_slice)[:,0,:,:]
        t3 = hxgxd / gxd[:,nax,nax]
        # Fourth term
        gxgxd = self.tmap_component.grad_x_partial_xd(x, params_ti, idxs_slice)[:,0,:]
        t4 = (gxgxd[:,nax,:] * gxgxd[:,:,nax]) / gxd[:,nax,nax]**2
        # Output
        out = t1 + t2 + t3 - t4
        return out[:,nax,:,:]

    def grad_a_hess_x(self, x, params={}, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf a} \nabla^2_{\bf x} \log T_{k}^\sharp \pi({\bf x_{1:k}})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,k`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,n,k,k`]) -- values of
            :math:`\nabla^2_{\bf x} \log T_{k}^\sharp \pi` at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_ti = params['params_t']
        except (KeyError,TypeError):
            idxs_slice = slice(None)
            params_ti = None

        # check if base distribution is standard normal
        from TransportMaps.Distributions.FrozenDistributions \
            import StandardNormalDistribution
        if issubclass(type(self.base_distribution),
                      StandardNormalDistribution) == False:
            raise NotImplementedError('Base distribution must be standard normal')

        # First term
        ev = self.tmap_component.evaluate(x, params_ti, idxs_slice)[:,0]
        hxlpdf = self.base_distribution.hess_x_log_pdf(ev[:,nax], params_pi)[:,0,0]
        gx = self.tmap_component.grad_x(x, params_ti, idxs_slice)[:,0,:]
        gagx = self.tmap_component.grad_a_grad_x(x, params_ti, idxs_slice)[:,0,:,:]
        t1 = hxlpdf[:,nax,nax,nax]*gagx[:,:,:,nax]*gx[:,nax,nax,:]

        # Second term
        t2 = hxlpdf[:,nax,nax,nax]*gagx[:,:,nax,:]*gx[:,nax,:,nax]
        
        # Third term
        ga = self.tmap_component.grad_a(x, params_ti, idxs_slice)[:,0,:]
        hx = self.tmap_component.hess_x(x, params_ti, idxs_slice)[:,0,:,:]
        t3 = hxlpdf[:,nax,nax,nax]*ga[:,:,nax,nax]*hx[:,nax,:,:]

        # Fourth term
        gxlpdf = self.base_distribution.grad_x_log_pdf(ev[:,nax], params_pi)[:,0]
        gahx = self.tmap_component.grad_a_hess_x(x, params_ti, idxs_slice)[:,0,:,:,:]
        t4 = gxlpdf[:,nax,nax,nax]*gahx

        # Fifth term (log det term)
        # Compute grad_a_hess_x_sum
        a = self.tmap_component
        dxk = a.partial_xd(x)[:,0]
        dadx2dxk = a.grad_a_hess_x_partial_xd(x)[:,0,:,:,:]
        dadxk    = a.grad_a_partial_xd(x)[:,0,:]
        dadxdxk  = a.grad_a_grad_x_partial_xd(x)[:,0,:,:]
        dx2dxk   = a.hess_x_partial_xd(x)[:,0,:,:]
        dxdxkT   = a.grad_x_partial_xd(x)[:,0,:]
        dxdxkT2  = dxdxkT[:,nax,:,nax] * dxdxkT[:,nax,nax,:]
        B = dadxdxk[:,:,:,nax]*dxdxkT[:,nax,nax,:]
        t5 = (dadx2dxk / dxk[:,nax,nax,nax]) - \
                (dx2dxk[:,nax,:,:]*dadxk[:,:,nax,nax])/(dxk**2.)[:,nax,nax,nax] - \
                (B + B.transpose((0,1,3,2)))/(dxk**2.)[:,nax,nax,nax] + \
                2*(dxdxkT2*dadxk[:,:,nax,nax])/(dxk**3.)[:,nax,nax,nax]

        # Output 
        out = t1 + t2 + t3 + t4 + t5
        return out[:,nax,:,:,:]
