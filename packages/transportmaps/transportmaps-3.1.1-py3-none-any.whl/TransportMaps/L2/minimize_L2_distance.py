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

import numpy as np
import numpy.linalg as npla
import scipy.optimize as sciopt
import scipy.linalg as scila

from ..L2 import L2squared_misfit, grad_a_L2squared_misfit, hess_a_L2squared_misfit, \
    storage_hess_a_L2squared_misfit, action_stored_hess_a_L2squared_misfit
from ..MPI import mpi_map, SumChunkReduce, mpi_map_alloc_dmem, mpi_bcast_dmem
from ..Maps.Functionals import ParametricFunctional
from ..Maps import ParametricComponentwiseMap, AffineTriangularMap


__all__ = [
    'map_regression',
    'functional_regression',
    'functional_regression_objective',
    'functional_regression_grad_a_objective',
    'functional_regression_hess_a_objective',
    'functional_regression_action_storage_hess_a_objective',
    'affine_triangular_map_regression'
]


def map_regression(
        tm: ParametricComponentwiseMap,
        t,
        tparams=None, d=None, qtype=None, qparams=None,
        x=None, w=None, x0=None,
        regularization=None, tol=1e-4, maxit=100,
        batch_size_list=None, mpi_pool_list=None):
    r""" Compute :math:`{\bf a}^* = \arg\min_{\bf a} \Vert T - T[{\bf a}] \Vert_{\pi}`.

    This regression problem can be completely decoupled if the measure
    is a product measure, obtaining

    .. math::

       a^{(i)*} = \arg\min_{\bf a^{(i)}} \Vert T_i - T_i[{\bf a}^{(i)}] \Vert_{\pi_i}

    Args:
      tm (ParametricComponentwiseMap): transport map :math:`T`
      t (function or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
        :math:`t` with signature ``t(x)`` or its functions values
      tparams (dict): parameters for function :math:`t`
      d (Distribution): distribution :math:`\pi`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      x0 (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients to be used
        as initial values for the optimization
      regularization (dict): defines the regularization to be used.
        If ``None``, no regularization is applied.
        If key ``type=='L2'`` then applies Tikonhov regularization with
        coefficient in key ``alpha``.
      tol (float): tolerance to be used to solve the regression problem.
      maxit (int): maximum number of iterations
      batch_size_list (:class:`list<list>` [d] :class:`tuple<tuple>` [3] :class:`int<int>`):
        Each of the tuples in the list corresponds to each component of the map.
        The entries of the tuple define whether to evaluate the regression
        in batches of a certain size or not.
        A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool_list (:class:`list<list>` [d] :class:`mpi_map.MPI_Pool` or ``None``):
        pool of processes to be used for function evaluation, gradient evaluation and
        Hessian evaluation for each component of the approximation.
        Value ``None`` will use serial evaluation.

    Returns:
      (:class:`list<list>` [:math:`d`]) containing log information from the
      optimizer.

    .. seealso:: :mod:`MonotonicApproximation`

    .. note:: the resulting coefficients :math:`{\bf a}` are automatically
       set at the end of the optimization. Use :func:`get_coeffs` in order
       to retrieve them.

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
       exclusive, but one pair of them is necessary.
    """
    if isinstance(tm, AffineTriangularMap):
        return affine_triangular_map_regression(
            tm, t, tparams, d=d, qtype=qtype, qparams=qparams, x=x, w=w, regularization=regularization
        )

    if batch_size_list is None:
        batch_size_list = [(None, None, None)] * tm.dim_out
    if len(batch_size_list) != tm.dim_out:
        raise ValueError("len(batch_size_list) must be equal to tm.dim_out")
    if mpi_pool_list is None:
        mpi_pool_list = [None] * tm.dim_out
    if len(mpi_pool_list) != tm.dim_out:
        raise ValueError("len(mpi_pool_list) must be equal to tm.dim_out")
    if (x is None) and (w is None):
        (x, w) = d.quadrature(qtype, qparams)
    if isinstance(t, np.ndarray):
        T = t
    else:
        T = t(x)

    log_entry_list = []
    start_x0 = 0
    reg = None
    tm.logger.info("Starting decoupled regression of map.")
    for i, (a, avar, batch_size_tuple, mpi_pool) in enumerate(zip(
            tm.approx_list, tm.active_vars, batch_size_list, mpi_pool_list)):
        tm.logger.debug("Regression on component %i" % i + \
                          " (dim: %d - ncoeffs: %d" % (a.dim_in, a.n_coeffs) + \
                          " - npoints: %d)" % x.shape[0])
        if regularization is not None and regularization['type'] == 'L2':
            reg = {'type': 'L2',
                   'alpha': a.n_coeffs * regularization['alpha'] / tm.n_coeffs}
        x0a = None
        if x0 is not None:
            x0a = x0[start_x0:start_x0 + a.n_coeffs]
            start_x0 += a.n_coeffs
        (coeffs, log_entry) = functional_regression(
            a, T[:, i], x=x[:, avar], w=w, x0=x0a,
            regularization=reg, tol=tol,
            maxit=maxit,
            batch_size=batch_size_tuple,
            mpi_pool=mpi_pool
        )
        log_entry_list.append(log_entry)
        if not log_entry['success']:
            tm.logger.warning("Regression on component %i failed." % i)
    tm.logger.info("Finished decoupled regression of map.")
    return log_entry_list

