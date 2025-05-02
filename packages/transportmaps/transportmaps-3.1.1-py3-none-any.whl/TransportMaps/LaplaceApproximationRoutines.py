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
from typing import Union

import numpy as np
import numpy.linalg as npla
import scipy.optimize as sciopt

from .Misc import logger
from .DerivativesChecks import fd
from .Distributions.FrozenDistributions import \
    StandardNormalDistribution, NormalDistribution
from .Distributions.Deprecated import GaussianDistribution
from .Distributions.Inference.InferenceBase import \
    BayesPosteriorDistribution
from .Likelihoods.LikelihoodBase import \
    AdditiveLogLikelihood, IndependentLogLikelihood
from .RandomizedLinearAlgebra.RandomizedLinearAlgebra import \
    randomized_direct_eig, randomized_direct_svd

__all__ = [
    'laplace_approximation','laplace_approximation_withBounds',
]

nax = np.newaxis


def is_normal(pi):
    return issubclass(type(pi.prior), NormalDistribution) or \
        issubclass(type(pi.prior), GaussianDistribution) or \
        issubclass(type(pi.prior), StandardNormalDistribution)


def laplace_approximation(
        pi,
        params: Union[dict, None] = None,
        x0=None,
        tol=1e-5,
        ders=2,
        fungrad=False,
        hessact=False,
        hess_approx='low-rank',
        hess_fd_eps=1e-6,
        low_rank_rnd_eps=1e-5,
        low_rank_rnd_ovsamp=10,
        low_rank_rnd_pow_n=0
):
    r""" Compute the Laplace approximation of the distribution :math:`\pi`.

    Args:
      pi (Distribution): distribution :math:`\pi`
      params (dict): parameters for distribution :math:`\pi`
      tol (float): tolerance to be used to solve the maximization problem.
      ders (int): order of derivatives available for the solution of the
        optimization problem. 0 -> derivative free, 1 -> gradient, 2 -> hessian.
      fungrad (bool): whether the distribution :math:`\pi` provide the method
        :func:`Distribution.tuple_grad_x_log_pdf` computing the evaluation and the
        gradient in one step. This is used only for ``ders>=1``.
      hessact (bool): whether the distribution :math:`\pi` provides the method
        :func:`Distribution.action_hess_x_log_pdf` computing the action of the
        Hessian on a vector. This is used only for ``ders==2``
      hess_approx (str): whether to compute a finite difference Hessian ``fd``,
        or a low-rank approximation of it ``low-rank``. This is used only if ``ders==1``.
      hess_fd_eps (float): tolerance for finite difference Hessian
      low_rank_rnd_eps (float): tolerance to be used in the pursue of a randomized
        low-rank approximation of the prior preconditioned Hessian of the log-likelihood
      low_rank_rnd_pow_n (int): number of power iterations to be used in the pursue of a randomized
        low-rank approximation of the prior preconditioned Hessian of the log-likelihood
      low_rank_rnd_ovsamp (int): oversampling to be used in the pursue of a randomized
        low-rank approximation of the prior preconditioned Hessian of the log-likelihood

    Returns:
      (:class:`NormalDistribution`) -- Laplace approximation
    """
    # Minimize :math:`-\log \pi`
    if params is None:
        params = {}
    params['nobj'] = 0
    params['gx_nobj'] = 0
    params['hx_nobj'] = 0
    def objective(x, params, cache=None):
        reset_cache(cache)
        params['nobj'] += 1
        out = - pi.log_pdf(x[nax,:], cache=cache)[0]
        logger.info("Lap. Obj. Eval. %d - f val. = %.10e" % (params['nobj'], out))
        return out
    def dx_objective(x, params, cache=None):
        params['gx_nobj'] += 1
        out = - pi.grad_x_log_pdf(x[nax,:], cache=cache)[0,:]
        logger.info(
            "Lap. Grad. Obj. Eval. %d " % params['nobj'] + \
            "- ||grad f|| = %.10e" % npla.norm(out))
        return out
    def tuple_dx_objective(x, params, cache=None):
        reset_cache(cache)
        params['nobj'] += 1
        params['gx_nobj'] += 1
        ev, gx = pi.tuple_grad_x_log_pdf(x[nax,:], cache=cache)
        ev = -ev[0]
        gx = -gx[0,:]
        logger.info("Lap. Obj. Eval. %d - f val. = %.10e" % (params['nobj'], ev))
        logger.info(
            "Lap. Grad. Obj. Eval. %d " % params['nobj'] + \
            "- ||grad f|| = %.10e" % npla.norm(gx))
        return ev, gx
    def dx2_objective(x, params, cache=None):
        params['hx_nobj'] += 1
        out = - pi.hess_x_log_pdf(x[nax,:], cache=cache)[0,:,:]
        logger.info(
            "Lap. Hess. Obj. Eval. %d " % params['hx_nobj'])
        return out
    def action_dx2_objective(x, dx, params, cache=None):
        params['hx_nobj'] += 1
        out = - pi.action_hess_x_log_pdf(x[nax,:], dx[nax,:], cache=cache)[0,:]
        logger.info(
            "Lap. Action Hess. Obj. Eval. %d " % params['hx_nobj'])
        return out
    def reset_cache(cache):
        if cache is not None:
            tot_size = cache['tot_size']
            cache.clear()
            cache['tot_size'] = tot_size
    if x0 is None:
        if issubclass(type(pi), BayesPosteriorDistribution):
            try:
                x0 = pi.prior.rvs(1).flatten()
            except NotImplementedError:
                logger.warning(
                    "laplace_approximation(): " + \
                    "Sampling from the prior is not implemented. " + \
                    "Initial conditions set to zero.")
                x0 = np.zeros(pi.dim)
        else:
            x0 = np.zeros(pi.dim) # Random or zero starting point? Or input argument?
    options = {'maxiter': 10000,
               'disp': False}

    cache = {'tot_size': 1}
    args = (params, cache)

    if ders >= 1:
        if fungrad:
            fun = tuple_dx_objective
            jac = True
        else:
            fun = objective
            jac = dx_objective
    
    if ders == 0:
        res = sciopt.minimize(
            objective, args=args, x0=x0,
            method='BFGS', tol=tol, options=options)
    elif ders == 1:
        res = sciopt.minimize(
            fun, args=args, x0=x0, jac=jac,
            method='BFGS', tol=tol, options=options)
    elif ders == 2:
        if hessact:
            res = sciopt.minimize(
                fun, args=args, x0=x0, jac=jac,
                hessp=action_dx2_objective,
                method='newton-cg', tol=tol, options=options)
        else:
            res = sciopt.minimize(
                fun, args=args, x0=x0, jac=jac,
                hess=dx2_objective, method='newton-cg',
                tol=tol, options=options)
    else:
        raise ValueError("ders parameter not valid. Chose between 0,1,2.")
    # Log
    if res['success']:
        logger.info("Optimization terminated successfully")
    else:
        logger.info("Optimization failed.")
        logger.info("Message: %s" % res['message'])
    logger.info("  Function value:          %6f" % res['fun'])
    if ders >= 1:
        logger.info(
            "  Jacobian: " + \
            "2-norm: %e " % npla.norm(res['jac'], 2) + \
            "inf-norm: %e" % npla.norm(res['jac'], np.inf)
        )
    logger.info("  Number of iterations:    %6d" % res['nit'])
    logger.info("  N. function evaluations: %6d" % res['nfev'])
    if ders >= 1:
        logger.info("  N. Jacobian evaluations: %6d" % res['njev'])
    if ders >= 2:
        logger.info("  N. Hessian evaluations:  %6d" % res['nhev'])
        
    # Set MAP point
    x_map = res['x']
    # Compute the Hessian at the maximizer
    if ders > 0:
        if ders == 2:
            if not hessact:
                hess_map = - pi.hess_x_log_pdf( x_map[nax,:] )[0,:,:]
                d_laplace = NormalDistribution(x_map, precision=hess_map)
            elif issubclass(type(pi), BayesPosteriorDistribution) and is_normal(pi):
                logger.info("Building low-rank approximation of the Hessian " + \
                            "from action of the Hessian")
                # Low-rank Hessian from action of Hessian
                sqrt = bayes_low_rank_sqrt_approximation_hessact(
                    x_map[nax,:], pi, low_rank_rnd_eps, low_rank_rnd_ovsamp,
                    power_n=low_rank_rnd_pow_n)
                d_laplace = NormalDistribution(x_map, square_root_covariance=sqrt)
        elif ders==1 and hess_approx == 'low-rank' and \
             issubclass(type(pi), BayesPosteriorDistribution) and is_normal(pi) and \
             (
                 ( issubclass(type(pi.logL), AdditiveLogLikelihood) and is_normal(pi) ) or \
                 (
                     issubclass(type(pi.logL), IndependentLogLikelihood) and \
                     all(
                         ( issubclass(type(ll), AdditiveLogLikelihood) and is_normal(pi) ) for \
                         ll in pi.logL.factors
                     )
                 )
             ):
            logger.info("Building low-rank approximation of the Hessian from gradients")
            # Construct low-rank approximation
            sqrt = bayes_low_rank_sqrt_approximation_outer_grad(
                x_map[nax,:], pi, low_rank_rnd_eps, low_rank_rnd_ovsamp,
                power_n=low_rank_rnd_pow_n)
            d_laplace = NormalDistribution(x_map, square_root_covariance=sqrt)
        else: # Finite difference
            logger.info("Building finite difference approximation of the Hessian")
            hess_map = - fd(pi.grad_x_log_pdf, x_map[nax,:], hess_fd_eps)[0,:,:]
            d_laplace = NormalDistribution(x_map, precision=hess_map)
    else:
        raise NotImplementedError("The finite difference Hessian is not implemented " + \
                                  "for ders==0.")
    return d_laplace


