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

import logging
import pickle
from typing import Union, List

import numpy as np
import numpy.linalg as npla
import scipy.optimize as sciopt

from .KL_divergence import kl_divergence, grad_a_kl_divergence, tuple_grad_a_kl_divergence, hess_a_kl_divergence, \
    action_hess_a_kl_divergence, storage_hess_a_kl_divergence, action_stored_hess_a_kl_divergence, \
    kl_divergence_component, grad_a_kl_divergence_component, hess_a_kl_divergence_component
from ..DerivativesChecks import fd as finite_difference
from ..MPI import mpi_map, distributed_sampling, mpi_map_alloc_dmem, \
    mpi_bcast_dmem, SumChunkReduce, TupleSumChunkReduce
from ..Distributions import Distribution, \
    PullBackTransportMapDistribution, \
    PushForwardTransportMapDistribution, \
    ParametricTransportMapDistribution, \
    ProductDistribution
from ..Maps import ParametricComponentwiseMap
from ..Maps.Functionals import ProductDistributionParametricPullbackComponentFunction


__all__ = [
    # Minimize KL divergence
    'minimize_kl_divergence',
    # Minimize KL divergence objectives
    'minimize_kl_divergence_objective',
    'minimize_kl_divergence_grad_a_objective',
    'minimize_kl_divergence_tuple_grad_a_objective',
    'minimize_kl_divergence_hess_a_objective',
    'minimize_kl_divergence_action_hess_a_objective',
    'minimize_kl_divergence_action_storage_hess_a_objective',
    # Minimize KL divergence component for product target distributions
    'minimize_kl_divergence_component',
    # Minimize KL divergence component objectives
    'minimize_kl_divergence_component_objective',
    'minimize_kl_divergence_component_grad_a_objective',
    'minimize_kl_divergence_component_hess_a_objective',
    # Minimize KL divergence for pointwise monotone maps
    'minimize_kl_divergence_pointwise_monotone',
    # Constraints
    'minimize_kl_divergence_pointwise_monotone_constraints',
    'minimize_kl_divergence_pointwise_monotone_da_constraints',
    # Minimize KL divergence for pointwise monotone maps component for product target distributions
    'minimize_kl_divergence_pointwise_monotone_component',
    # Constraints
    'minimize_kl_divergence_pointwise_monotone_component_constraints',
    'minimize_kl_divergence_pointwise_monotone_component_da_constraints'
]

nax = np.newaxis


def generate_quadrature(
        d1: Distribution,
        x, w,
        qtype, qparams,
        mpi_pool
):
    if (x is None) and (w is None):
        if qtype == 0: # Sample separately on the cores (lower memory)
            (x, w) = distributed_sampling(
                d1, 0, qparams, mpi_pool=mpi_pool)
        else:
            (x, w) = d1.quadrature(qtype, qparams, mpi_pool=mpi_pool)
            def alloc_quadrature(x, w):
                return (x, w)
            (x, w) = mpi_map_alloc_dmem(
                alloc_quadrature,
                scatter_tuple=(['x','w'],[x,w]),
                dmem_key_out_list=['x', 'w'],
                mpi_pool=mpi_pool)
    else:
        def alloc_quadrature(x, w):
            return (x, w)
        (x, w) = mpi_map_alloc_dmem(
            alloc_quadrature,
            scatter_tuple=(['x','w'],[x,w]),
            dmem_key_out_list=['x', 'w'],
            mpi_pool=mpi_pool)
    return x, w