def functional_regression(
        fn: ParametricFunctional,
        f,
        fparams=None, d=None, qtype=None, qparams=None,
        x=None, w=None, x0=None, regularization=None, tol=1e-4, maxit=100,
        batch_size=(None, None, None), mpi_pool=None, import_set=set()
):
    r""" Compute :math:`{\bf a}^* = \arg\min_{\bf a} \Vert f - f_{\bf a} \Vert_{\pi}`.

    Args:
      fn (ParametricFunctional): the function :math:`f_{\bf a}`
      f (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
        :math:`f` or its functions values
      fparams (dict): parameters for function :math:`f`
      d (Distribution): distribution :math:`\pi`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      x0 (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients to be used
        as initial values for the optimization
      regularization (dict): defines the regularization to be used.
        If ``None``, no regularization is applied.
        If key ``type=='L2'`` then applies Tikonhov regularization with
        coefficient in key ``alpha``.
      tol (float): tolerance to be used to solve the regression problem.
      maxit (int): maximum number of iterations
      batch_size (:class:`list<list>` [3] of :class:`int<int>`): the list contains the
        size of the batch to be used for each iteration. A size ``1`` correspond
        to a completely non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one.
      mpi_pool (:class:`mpi_map.MPI_Pool`): pool of processes to be used
      import_set (set): list of couples ``(module_name,as_field)`` to be imported
        as ``import module_name as as_field`` (for MPI purposes)

    Returns:
      (:class:`tuple<tuple>`(:class:`ndarray<numpy.ndarray>` [:math:`N`],
      :class:`list<list>`)) -- containing the :math:`N` coefficients and
      log information from the optimizer.

    .. seealso:: :func:`TransportMaps.TriangularTransportMap.regression`

    .. note:: the resulting coefficients :math:`{\bf a}` are automatically
       set at the end of the optimization. Use :func:`coeffs` in order
       to retrieve them.

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
       exclusive, but one pair of them is necessary.
    """
    if (x is None) and (w is None):
        (x, w) = d.quadrature(qtype, qparams)

    params = {}
    params['fn'] = fn
    params['x'] = x
    params['w'] = w
    params['regularization'] = regularization
    params['batch_size'] = batch_size
    params['nobj'] = 0
    params['nda_obj'] = 0
    params['nda2_obj'] = 0
    params['nda2_obj_dot'] = 0
    params['hess_assembled'] = False
    params['mpi_pool'] = mpi_pool
    options = {'maxiter': maxit,
               'disp': False}
    if x0 is None:
        x0 = fn.get_default_init_values_regression()
    if fn.logger.getEffectiveLevel() <= logging.DEBUG:
        fn.logger.debug("regression(): Precomputation started")
    if isinstance(f, np.ndarray):
        params['fvals'] = f
    else:
        scatter_tuple = (['x'], [x])
        bcast_tuple = (['precomp'], [fparams])
        params['fvals'] = mpi_map("evaluate", scatter_tuple=scatter_tuple,
                                  bcast_tuple=bcast_tuple,
                                  obj=f, mpi_pool=mpi_pool)
    # Init precomputation memory
    params['params1'] = {}
    mpi_bcast_dmem(params1=params['params1'], f1=fn, mpi_pool=mpi_pool)
    # Precompute
    scatter_tuple = (['x'], [x])
    mpi_map("precomp_regression", scatter_tuple=scatter_tuple,
            dmem_key_in_list=['params1'],
            dmem_arg_in_list=['precomp'],
            dmem_val_in_list=[params['params1']],
            obj='f1', obj_val=fn,
            mpi_pool=mpi_pool, concatenate=False)

    if fn.logger.getEffectiveLevel() <= logging.DEBUG:
        fn.logger.debug("regression(): Precomputation ended")

    # Callback variables
    fn.params_callback = params

    # Minimize
    res = sciopt.minimize(
        functional_regression_objective, args=params, x0=x0,
        jac=functional_regression_grad_a_objective,
        # hessp=functional_regression_action_storage_hess_a_objective,
        # method='Newton-CG',
        method='BFGS',
        tol=tol, options=options,
        callback=fn.regression_callback)
    if not res['success']:
        fn.logger.warn("Regression failure: " + res['message'])

    # Clean up callback stuff
    del fn.params_callback

    coeffs = res['x']
    fn.coeffs = coeffs
    return (coeffs, res)