def bayes_low_rank_sqrt_approximation_outer_grad(x, pi, eps, r, power_n):
    def action(dx, gx_ll_list, factors, prior, dim, dim_obs):
        Y = np.zeros((dim, dx.shape[1]))
        start = 0    
        for gx_ll, (ll, xidxs) in zip(gx_ll_list, factors):
            stop = start + ll.y.shape[0]
            # Compute (\Gamma_{obs}^{-1/2} dx) for the current factor
            G = ll.pi.solve_square_root_covariance_transposed(dx[start:stop,:])
            # Compute ((\nabla_x G(x))^T \Gamma_{obs}^{-1/2} dx) for the current factors
            Y[xidxs,:] += np.einsum(
                'ij,i...->j...', gx_ll, G )
            # Y[xidxs,:] += np.einsum(
            #     '...ij,i...->j...',
            #     ll.T.grad_x(np.tile(x,(dx.shape[1],1))), G )
            start = stop
        # Compute (\Gamma_pr^{\top/2}(\nabla_x G(x))^\top \Gamma_{obs}^{-\top/2} dx))
        Y = prior.square_root_covariance.T.dot(Y)
        return Y
    def action_transpose(dx, gx_ll_list, factors, prior, dim, dim_obs):
        # Compute (\Gamma_pr^{1/2} dx)
        P = prior.square_root_covariance.dot(dx)
        Y = np.zeros((dim_obs, dx.shape[1]))
        start = 0
        for gx_ll, (ll, xidxs) in zip(gx_ll_list, factors):
            stop = start + ll.y.shape[0]
            # Compute ((\nabla_x G(x)) \Gamma_pr^{1/2} dx)
            GP = np.einsum(
                'ij,j...->i...', gx_ll, P)
            # GP = np.einsum(
            #     '...ij,j...->i...',
            #     ll.T.grad_x(np.tile(x,(dx.shape[1],1))), P)
            # Compute (\Gamma_{obs}^{-1/2} (\nabla_x G(x)) \Gamma_pr^{1/2} dx)
            Y[start:stop,:] = ll.pi.solve_square_root_covariance(GP)
            start = stop
        return Y
        
    if issubclass(type(pi.logL), AdditiveLogLikelihood):
        factors = [(pi.logL, list(range(pi.logL.dim_in)))]
    else:
        factors = pi.logL.factors
    dim_obs = sum( [ ll.y.shape[0] for ll,_ in factors ] )
    dim = pi.logL.dim_in
    gx_ll_list = [] # Precompute all the gradients of the log-likelihoods at x
    for ll, xidxs in factors:
        gx_ll_list.append( ll.T.grad_x(x[:,xidxs])[0,:,:] )
    kwargs = {'gx_ll_list': gx_ll_list, 'factors': factors, 'prior': pi.prior, \
              'dim': dim, 'dim_obs': dim_obs}
    K, S, Vt = randomized_direct_svd(
        action, action_transpose, dim_obs, dim, eps, r, power_n=power_n,
        kwargs=kwargs)
    D = S**2
    sqrt = np.dot(K * (1/np.sqrt(1+D) - 1)[np.newaxis,:], K.T) + \
           np.eye(pi.prior.dim)
    sqrt = pi.prior.square_root_covariance.dot( sqrt )
    return sqrt