def minimize_kl_divergence(
        d1: Distribution,
        d2: ParametricTransportMapDistribution,
        qtype: int = None, qparams=None,
        x=None, w=None,
        params_d1=None, params_d2=None,
        x0=None,
        regularization=None,
        method=None,
        tol=1e-4,
        maxit=100,
        ders=2,
        options=None,
        fungrad=False,
        hessact=False,
        precomp_type='uni',
        batch_size=None,
        mpi_pool=None,
        grad_check=False, hess_check=False
):
    r""" Solve :math:`\arg \min_{\bf a}\mathcal{D}_{KL}\left(\pi, (T^\sharp\pi_{\rm tar})_{\bf a}\right)`

    Args:
      d1: sampling distribution
      d2: target distribution :math:`\pi_{\rm tar}`
      qtype (int): quadrature type number provided by :math:`\pi`
      qparams (object): inputs necessary to the generation of the selected
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
      params_d1 (dict): parameters for the evaluation of :math:`\pi`
      params_d2 (dict): parameters for the evaluation of :math:`\pi_{\rm tar}`
      x0 (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients to be used
        as initial values for the optimization
      regularization (dict): defines the regularization to be used.
        If ``None``, no regularization is applied.
        If key ``type=='L2'`` then applies Tikonhov regularization with
        coefficient in key ``alpha``.
      method (str): optimization method to be used (see scipy.optimize.minimize)
        If ``None``, the default methods are defined depending on the derivative order provided:
        With ``ders==0`` it will use ``method='BFGS'``, with ``ders==1`` it will use ``method='BFGS'``,
        with ``ders==2`` it will use ``method='Newton-CG'``.
      tol (float): tolerance to be used to solve the KL-divergence problem.
      maxit (int): maximum number of iterations
      ders (int): order of derivatives available for the solution of the
        optimization problem. 0 -> derivative free, 1 -> gradient, 2 -> hessian.
      options (dict): options to be passed to the optimization method (see scipy.optimize.minimize)
      fungrad (bool): whether the target distribution provide the method
        :func:`Distribution.tuple_grad_x_log_pdf` computing the evaluation and the
        gradient in one step. This is used only for ``ders==1``.
      hessact (bool): use the action of the Hessian. The target distribution must
        implement the function :func:`Distribution.action_hess_x_log_pdf`.
      precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
        multivariate Vandermonde matrices 'multi'
      batch_size (:class:`list<list>` [3 or 2] of :class:`int<int>`):
        the list contains the
        size of the batch to be used for each iteration. A size ``1`` correspond
        to a completely non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one.
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processes
      grad_check (bool): whether to use finite difference to check the correctness of
        of the gradient
      hess_check (bool): whether to use finite difference to check the correctenss of
        the Hessian

    Returns:
      log (dict): log informations from the solver
    """
    if (
            (isinstance(mpi_pool, list) and any(p is not None for p in mpi_pool)) or
            (not isinstance(mpi_pool, list) and mpi_pool is not None)
    ):
        raise NotImplementedError("MPI support has been removed")

    d2.transport_map.logger.debug("minimize_kl_divergence(): generation of quadrature points")
    (x, w) = generate_quadrature(
        d1, x, w, qtype, qparams,
        mpi_pool[0] if isinstance(mpi_pool, list) else mpi_pool
    )

    if isinstance(d2, PullBackTransportMapDistribution) and \
            issubclass(type(d2.base_distribution), ProductDistribution) and \
            issubclass(type(d2.transport_map), ParametricComponentwiseMap):
        # The target distribution is a product distribution and the transportmap is"
        # defined componentwise.
        d2.transport_map.logger.debug("Componentwise minimization")
        if batch_size is None:
            batch_size_list = [None] * d2.transport_map.dim
        else:
            batch_size_list = batch_size
        if mpi_pool is None:
            mpi_pool_list = [None] * d2.transport_map.dim
        else:
            mpi_pool_list = mpi_pool
        log_list = []
        start_coeffs = 0
        (x, w) = generate_quadrature(d1, x, w, qtype, qparams, None)
        for i, (a, avars, batch_size, mpi_pool) in enumerate(zip(
                d2.transport_map.approx_list, d2.transport_map.active_vars,
                batch_size_list, mpi_pool_list)):
            f = ProductDistributionParametricPullbackComponentFunction(
                a, d2.base_distribution.get_component([i]))
            stop_coeffs = start_coeffs + a.n_coeffs
            sub_x0 = None if x0 is None else x0[start_coeffs:stop_coeffs]
            start_coeffs = stop_coeffs
            log = minimize_kl_divergence_component(
                f, x[:, avars], w, x0=sub_x0,
                regularization=regularization,
                tol=tol, maxit=maxit, ders=ders,
                fungrad=fungrad, precomp_type=precomp_type,
                batch_size=batch_size,
                mpi_pool=mpi_pool
            )
            log_list.append(log)
        return log_list

    d2.transport_map.logger.debug("minimize_kl_divergence(): Fully coupled minimization")
    d2.transport_map.logger.debug("minimize_kl_divergence(): Precomputation started")
    # Distribute objects
    d2.reset_counters()  # Reset counters on copy to avoid couting twice
    mpi_bcast_dmem(d2=d2, mpi_pool=mpi_pool)

    # Set mpi_pool in the object
    if batch_size is None:
        batch_size = [None] * 3
    d2.transport_map.logger.debug("minimize_kl_divergence(): batch sizes: %s" % str(batch_size))

    # Link tm to d2.transport_map
    def link_tm_d2(d2):
        return (d2.transport_map,)

    (tm,) = mpi_map_alloc_dmem(
        link_tm_d2, dmem_key_in_list=['d2'], dmem_arg_in_list=['d2'],
        dmem_val_in_list=[d2], dmem_key_out_list=['tm'],
        mpi_pool=mpi_pool)

    if isinstance(d2, PullBackTransportMapDistribution):
        # Init memory
        params2 = {
            'params_pi': params_d2,
            'params_t': {'components': [{} for i in range(d2.transport_map.dim)]}}
        mpi_bcast_dmem(params2=params2, mpi_pool=mpi_pool)

        # precomp_minimize_kl_divergence
        bcast_tuple = (['precomp_type'], [precomp_type])
        mpi_map("precomp_minimize_kl_divergence",
                bcast_tuple=bcast_tuple,
                dmem_key_in_list=['params2', 'x'],
                dmem_arg_in_list=['params', 'x'],
                dmem_val_in_list=[params2, x],
                obj='tm', obj_val=tm,
                mpi_pool=mpi_pool, concatenate=False)
    elif isinstance(d2, PushForwardTransportMapDistribution):
        # Init memory
        params2 = {'params_pi': params_d2,
                   'params_t': {}}
        mpi_bcast_dmem(params2=params2, mpi_pool=mpi_pool)
    else:
        raise AttributeError("Not recognized distribution type")
    # allocate cache
    (cache,) = mpi_map_alloc_dmem(
        "allocate_cache_minimize_kl_divergence",
        dmem_key_in_list=['x'],
        dmem_arg_in_list=['x'],
        dmem_val_in_list=[x],
        dmem_key_out_list=['cache'],
        obj='tm', obj_val=tm,
        mpi_pool=mpi_pool, concatenate=False)
    d2.transport_map.logger.debug("minimize_kl_divergence(): Precomputation ended")
    params = {}
    params['nobj'] = 0
    params['nda_obj'] = 0
    params['nda2_obj'] = 0
    params['nda2_obj_dot'] = 0
    params['x'] = x
    params['w'] = w
    params['d1'] = d1
    params['d2'] = d2
    params['params1'] = params_d1
    params['params2'] = params2
    params['cache'] = cache
    params['batch_size'] = batch_size
    params['regularization'] = regularization
    params['grad_check'] = grad_check
    params['hess_check'] = hess_check
    params['hess_assembled'] = False
    params['mpi_pool'] = mpi_pool

    if x0 is None:
        x0 = d2.transport_map.get_default_init_values_minimize_kl_divergence()

    params['objective_cache_coeffs'] = x0 - 1.

    # Callback variables
    d2.transport_map.it_callback = 0
    d2.transport_map.ders_callback = ders
    d2.transport_map.params_callback = params

    # Options for optimizer
    if options is None:
        options = {}
    options['maxiter'] = options.get('maxiter', maxit)
    options['disp'] = options.get('disp', False)

    if ders >= 1:
        if fungrad:
            fun = minimize_kl_divergence_tuple_grad_a_objective
            jac = True
        else:
            fun = minimize_kl_divergence_objective
            jac = minimize_kl_divergence_grad_a_objective

    # Solve
    d2.transport_map.logger.info("Gradient norm tolerance set to " + str(tol))
    if ders == 0:
        d2.transport_map.logger.info(f"Starting {method} without user provided Jacobian")
        if method is None:
            method = 'BFGS'
        if method == 'BFGS':
            options['norm'] = np.inf
        res = sciopt.minimize(
            minimize_kl_divergence_objective,
            args=params, x0=x0, method=method, tol=tol,
            options=options, callback=d2.transport_map.minimize_kl_divergence_callback)
    elif ders == 1:
        d2.transport_map.logger.info(f"Starting {method} with user provided Jacobian")
        if method is None:
            method = 'BFGS'
        if method == 'BFGS':
            options['norm'] = 2
        res = sciopt.minimize(
            fun, args=params, x0=x0, jac=jac, method=method,
            tol=tol, options=options,
            callback=d2.transport_map.minimize_kl_divergence_callback)
    elif ders == 2:
        if method is None:
            method = 'Newton-CG'
        if hessact:
            d2.transport_map.logger.info(f"Starting {method} with user provided action of Hessian")
            res = sciopt.minimize(
                fun, args=params, x0=x0, jac=jac,
                hessp=minimize_kl_divergence_action_hess_a_objective,
                method=method, tol=tol, options=options,
                callback=d2.transport_map.minimize_kl_divergence_callback)
        else:
            d2.transport_map.logger.info(f"Starting {method} with user provided Hessian")
            res = sciopt.minimize(
                fun, args=params, x0=x0, jac=jac,
                hessp=minimize_kl_divergence_action_storage_hess_a_objective,
                method=method, tol=tol, options=options,
                callback=d2.transport_map.minimize_kl_divergence_callback)
    else:
        raise ValueError("Value of ders must be one of [0, 1, 2]")

    # Clean up callback stuff
    del d2.transport_map.it_callback
    del d2.transport_map.ders_callback
    del d2.transport_map.params_callback

    # Get d2 from children processes and update counters
    if mpi_pool is not None:
        d2_child_list = mpi_pool.get_dmem('d2')
        d2.update_ncalls_tree(d2_child_list[0][0])
        for (d2_child,) in d2_child_list:
            d2.update_nevals_tree(d2_child)
            d2.update_teval_tree(d2_child)

    # Log
    log = {}
    log['success'] = res['success']
    log['message'] = res['message']
    log['fval'] = res['fun']
    log['nit'] = res.get('nit', res['fun'])
    log['n_fun_ev'] = params['nobj']
    if ders >= 1:
        log['n_jac_ev'] = params['nda_obj']
        log['jac'] = res['jac']
    if ders >= 2:
        log['n_hess_ev'] = params['nda2_obj']

    # Attach cache to log
    if mpi_pool is None:
        log['cache'] = cache
    else:
        log['cache'] = [t[0] for t in mpi_pool.get_dmem('cache')]

    # Display stats
    if log['success']:
        d2.transport_map.logger.info("minimize_kl_divergence: Optimization terminated successfully")
    else:
        d2.transport_map.logger.warn("minimize_kl_divergence: Minimization of KL-divergence failed.")
        d2.transport_map.logger.warn("minimize_kl_divergence: Message: %s" % log['message'])
    d2.transport_map.logger.info("minimize_kl_divergence:   Function value: %e" % log['fval'])
    if ders >= 1:
        d2.transport_map.logger.info(
            "minimize_kl_divergence:   Jacobian " + \
            "2-norm: %e " % npla.norm(log['jac'], 2) + \
            "inf-norm: %e" % npla.norm(log['jac'], np.inf)
        )
    d2.transport_map.logger.info("minimize_kl_divergence:   Number of iterations:    %6d" % log['nit'])
    d2.transport_map.logger.info("minimize_kl_divergence:   N. function evaluations: %6d" % log['n_fun_ev'])
    if ders >= 1:
        d2.transport_map.logger.info(
            "minimize_kl_divergence:   N. Jacobian evaluations: %6d" % log['n_jac_ev'])
    if ders >= 2:
        d2.transport_map.logger.info(
            "minimize_kl_divergence:   N. Hessian evaluations:  %6d" % log['n_hess_ev'])

    # Clear mpi_pool and detach object
    if mpi_pool is not None:
        mpi_pool.clear_dmem()

    # Set coefficients
    d2.coeffs = res['x']
    return log


def minimize_kl_divergence_objective(a, params):
    r""" Objective function :math:`\mathcal{D}_{KL}\left(\pi_1, \pi_{2,{\bf a}}\right)` for the KL-divergence minimization.

    Args:
      a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
      params (dict): dictionary of parameters
    """
    params['nobj'] += 1
    x = params['x']
    w = params['w']
    d1 = params['d1']
    d2 = params['d2']
    params1 = params['params1']
    params2 = params['params2']
    cache = params['cache']
    batch_size = params['batch_size']
    mpi_pool = params['mpi_pool']
    # Update distribution coefficients
    d2.coeffs = a
    bcast_tuple = (['coeffs'],[a])
    mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
            obj='d2', obj_val=d2,
            mpi_pool=mpi_pool, concatenate=False)
    # Reset cache
    if (params['objective_cache_coeffs'] != d2.transport_map.coeffs).any():
        params['objective_cache_coeffs'] = d2.transport_map.coeffs.copy()
        dmem_key_in_list = ['cache']
        dmem_arg_in_list = ['cache']
        dmem_val_in_list = [cache]
        mpi_map("reset_cache_minimize_kl_divergence",
                dmem_key_in_list=dmem_key_in_list,
                dmem_arg_in_list=dmem_arg_in_list,
                dmem_val_in_list=dmem_val_in_list,
                obj='tm', obj_val=d2.transport_map,
                mpi_pool=mpi_pool,
                concatenate=False)
    # Evaluate KL-divergence
    bcast_tuple = (['d1', 'batch_size', 'd1_entropy'],
                   [None, batch_size[0], False])
    dmem_key_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
    dmem_arg_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
    dmem_val_in_list = [x, w, d2, params1, params2, cache]
    reduce_obj = SumChunkReduce(axis=0)
    out = mpi_map(kl_divergence, 
                  bcast_tuple=bcast_tuple,
                  dmem_key_in_list=dmem_key_in_list,
                  dmem_arg_in_list=dmem_arg_in_list,
                  dmem_val_in_list=dmem_val_in_list,
                  reduce_obj=reduce_obj,
                  mpi_pool=mpi_pool)
    if params['regularization'] == None:
        pass
    elif params['regularization']['type'] == 'L2':
        out += params['regularization']['alpha'] * \
               npla.norm( a - d2.transport_map.get_identity_coeffs() ,2)**2.
    elif params['regularization']['type'] == 'L1':
        # using ||a||_1 regularization (not squared)
        centered_coeffs = a - d2.transport_map.get_identity_coeffs() 
        weighted_a = params['regularization']['alpha']*params['regularization']['l1_weights']*centered_coeffs
        out += npla.norm(weighted_a,1)
        #print(params['regularization']['alpha'] * params['regularization']['l1_weights'])
    # LOGGING
    d2.transport_map.logger.debug("KL Obj. Eval. %d - KL-divergence = %.10e" % (params['nobj'], out))
    # if d2.transport_map.logger.getEffectiveLevel() <= logging.DEBUG:
    #     gx = np.min(d2.transport_map.grad_x(x))
    #     d2.transport_map.logger.debug("KL-evaluation %d - min(grad_x) = %e" % (
    #         params['nobj'], min_gx))
    params['fval'] = out
    return out