def functional_regression_objective(a, params):
    r""" Objective function :math:`\Vert f - f_{\bf a} \Vert^2_{\pi}`

    Args:
      a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
      params (dict): dictionary of parameters
    """
    fn = params['fn']
    params['nobj'] += 1
    x = params['x']
    w = params['w']
    fvals = params['fvals']
    batch_size = params['batch_size'][0]
    mpi_pool = params['mpi_pool']
    # Update coefficients
    bcast_tuple = (['coeffs'], [a])
    mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
            obj='f1', obj_val=fn,
            mpi_pool=mpi_pool, concatenate=False)
    # Evaluate L2 misfit
    scatter_tuple = (['x', 'w', 'f2'], [x, w, fvals])
    bcast_tuple = (['batch_size'], [batch_size])
    dmem_key_in_list = ['f1', 'params1']
    dmem_arg_in_list = ['f1', 'params1']
    dmem_val_in_list = [fn, params['params1']]
    reduce_obj = SumChunkReduce(axis=0)
    out = mpi_map(L2squared_misfit, scatter_tuple=scatter_tuple,
                  bcast_tuple=bcast_tuple,
                  dmem_key_in_list=dmem_key_in_list,
                  dmem_arg_in_list=dmem_arg_in_list,
                  dmem_val_in_list=dmem_val_in_list,
                  reduce_obj=reduce_obj,
                  mpi_pool=mpi_pool)
    if params['regularization'] is None:
        pass
    elif params['regularization']['type'] == 'L2':
        out += params['regularization']['alpha'] * \
               npla.norm(a - fn.regression_nominal_coeffs(), 2) ** 2.
    fn.logger.debug("Regression Obj. Eval. %d - L2-misfit = %.10e" % (params['nobj'], out))
    return out


def functional_regression_grad_a_objective(a, params):
    r""" Objective function :math:`\nabla_{\bf a} \Vert f - f_{\bf a} \Vert^2_{\pi}`

    Args:
      a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
      params (dict): dictionary of parameters
    """
    fn = params['fn']
    params['nda_obj'] += 1
    x = params['x']
    w = params['w']
    fvals = params['fvals']
    batch_size = params['batch_size'][1]
    mpi_pool = params['mpi_pool']
    # Update coefficients
    bcast_tuple = (['coeffs'], [a])
    mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
            obj='f1', obj_val=fn,
            mpi_pool=mpi_pool, concatenate=False)
    # Evaluate grad_a L2 misfit
    scatter_tuple = (['x', 'w', 'f2'], [x, w, fvals])
    bcast_tuple = (['batch_size'], [batch_size])
    dmem_key_in_list = ['f1', 'params1']
    dmem_arg_in_list = ['f1', 'params1']
    dmem_val_in_list = [fn, params['params1']]
    reduce_obj = SumChunkReduce(axis=0)
    out = mpi_map(grad_a_L2squared_misfit,
                  scatter_tuple=scatter_tuple,
                  bcast_tuple=bcast_tuple,
                  dmem_key_in_list=dmem_key_in_list,
                  dmem_arg_in_list=dmem_arg_in_list,
                  dmem_val_in_list=dmem_val_in_list,
                  reduce_obj=reduce_obj,
                  mpi_pool=mpi_pool)
    if params['regularization'] is None:
        pass
    elif params['regularization']['type'] == 'L2':
        out += params['regularization']['alpha'] * \
               2. * (a - fn.regression_nominal_coeffs())
    fn.logger.debug("Regression Grad_a Obj. Eval. %d - ||grad_a L2-misfit|| = %.10e" % (
        params['nda_obj'], npla.norm(out)))
    return out


