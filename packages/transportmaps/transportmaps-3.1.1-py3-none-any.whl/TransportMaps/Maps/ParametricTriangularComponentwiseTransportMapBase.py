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

from ..Misc import \
    required_kwargs, \
    counted, cached, get_sub_cache

from .Functionals import \
    ParametricFunctionApproximation
from .ParametricTriangularComponentwiseMapBase import ParametricTriangularComponentwiseMap
from .ParametricComponentwiseTransportMapBase import ParametricComponentwiseTransportMap
from .TriangularComponentwiseTransportMapBase import TriangularComponentwiseTransportMap

__all__ = [
    'ParametricTriangularComponentwiseTransportMap'
]

nax = np.newaxis


class ParametricTriangularComponentwiseTransportMap(
        ParametricTriangularComponentwiseMap,
        ParametricComponentwiseTransportMap,
        TriangularComponentwiseTransportMap
):
    r""" Triangular transport map :math:`T[{\bf a}_{1:d_x}]({\bf x})=[T_1[{\bf a}_1], \ldots,T_{d_x}[{\bf a}_{d_x}]]^\top`, where :math:`T_i[{\bf a}_i]({\bf x}):\mathbb{R}^{n_i}\times\mathbb{R}^{d_x}\rightarrow\mathbb{R}`.
    """
    @required_kwargs('active_vars', 'approx_list')
    def __init__(self, **kwargs):
        r"""
        Args:
          active_vars (:class:`list<list>` [:math:`d_x`] of :class:`list<list>`): for
            each dimension lists the active variables.
          approx_list (:class:`list<list>` [:math:`d_x`] of :class:`ParametricMonotoneFunctional<TransportMaps.Maps.Functionals.ParametricMonotoneFunctional>`):
            list of monotone functional approximations for each dimension
        """
        super(ParametricTriangularComponentwiseTransportMap,self).__init__(**kwargs)

    @cached([('components','dim_out')])
    @counted
    def grad_a_partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`[\nabla_{\bf a}\partial_{{\bf x}_k} T_k]_k`

        This is

        .. math::

           \left[ \begin{array}{ccccc}
             \nabla_{{\bf a}_1}\partial_{{\bf x}_1}T_1 & 0 & \cdots & & 0 \\
             0 \nabla_{{\bf a}_2}\partial_{{\bf x}_2}T_2 & 0 & \cdots & 0 \\
             \vdots & \ddots & & & \\
             0 & & \cdots & 0 & \nabla_{{\bf a}_d}\partial_{{\bf x}_d}T_d
           \end{array} \right]
        
        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict<dict>`): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`[\partial_{{\bf x}_1}T_1({\bf x}_1,{\bf a}^{(1)}),\ldots,\partial_{{\bf x}_d}T_d({\bf x}_{1:d},{\bf a}^{(d)})]` at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        # Init sub-cache if necessary
        comp_cache = get_sub_cache(cache, ('components',self.dim_out))
        # Evaluate
        self.precomp_partial_xd(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.dim_out, self.n_coeffs))
        start = 0
        for k,(a,avar,p, c) in enumerate(zip(self.approx_list,self.active_vars,
                                             precomp['components'], comp_cache)):
            gapxd = a.grad_a_partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)[:,0,:]
            stop = start + gapxd.shape[1]
            out[:,k,start:stop] = gapxd
            start = stop
        return out

    @cached([('components','dim_out')])
    @counted
    def grad_a_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`\nabla_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict<dict>`): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
             :math:`\nabla_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
             at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x`
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        # Init sub-cache if necessary
        comp_cache = get_sub_cache(cache, ('components',self.dim_out))
        # Evaluate
        self.precomp_partial_xd(x, precomp)
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.n_coeffs))
        start = 0
        for k,(a,avar,p, c) in enumerate(zip(self.approx_list,self.active_vars,
                                             precomp['components'], comp_cache)):
            pxd = a.partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)[:,0]
            gapxd = a.grad_a_partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)[:,0,:]
            # Evaluate
            stop = start + gapxd.shape[1]
            out[:,start:stop] = gapxd / pxd[:,nax]
            start = stop
        return out

    @cached([('components','dim_out')],False)
    @counted
    def hess_a_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`\nabla^2_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict<dict>`): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,N,N`]) --
           :math:`\nabla^2_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_a_log_det_grad_x`
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        # Init sub-cache if necessary
        comp_cache = get_sub_cache(cache, ('components',self.dim_out))
        # Evaluate
        self.precomp_partial_xd(x, precomp)
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.n_coeffs, self.n_coeffs))
        start = 0
        for k,(a,avar,p, c) in enumerate(zip(self.approx_list,self.active_vars,
                                             precomp['components'], comp_cache)):
            pxd = a.partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)[:,0]
            gapxd = a.grad_a_partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)[:,0,:]
            # Evaluate
            stop = start + gapxd.shape[1]
            out[:,start:stop,start:stop] = \
                a.hess_a_partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)[:,0,:,:] \
                * (1./pxd)[:,nax,nax]
            pxd2 = pxd**2.
            pxd2[pxd2<=1e-14] = 1e-14
            out[:,start:stop,start:stop] -= (gapxd[:,:,nax] * gapxd[:,nax,:]) \
                                            * (1./pxd2)[:,nax,nax]
            start = stop
        return out

    @cached([('components','dim_out')],False)
    @counted
    def action_hess_a_log_det_grad_x(self, x, da, precomp=None,
                                     idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`\langle\nabla^2_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a}), \delta{\bf a}\rangle`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          da (:class:`ndarray<numpy.ndarray>` [:math:`N`]): direction
            on which to evaluate the Hessian
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict<dict>`): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
           :math:`\langle\nabla^2_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a}), \delta{\bf a}\rangle`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_a_log_det_grad_x`
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        # Init sub-cache if necessary
        comp_cache = get_sub_cache(cache, ('components',self.dim_out))
        # Evaluate
        self.precomp_partial_xd(x, precomp)
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.n_coeffs))
        start = 0
        for k,(a,avar,p, c) in enumerate(zip(self.approx_list,self.active_vars,
                                             precomp['components'], comp_cache)):
            pxd = a.partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)[:,0]
            gapxd = a.grad_a_partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)[:,0,:]
            # Evaluate
            stop = start + gapxd.shape[1]
            hapxd = a.hess_a_partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)[:,0,:,:]
            out[:,start:stop] = np.einsum('...ij,j->...i', hapxd, da[start:stop]) \
                                * (1./pxd)[:,nax]
            pxd2 = pxd**2.
            pxd2[pxd2<=1e-14] = 1e-14
            tmp = np.dot(gapxd, da[start:stop])
            out[:,start:stop] -= gapxd * tmp[:,nax] * (1./pxd2)[:,nax]
            start = stop
        return out

    @counted
    def grad_a_hess_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None),
                                     *args, **kwargs):
        r""" Compute: :math:`\nabla_{\bf a}\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           :math:`\nabla_{\bf a}\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        self.precomp_hess_x_partial_xd(x, precomp)
        out = np.zeros((x.shape[0], self.n_coeffs, self.dim, self.dim))
        start = 0
        for k,(a,avar,p) in enumerate(zip(self.approx_list, self.active_vars,
                                          precomp['components'])):

            # Compute grad_a_hess_x_sum
            dxk = a.partial_xd(x[:,avar],p)[:,0]
            dadx2dxk = a.grad_a_hess_x_partial_xd(x[:,avar],p)[:,0,:,:,:]
            dadxk    = a.grad_a_partial_xd(x[:,avar],p)[:,0,:]
            dadxdxk  = a.grad_a_grad_x_partial_xd(x[:,avar],p)[:,0,:,:]
            dx2dxk   = a.hess_x_partial_xd(x[:,avar],p)[:,0,:,:]
            dxdxkT   = a.grad_x_partial_xd(x[:,avar], p)[:,0,:]
            dxdxkT2  = dxdxkT[:,nax,:,nax] * dxdxkT[:,nax,nax,:]
            B = dadxdxk[:,:,:,nax]*dxdxkT[:,nax,nax,:]
            grad_a_hess_x_sum = (dadx2dxk / dxk[:,nax,nax,nax]) - \
                    (dx2dxk[:,nax,:,:]*dadxk[:,:,nax,nax])/(dxk**2.)[:,nax,nax,nax] - \
                    (B + B.transpose((0,1,3,2)))/(dxk**2.)[:,nax,nax,nax] + \
                    2*(dxdxkT2*dadxk[:,:,nax,nax])/(dxk**3.)[:,nax,nax,nax]

            # 2d numpy advanced indexing
            nvar = len(avar)
            stop  = start + dadxk.shape[1]
            tmp = 0
            for coeff_idx in range(start, stop):

                rr,cc = np.meshgrid(avar, avar)
                rr = list( rr.flatten() )
                cc = list( cc.flatten() )

                # Find index for coefficients and assign to out
                idxs  = (slice(None), coeff_idx, rr, cc)
                out[idxs] += grad_a_hess_x_sum[:,tmp,:,:].reshape((x.shape[0], nvar**2))
                tmp = tmp + 1

            start = stop

        return out

    @counted
    def grad_a_inverse(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf a} T^{-1}({\bf x},{\bf a})`

        By the definition of the transport map :math:`T({\bf x},{\bf a})`,
        the components :math:`T_1 ({\bf x}_1, {\bf a}^{(1)})`,
        :math:`T_2 ({\bf x}_{1:2}, {\bf a}^{(2)})`, ...
        are defined by different sets of parameters :math:`{\bf a}^{(1)}`,
        :math:`{\bf a}^{(2)}`, etc.

        Differently from :func:`grad_a`,
        :math:`\nabla_{\bf a} T^{-1}({\bf x},{\bf a})`
        is not block diagonal, but only lower block triangular
        Consequentely this function will return the full gradient.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,N`]) --
              :math:`\nabla_{\bf a} T^{-1}({\bf x},{\bf a})`

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        try:
            xinv = precomp['xinv']
        except (TypeError, KeyError):
            xinv = self.inverse(x, precomp)
        gx = self.grad_x(xinv, precomp) # Lower triangular
        ga = self.grad_a(xinv, precomp) # List of diagonal blocks
        out = np.zeros((xinv.shape[0],self.dim,self.n_coeffs))
        rhs = np.zeros((self.dim, self.n_coeffs))
        for i in range(xinv.shape[0]):
            start = 0
            for d, gad in enumerate(ga):
                rhs[d,start:start+gad.shape[1]] = gad[i,:]
                start += gad.shape[1]
            out[i,:,:] = - scila.solve_triangular(gx[i,:,:], rhs, lower=True)
        return out

    def precomp_minimize_kl_divergence(self, x, params, precomp_type='uni'):
        r""" Precompute necessary structures for the speed up of :func:`minimize_kl_divergence`

        Enriches the dictionaries in the ``precomp`` list if necessary.
        
        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters to be updated
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'

        Returns:
           (:class:`tuple<tuple>` (None,:class:`dict<dict>`)) -- dictionary of necessary
              strucutres. The first argument is needed for consistency with 
        """
        # Fill precomputed Vandermonde matrices etc.
        self.precomp_evaluate(x, params['params_t'], precomp_type)
        self.precomp_partial_xd(x, params['params_t'], precomp_type)

    def allocate_cache_minimize_kl_divergence(self, x):
        r""" Allocate cache space for the KL-divergence minimization

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
        """
        cache = {'tot_size': x.shape[0]}
        return (cache, )

    def reset_cache_minimize_kl_divergence(self, cache):
        r""" Reset the cache space for the KL-divergence minimization

        Args:
          cache (dict): dictionary of cached values
        """
        tot_size = cache['tot_size']
        cache.clear()
        cache['tot_size'] = tot_size

    def get_default_init_values_minimize_kl_divergence(self):
        raise NotImplementedError("To be implemented in sub-classes")

    # def minimize_kl_divergence_complete(self, d1, d2,
    #                                     x=None, w=None,
    #                                     params_d1=None, params_d2=None,
    #                                     x0=None,
    #                                     regularization=None,
    #                                     tol=1e-4, maxit=100, ders=2,
    #                                     fungrad=False, hessact=False,
    #                                     precomp_type='uni',
    #                                     batch_size=None,
    #                                     mpi_pool=None,
    #                                     grad_check=False, hess_check=False):
    #     r"""
    #     Computes :math:`{\bf a}^* = \arg\min_{\bf a}\mathcal{D}_{KL}\left(\pi_1, \pi_{2,{\bf a}}\right)`
    #     for non-product distributions.

    #     .. seealso:: :fun:`TriangularTransportMap.minimize_kl_divergence` for a description of the parameters
    #     """    
    #     self.logger.debug("minimize_kl_divergence(): Precomputation started")

    #     # Distribute objects
    #     d2_distr = pickle.loads( pickle.dumps(d2) )
    #     d2_distr.reset_counters() # Reset counters on copy to avoid couting twice
    #     mpi_bcast_dmem(d2=d2_distr, mpi_pool=mpi_pool)

    #     # Set mpi_pool in the object
    #     if batch_size is None:
    #         batch_size = [None] * 3
    #     self.logger.debug("minimize_kl_divergence(): batch sizes: %s" % str(batch_size))

    #     # Link tm to d2.transport_map
    #     def link_tm_d2(d2):
    #         return (d2.transport_map,)
    #     (tm,) = mpi_map_alloc_dmem(
    #             link_tm_d2, dmem_key_in_list=['d2'], dmem_arg_in_list=['d2'],
    #             dmem_val_in_list=[d2], dmem_key_out_list=['tm'],
    #             mpi_pool=mpi_pool)

    #     from TransportMaps.Distributions.TransportMapDistributions import \
    #         PullBackTransportMapDistribution, PushForwardTransportMapDistribution
    #     if isinstance(d2, PullBackTransportMapDistribution):
    #         # Init memory
    #         params2 = {
    #             'params_pi': params_d2,
    #             'params_t': {'components': [{} for i in range(self.dim)]} }
    #         mpi_bcast_dmem(params2=params2, mpi_pool=mpi_pool)
            
    #         # precomp_minimize_kl_divergence
    #         bcast_tuple = (['precomp_type'],[precomp_type])
    #         mpi_map("precomp_minimize_kl_divergence",
    #                 bcast_tuple=bcast_tuple,
    #                 dmem_key_in_list=['params2', 'x'],
    #                 dmem_arg_in_list=['params', 'x'],
    #                 dmem_val_in_list=[params2, x],
    #                 obj='tm', obj_val=tm,
    #                 mpi_pool=mpi_pool, concatenate=False)
    #     elif isinstance(d2, PushForwardTransportMapDistribution):
    #         # Init memory
    #         params2 = { 'params_pi': params_d2,
    #                     'params_t': {} }
    #         mpi_bcast_dmem(params2=params2, mpi_pool=mpi_pool)
    #     else:
    #         raise AttributeError("Not recognized distribution type")
    #     # allocate cache
    #     (cache, ) = mpi_map_alloc_dmem(
    #         "allocate_cache_minimize_kl_divergence",
    #         dmem_key_in_list=['x'],
    #         dmem_arg_in_list=['x'],
    #         dmem_val_in_list=[x],
    #         dmem_key_out_list=['cache'],
    #         obj='tm', obj_val=tm,
    #         mpi_pool=mpi_pool, concatenate=False)        
    #     self.logger.debug("minimize_kl_divergence(): Precomputation ended")
    #     params = {}
    #     params['nobj'] = 0
    #     params['nda_obj'] = 0
    #     params['nda2_obj'] = 0
    #     params['nda2_obj_dot'] = 0
    #     params['x'] = x
    #     params['w'] = w
    #     params['d1'] = d1
    #     params['d2'] = d2
    #     params['params1'] = params_d1
    #     params['params2'] = params2
    #     params['cache'] = cache
    #     params['batch_size'] = batch_size
    #     params['regularization'] = regularization
    #     params['grad_check'] = grad_check
    #     params['hess_check'] = hess_check
    #     params['hess_assembled'] = False
    #     params['mpi_pool'] = mpi_pool

    #     if x0 is None:
    #         x0 = self.get_default_init_values_minimize_kl_divergence()

    #     params['objective_cache_coeffs'] = x0 - 1.

    #     # Callback variables
    #     self.it_callback = 0
    #     self.ders_callback = ders
    #     self.params_callback = params

    #     # Options for optimizer
    #     options = {'maxiter': maxit,
    #                'disp': False}

    #     if ders >= 1:
    #         if fungrad:
    #             fun = self.minimize_kl_divergence_tuple_grad_a_objective
    #             jac = True
    #         else:
    #             fun = self.minimize_kl_divergence_objective
    #             jac = self.minimize_kl_divergence_grad_a_objective
        
    #     # Solve
    #     self.logger.info("Gradient norm tolerance set to "+str(tol))
    #     if ders == 0:
    #         self.logger.info("Starting BFGS without user provided Jacobian")
    #         options['norm'] = np.inf
    #         res = sciopt.minimize(
    #             self.minimize_kl_divergence_objective,
    #             args=params, x0=x0, method='BFGS', tol=tol,
    #             options=options, callback=self.minimize_kl_divergence_callback)
    #     elif ders == 1:
    #         self.logger.info("Starting BFGS with user provided Jacobian")
    #         # options['norm'] = np.inf
    #         options['norm'] = 2
    #         res = sciopt.minimize(
    #             fun, args=params, x0=x0, jac=jac, method='BFGS',
    #             tol=tol, options=options,
    #             callback=self.minimize_kl_divergence_callback)
    #     elif ders == 2:
    #         if hessact:
    #             self.logger.info("Starting Newton-CG with user provided action of Hessian")
    #             res = sciopt.minimize(
    #                 fun, args=params, x0=x0, jac=jac,
    #                 hessp=self.minimize_kl_divergence_action_hess_a_objective,
    #                 method='Newton-CG', tol=tol, options=options,
    #                 callback=self.minimize_kl_divergence_callback)
    #         else:
    #             self.logger.info("Starting Newton-CG with user provided Hessian")
    #             res = sciopt.minimize(
    #                 fun, args=params, x0=x0, jac=jac,
    #                 hessp=self.minimize_kl_divergence_action_storage_hess_a_objective,
    #                 method='Newton-CG', tol=tol, options=options,
    #                 callback=self.minimize_kl_divergence_callback)

    #     # Clean up callback stuff
    #     del self.it_callback
    #     del self.ders_callback
    #     del self.params_callback

    #     # Get d2 from children processes and update counters
    #     if mpi_pool is not None:
    #         d2_child_list = mpi_pool.get_dmem('d2')
    #         d2.update_ncalls_tree( d2_child_list[0][0] )
    #         for (d2_child,) in d2_child_list:
    #             d2.update_nevals_tree(d2_child)
    #             d2.update_teval_tree(d2_child)

    #     # Log
    #     log = {}
    #     log['success'] = res['success']
    #     log['message'] = res['message']
    #     log['fval'] = res['fun']
    #     log['nit'] = res['nit']
    #     log['n_fun_ev'] = params['nobj']
    #     if ders >= 1:
    #         log['n_jac_ev'] = params['nda_obj']
    #         log['jac'] = res['jac']
    #     if ders >= 2:
    #         log['n_hess_ev'] = params['nda2_obj']
            
    #     # Attach cache to log
    #     if mpi_pool is None:
    #         log['cache'] = cache
    #     else:
    #         log['cache'] = [ t[0] for t in mpi_pool.get_dmem('cache') ]
            
    #     # Display stats
    #     if log['success']:
    #         self.logger.info("minimize_kl_divergence: Optimization terminated successfully")
    #     else:
    #         self.logger.warn("minimize_kl_divergence: Minimization of KL-divergence failed.")
    #         self.logger.warn("minimize_kl_divergence: Message: %s" % log['message'])
    #     self.logger.info("minimize_kl_divergence:   Function value: %e" % log['fval'])
    #     if ders >= 1:
    #         self.logger.info(
    #             "minimize_kl_divergence:   Jacobian " + \
    #             "2-norm: %e " % npla.norm(log['jac'],2) + \
    #             "inf-norm: %e" % npla.norm(log['jac'],np.inf)
    #         )
    #     self.logger.info("minimize_kl_divergence:   Number of iterations:    %6d" % log['nit'])
    #     self.logger.info("minimize_kl_divergence:   N. function evaluations: %6d" % log['n_fun_ev'])
    #     if ders >= 1:
    #         self.logger.info(
    #             "minimize_kl_divergence:   N. Jacobian evaluations: %6d" % log['n_jac_ev'])
    #     if ders >= 2:
    #         self.logger.info(
    #             "minimize_kl_divergence:   N. Hessian evaluations:  %6d" % log['n_hess_ev'])
            
    #     # Clear mpi_pool and detach object
    #     if mpi_pool is not None:
    #         mpi_pool.clear_dmem()
        
    #     # Set coefficients
    #     d2.coeffs = res['x']
    #     return log