def minimize_kl_divergence_grad_a_objective(a, params):
    r""" Gradient of the objective function :math:`\mathcal{D}_{KL}\left(\pi_1, \pi_{2,{\bf a}}\right)` for the KL-divergence minimization.

    Args:
      a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
      params (dict): dictionary of parameters
    """
    params['nda_obj'] += 1
    x = params['x']
    w = params['w']
    d1 = params['d1']
    d2 = params['d2']
    params1 = params['params1']
    params2 = params['params2']
    cache = params['cache']
    batch_size = params['batch_size']
    mpi_pool = params['mpi_pool']
    # Update distribution coefficients
    d2.coeffs = a
    bcast_tuple = (['coeffs'],[a])
    mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
            obj='d2', obj_val=d2,
            mpi_pool=mpi_pool, concatenate=False)
    # Reset cache
    if (params['objective_cache_coeffs'] != d2.transport_map.coeffs).any():
        params['objective_cache_coeffs'] = d2.transport_map.coeffs.copy()
        dmem_key_in_list = ['cache']
        dmem_arg_in_list = ['cache']
        dmem_val_in_list = [cache]
        mpi_map("reset_cache_minimize_kl_divergence",
                dmem_key_in_list=dmem_key_in_list,
                dmem_arg_in_list=dmem_arg_in_list,
                dmem_val_in_list=dmem_val_in_list,
                obj='tm', obj_val=d2.transport_map,
                mpi_pool=mpi_pool,
                concatenate=False)
    # Evaluate grad_a KL-divergence
    bcast_tuple = (['d1', 'batch_size'],
                   [None, batch_size[1]])
    dmem_key_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
    dmem_arg_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
    dmem_val_in_list = [x, w, d2, params1, params2, cache]
    reduce_obj = SumChunkReduce(axis=0)
    out = mpi_map(grad_a_kl_divergence, 
                  bcast_tuple=bcast_tuple,
                  dmem_key_in_list=dmem_key_in_list,
                  dmem_arg_in_list=dmem_arg_in_list,
                  dmem_val_in_list=dmem_val_in_list,
                  reduce_obj=reduce_obj,
                  mpi_pool=mpi_pool)
    if params['regularization'] == None:
        pass
    elif params['regularization']['type'] == 'L2':
        out += params['regularization']['alpha'] \
               * 2. * (a - d2.transport_map.get_identity_coeffs())
    elif params['regularization']['type'] == 'L1':
        alpha_reg = params['regularization']['alpha']*params['regularization']['l1_weights']
        # if only scalar is prescribed, set alpha as vector of equal values
        #if np.isscalar(alpha_reg):
        #    alpha_reg = alpha_reg*np.ones(len(a))
        tol_l1    = params['regularization']['tol_l1']
        centered_coeffs = a - d2.transport_map.get_identity_coeffs()
        for i_a, x_a in enumerate(centered_coeffs):
            if np.abs(x_a) >= tol_l1:
                out[i_a] += alpha_reg[i_a] * np.sign(x_a)
            elif np.abs(x_a) < tol_l1 and out[i_a] < -1. * alpha_reg[i_a]:
                out[i_a] += alpha_reg[i_a]
            elif np.abs(x_a) < tol_l1 and out[i_a] > 1. * alpha_reg[i_a]:
                out[i_a] -= alpha_reg[i_a]
            elif np.abs(x_a) < tol_l1 and np.abs(out[i_a]) <= 1. * alpha_reg[i_a]:
                out[i_a] = 0.

    if params['grad_check']:
        da = 1e-4
        fdg = finite_difference(minimize_kl_divergence_objective, a, da, params)
        maxerr = np.max(np.abs(out - fdg))
        if maxerr > da and d2.transport_map.logger.getEffectiveLevel() <= logging.WARNING:
            d2.transport_map.logger.warning("Grad_a KL-evaluation %d - " % params['nda_obj'] + \
                                "grad_a check FAIL - " + \
                                "maxerr=%e (da=%e)" % (maxerr, da))
    if d2.transport_map.logger.getEffectiveLevel() <= logging.DEBUG:
        d2.transport_map.logger.debug("KL Grad_a Obj. Eval. %d - 2-norm = %.5e - inf-norm = %.5e" % (
            params['nda_obj'], npla.norm(out), npla.norm(out, ord=np.inf)))
    # if d2.transport_map.logger.getEffectiveLevel() <= logging.DEBUG:
    #     d2.transport_map.logger.debug("KL-evaluation %d - grad_a KLdiv = \n%s" % (
    #         params['nda_obj'], out))
    params['jac'] = out
    return out

def minimize_kl_divergence_tuple_grad_a_objective(a, params):
    r""" Function evaluation and gradient of the objective :math:`\mathcal{D}_{KL}\left(\pi_1, \pi_{2,{\bf a}}\right)` for the KL-divergence minimization.

    Args:
      a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
      params (dict): dictionary of parameters
    """
    params['nobj'] += 1
    params['nda_obj'] += 1
    x = params['x']
    w = params['w']
    d1 = params['d1']
    d2 = params['d2']
    params1 = params['params1']
    params2 = params['params2']
    cache = params['cache']
    batch_size = params['batch_size']
    mpi_pool = params['mpi_pool']
    # Update distribution coefficients
    d2.coeffs = a
    bcast_tuple = (['coeffs'],[a])
    mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
            obj='d2', obj_val=d2,
            mpi_pool=mpi_pool, concatenate=False)
    # Reset cache
    if (params['objective_cache_coeffs'] != d2.transport_map.coeffs).any():
        params['objective_cache_coeffs'] = d2.transport_map.coeffs.copy()
        dmem_key_in_list = ['cache']
        dmem_arg_in_list = ['cache']
        dmem_val_in_list = [cache]
        mpi_map("reset_cache_minimize_kl_divergence",
                dmem_key_in_list=dmem_key_in_list,
                dmem_arg_in_list=dmem_arg_in_list,
                dmem_val_in_list=dmem_val_in_list,
                obj='tm', obj_val=d2.transport_map,
                mpi_pool=mpi_pool,
                concatenate=False)
    # Evaluate grad_a KL-divergence
    bcast_tuple = (['d1', 'batch_size', 'd1_entropy'],
                   [None, batch_size[1], False])
    dmem_key_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
    dmem_arg_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
    dmem_val_in_list = [x, w, d2, params1, params2, cache]
    reduce_obj = TupleSumChunkReduce(axis=0)
    ev, ga = mpi_map(tuple_grad_a_kl_divergence, 
                     bcast_tuple=bcast_tuple,
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     reduce_obj=reduce_obj,
                     mpi_pool=mpi_pool)
    if params['regularization'] == None:
        pass
    elif params['regularization']['type'] == 'L2':
        ev += params['regularization']['alpha'] * \
              npla.norm(a - d2.transport_map.get_identity_coeffs(),2)**2.
        ga += params['regularization']['alpha'] \
              * 2. * (a - d2.transport_map.get_identity_coeffs())
    if params['grad_check']:
        da = 1e-4
        fdg = finite_difference(minimize_kl_divergence_objective, a, da, params)
        maxerr = np.max(np.abs(ga - fdg))
        if maxerr > da and d2.transport_map.logger.getEffectiveLevel() <= logging.WARNING:
            d2.transport_map.logger.warning("Grad_a KL-evaluation %d - " % params['nda_obj'] + \
                                "grad_a check FAIL - " + \
                                "maxerr=%e (da=%e)" % (maxerr, da))
    # LOGGING
    if d2.transport_map.logger.getEffectiveLevel() <= logging.DEBUG:
        d2.transport_map.logger.debug("KL Obj. Eval. %d - KL-divergence = %.10e" % (params['nobj'], ev))
        d2.transport_map.logger.debug("KL Grad_a Obj. Eval. %d - 2-norm = %.5e - inf-norm = %.5e" % (
            params['nda_obj'], npla.norm(ga), npla.norm(ga, ord=np.inf)))
    # if d2.transport_map.logger.getEffectiveLevel() <= logging.DEBUG:
    #     d2.transport_map.logger.debug("KL-evaluation %d - grad_a KLdiv = \n%s" % (
    #         params['nda_obj'], out))
    params['fval'] = ev    
    params['jac'] = ga
    return ev, ga