def functional_regression_hess_a_objective(a, params):
    r""" Objective function :math:`\nabla_{\bf a}^2 \Vert f - f_{\bf a} \Vert^2_{\pi}`

    Args:
      a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
      params (dict): dictionary of parameters
    """
    fn = params['fn']
    params['nda2_obj'] += 1
    x = params['x']
    w = params['w']
    fvals = params['fvals']
    batch_size = params['batch_size'][2]
    mpi_pool = params['mpi_pool']
    # Update coefficients
    bcast_tuple = (['coeffs'], [a])
    mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
            obj='f1', obj_val=fn,
            mpi_pool=mpi_pool, concatenate=False)
    # Evaluate hess_a L2 misfit
    scatter_tuple = (['x', 'w', 'f2'], [x, w, fvals])
    bcast_tuple = (['batch_size'], [batch_size])
    dmem_key_in_list = ['f1', 'params1']
    dmem_arg_in_list = ['f1', 'params1']
    dmem_val_in_list = [fn, params['params1']]
    reduce_obj = SumChunkReduce(axis=0)
    out = mpi_map(hess_a_L2squared_misfit,
                  scatter_tuple=scatter_tuple,
                  bcast_tuple=bcast_tuple,
                  dmem_key_in_list=dmem_key_in_list,
                  dmem_arg_in_list=dmem_arg_in_list,
                  dmem_val_in_list=dmem_val_in_list,
                  reduce_obj=reduce_obj,
                  mpi_pool=mpi_pool)
    if params['regularization'] is None:
        pass
    elif params['regularization']['type'] == 'L2':
        out += np.diag( np.ones(len(fn.coeffs))*2.*params['regularization']['alpha'] )
    fn.logger.debug("Regression Hess_a Obj. Eval. %d " % params['nda2_obj'])
    return out


def functional_regression_action_storage_hess_a_objective(a, v, params):
    r""" Assemble/fetch Hessian :math:`\nabla_{\bf a}^2 \Vert f - f_{\bf a} \Vert^2_{\pi}` and evaluate its action on :math:`v`

    Args:
      a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
      v (:class:`ndarray<numpy.ndarray>` [:math:`N`]): vector on which to apply the Hessian
      params (dict): dictionary of parameters
    """
    fn = params['fn']
    x = params['x']
    w = params['w']
    fvals = params['fvals']
    batch_size = params['batch_size'][2]
    mpi_pool = params['mpi_pool']
    # Update coefficients
    bcast_tuple = (['coeffs'], [a])
    mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
            obj='f1', obj_val=fn,
            mpi_pool=mpi_pool, concatenate=False)
    # Assemble Hessian
    if not params['hess_assembled']:
        params['nda2_obj'] += 1
        scatter_tuple = (['x', 'w', 'f2'], [x, w, fvals])
        bcast_tuple = (['batch_size'], [batch_size])
        dmem_key_in_list = ['f1', 'params1']
        dmem_arg_in_list = ['f1', 'params1']
        dmem_val_in_list = [fn, params['params1']]
        dmem_key_out_list = ['hess_a_L2_misfit']
        (params['hess_a_L2_misfit'], ) = mpi_map_alloc_dmem(
            storage_hess_a_L2squared_misfit, scatter_tuple=scatter_tuple,
            bcast_tuple=bcast_tuple, dmem_key_in_list=dmem_key_in_list,
            dmem_arg_in_list=dmem_arg_in_list, dmem_val_in_list=dmem_val_in_list,
            dmem_key_out_list=dmem_key_out_list,
            mpi_pool=mpi_pool, concatenate=False)
        params['hess_assembled'] = True
        fn.logger.debug("Regression Storage Hess_a Obj. Eval. %d " % params['nda2_obj'])
    # Evaluate the action of hess_a L2 misfit
    params['nda2_obj_dot'] += 1
    bcast_tuple = (['v'], [v])
    dmem_key_in_list = ['hess_a_L2_misfit']
    dmem_arg_in_list = ['H']
    dmem_val_in_list = [params['hess_a_L2_misfit']]
    reduce_obj = SumChunkReduce(axis=0)
    out = mpi_map(action_stored_hess_a_L2squared_misfit,
                  bcast_tuple=bcast_tuple,
                  dmem_key_in_list=dmem_key_in_list,
                  dmem_arg_in_list=dmem_arg_in_list,
                  dmem_val_in_list=dmem_val_in_list,
                  reduce_obj=reduce_obj,
                  mpi_pool=mpi_pool)
    if params['regularization'] is None:
        pass
    elif params['regularization']['type'] == 'L2':
        regmat = np.diag( np.ones(len(fn.coeffs))*2.*params['regularization']['alpha'] )
        out += np.dot(regmat, v)
    fn.logger.debug("Regression Action Hess_a Obj. Eval. %d " % params['nda2_obj_dot'])
    return out