def bayes_low_rank_sqrt_approximation_hessact(x, pi, eps, r, power_n):
    def action(dx, x, logL, prior):
        Y = prior.square_root_covariance.dot(dx)
        Y = - logL.action_hess_x(np.tile(x,(dx.shape[1],1)), Y.T)[:,0,:].T
        Y = prior.square_root_covariance.T.dot(Y)
        return Y
    kwargs = {'x': x, 'logL': pi.logL, 'prior': pi.prior}
    D, K = randomized_direct_eig(
        action, pi.dim, eps, r, power_n=power_n, kwargs=kwargs)
    sqrt = np.dot(K * (1/np.sqrt(1+D) - 1)[np.newaxis,:], K.T) + \
           np.eye(pi.prior.dim)
    sqrt = pi.prior.square_root_covariance.dot( sqrt )
    return sqrt
    # K = np.dot(pi.prior.square_root, K)
    # Gpos = pi.prior.sigma - np.dot(K * (D/(1+D))[np.newaxis,:], K.T)
    # return npla.cholesky(Gpos)

def laplace_approximation_withBounds(pi, params=None, tol=1e-5, ders=2, disp=True, bounds = None):
    r""" Compute the Laplace approximation of the distribution :math:`\pi`.

    Args:
      pi (Distribution): distribution :math:`\pi`
      params (dict): parameters for distribution :math:`\pi`
      tol (float): tolerance to be used to solve the maximization problem.
      ders (int): order of derivatives available for the solution of the
        optimization problem. 0 -> derivative free, 1 -> gradient, 2 -> hessian.
      disp (bool): whether to display output from optimizer.

    Returns:
      (:class:`NormalDistribution`) -- Laplace approximation
    """
    nax = np.newaxis
    # Minimize :math:`-\log \pi`
    def objective(x, params):
        return - pi.log_pdf(x[nax,:], params)[0]
    def dx_objective(x, params):
        return - pi.grad_x_log_pdf(x[nax,:], params)[0,:]
    def dx2_objective(x, params):
        return - pi.hess_x_log_pdf(x[nax,:], params)[0,:,:]
    x0 = np.zeros(pi.dim) # Random or zero starting point? Or input argument?
    options = {'maxiter': 10000,
               'disp': disp}
    if ders == 0:
        res = sciopt.minimize(objective, args=params,
                              x0=x0,
                              method='L-BFGS-B',
                              tol=tol,
                              options=options, bounds = bounds)
    elif ders == 1:
        res = sciopt.minimize(objective, args=params,
                              x0=x0,
                              jac=dx_objective,
                              method='L-BFGS-B',
                              tol=tol,
                              options=options, bounds = bounds)
    elif ders == 2:
        res = sciopt.minimize(objective, args=params,
                              x0=x0,
                              jac=dx_objective,
                              hess=dx2_objective,
                              method='TNC',
                              tol=tol,
                              options=options, bounds = bounds)
    else:
        raise ValueError("ders parameter not valid. Chose between 0,1,2.")
    x_map = res['x']
    # Compute the Hessian at the maximizer
    hess_map = - pi.hess_x_log_pdf( x_map[nax,:] )[0,:,:]
    # Define the Gaussian distribution/Laplace approximation
    d_laplace = NormalDistribution(x_map, precision=hess_map)
    return d_laplace