def minimize_kl_divergence_hess_a_objective(a, params):
    r""" Hessian of the objective function :math:`\mathcal{D}_{KL}\left(\pi_1, \pi_{2,{\bf a}}\right)` for the KL-divergence minimization.

    Args:
      a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
      params (dict): dictionary of parameters
    """
    params['nda2_obj'] += 1
    x = params['x']
    w = params['w']
    d1 = params['d1']
    d2 = params['d2']
    params1 = params['params1']
    params2 = params['params2']
    cache = params['cache']
    batch_size = params['batch_size']
    mpi_pool = params['mpi_pool']
    # Update distribution coefficients
    d2.coeffs = a
    bcast_tuple = (['coeffs'],[a])
    mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
            obj='d2', obj_val=d2,
            mpi_pool=mpi_pool, concatenate=False)
    # Reset cache
    if (params['objective_cache_coeffs'] != d2.transport_map.coeffs).any():
        params['objective_cache_coeffs'] = d2.transport_map.coeffs.copy()
        dmem_key_in_list = ['cache']
        dmem_arg_in_list = ['cache']
        dmem_val_in_list = [cache]
        mpi_map("reset_cache_minimize_kl_divergence",
                dmem_key_in_list=dmem_key_in_list,
                dmem_arg_in_list=dmem_arg_in_list,
                dmem_val_in_list=dmem_val_in_list,
                obj='tm', obj_val=d2.transport_map,
                mpi_pool=mpi_pool,
                concatenate=False)
    # Evaluate hess_a KL-divergence
    bcast_tuple = (['d1', 'batch_size'],
                   [None, batch_size[2]])
    dmem_key_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
    dmem_arg_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
    dmem_val_in_list = [x, w, d2, params1, params2, cache]
    reduce_obj = SumChunkReduce(axis=0)
    out = mpi_map(hess_a_kl_divergence, 
                  bcast_tuple=bcast_tuple,
                  dmem_key_in_list=dmem_key_in_list,
                  dmem_arg_in_list=dmem_arg_in_list,
                  dmem_val_in_list=dmem_val_in_list,
                  reduce_obj=reduce_obj,
                  mpi_pool=mpi_pool)
    if params['regularization'] == None:
        pass
    elif params['regularization']['type'] == 'L2':
        out += np.diag( np.ones(d2.n_coeffs)*2.*params['regularization']['alpha'] )
    if params['hess_check']:
        da = 1e-4
        fdg = finite_difference(minimize_kl_divergence_grad_a_objective, a, da, params)
        maxerr = np.max(np.abs(out - fdg))
        if maxerr > da:
            d2.transport_map.logger.warning("Hess_a KL-evaluation %d - " % params['nda2_obj'] + \
                                "hess_a check FAIL - " + \
                                "maxerr=%e (da=%e)" % (maxerr, da))
    if d2.transport_map.logger.getEffectiveLevel() <= logging.DEBUG:
        d2.transport_map.logger.debug("KL Hess_a Obj. Eval. %d " % params['nda2_obj'])
    # if d2.transport_map.logger.getEffectiveLevel() <= logging.DEBUG:
    #     import pickle
    #     U,S,V = scila.svd(out)
    #     try:
    #         with open('svd.dat', 'rb') as stream:
    #             ll = pickle.load(stream)
    #     except IOError:
    #         ll = []
    #     ll.append(S)
    #     with open('svd.dat', 'wb') as stream:
    #         pickle.dump(ll, stream)
    return out


def minimize_kl_divergence_action_hess_a_objective(a, da, params):
    r""" Action of the Hessian of the objective function :math:`\mathcal{D}_{KL}\left(\pi_1, \pi_{2,{\bf a}}\right)` on the direction ``v``

    Args:
      a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
      da (:class:`ndarray<numpy.ndarray>` [:math:`N`]):
        vector on which to apply the Hessian
      params (dict): dictionary of parameters
    """
    params['nda2_obj'] += 1
    x = params['x']
    w = params['w']
    d1 = params['d1']
    d2 = params['d2']
    params1 = params['params1']
    params2 = params['params2']
    cache = params['cache']
    batch_size = params['batch_size']
    mpi_pool = params['mpi_pool']
    # Update distribution coefficients
    d2.coeffs = a
    bcast_tuple = (['coeffs'],[a])
    mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
            obj='d2', obj_val=d2,
            mpi_pool=mpi_pool, concatenate=False)
    # Reset cache
    if (params['objective_cache_coeffs'] != d2.transport_map.coeffs).any():
        params['objective_cache_coeffs'] = d2.transport_map.coeffs.copy()
        dmem_key_in_list = ['cache']
        dmem_arg_in_list = ['cache']
        dmem_val_in_list = [cache]
        mpi_map("reset_cache_minimize_kl_divergence",
                dmem_key_in_list=dmem_key_in_list,
                dmem_arg_in_list=dmem_arg_in_list,
                dmem_val_in_list=dmem_val_in_list,
                obj='tm', obj_val=d2.transport_map,
                mpi_pool=mpi_pool,
                concatenate=False)
    # Evaluate hess_a KL-divergence
    bcast_tuple = (['da','d1', 'batch_size'],
                   [da, None, batch_size[2]])
    dmem_key_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
    dmem_arg_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
    dmem_val_in_list = [x, w, d2, params1, params2, cache]
    reduce_obj = SumChunkReduce(axis=0)
    out = mpi_map(action_hess_a_kl_divergence, 
                  bcast_tuple=bcast_tuple,
                  dmem_key_in_list=dmem_key_in_list,
                  dmem_arg_in_list=dmem_arg_in_list,
                  dmem_val_in_list=dmem_val_in_list,
                  reduce_obj=reduce_obj,
                  mpi_pool=mpi_pool)
    if params['regularization'] == None:
        pass
    elif params['regularization']['type'] == 'L2':
        out += 2. * params['regularization']['alpha'] * da 
    elif params['regularization']['type'] == 'L1':
        # common to ignore effect of L1 on hessian of regularized objective
        out += 0.
    if d2.transport_map.logger.getEffectiveLevel() <= logging.DEBUG:
        d2.transport_map.logger.debug(
            "KL action Hess_a Obj. Eval. %d" % params['nda2_obj'] + \
            " - 2-norm = %e" % npla.norm(out, 2) + \
            " - inf-norm = %e" % npla.norm(out,np.inf)
        )
    # if d2.transport_map.logger.getEffectiveLevel() <= logging.DEBUG:
    #     import pickle
    #     U,S,V = scila.svd(out)
    #     try:
    #         with open('svd.dat', 'rb') as stream:
    #             ll = pickle.load(stream)
    #     except IOError:
    #         ll = []
    #     ll.append(S)
    #     with open('svd.dat', 'wb') as stream:
    #         pickle.dump(ll, stream)
    return out


def minimize_kl_divergence_action_storage_hess_a_objective(a, v, params):
    r""" Assemble the Hessian :math:`\mathcal{D}_{KL}\left(\pi_1, \pi_{2,{\bf a}}\right)` and compute its action on the vector :math:`v`, for the KL-divergence minimization problem.

    Args:
      a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
      v (:class:`ndarray<numpy.ndarray>` [:math:`N`]): vector on which to apply the Hessian
      params (dict): dictionary of parameters
    """
    x = params['x']
    w = params['w']
    d1 = params['d1']
    d2 = params['d2']
    params1 = params['params1']
    params2 = params['params2']
    cache = params['cache']
    batch_size = params['batch_size']
    mpi_pool = params['mpi_pool']
    # Update distribution coefficients
    d2.coeffs = a
    bcast_tuple = (['coeffs'],[a])
    mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
            obj='d2', obj_val=d2,
            mpi_pool=mpi_pool, concatenate=False)
    # Reset cache
    if (params['objective_cache_coeffs'] != d2.transport_map.coeffs).any():
        params['objective_cache_coeffs'] = d2.transport_map.coeffs.copy()
        # Reset cache
        dmem_key_in_list = ['cache']
        dmem_arg_in_list = ['cache']
        dmem_val_in_list = [cache]
        mpi_map("reset_cache_minimize_kl_divergence",
                dmem_key_in_list=dmem_key_in_list,
                dmem_arg_in_list=dmem_arg_in_list,
                dmem_val_in_list=dmem_val_in_list,
                obj='tm', obj_val=d2.transport_map,
                mpi_pool=mpi_pool,
                concatenate=False)
    # Assemble Hessian
    if not params['hess_assembled']:
        # Assemble
        params['nda2_obj'] += 1
        bcast_tuple = (['d1', 'batch_size'],
                       [None, batch_size[2]])
        dmem_key_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
        dmem_arg_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
        dmem_val_in_list = [x, w, d2, params1, params2, cache]
        dmem_key_out_list = ['hess_a_kl_divergence']
        (params['hess_a_kl_divergence'], ) = mpi_map_alloc_dmem(
            storage_hess_a_kl_divergence, 
            bcast_tuple=bcast_tuple, dmem_key_in_list=dmem_key_in_list,
            dmem_arg_in_list=dmem_arg_in_list, dmem_val_in_list=dmem_val_in_list,
            dmem_key_out_list=dmem_key_out_list,
            mpi_pool=mpi_pool, concatenate=False)
        params['hess_assembled'] = True
        if d2.transport_map.logger.getEffectiveLevel() <= logging.DEBUG:
            d2.transport_map.logger.debug("KL Storage Hess_a Obj. Eval. %d " % params['nda2_obj'])
    params['nda2_obj_dot'] += 1
    # Evaluate the action of hess_a KL-divergence
    bcast_tuple = (['v'], [v])
    dmem_key_in_list = ['hess_a_kl_divergence']
    dmem_arg_in_list = ['H']
    dmem_val_in_list = [params['hess_a_kl_divergence']]
    reduce_obj = SumChunkReduce(axis=0)
    out = mpi_map(action_stored_hess_a_kl_divergence,
                  bcast_tuple=bcast_tuple,
                  dmem_key_in_list=dmem_key_in_list,
                  dmem_arg_in_list=dmem_arg_in_list,
                  dmem_val_in_list=dmem_val_in_list,
                  reduce_obj=reduce_obj,
                  mpi_pool=mpi_pool)
    if params['regularization'] == None:
        pass
    elif params['regularization']['type'] == 'L2':
        out += 2.*params['regularization']['alpha'] * v
    # if d2.transport_map.logger.getEffectiveLevel() <= logging.DEBUG:
    #     d2.transport_map.logger.debug("KL Action Hess_a Obj. Eval. %d " % params['nda2_obj_dot'] + \
    #                      "- v^T H v = %.10e" % np.dot(out,v))
    return out