def affine_triangular_map_regression(
        tm: ParametricComponentwiseMap,
        t,
        tparams=None, d=None, qtype=None, qparams=None,
        x=None, w=None, regularization=None, **kwargs):
    r""" Compute :math:`{\bf a}^* = \arg\min_{\bf a} \Vert T - T({\bf a}) \Vert_{\pi}`.

    This regression problem can be completely decoupled if the measure
    is a product measure, obtaining

    .. math::

       a^{(i)*} = \arg\min_{\bf a^{(i)}} \Vert T_i - T_i({\bf a}^{(i)}) \Vert_{\pi_i}

    Args:
      tm (ParametricComponentwiseMap): map :math:`T({\bf a})`
      t (function or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
        :math:`t` with signature ``t(x)`` or its functions values
      tparams (dict): parameters for function :math:`t`
      d (Distribution): distribution :math:`\pi`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      regularization (dict): defines the regularization to be used.
        If ``None``, no regularization is applied.
        If key ``type=='L2'`` then applies Tikonhov regularization with
        coefficient in key ``alpha``.

    Returns:
      (:class:`tuple<tuple>` (:class:`ndarray<numpy.ndarray>` [:math:`N`],
      :class:`list<list>`)) -- containing the :math:`N` coefficients and
      log information.

    .. note:: the resulting coefficients :math:`{\bf a}` are automatically
       set at the end of the optimization. Use :func:`get_coeffs` in order
       to retrieve them.

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
       exclusive, but one pair of them is necessary.
    """
    if not isinstance(tm, AffineTriangularMap):
        raise ValueError('This routine for regression is designed only for AffineTriangularMap')

    if (x is None) and (w is None):
        (x,w) = d.quadrature(qtype, qparams)
    if isinstance(t, np.ndarray):
        T = t
    else:
        T = t(x)
    # Build weighted invsersion matrix
    X = np.hstack( (np.ones((x.shape[0],1)), x) )
    XW = X * w[:,np.newaxis]
    P = np.dot(XW.T, X)
    # Regularization
    if regularization is not None:
        if regularization['type'] == 'L2':
            P += regularization['alpha'] * np.eye(P.shape[0])
        else:
            raise NotImplementedError(
                "Regularization type %s not implemented." % regularization['type'])
    # Compute cholesky decomposition of inversion matrix
    U = scila.cholesky(P)
    # Iterate over the dimensions and solve for each component
    # (enforcing lower triangular structure)
    cnst = np.zeros(tm.dim)
    lin = np.zeros((tm.dim,tm.dim))
    for i in range(tm.dim):
        XWi = XW[:,:i+2]
        Ui = U[:i+2,:i+2]
        Ti = T[:,i]
        # Compute right hand side
        rhs = np.dot(XWi.T, Ti)
        # Solve system
        beta = scila.solve_triangular(Ui, rhs, lower=False, trans='T')
        beta = scila.solve_triangular(Ui, beta, lower=False)
        # Write coefficients
        cnst[i] = beta[0]
        lin[i,:i+1] = beta[1:]
    tm.c = cnst
    tm.L = lin
    log = {'success': True}
    return (tm.coeffs, log)