def minimize_kl_divergence_component(
        f: ProductDistributionParametricPullbackComponentFunction,
        x, w,
        x0=None,
        regularization=None,
        tol=1e-4, maxit=100, ders=2,
        fungrad=False,
        precomp_type='uni',
        batch_size=None,
        cache_level=1,
        mpi_pool=None
):
    r""" Compute :math:`{\bf a}^\star = \arg\min_{\bf a}-\sum_{i=0}^m \log\pi\circ T_k(x_i) + \log\partial_{x_k}T_k(x_i) = \arg\min_{\bf a}-\sum_{i=0}^m f(x_i)`

    Args:
      f : function :math:`f`
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
      x0 (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients to be used
        as initial values for the optimization
      regularization (dict): defines the regularization to be used.
        If ``None``, no regularization is applied.
        If key ``type=='L2'`` then applies Tikonhov regularization with
        coefficient in key ``alpha``.
      tol (float): tolerance to be used to solve the KL-divergence problem.
      maxit (int): maximum number of iterations
      ders (int): order of derivatives available for the solution of the
        optimization problem. 0 -> derivative free, 1 -> gradient, 2 -> hessian.
      fungrad (bool): whether the distributions :math:`\pi_1,\pi_2` provide the method
        :func:`Distribution.tuple_grad_x_log_pdf` computing the evaluation and the
        gradient in one step. This is used only for ``ders==1``.
      precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
        multivariate Vandermonde matrices 'multi'
      batch_size (:class:`list<list>` [3 or 2] of :class:`int<int>` or :class:`list<list>` of ``batch_size``):
        the list contains the
        size of the batch to be used for each iteration. A size ``1`` correspond
        to a completely non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one.
        If the target distribution is a :class:`ProductDistribution`, then
        the optimization problem decouples and
        ``batch_size`` is a list of lists containing the batch sizes to be
        used for each component of the map.
      cache_level (int): use high-level caching during the optimization, storing the
        function evaluation ``0``, and the gradient evaluation ``1`` or
        nothing ``-1``
      mpi_pool (:class:`mpi_map.MPI_Pool` or :class:`list<list>` of ``mpi_pool``):
        pool of processes to be used, ``None`` stands for one process.
        If the target distribution is a :class:`ProductDistribution`, then
        the minimization problem decouples and ``mpi_pool`` is a list containing
        ``mpi_pool``s for each component of the map.
    """
    f.tmap_component.logger.debug("minimize_kl_divergence_component(): Precomputation started")

    if batch_size is None:
        batch_size = [None] * 3
    # Distribute objects
    mpi_bcast_dmem(f=f, mpi_pool=mpi_pool)

    # Link tm_comp to f.tmap_component
    def link_tmcmp(f):
        return (f.tmap_component,)

    (tm_comp,) = mpi_map_alloc_dmem(
        link_tmcmp, dmem_key_in_list=['f'], dmem_arg_in_list=['f'],
        dmem_val_in_list=[f], dmem_key_out_list=['tm_comp'],
        mpi_pool=mpi_pool)
    # Init memory
    paramsf = {'params_pi': None,
               'params_t': {}}
    mpi_bcast_dmem(paramsf=paramsf, mpi_pool=mpi_pool)
    dmem_key_in_list = ['paramsf']
    dmem_arg_in_list = ['params']
    dmem_val_in_list = [paramsf]
    # precomp_minimize_kl_divergence_component
    scatter_tuple = (['x'], [x])
    bcast_tuple = (['precomp_type'], [precomp_type])
    mpi_map("precomp_minimize_kl_divergence_component",
            scatter_tuple=scatter_tuple,
            bcast_tuple=bcast_tuple,
            dmem_key_in_list=dmem_key_in_list,
            dmem_arg_in_list=dmem_arg_in_list,
            dmem_val_in_list=dmem_val_in_list,
            obj='tm_comp', obj_val=tm_comp,
            mpi_pool=mpi_pool, concatenate=False)
    # allocate_cache_minimize_kl_divergence_component
    scatter_tuple = (['x'], [x])
    (cache,) = mpi_map_alloc_dmem(
        "allocate_cache_minimize_kl_divergence_component",
        scatter_tuple=scatter_tuple,
        dmem_key_out_list=['cache'],
        obj='tm_comp', obj_val=tm_comp,
        mpi_pool=mpi_pool, concatenate=False)
    f.tmap_component.logger.debug("minimize_kl_divergence(): Precomputation ended")
    params = {}
    params['nobj'] = 0
    params['nda_obj'] = 0
    params['nda2_obj'] = 0
    params['nda2_obj_dot'] = 0
    params['x'] = x
    params['w'] = w
    params['f'] = f
    params['paramsf'] = paramsf
    params['cache'] = cache
    params['batch_size'] = batch_size
    params['regularization'] = regularization
    params['hess_assembled'] = False
    params['mpi_pool'] = mpi_pool

    if x0 is None:
        x0 = f.tmap_component.get_default_init_values_minimize_kl_divergence_component()

    params['objective_cache_coeffs'] = x0 - 1.

    # Callback variables
    f.tmap_component.it_callback = 0
    f.tmap_component.ders_callback = ders
    f.tmap_component.params_callback = params

    # Options for optimizer
    options = {'maxiter': maxit,
               'disp': False}

    # Solve
    if ders == 0:
        res = sciopt.minimize(minimize_kl_divergence_component_objective,
                              args=params,
                              x0=x0,
                              method='BFGS',
                              tol=tol,
                              options=options,
                              callback=f.tmap_component.minimize_kl_divergence_component_callback)
    elif ders == 1:
        if fungrad:
            raise NotImplementedError("Option fungrad not implemented for maps from samples")
            # res = sciopt.minimize(
            #     f.tmap_component.minimize_kl_divergence_component_tuple_grad_a_objective,
            #     args=params,
            #     x0=x0,
            #     jac=True,
            #     method='BFGS',
            #     tol=tol,
            #     options=options,
            #     callback=f.tmap_component.minimize_kl_divergence_component_callback)
        else:
            res = sciopt.minimize(
                minimize_kl_divergence_component_objective,
                args=params,
                x0=x0,
                jac=minimize_kl_divergence_component_grad_a_objective,
                method='BFGS',
                tol=tol,
                options=options,
                callback=f.tmap_component.minimize_kl_divergence_component_callback)
    elif ders == 2:
        res = sciopt.minimize(
            minimize_kl_divergence_component_objective, args=params, x0=x0,
            jac=minimize_kl_divergence_component_grad_a_objective,
            hess=minimize_kl_divergence_component_hess_a_objective,
            method='newton-cg', tol=tol, options=options,
            callback=f.tmap_component.minimize_kl_divergence_component_callback)

    # Clean up callback stuff
    del f.tmap_component.it_callback
    del f.tmap_component.ders_callback
    del f.tmap_component.params_callback

    # Log
    log = {}
    log['success'] = res['success']
    log['message'] = res['message']
    log['fval'] = res['fun']
    log['nit'] = res['nit']
    log['n_fun_ev'] = params['nobj']
    if ders >= 1:
        log['n_jac_ev'] = params['nda_obj']
        log['jac'] = res['jac']
    if ders >= 2:
        log['n_hess_ev'] = params['nda2_obj']
    # Display stats
    if log['success']:
        f.tmap_component.logger.info("Optimization terminated successfully")
    else:
        f.tmap_component.logger.info("Optimization failed.")
        f.tmap_component.logger.info("Message: %s" % log['message'])
    f.tmap_component.logger.info("  Function value:          %6f" % log['fval'])
    if ders >= 1:
        f.tmap_component.logger.info("  Norm of the Jacobian:    %6f" % npla.norm(log['jac']))
    f.tmap_component.logger.info("  Number of iterations:    %6d" % log['nit'])
    f.tmap_component.logger.info("  N. function evaluations: %6d" % log['n_fun_ev'])
    if ders >= 1:
        f.tmap_component.logger.info("  N. Jacobian evaluations: %6d" % log['n_jac_ev'])
    if ders >= 2:
        f.tmap_component.logger.info("  N. Hessian evaluations:  %6d" % log['n_hess_ev'])

    # Set coefficients
    f.tmap_component.coeffs = res['x']
    return log


def minimize_kl_divergence_component_objective(a, params):
    r""" Objective function :math:`-\sum_{i=0}^m f(x_i) = -\sum_{i=0}^m \log\pi\circ T_k(x_i) + \log\partial_{x_k}T_k(x_i)`

    Args:
      a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
      params (dict): dictionary of parameters
    """
    params['nobj'] += 1
    x = params['x']
    w = params['w']
    f = params['f']
    paramsf = params['paramsf']
    cache = params['cache']
    batch_size = params['batch_size']
    mpi_pool = params['mpi_pool']
    # Update coefficients
    f.tmap_component.coeffs = a
    bcast_tuple = (['coeffs'], [a])
    mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
            obj='tm_comp', obj_val=f.tmap_component,
            mpi_pool=mpi_pool, concatenate=False)
    # Reset cache
    if (params['objective_cache_coeffs'] != f.tmap_component.coeffs).any():
        params['objective_cache_coeffs'] = f.tmap_component.coeffs.copy()
        dmem_key_in_list = ['cache']
        dmem_arg_in_list = ['cache']
        dmem_val_in_list = [cache]
        mpi_map("reset_cache_minimize_kl_divergence_component",
                dmem_key_in_list=dmem_key_in_list,
                dmem_arg_in_list=dmem_arg_in_list,
                dmem_val_in_list=dmem_val_in_list,
                obj='tm_comp', obj_val=f.tmap_component,
                mpi_pool=mpi_pool,
                concatenate=False)
    # Evaluate KL-divergence
    scatter_tuple = (['x', 'w'], [x, w])
    bcast_tuple = (['batch_size'],
                   [batch_size[0]])
    dmem_key_in_list = ['f', 'paramsf', 'cache']
    dmem_arg_in_list = ['f', 'params', 'cache']
    dmem_val_in_list = [f, paramsf, cache]
    reduce_obj = SumChunkReduce(axis=0)
    out = mpi_map(kl_divergence_component,
                  scatter_tuple=scatter_tuple,
                  bcast_tuple=bcast_tuple,
                  dmem_key_in_list=dmem_key_in_list,
                  dmem_arg_in_list=dmem_arg_in_list,
                  dmem_val_in_list=dmem_val_in_list,
                  reduce_obj=reduce_obj,
                  mpi_pool=mpi_pool)
    if params['regularization'] == None:
        pass
    elif params['regularization']['type'] == 'L2':
        centered_coeffs = a - f.tmap_component.get_identity_coeffs()
        out += params['regularization']['alpha'] * npla.norm(centered_coeffs, 2) ** 2.
    elif params['regularization']['type'] == 'L1':
        # using ||a||_1 regularization (not squared)
        centered_coeffs = a - f.tmap_component.get_identity_coeffs()
        out += params['regularization']['alpha'] * npla.norm(centered_coeffs, 1)
    f.tmap_component.logger.debug("KL Obj. Eval. %d - KL-divergence = %.10e" % (params['nobj'], out))
    return out


def minimize_kl_divergence_component_grad_a_objective(a, params):
    r""" Gradient of the objective function :math:`-\sum_{i=0}^m \nabla_{\bf a} f[{\bf a}](x_i) = -\sum_{i=0}^m \nabla_{\bf a} \left( \log\pi\circ T_k[{\bf a}](x_i) + \log\partial_{x_k}T_k[{\bf a}](x_i)\right)`

    Args:
      a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
      params (dict): dictionary of parameters
    """
    params['nda_obj'] += 1
    x = params['x']
    w = params['w']
    f = params['f']
    paramsf = params['paramsf']
    cache = params['cache']
    batch_size = params['batch_size']
    mpi_pool = params['mpi_pool']
    # Update coefficients
    f.tmap_component.coeffs = a
    bcast_tuple = (['coeffs'], [a])
    mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
            obj='tm_comp', obj_val=f.tmap_component,
            mpi_pool=mpi_pool, concatenate=False)
    # Reset cache
    if (params['objective_cache_coeffs'] != f.tmap_component.coeffs).any():
        params['objective_cache_coeffs'] = f.tmap_component.coeffs.copy()
        # Reset cache
        dmem_key_in_list = ['cache']
        dmem_arg_in_list = ['cache']
        dmem_val_in_list = [cache]
        mpi_map("reset_cache_minimize_kl_divergence_component",
                dmem_key_in_list=dmem_key_in_list,
                dmem_arg_in_list=dmem_arg_in_list,
                dmem_val_in_list=dmem_val_in_list,
                obj='tm_comp', obj_val=f.tmap_component,
                mpi_pool=mpi_pool,
                concatenate=False)
    # Evaluate KL-divergence
    scatter_tuple = (['x', 'w'], [x, w])
    bcast_tuple = (['batch_size'],
                   [batch_size[0]])
    dmem_key_in_list = ['f', 'paramsf']
    dmem_arg_in_list = ['f', 'params']
    dmem_val_in_list = [f, paramsf]
    reduce_obj = SumChunkReduce(axis=0)
    out = mpi_map(grad_a_kl_divergence_component,
                  scatter_tuple=scatter_tuple,
                  bcast_tuple=bcast_tuple,
                  dmem_key_in_list=dmem_key_in_list,
                  dmem_arg_in_list=dmem_arg_in_list,
                  dmem_val_in_list=dmem_val_in_list,
                  reduce_obj=reduce_obj,
                  mpi_pool=mpi_pool)
    if params['regularization'] == None:
        pass
    elif params['regularization']['type'] == 'L2':
        out += params['regularization']['alpha'] * 2. * a
    if f.tmap_component.logger.getEffectiveLevel() <= logging.DEBUG:
        f.tmap_component.logger.debug("KL Grad_a Obj. Eval. %d - ||grad_a KLdiv|| = %.10e" % (
            params['nda_obj'], npla.norm(out)))
    return out


def minimize_kl_divergence_component_hess_a_objective(a, params):
    r""" Hessian of the objective function :math:`-\sum_{i=0}^m \nabla^2_{\bf a} f[{\bf a}](x_i) = -\sum_{i=0}^m \nabla^2_{\bf a} \left( \log\pi\circ T_k[{\bf a}](x_i) + \log\partial_{x_k}T_k[{\bf a}](x_i)\right)`

    Args:
      a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
      params (dict): dictionary of parameters
    """
    params['nda2_obj'] += 1
    x = params['x']
    w = params['w']
    f = params['f']
    paramsf = params['paramsf']
    cache = params['cache']
    batch_size = params['batch_size']
    mpi_pool = params['mpi_pool']
    # Update coefficients
    f.tmap_component.coeffs = a
    bcast_tuple = (['coeffs'], [a])
    mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
            obj='tm_comp', obj_val=f.tmap_component,
            mpi_pool=mpi_pool, concatenate=False)
    # Reset cache
    if (params['objective_cache_coeffs'] != f.tmap_component.coeffs).any():
        params['objective_cache_coeffs'] = f.tmap_component.coeffs.copy()
        # Reset cache
        dmem_key_in_list = ['cache']
        dmem_arg_in_list = ['cache']
        dmem_val_in_list = [cache]
        mpi_map("reset_cache_minimize_kl_divergence_component",
                dmem_key_in_list=dmem_key_in_list,
                dmem_arg_in_list=dmem_arg_in_list,
                dmem_val_in_list=dmem_val_in_list,
                obj='tm_comp', obj_val=f.tmap_component,
                mpi_pool=mpi_pool,
                concatenate=False)
    # Evaluate KL-divergence
    scatter_tuple = (['x', 'w'], [x, w])
    bcast_tuple = (['batch_size'],
                   [batch_size[0]])
    dmem_key_in_list = ['f', 'paramsf']
    dmem_arg_in_list = ['f', 'params']
    dmem_val_in_list = [f, paramsf]
    reduce_obj = SumChunkReduce(axis=0)
    out = mpi_map(hess_a_kl_divergence_component,
                  scatter_tuple=scatter_tuple,
                  bcast_tuple=bcast_tuple,
                  dmem_key_in_list=dmem_key_in_list,
                  dmem_arg_in_list=dmem_arg_in_list,
                  dmem_val_in_list=dmem_val_in_list,
                  reduce_obj=reduce_obj,
                  mpi_pool=mpi_pool)
    if params['regularization'] == None:
        pass
    elif params['regularization']['type'] == 'L2':
        out += np.diag(np.ones(f.tmap_component.n_coeffs) * 2. * params['regularization']['alpha'])
    if f.tmap_component.logger.getEffectiveLevel() <= logging.DEBUG:
        f.tmap_component.logger.debug("KL Hess_a Obj. Eval. %d " % params['nda2_obj'])
    return out


def minimize_kl_divergence_pointwise_monotone(
        d1: Distribution,
        d2: ParametricTransportMapDistribution,
        x=None, w=None,
        params_d1=None, params_d2=None,
        x0=None,
        regularization=None,
        tol=1e-4, maxit=100, ders=1,
        fungrad=False, hessact=False,
        precomp_type='uni',
        batch_size=None,
        mpi_pool=None,
        grad_check=False, hess_check=False
):
        r""" Compute: :math:`{\bf a}^* = \arg\min_{\bf a}\mathcal{D}_{KL}\left(\pi_1, \pi_{2,{\bf a}}\right)`

        Args:
          d1 (Distribution): distribution :math:`\pi_1`
          d2 (Distribution): distribution :math:`\pi_2`
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
          w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
          params_d1 (dict): parameters for distribution :math:`\pi_1`
          params_d2 (dict): parameters for distribution :math:`\pi_2`
          x0 (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients to be used
            as initial values for the optimization
          regularization (dict): defines the regularization to be used.
            If ``None``, no regularization is applied.
            If key ``type=='L2'`` then applies Tikonhov regularization with
            coefficient in key ``alpha``.
          tol (float): tolerance to be used to solve the KL-divergence problem.
          maxit (int): maximum number of iterations
          ders (int): order of derivatives available for the solution of the
            optimization problem. 0 -> derivative free (SLSQP), 1 -> gradient (SLSQP).
          fungrad (bool): whether the target distribution provides the method
            :func:`Distribution.tuple_grad_x_log_pdf` computing the evaluation and the
            gradient in one step. This is used only for ``ders==1``.
          hessact (bool): this option is disabled for linear span maps (no Hessian used)
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'
          batch_size (:class:`list<list>` [2] of :class:`int<int>`): the list contains the
            size of the batch to be used for each iteration. A size ``1`` correspond
            to a completely non-vectorized evaluation. A size ``None`` correspond to a
            completely vectorized one.
            If the target distribution is a :class:`ProductDistribution`, then
            the optimization problem decouples and
            ``batch_size`` is a list of lists containing the batch sizes to be
            used for each component of the map.
          mpi_pool (:class:`mpi_map.MPI_Pool` or :class:`list<list>` of ``mpi_pool``):
            pool of processes to be used, ``None`` stands for one process.
            If the target distribution is a :class:`ProductDistribution`, then
            the minimization problem decouples and ``mpi_pool`` is a list containing
            ``mpi_pool``s for each component of the map.
          grad_check (bool): whether to use finite difference to check the correctness of
            of the gradient
          hess_check (bool): whether to use finite difference to check the correctenss of
            the Hessian

        Returns:
          log (dict): log informations from the solver

        .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
          exclusive, but one pair of them is necessary.
        """
        if ders < 0:
            d2.transport_map.logger.warning("Value for ders too low (%d). Set to 0." % ders)
            ders = 0
        if ders > 1:
            d2.transport_map.logger.warning("Value for ders too high (%d). Set to 1." % ders)
            ders = 1

        d2.transport_map.logger.debug("minimize_kl_divergence(): Precomputation started")

        if batch_size is None:
            batch_size = [None] * 2

        # Distribute objects
        d2_distr = pickle.loads(pickle.dumps(d2))
        d2_distr.reset_counters() # Reset counters on copy to avoid couting twice
        mpi_bcast_dmem(d2=d2_distr, mpi_pool=mpi_pool)
        # Link tm to d2.transport_map
        def link_tm_d2(d2):
            return (d2.transport_map,)
        (tm,) = mpi_map_alloc_dmem(
            link_tm_d2, dmem_key_in_list=['d2'], dmem_arg_in_list=['d2'],
            dmem_val_in_list=[d2], dmem_key_out_list=['tm'],
            mpi_pool=mpi_pool)

        from TransportMaps.Distributions.TransportMapDistributions import \
            PullBackTransportMapDistribution, PushForwardTransportMapDistribution
        if isinstance(d2, PullBackTransportMapDistribution):
            # Init memory
            params2 = {
                'params_pi': params_d2,
                'params_t': {'components': [{} for i in range(d2.transport_map.dim)]} }
            mpi_bcast_dmem(params2=params2, mpi_pool=mpi_pool)

            # precomp_minimize_kl_divergence
            bcast_tuple = (['precomp_type'],[precomp_type])
            mpi_map("precomp_minimize_kl_divergence",
                    bcast_tuple=bcast_tuple,
                    dmem_key_in_list=['params2', 'x'],
                    dmem_arg_in_list=['params', 'x'],
                    dmem_val_in_list=[params2, x],
                    obj='tm', obj_val=tm,
                    mpi_pool=mpi_pool, concatenate=False)
            # allocate_cache_minimize_kl_divergence
            (cache, ) = mpi_map_alloc_dmem(
                "allocate_cache_minimize_kl_divergence",
                dmem_key_in_list=['x'],
                dmem_arg_in_list=['x'],
                dmem_val_in_list=[x],
                dmem_key_out_list=['cache'],
                obj='tm', obj_val=tm,
                mpi_pool=mpi_pool, concatenate=False)
        elif isinstance(d2, PushForwardTransportMapDistribution):
            # Init memory
            params2 = { 'params_pi': params_d2,
                        'params_t': {} }
            mpi_bcast_dmem(params2=params2, mpi_pool=mpi_pool)
            # allocate cache
            (cache, ) = mpi_map_alloc_dmem(
                "allocate_cache_minimize_kl_divergence",
                dmem_key_in_list=['x'],
                dmem_arg_in_list=['x'],
                dmem_val_in_list=[x],
                dmem_key_out_list=['cache'],
                obj='tm', obj_val=tm,
                mpi_pool=mpi_pool, concatenate=False)
        else:
            raise AttributeError("Not recognized distribution type")
        # Append the slices indices
        if d2.transport_map.logger.getEffectiveLevel() <= logging.DEBUG:
            d2.transport_map.logger.debug("minimize_kl_divergence(): Precomputation ended")
        params = {}
        params['nobj'] = 0
        params['nda_obj'] = 0
        params['nda2_obj'] = 0
        params['nda2_obj_dot'] = 0
        params['x'] = x
        params['w'] = w
        params['d1'] = d1
        params['d2'] = d2
        params['params1'] = params_d1
        params['params2'] = params2
        params['cache'] = cache
        params['batch_size'] = batch_size
        params['regularization'] = regularization
        params['grad_check'] = grad_check
        params['hess_check'] = hess_check
        params['mpi_pool'] = mpi_pool

        # Link params_t on the first level of params
        # (this is needed for the MPI implementation of the constraints)
        def link_params_t(params):
            return (params['params_t'],)
        (params['params_t'],) = mpi_map_alloc_dmem(
            link_params_t,
            dmem_key_in_list = ['params2'],
            dmem_arg_in_list = ['params'],
            dmem_val_in_list = [params2],
            dmem_key_out_list = ['params_t'],
            mpi_pool=mpi_pool)

        cons = ({'type': 'ineq',
                 'fun': minimize_kl_divergence_pointwise_monotone_constraints,
                 'jac': minimize_kl_divergence_pointwise_monotone_da_constraints,
                 'args': (params,)})

        if x0 is None:
            x0 = d2.transport_map.get_default_init_values_minimize_kl_divergence()

        params['objective_cache_coeffs'] = x0 - 1.

        # Callback variables
        d2.transport_map.it_callback = 0
        d2.transport_map.ders_callback = ders
        d2.transport_map.params_callback = params

        # Options for optimizer
        options = {'maxiter': maxit,
                   'disp': False}

        # Solve
        if ders == 0:
            res = sciopt.minimize(minimize_kl_divergence_objective,
                                  args=params,
                                  x0=x0,
                                  constraints=cons,
                                  method='SLSQP',
                                  tol=tol,
                                  options=options,
                                  callback=d2.transport_map.minimize_kl_divergence_callback)
        elif ders == 1:
            if fungrad:
                res = sciopt.minimize(minimize_kl_divergence_tuple_grad_a_objective,
                                      args=params, x0=x0,
                                      jac=True,
                                      constraints=cons,
                                      method='SLSQP',
                                      tol=tol,
                                      options=options,
                                      callback=d2.transport_map.minimize_kl_divergence_callback)
            else:
                res = sciopt.minimize(minimize_kl_divergence_objective, args=params,
                                      x0=x0,
                                      jac=minimize_kl_divergence_grad_a_objective,
                                      constraints=cons,
                                      method='SLSQP',
                                      tol=tol,
                                      options=options,
                                      callback=d2.transport_map.minimize_kl_divergence_callback)

        # Clean up callback stuff
        del d2.transport_map.it_callback
        del d2.transport_map.ders_callback
        del d2.transport_map.params_callback

        # Get d2 from children processes and update counters
        if mpi_pool is not None:
            d2_child_list = mpi_pool.get_dmem('d2')
            d2.update_ncalls_tree( d2_child_list[0][0] )
            for (d2_child,) in d2_child_list:
                d2.update_nevals_tree(d2_child)
                d2.update_teval_tree(d2_child)

        # Log
        log = {}
        log['success'] = res['success']
        log['message'] = res['message']
        log['fval'] = res['fun']
        log['nit'] = res['nit']
        log['n_fun_ev'] = params['nobj']
        if ders >= 1:
            log['n_jac_ev'] = params['nda_obj']
            log['jac'] = res['jac']

        # Attach cache to log
        if mpi_pool is None:
            log['cache'] = cache
        else:
            log['cache'] = mpi_pool.get_dmem('cache')

        # Display stats
        if log['success']:
            d2.transport_map.logger.info("minimize_kl_divergence: Optimization terminated successfully")
        else:
            d2.transport_map.logger.warn("minimize_kl_divergence: Minimization of KL-divergence failed.")
            d2.transport_map.logger.warn("minimize_kl_divergence: Message: %s" % log['message'])
        d2.transport_map.logger.info("minimize_kl_divergence:   Function value:          %6f" % log['fval'])
        if ders >= 1:
            d2.transport_map.logger.info("minimize_kl_divergence:   Norm of the Jacobian:    %6f" % npla.norm(log['jac']))
        d2.transport_map.logger.info("minimize_kl_divergence:   Number of iterations:    %6d" % log['nit'])
        d2.transport_map.logger.info("minimize_kl_divergence:   N. function evaluations: %6d" % log['n_fun_ev'])
        if ders >= 1:
            d2.transport_map.logger.info("minimize_kl_divergence:   N. Jacobian evaluations: %6d" % log['n_jac_ev'])

        # Clear mpi_pool and detach object
        if mpi_pool is not None:
            mpi_pool.clear_dmem()

        # Set coefficients
        d2.coeffs = res['x']
        return log


def minimize_kl_divergence_pointwise_monotone_constraints(a, params):
    d2 = params['d2']
    tm = d2.transport_map
    mpi_pool = params['mpi_pool']
    # Update distribution coefficients
    bcast_tuple = (['coeffs'],[a])
    mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
            obj='tm', obj_val=tm,
            mpi_pool=mpi_pool, concatenate=False)
    # Evaluate
    x = params['x']
    dmem_key_in_list = ['params_t', 'x']
    dmem_arg_in_list = ['precomp', 'x']
    dmem_val_in_list = [ params['params_t'], x ]
    out = mpi_map("partial_xd",
                  dmem_key_in_list=dmem_key_in_list,
                  dmem_arg_in_list=dmem_arg_in_list,
                  dmem_val_in_list=dmem_val_in_list,
                  obj='tm', obj_val=tm,
                  mpi_pool=mpi_pool)
    return out.reshape( out.shape[0] * out.shape[1] )


def minimize_kl_divergence_pointwise_monotone_da_constraints(a, params):
    d2 = params['d2']
    tm = d2.transport_map
    mpi_pool = params['mpi_pool']
    # Update distribution coefficients
    bcast_tuple = (['coeffs'],[a])
    mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
            obj='tm', obj_val=tm,
            mpi_pool=mpi_pool, concatenate=False)
    # Evaluate
    x = params['x']
    dmem_key_in_list = ['params_t', 'x']
    dmem_arg_in_list = ['precomp', 'x']
    dmem_val_in_list = [ params['params_t'], x ]
    out = mpi_map("grad_a_partial_xd",
                  dmem_key_in_list=dmem_key_in_list,
                  dmem_arg_in_list=dmem_arg_in_list,
                  dmem_val_in_list=dmem_val_in_list,
                  obj='tm', obj_val=tm,
                  mpi_pool=mpi_pool)
    return out.reshape( (out.shape[0]*out.shape[1], tm.n_coeffs) )


def minimize_kl_divergence_pointwise_monotone_component(
        f, x, w,
        x0=None,
        regularization=None,
        tol=1e-4, maxit=100, ders=2,
        fungrad=False,
        precomp_type='uni',
        batch_size=None,
        cache_level=1,
        mpi_pool=None
):
    r""" Compute :math:`{\bf a}^\star = \arg\min_{\bf a}-\sum_{i=0}^m \log\pi\circ T_k(x_i) + \log\partial_{x_k}T_k(x_i) = \arg\min_{\bf a}-\sum_{i=0}^m f(x_i)`

    Args:
      f (ProductDistributionParametricPullbackComponentFunction): function :math:`f`
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
      x0 (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients to be used
        as initial values for the optimization
      regularization (dict): defines the regularization to be used.
        If ``None``, no regularization is applied.
        If key ``type=='L2'`` then applies Tikonhov regularization with
        coefficient in key ``alpha``.
      tol (float): tolerance to be used to solve the KL-divergence problem.
      maxit (int): maximum number of iterations
      ders (int): order of derivatives available for the solution of the
        optimization problem. 0 -> derivative free, 1 -> gradient, 2 -> hessian.
      fungrad (bool): whether the distributions :math:`\pi_1,\pi_2` provide the method
        :func:`Distribution.tuple_grad_x_log_pdf` computing the evaluation and the
        gradient in one step. This is used only for ``ders==1``.
      precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
        multivariate Vandermonde matrices 'multi'
      batch_size (:class:`list<list>` [3 or 2] of :class:`int<int>` or :class:`list<list>` of ``batch_size``):
        the list contains the
        size of the batch to be used for each iteration. A size ``1`` correspond
        to a completely non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one.
        If the target distribution is a :class:`ProductDistribution`, then
        the optimization problem decouples and
        ``batch_size`` is a list of lists containing the batch sizes to be
        used for each component of the map.
      cache_level (int): use high-level caching during the optimization, storing the
        function evaluation ``0``, and the gradient evaluation ``1`` or
        nothing ``-1``
      mpi_pool (:class:`mpi_map.MPI_Pool` or :class:`list<list>` of ``mpi_pool``):
        pool of processes to be used, ``None`` stands for one process.
        If the target distribution is a :class:`ProductDistribution`, then
        the minimization problem decouples and ``mpi_pool`` is a list containing
        ``mpi_pool``s for each component of the map.
    """
    f.tmap_component.logger.debug("minimize_kl_divergence_component(): Precomputation started")

    if batch_size is None:
        batch_size = [None] * 3
    # Distribute objects
    mpi_bcast_dmem(f=f, mpi_pool=mpi_pool)
    # Link tm_comp to f.tmap_component
    def link_tmcmp(f):
        return (f.tmap_component,)
    (tm_comp,) = mpi_map_alloc_dmem(
        link_tmcmp, dmem_key_in_list=['f'], dmem_arg_in_list=['f'],
        dmem_val_in_list=[f], dmem_key_out_list=['tm_comp'],
        mpi_pool=mpi_pool)
    # Init memory
    paramsf = {'params_pi': None,
               'params_t': {} }
    mpi_bcast_dmem(paramsf=paramsf, mpi_pool=mpi_pool)
    dmem_key_in_list = ['paramsf']
    dmem_arg_in_list = ['params']
    dmem_val_in_list = [paramsf]
    # precomp_minimize_kl_divergence_component
    scatter_tuple = (['x'],[x])
    bcast_tuple = (['precomp_type'],[precomp_type])
    mpi_map("precomp_minimize_kl_divergence_component",
            scatter_tuple=scatter_tuple,
            bcast_tuple=bcast_tuple,
            dmem_key_in_list=dmem_key_in_list,
            dmem_arg_in_list=dmem_arg_in_list,
            dmem_val_in_list=dmem_val_in_list,
            obj='tm_comp', obj_val=tm_comp,
            mpi_pool=mpi_pool, concatenate=False)
    # allocate_cache_minimize_kl_divergence_component
    scatter_tuple = (['x'],[x])
    (cache, ) = mpi_map_alloc_dmem(
        "allocate_cache_minimize_kl_divergence_component",
        scatter_tuple=scatter_tuple,
        dmem_key_out_list=['cache'],
        obj='tm_comp', obj_val=tm_comp,
        mpi_pool=mpi_pool, concatenate=False)
    f.tmap_component.logger.debug("minimize_kl_divergence(): Precomputation ended")

    params = {}
    params['nobj'] = 0
    params['nda_obj'] = 0
    params['x'] = x
    params['w'] = w
    params['f'] = f
    params['paramsf'] = paramsf
    params['batch_size'] = batch_size
    params['cache'] = cache
    params['regularization'] = regularization
    params['mpi_pool'] = mpi_pool

    if x0 is None:
        x0 = f.tmap_component.get_default_init_values_minimize_kl_divergence_component()

    # Link params_t on the first level of params
    # (this is needed for the MPI implementation of the constraints)
    def link_params_t(params):
        return (params['params_t'],)
    (params['params_t'],) = mpi_map_alloc_dmem(
        link_params_t,
        dmem_key_in_list = ['paramsf'],
        dmem_arg_in_list = ['params'],
        dmem_val_in_list = [paramsf],
        dmem_key_out_list = ['params_t'],
        mpi_pool=mpi_pool)

    cons = ({'type': 'ineq',
             'fun': minimize_kl_divergence_pointwise_monotone_component_constraints,
             'jac': minimize_kl_divergence_pointwise_monotone_component_da_constraints,
             'args': (params,)})

    if cache_level >= 0:
        params['objective_cache_coeffs'] = x0 - 1.

    # Callback variables
    f.tmap_component.it_callback = 0
    f.tmap_component.ders_callback = ders
    f.tmap_component.params_callback = params

    # Options for optimizer
    options = {'maxiter': maxit,
               'disp': False}

    # Solve
    if ders == 0:
        res = sciopt.minimize(minimize_kl_divergence_component_objective,
                              args=params,
                              x0=x0,
                              constraints=cons,
                              method='SLSQP',
                              tol=tol,
                              options=options,
                              callback=f.tmap_component.minimize_kl_divergence_component_callback)
    elif ders == 1:
        if fungrad:
            raise NotImplementedError("Option fungrad not implemented for maps from samples")
            # res = sciopt.minimize(minimize_kl_divergence_tuple_grad_a_objective,
            #                       args=params, x0=x0,
            #                       jac=True,
            #                       constraints=cons,
            #                       method='SLSQP',
            #                       tol=tol,
            #                       options=options,
            #                       callback=f.tmap_component.minimize_kl_divergence_callback)
        else:
            res = sciopt.minimize(
                minimize_kl_divergence_component_objective, args=params,
                x0=x0,
                jac=minimize_kl_divergence_component_grad_a_objective,
                constraints=cons,
                method='SLSQP',
                tol=tol,
                options=options,
                callback=f.tmap_component.minimize_kl_divergence_component_callback)
    else:
        raise NotImplementedError(
            "ders is %d, but must be ders=[0,1] " % ders + \
            "with MonotonicLinearSpanApproximation."
        )

    # Clean up callback stuff
    del f.tmap_component.it_callback
    del f.tmap_component.ders_callback
    del f.tmap_component.params_callback

    # Log
    log = {}
    log['success'] = res['success']
    log['message'] = res['message']
    log['fval'] = res['fun']
    log['nit'] = res['nit']
    log['n_fun_ev'] = params['nobj']
    if ders >= 1:
        log['n_jac_ev'] = params['nda_obj']
        log['jac'] = res['jac']
    # Display stats
    if log['success']:
        f.tmap_component.logger.info("Optimization terminated successfully")
    else:
        f.tmap_component.logger.info("Optimization failed.")
        f.tmap_component.logger.info("Message: %s" % log['message'])
    f.tmap_component.logger.info("  Function value:          %6f" % log['fval'])
    if ders >= 1:
        f.tmap_component.logger.info("  Norm of the Jacobian:    %6f" % npla.norm(log['jac']))
    f.tmap_component.logger.info("  Number of iterations:    %6d" % log['nit'])
    f.tmap_component.logger.info("  N. function evaluations: %6d" % log['n_fun_ev'])
    if ders >= 1:
        f.tmap_component.logger.info("  N. Jacobian evaluations: %6d" % log['n_jac_ev'])

    # Set coefficients
    f.tmap_component.coeffs = res['x']
    return log


def minimize_kl_divergence_pointwise_monotone_component_constraints(a, params):
    f = params['f']
    tmap_component = f.tmap_component
    mpi_pool = params['mpi_pool']
    # Update coefficients
    bcast_tuple = (['coeffs'],[a])
    mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
            obj='tm_comp', obj_val=tmap_component,
            mpi_pool=mpi_pool, concatenate=False)
    # Evaluate
    x = params['x']
    scatter_tuple = (['x'], [x])
    dmem_key_in_list = ['params_t']
    dmem_arg_in_list = ['precomp']
    dmem_val_in_list = [ params['params_t'] ]
    out = mpi_map("partial_xd", scatter_tuple=scatter_tuple,
                  dmem_key_in_list=dmem_key_in_list,
                  dmem_arg_in_list=dmem_arg_in_list,
                  dmem_val_in_list=dmem_val_in_list,
                  obj='tm_comp', obj_val=tmap_component,
                  mpi_pool=mpi_pool)
    return out[:,0]


def minimize_kl_divergence_pointwise_monotone_component_da_constraints(a, params):
    f = params['f']
    tmap_component = f.tmap_component
    mpi_pool = params['mpi_pool']
    # Update coefficients
    bcast_tuple = (['coeffs'],[a])
    mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
            obj='tm_comp', obj_val=tmap_component,
            mpi_pool=mpi_pool, concatenate=False)
    # Evaluate
    x = params['x']
    scatter_tuple = (['x'], [x])
    dmem_key_in_list = ['params_t']
    dmem_arg_in_list = ['precomp']
    dmem_val_in_list = [ params['params_t'] ]
    out = mpi_map("grad_a_partial_xd", scatter_tuple=scatter_tuple,
                  dmem_key_in_list=dmem_key_in_list,
                  dmem_arg_in_list=dmem_arg_in_list,
                  dmem_val_in_list=dmem_val_in_list,
                  obj='tm_comp', obj_val=tmap_component,
                  mpi_pool=mpi_pool)
    return out[:, 0, :]
