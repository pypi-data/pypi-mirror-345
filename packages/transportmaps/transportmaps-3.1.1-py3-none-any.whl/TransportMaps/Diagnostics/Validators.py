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
import numpy.linalg as npla
import numpy.random as npr
import scipy.stats as stats
import scipy.optimize as sciopt
from TransportMaps.KL import minimize_kl_divergence

from TransportMaps.Misc import read_and_cast_input
from TransportMaps.External import DARKSPARK_SUPPORT
from TransportMaps import \
    mpi_map, mpi_bcast_dmem, \
    ExpectationReduce, \
    distributed_sampling, \
    no_cost_function
from TransportMaps.ObjectBase import TMO
from TransportMaps.Distributions import \
    PullBackParametricTransportMapDistribution

if DARKSPARK_SUPPORT:
    from DARKSparK.multiDimensionalFunction import MultiDimensionalFunction,Reals64

__all__ = ['KLMinimizationValidator',
           'SampleAverageApproximationKLMinimizationValidator',
           # 'GradientChi2KLMinimizationValidator',
           # 'GradientToleranceRegionKLMinimizationValidator',
           'GradientBootstrapKLMinimizationValidator',
           'DimensionAdaptiveSparseGridKLMinimizationValidator']

class KLMinimizationValidator(TMO):
    def __init__(
            self, eps,
            cost_function=no_cost_function,
            max_cost=np.inf, 
            max_nsamps=np.inf,
            stop_on_fcast=False):
        super(KLMinimizationValidator, self).__init__()
        self.eps = eps
        self.cost_function = cost_function
        self.max_cost = max_cost
        self.max_nsamps = max_nsamps
        self.stop_on_fcast = stop_on_fcast

    def pre_solve(self, base_distribution, target_distribution,transport_map,
                  validation_params):
        r""" Implements a routine to be initialize variables before the solving stage.

        This function should initialize quantities that are needed for a particular validator.
        """
        pass

    def post_solve(self, base_distribution, target_distribution,transport_map,
                   validation_params):
        r""" Implements a routine to be make sure the variables set in presolve are in the correct state post exiting the solving stage.

        Since, in principle, algorithms can be stopped and re-started, this allows variables to be cleaned up when not needed. 
        """
        pass

    def solve_to_tolerance(
            self,
            transport_map,
            base_distribution,
            target_distribution,
            solve_params,
            mpi_pool=None):

        validation_params = {}
        validation_params['ref_params'] = {}
        validation_params['solve_params'] = solve_params
        self.pre_solve(base_distribution, target_distribution,transport_map,
                       validation_params)
        log = {}
        max_nsamps_flag = solve_params.get(
            'x', np.zeros((0))).shape[0] >= self.max_nsamps
        cost = self.cost_function(
            ncalls=getattr(target_distribution, 'ncalls', {}),
            nevals=getattr(target_distribution, 'nevals', {}),
            teval=getattr(target_distribution, 'teval', {}))
        cost_flag = cost > self.max_cost
        fcast_cost = 0.
        fcast_cost_flag = False
        err = np.inf
        target_err = 0.
        prune_params = None
        pull_tar = PullBackParametricTransportMapDistribution(
            transport_map, target_distribution)
        ncalls_x_solve = getattr(target_distribution, 'ncalls', {}).copy()
        lst_ncalls = getattr(target_distribution, 'ncalls', {}).copy()

        it = 1
        while err > target_err and not cost_flag:
            self.logger.info("Starting solve_to_tolerance iteration "+str(it))
            if it > 1:
                if max_nsamps_flag:
                    # The number of samples is already exceeding or at max.
                    # No refinement possible.
                    break
            
            # Compute refinement and forecast cost flag
            nsamps = self.refinement(
                base_distribution, pull_tar,
                validation_params=validation_params)
            self.logger.info("Refinement - nsamps: %d" % nsamps)
            if nsamps >= self.max_nsamps:
                self.logger.warning("Maximum number of samples reached.")
                max_nsamps_flag = True
                # If the maximum number of samples is just met,
                # let it run one more iteration.
                if nsamps > self.max_nsamps:
                    break
            if self.stop_on_fcast:
                fcast_cost = self.cost_function(
                    ncalls=target_distribution.ncalls,
                    nevals=target_distribution.nevals,
                    teval=target_distribution.teval,
                    ncalls_x_solve=ncalls_x_solve, new_nx=nsamps)
                fcast_cost_flag = fcast_cost > self.max_cost
                if fcast_cost_flag: # Stop
                    self.logger.warning("Predicted cost exceeds maximum cost allowed.")
                    break
                solve_params['x0'] = transport_map.coeffs # Warm start

           
            # Solve
            log = minimize_kl_divergence(
                base_distribution, pull_tar,
                mpi_pool=mpi_pool, **solve_params)

            if not log['success']:
                cost = self.cost_function(
                    ncalls=target_distribution.ncalls,
                    nevals=target_distribution.nevals,
                    teval=target_distribution.teval)
                break
            solve_params['x0'] = transport_map.coeffs # Warm start
            validation_params['solve_log'] = log
            err, target_err, prune_params = self.error_estimation(
                base_distribution, pull_tar, validation_params,
                full_output=True, mpi_pool=mpi_pool)
            ncalls_x_solve = {
                key: value - lst_ncalls.get(key,0)
                for key, value in pull_tar.ncalls.items()}
            lst_ncalls = pull_tar.ncalls.copy()
            cost = self.cost_function(
                ncalls=target_distribution.ncalls,
                nevals=target_distribution.nevals,
                teval=target_distribution.teval)
            cost_flag = cost > self.max_cost
            self.print_info(err, target_err, cost, validation_params, prune_params)
            it += 1

        self.post_solve(base_distribution, target_distribution, transport_map,
                        validation_params)
        log['validator_max_nsamps_exceeded'] = max_nsamps_flag
        log['validator_cost'] = cost
        log['validator_cost_exceeded'] = cost_flag
        log['validator_fcast_cost'] = fcast_cost
        log['validator_fcast_cost_exceeded'] = fcast_cost_flag
        log['validator_error'] = err
        log['validator_prune_params'] = prune_params
        log['validator_target_error'] = target_err
        return log

    def print_info(self, err, target_err, cost, validation_params, prune_params):
        solve_params = validation_params['solve_params']
        self.logger.info(
            "nsamps: %d - " % solve_params['qparams'] + \
            "err: %.3e (target: %.3e)" % (err, target_err) + \
            " - cost: %.2e" % cost)

    def stopping_criterion(self, *args, **kwargs):
        r""" Implements the stopping criterion for the particular validator

        This function should return a target error value
        (e.g. the target error taking into account the magnitude
        of the objective and the absolute/relative tolerances).

        In theory
        :fun:`error_estimation<KLMinimizationValidator.error_estimation>`
        could handle everything by itself. This abstract method aims
        to provide more structure to the code.

        See the implementation
        :fun:`SampleAverageApproximationKLMinimizationValidator.stopping_criterion`
        for an example.
        """
        raise NotImplementedError("To be implemented in subclasses if needed")
        
    def error_estimation(self, base_distribution, pull_tar,
                         error_estimation_params, *args, **kwargs):
        raise NotImplementedError("To be implemented in subclasses")

    def refinement(self, base_distribution, pull_tar,
                   qtype, qparams, ref_params, *args, **kwargs):
        r"""
        Returns:
          (:class:`tuple`) -- containing the new ``qparams`` and the
            number of points corresponding to it.
        """
        raise NotImplementedError("To be implemented in subclasses")

class SampleAverageApproximationKLMinimizationValidator(KLMinimizationValidator):
    def __init__(self, eps,
                 eps_abs=1e-13,
                 cost_function=no_cost_function,
                 max_cost=np.inf,
                 max_nsamps=np.inf,
                 stop_on_fcast=False,
                 upper_mult=10,
                 lower_n=2,
                 alpha=0.05,
                 lmb_def=2,
                 lmb_max=10):
        if upper_mult < 1:
            raise AttributeError("The upper_mult argument must be a float >= 1")
        if lower_n < 2:
            raise AttributeError("The lower_n argument must be an integer >= 2")
        self.eps_abs = eps_abs
        self.upper_mult = upper_mult
        self.lower_n = lower_n
        self.alpha = alpha
        self.lmb_def = lmb_def
        self.lmb_max = lmb_max
        super(SampleAverageApproximationKLMinimizationValidator,
              self).__init__(
                  eps, cost_function=cost_function, max_cost=max_cost,
                  max_nsamps=max_nsamps, stop_on_fcast=stop_on_fcast)
        
    def print_info(self, err, target_err, cost, validation_params, prune_params):
        solve_params = validation_params['solve_params']
        ref_params =  validation_params['ref_params']
        self.logger.info(
            "nsamps: %d" % solve_params['qparams'] + \
            " - err: %.3e [L: %.3e, U:%.3e] (target: %.3e)" % (
                err, ref_params['lower_interval'],
                ref_params['upper_interval'], target_err) + \
            " - cost: %.2e" % cost)

    def stopping_criterion(self, err_mag=None):
        if err_mag is not None:
            return err_mag * self.eps + self.eps_abs
        else:
            return 0.
        
    def error_estimation(
            self, base_distribution, pull_tar, validation_params,
            full_output=False, mpi_pool=None):
        ref_params = validation_params['ref_params']
        solve_params = validation_params['solve_params']
        if solve_params['qtype'] != 0:
            raise AttributeError(
                "The Sample Average Approximation validator is defined only for " + \
                "Monte Carlo quadrature rules")
        tm = pull_tar.transport_map
        # Compute upper bound (distributed sampling)
        upper_nsamps = int(np.ceil(self.upper_mult * solve_params['qparams']))
        (x, w) = distributed_sampling(
            base_distribution, 0, upper_nsamps, mpi_pool=mpi_pool)
        v2 = - mpi_map(
            "log_pdf", obj=pull_tar,
            dmem_key_in_list=['x'],
            dmem_arg_in_list=['x'],
            dmem_val_in_list=[x],
            mpi_pool=mpi_pool)
        if solve_params.get('regularization') is not None:
            if solve_params['regularization']['type'] == 'L2':
                v2 += solve_params['regularization']['alpha'] * \
                      npla.norm(tm.coeffs - tm.get_identity_coeffs(), 2)**2.
        upper_mean = np.sum( v2 ) / float(upper_nsamps)
        upper_var = np.sum( (v2 - upper_mean)**2 ) / float(upper_nsamps-1)
        upper_interval = stats.t.ppf(1-self.alpha, upper_nsamps) * \
                         np.sqrt(upper_var/float(upper_nsamps))
        upper_bound = upper_mean + upper_interval
        # Compute lower bound
        res_x = solve_params.pop('x')
        res_w = solve_params.pop('w')
        res_coeffs = pull_tar.coeffs[:]
        lower_nsamps = self.lower_n
        v2 = np.zeros(lower_nsamps)
        coeffs = np.zeros((lower_nsamps, tm.n_coeffs))
        for i in range(lower_nsamps):
            log = minimize_kl_divergence(
                base_distribution, pull_tar,
                mpi_pool=mpi_pool, **solve_params)
            v2[i] = log['fval']
            coeffs[i,:] = tm.coeffs
        lower_mean = np.sum(v2) / float(lower_nsamps)
        lower_var = np.sum((v2 - lower_mean)**2) / float(lower_nsamps-1)
        lower_interval = stats.t.ppf(1-self.alpha, lower_nsamps) * \
                         np.sqrt(lower_var/float(lower_nsamps))
        lower_bound = lower_mean - lower_interval
        pull_tar.coeffs = res_coeffs # Restore coefficients
        solve_params['x'] = res_x
        solve_params['w'] = res_w
        # Error as the gap between the bounds
        err = max(0., upper_bound - lower_bound)
        if full_output:
            # Refinement parameters
            ref_params['upper_nsamps'] = upper_nsamps
            ref_params['upper_mean'] = upper_mean
            ref_params['upper_var'] = upper_var
            ref_params['upper_interval'] = upper_interval
            ref_params['lower_nsamps'] = lower_nsamps
            ref_params['lower_mean'] = lower_mean
            ref_params['lower_var'] = lower_var
            ref_params['lower_interval'] = lower_interval
            # Pruning parameter as 1/stand.dev. of coefficients scaled to (0,1)
            std_coeffs = np.std(coeffs, axis=0)
            prune_params = (1/std_coeffs)/max(1/std_coeffs)
            target_err = self.stopping_criterion(upper_mean)
            return err, target_err, prune_params
        else:
            return err

    def refinement(self, base_distribution, pull_tar, validation_params):
        ref_params = validation_params['ref_params']
        solve_params = validation_params['solve_params']
        qparams = solve_params['qparams']
        if solve_params['qtype'] != 0:
            raise AttributeError(
                "The Sample Average Approximation validator is defined only for " + \
                "Monte Carlo quadrature rules")
        if 'upper_mean' not in ref_params:
            # If this is the first iteration
            q = solve_params['qparams']
        else:
            # If one error estimation has already been done
            X = self.stopping_criterion(ref_params['upper_mean']) - \
                (ref_params['upper_mean'] - ref_params['lower_mean']) - \
                stats.t.ppf(1-self.alpha, ref_params['upper_nsamps']) * \
                np.sqrt(ref_params['upper_var']/ref_params['upper_nsamps'])
            if X > 0:
                def f(m, alpha, X, lv):
                    return stats.t.ppf(1-alpha, m) / m * np.sqrt(lv) - X
                if np.sign(
                        f(ref_params['lower_nsamps'], self.alpha,
                          X, ref_params['lower_var']) ) * \
                    np.sign(
                        f(self.lmb_max, self.alpha,
                          X, ref_params['lower_var']) ) == -1:
                    m = sciopt.bisect(
                        f, ref_params['lower_nsamps'], self.lmb_max,
                        args=(self.alpha, X, ref_params['lower_var']))
                    q = int(np.ceil( m/ref_params['lower_nsamps'] * qparams ))
                else:
                    q = int( np.ceil(self.lmb_def * qparams) )
            else:
                q = int( np.ceil(self.lmb_def * qparams) )
            q = min(q, self.max_nsamps)
            solve_params['qparams'] = q
        x, w = base_distribution.quadrature(0, q)
        solve_params['x'] = x
        solve_params['w'] = w
        return q

# class GradientChi2KLMinimizationValidator(KLMinimizationValidator):
#     def __init__(self, eps,
#                  cost_function=no_cost_function, max_cost=np.inf,
#                  max_nsamps=np.inf, stop_on_fcast=False,
#                  n_grad_samps=10, n_bootstrap=None,
#                  alpha=0.95, lmb_def=2, lmb_max=10,
#                  fungrad=False):
#         self.n_grad_samps = n_grad_samps
#         self.n_bootstrap = n_bootstrap
#         self.alpha = alpha
#         self.lmb_def = lmb_def
#         self.lmb_max = lmb_max
#         self.fungrad = fungrad
#         super(GradientChi2KLMinimizationValidator,
#               self).__init__(eps, cost_function, max_cost, max_nsamps, stop_on_fcast)
        
#     def error_estimation(
#             self, base_distribution, pull_tar, solve_params, full_output=False):
#         if solve_params['qtype'] != 0:
#             raise AttributeError(
#                 "The Gradient Stability validator is defined only for " + \
#                 "Monte Carlo quadrature rules")
#         tm = pull_tar.transport_map
#         # Compute mean and variance of the gradient
#         nsamps = int(np.ceil( self.n_grad_samps * solve_params['qparams'] ))
#         x, w = base_distribution.quadrature(
#             qtype=solve_params['qtype'], qparams=nsamps)
#         scatter_tuple = (['x'], [x])
#         if not self.fungrad:
#             grad = - mpi_map(
#                 "grad_a_log_pdf", obj=pull_tar, scatter_tuple=scatter_tuple,
#                 mpi_pool=solve_params.get('mpi_pool'))
#         else:
#             _, grad = - mpi_map(
#                 "tuple_grad_a_log_pdf", obj=pull_tar, scatter_tuple=scatter_tuple,
#                 mpi_pool=solve_params.get('mpi_pool'))
#         if solve_params.get('regularization') is not None:
#             if solve_params['regularization']['type'] == 'L2':
#                 grad += solve_params['regularization']['alpha'] * 2. * \
#                         (tm.coeffs - tm.get_identity_coeffs())
#         # Use randomized resampling to avoid being forced to use n_grad_samps > tm.n_coeffs
#         if self.n_bootstrap is None:
#             avg_grads = np.mean( grad.reshape((
#                 solve_params['qparams'], self.n_grad_samps, tm.n_coeffs)), axis=0 )
#         else:
#             avg_grads = np.zeros((self.n_bootstrap, tm.n_coeffs))
#             for i in range(self.n_bootstrap):
#                 idxs = npr.choice(nsamps, size=solve_params['qparams'], replace=True)
#                 avg_grads[i,:] = np.mean( grad[idxs,:], axis=0 )
#         mean = np.mean(avg_grads, axis=0)
#         cntr_avg_grads = avg_grads - mean
#         cov = np.dot(cntr_avg_grads.T, cntr_avg_grads) / float(solve_params['qparams']-1)
#         L = scila.cholesky(cov, lower=True)
#         cstar = stats.chi2(tm.n_coeffs).ppf(self.alpha)
#         # Solve maximization problem
#         A = - cstar/solve_params['qparams'] * np.dot(L.T,L)
#         b = - 2. * np.sqrt(cstar/solve_params['qparams']) * np.dot(mean, L)
#         c = - np.dot(mean, mean)
#         def f(x, A, b, c):
#             return np.dot(x,np.dot(A,x)) + np.dot(b, x) + c
#         def jac(x, A, b, c):
#             return 2. * np.dot(A,x) + b
#         def c1(x):
#             return 1 - np.dot(x,x)
#         def c1jac(x):
#             return - 2 * x
#         cons = ({'type': 'ineq', 'fun': c1, 'jac': c1jac})
#         res = sciopt.minimize(
#             f, np.zeros(tm.n_coeffs), method='SLSQP', jac=jac, 
#             args=(A, b, c), constraints=cons, tol=1e-12)
#         xstar = res['x']
#         # Compute err as sqrt(f(x))
#         err = np.sqrt(- f(xstar, A, b, c))
#         if full_output:
#             # Refinement parameters
#             ref_params = {
#                 'mean':mean,
#                 'L': L,
#                 'cstar': cstar,
#                 'xstar': xstar
#             }
#             # Prune parameter as 1/variance of directional gradient
#             var_coeffs = np.diag(cov)
#             prune_params = (1/var_coeffs)/max(1/var_coeffs)
#             return err, ref_params, prune_params
#         else:
#             return err

#     def refinement(self, base_distribution, pull_tar,
#                    qtype, qparams, ref_params):
#         if qtype != 0:
#             raise AttributeError(
#                 "The Gradient Stability validator is defined only for " + \
#                 "Monte Carlo quadrature rules")
#         # Load parameters
#         mu = ref_params['mean']
#         L = ref_params['L']
#         cstar = ref_params['cstar']
#         xstar = ref_params['xstar']
#         # Compute refinement
#         a = np.dot(mu,mu) - self.eps**2
#         if a <= 0:
#             Lx = np.dot(L, xstar)
#             b = 2. * np.sqrt(cstar) * np.dot(mu, np.dot(L, xstar))
#             c = cstar * np.dot(Lx.T, Lx)
#             z = (-b + np.sqrt(b**2-4*a*c))/ 2. / a
#             q = min( int(np.ceil(z**2)),
#                      self.lmb_max * qparams )
#         else:
#             q = int( np.ceil(self.lmb_def * qparams) )
#         return q, q
        
# class GradientToleranceRegionKLMinimizationValidator(KLMinimizationValidator):
#     def __init__(self, eps,
#                  cost_function=no_cost_function, max_cost=np.inf,
#                  max_nsamps=np.inf, stop_on_fcast=False,
#                  n_grad_samps=10, n_gap_resampling=10,
#                  beta=0.95, gamma=0.05, lmb_def=2, lmb_max=10,
#                  fungrad=False):
#         self.n_grad_samps = n_grad_samps
#         self.n_gap_resampling = n_gap_resampling
#         self.beta = beta
#         self.gamma = gamma
#         self.lmb_def = lmb_def
#         self.lmb_max = lmb_max
#         self.fungrad = fungrad
#         super(GradientStabilityKLMinimizationValidator,
#               self).__init__(eps, cost_function, max_cost, max_nsamps, stop_on_fcast)

#     def _cv(self, N, n, b, g):
#         n = self.n_grad_samps
#         b = self.beta
#         g = self.gamma
#         return (n-1) * stats.chi2(N, loc=float(N)/float(n)).ppf(b) / \
#             stats.chi2(n-N).ppf(1-g)
        
#     def error_estimation(
#             self, base_distribution, pull_tar, solve_params, full_output=False):
#         if solve_params['qtype'] != 0:
#             raise AttributeError(
#                 "The Gradient Stability validator is defined only for " + \
#                 "Monte Carlo quadrature rules")
#         tm = pull_tar.transport_map
#         # Compute mean and variance of the gradient
#         nsamps = int(np.ceil( self.n_grad_samps * solve_params['qparams'] ))
#         x, w = base_distribution.quadrature(
#             qtype=solve_params['qtype'], qparams=nsamps)
#         scatter_tuple = (['x'], [x])
#         if not self.fungrad:
#             grad = - mpi_map(
#                 "grad_a_log_pdf", obj=pull_tar, scatter_tuple=scatter_tuple,
#                 mpi_pool=solve_params.get('mpi_pool'))
#         else:
#             _, grad = - mpi_map(
#                 "tuple_grad_a_log_pdf", obj=pull_tar, scatter_tuple=scatter_tuple,
#                 mpi_pool=solve_params.get('mpi_pool'))
#         if solve_params.get('regularization') is not None:
#             if solve_params['regularization']['type'] == 'L2':
#                 grad += solve_params['regularization']['alpha'] * 2. * \
#                         (tm.coeffs - tm.get_identity_coeffs())
#         # Use randomized resampling to avoid being forced to use n_grad_samps > tm.n_coeffs
#         n = tm.n_coeffs + self.n_gap_resampling
#         avg_grads = np.zeros((n, tm.n_coeffs))
#         for i in range(n):
#             idxs = npr.choice(nsamps, size=solve_params['qparams'], replace=False)
#             avg_grads[i,:] = np.mean( grad[idxs,:], axis=0 )
#         mean = np.mean(avg_grads, axis=0)
#         cntr_avg_grads = avg_grads - mean
#         cov = np.dot(cntr_avg_grads.T, cntr_avg_grads) / float(n-1)
#         L = scila.cholesky(cov, lower=True)
#         cstar = self._cv(tm.n_coeffs, n, self.beta, self.gamma)
#         # Solve maximization problem
#         A = - cstar/solve_params['qparams'] * np.dot(L.T,L)
#         b = - 2. * np.sqrt(cstar/solve_params['qparams']) * np.dot(mean, L)
#         c = - np.dot(mean, mean)
#         def f(x, A, b, c):
#             return np.dot(x,np.dot(A,x)) + np.dot(b, x) + c
#         def jac(x, A, b, c):
#             return 2. * np.dot(A,x) + b
#         def c1(x):
#             return 1 - np.dot(x,x)
#         def c1jac(x):
#             return - 2 * x
#         cons = ({'type': 'ineq', 'fun': c1, 'jac': c1jac})
#         res = sciopt.minimize(
#             f, np.zeros(tm.n_coeffs), method='SLSQP', jac=jac, 
#             args=(A, b, c), constraints=cons, tol=1e-12)
#         xstar = res['x']
#         # Compute err as sqrt(f(x))
#         err = np.sqrt(f(xstar, A, b, c))
#         if full_output:
#             # Refinement parameters
#             ref_params = {
#                 'mean':mean,
#                 'L': L,
#                 'cstar': cstar,
#                 'xstar': xstar
#             }
#             # Compute prune parameters as 1/ variance of gradient
#             var_coeffs = np.diag(cov)
#             prune_params = (1/var_coeffs)/max(1/var_coeffs)
#             return err, ref_params, prune_params
#         else:
#             return err

#     def refinement(self, base_distribution, pull_tar,
#                    qtype, qparams, ref_params):
#         if qtype != 0:
#             raise AttributeError(
#                 "The Gradient Stability validator is defined only for " + \
#                 "Monte Carlo quadrature rules")
#         # Load parameters
#         mu = ref_params['mean']
#         L = ref_params['L']
#         cstar = ref_params['cstar']
#         xstar = ref_params['xstar']
#         # Compute refinement
#         a = np.dot(mu,mu) - self.eps**2
#         if a <= 0:
#             Lx = np.dot(L, xstar)
#             b = 2. * np.sqrt(cstar) * np.dot(mu, np.dot(L, xstar))
#             c = cstar * np.dot(Lx.T, Lx)
#             z = (-b + np.sqrt(b**2-4*a*c))/ 2. / a
#             q = int(np.ceil(z**2))
#         else:
#             q = int( np.ceil(self.lmb_def * qparams) )
#         return q, q

class GradientBootstrapKLMinimizationValidator(KLMinimizationValidator):
    r""" Bootstrap the gradient to check whether cost function is flat independently of the sample.

    For the current solution :math:`{\bf a}`,
    minimizing the cost :math:`\mathcal{Q}_n[\mathcal{J}[{\bf a}]({\bf x})]`,
    for the sample :math:`{\bf x}^\star`, check that

    .. math::

       \mathbb{P}\left[
       \left\Vert\mathcal{Q}_n[\nabla_{\bf a}\mathcal{J}[{\bf a}]({\bf x})]\right\Vert_2 \leq
       \delta \left\Vert\mathcal{Q}_n[\nabla_{\bf a}\mathcal{J}[{\bf a}]({\bf x}^\star)]\right\Vert_2 + \varepsilon
       \right] \geq \alpha
    
    Args:
      delta (float): multiplicative factor :math:`\delta`
    """
    def __init__(self, eps, delta=5,
                 cost_function=no_cost_function, max_cost=np.inf,
                 max_nsamps=np.inf, stop_on_fcast=False,
                 n_grad_samps=1, n_bootstrap=2000,
                 alpha=0.95, lmb_min=2, lmb_max=10):
        self.delta = delta
        self.n_grad_samps = n_grad_samps
        self.n_bootstrap = n_bootstrap
        self.alpha = alpha
        self.lmb_min = lmb_min
        self.lmb_max = lmb_max
        super(GradientBootstrapKLMinimizationValidator,
              self).__init__(eps, cost_function, max_cost, max_nsamps, stop_on_fcast)
        
    def update_tolerances(self):
        print("The target error is computed as: " + \
              "delta * ||\nabla_a J[a]||_2 + eps"
        )
        val, flag = read_and_cast_input("absolute tolerance (eps)", float, self.eps)
        if not flag:
            return flag
        self.eps = val
        val, flag = read_and_cast_input("gradient tolerance (delta)", float, self.delta)
        if not flag:
            return flag
        self.delta = val
        return flag
        
    def pre_solve(self, base_distribution, target_distribution, transport_map,
                  validation_params):
        validation_params['ref_params']['is_first_iter'] = True

    def stopping_criterion(self, obj=None, grad=None, validation_params=None):
        if validation_params['solve_params'].get('ders') == 1:
            # Use the target tolerance value. Since ders is 1, then 
            # the tolerance is referred to the l2 value of the gradient.
            return validation_params['solve_params'].get('tol') * self.delta + self.eps
        elif obj is not None and grad is not None:
            return npla.norm(grad, ord=2) * self.delta + self.eps
        else:
            return 0.
        
    def error_estimation(
            self, base_distribution, pull_tar, validation_params,
            full_output=False, mpi_pool=None):
        ref_params = validation_params['ref_params']
        solve_params = validation_params['solve_params']
        if solve_params['qtype'] != 0:
            raise AttributeError(
                "The Bootstrap Gradient validator is defined only for " + \
                "Monte Carlo quadrature rules.")
        tm = pull_tar.transport_map
        # Prepare the batch
        nsamps = int(np.ceil( self.n_grad_samps * solve_params['qparams'] ))
        x, w = base_distribution.quadrature(
            qtype=solve_params['qtype'], qparams=nsamps)
        grad = np.zeros((x.shape[0], tm.n_coeffs))
        # Prepare batching sizes
        bsize = solve_params.get('batch_size')
        if bsize is not None:
            bsize = bsize[1] if bsize[1] is not None else x.shape[0]
        else:
            bsize = x.shape[0]
        # Distribute the object
        mpi_bcast_dmem(d=pull_tar, mpi_pool=mpi_pool)    
        for n in range(0,x.shape[0],bsize):
            nend = min(x.shape[0], n+bsize)
            scatter_tuple = (['x'], [x[n:nend,:]])
            if not solve_params.get('fungrad', False):
                grad[n:nend,:] = mpi_map(
                    "grad_a_log_pdf",
                    scatter_tuple=scatter_tuple,
                    obj='d',
                    obj_val=pull_tar,
                    mpi_pool=mpi_pool)
            else:
                _, grad[n:nend,:] = mpi_map(
                    "tuple_grad_a_log_pdf",
                    scatter_tuple=scatter_tuple,
                    obj='d',
                    obj_val=pull_tar,
                    mpi_pool=mpi_pool)
        grad = - grad
        if solve_params.get('regularization') is not None:
            if solve_params['regularization']['type'] == 'L2':
                grad += solve_params['regularization']['alpha'] * 2. * \
                        (tm.coeffs - tm.get_identity_coeffs())

        # Update counters
        if mpi_pool is not None:
            d_child_list = mpi_pool.get_dmem('d')
            pull_tar.update_ncalls_tree( d_child_list[0][0] )
            for (d_child,) in d_child_list:
                pull_tar.update_nevals_tree(d_child)
                pull_tar.update_teval_tree(d_child)
        # Clear mpi_pool
        if mpi_pool is not None:
            mpi_pool.clear_dmem()
                
        # Compute the n_bootstrap norms of the gradient
        nrm_grad = np.zeros(self.n_bootstrap)
        avg_grads = np.zeros((self.n_bootstrap, tm.n_coeffs))
        for i in range(self.n_bootstrap):
            idxs = npr.choice(nsamps, size=nsamps, replace=True)
            avg_grads[i,:] = np.mean(grad[idxs,:], axis=0)
            nrm_grad[i] = npla.norm(avg_grads[i,:], ord=2)
        # Compute the 100*alpha% empirical percentile for n_bootstrap re-samples
        prc_idx = int(np.floor( self.alpha * self.n_bootstrap ))
        prc = nrm_grad[prc_idx]
        # Error is the 100*(1-alpha)% empirical percentile
        err = prc
        ref_params['error'] = err
        if full_output:
            # Prune parameters
            mean = np.mean(avg_grads, axis=0)
            cntr_avg_grads = avg_grads - mean
            var_coeffs = self.n_bootstrap / (self.n_bootstrap - 1) \
                         * np.mean(cntr_avg_grads**2, axis=0)
            prune_params = (1/var_coeffs)/max(1/var_coeffs)
            # Compute the target error
            solve_log = validation_params['solve_log']
            target_err = self.stopping_criterion(
                obj = solve_log['fval'],
                grad = solve_log['jac'],
                validation_params = validation_params
            )
            ref_params['target_error'] = target_err
            return err, target_err, prune_params
        else:
            return err

    def refinement(self, base_distribution, pull_tar, validation_params):
        ref_params = validation_params['ref_params']
        solve_params = validation_params['solve_params']
        if ref_params['is_first_iter']:
            ref_params['is_first_iter'] = False
            try:
                x = solve_params['x']
                w = solve_params['w']
            except KeyError:
                x, w = base_distribution.quadrature(0, solve_params['qparams'])
        else:
            err = ref_params['error']
            target_err = ref_params['target_error']
            missing_digits = np.log10( err / target_err )
            q = 10**(2 * missing_digits)
            nsamps = solve_params['qparams'] * max(
                self.lmb_min, min(self.lmb_max, q ) )
            solve_params['qparams'] = int(np.ceil(nsamps))
            x, w = base_distribution.quadrature(0, solve_params['qparams'])
        solve_params['x'] = x
        solve_params['w'] = w
        return solve_params['qparams']
        
class DimensionAdaptiveSparseGridKLMinimizationValidator(KLMinimizationValidator):
    def __init__(self, *args, **kwargs):
        if not DARKSPARK_SUPPORT:
            raise RuntimeError("Sparse Grid is not supported (install DARKSparK).")
        super(DimensionAdaptiveSparseGridKLMinimizationValidator, self).__init__(*args, **kwargs)
    
    def grad_l2_reg(self,alpha,pull_tar):
        return alpha* 2.* (pull_tar.transport_map.coeffs - pull_tar.transport_map.get_identity_coeffs())

    def grad_a_log_pdf_call(self, pull_tar,solve_params): 
        return  lambda x: -mpi_map("grad_a_log_pdf",
                            obj= pull_tar, 
                            dmem_key_in_list=['x'],
                            dmem_arg_in_list=['x'],
                            dmem_val_in_list=[x],
                            mpi_pool=solve_params.get('mpi_pool')).T

    def pre_solve(self, base_distribution, target_distribution,transport_map,
                  validation_params):
        solve_params = validation_params['solve_params']
        ref_params = validation_params['ref_params']
        solve_params['tol'] = self.eps
        ref_params['abs_tol'] = solve_params['tol'] / 10.#2.
        ref_params['solve_params'] = solve_params

    def post_solve(self, base_distribution, target_distribution,transport_map,
                   validation_params):
        solve_params = validation_params['solve_params']
        ref_params = validation_params['ref_params']
        solve_params['x'] = ref_params['x_err_est'] 
        solve_params['w'] = ref_params['w_err_est']
        del ref_params['x_err_est']
        del ref_params['w_err_est']

    def print_info(self, err, target_err, cost, validation_params, prune_params):
        solve_params = validation_params['solve_params']
        ref_params = validation_params['ref_params']
        self.logger.info(
            "Dimension Adaptive Sparse Grid num pts: %d - " % \
            ref_params.get('x_err_est').shape[0] + \
            "err: %.3e (target grad inf-norm: %.3e)" % (err, target_err) + \
            " - cost: %.2e" % cost)

    def stopping_criterion(
            self, solve_params):
        return solve_params['tol']
        
    def error_estimation(self, base_distribution, pull_tar,
                         validation_params, full_output=False):

        self.logger.info("Starting Error Estimation")

        ref_params          = validation_params['ref_params']
        solve_params        = validation_params['solve_params']
        qparams             = {'abs_tol': ref_params['abs_tol']}
        x, w = base_distribution.quadrature(
            qtype=4, qparams=qparams,
            f=MultiDimensionalFunction(
                self.grad_a_log_pdf_call(pull_tar,solve_params),
                Reals64(pull_tar.dim),
                Reals64(pull_tar.n_coeffs))) 

        #the error is inf norm of the (vector valued) integral of grad -log pullback of target + an optional l2 regularization term
        error_term = qparams['adapter'].vector_valued_integrals[-1]
        if solve_params.get('regularization') is not None:
            if solve_params['regularization']['type'] == 'L2':
                error_term += self.grad_l2_reg(solve_params['regularization']['alpha'],pull_tar)
        err = np.linalg.norm( error_term, np.inf)
        
        target_err = self.stopping_criterion(solve_params)
        if not err < target_err:
            #halve the abs_tol each time, but no need to refine past 1e-2 lower precision than the solve tol..
            ref_params['abs_tol'] /= 2.0
            ref_params['abs_tol'] = np.fmax(ref_params['abs_tol'],solve_params['tol'] / 100.0)
            del solve_params['x']
            del solve_params['w']

        #want new_quadrature_grad_norm to be small, below the optimization tolerance..
        ref_params['x_err_est'] = x
        ref_params['w_err_est'] = w

        #Future: prune params based on bias^2 instead of variance (sparse grid variance)??
        self.logger.info("Finished Error Estimation")

        return err, target_err, None #no prune params for now....

    def refinement(self, base_distribution, pull_tar, validation_params): 
        r"""
        Returns:
          (:class:`tuple`) -- containing the new ``qparams`` and the
            number of points corresponding to it.
        """
        self.logger.info("Starting Refinement")
        solve_params = validation_params['solve_params']
        ref_params = validation_params['ref_params']
        if 'x' not in solve_params:
            # this is usually the case, except for at the start of a new "validation stage"
            # where x, w were set to x_err_est and w_err_west in post_solve previously.
            # in this case, we reuse x (no need to do new quadrature before starting optimization)
            if 'x_err_est' in ref_params:
                #use the quadrature from error_estimation for next optimization
                self.logger.info("Reusing quadrature points from error estimation")
                solve_params['x'] = ref_params['x_err_est'] 
                solve_params['w'] = ref_params['w_err_est']
                del ref_params['x_err_est']
                del ref_params['w_err_est']
            else: 
                # only reaches here first iteration of first optimzation -
                # default level 1 grid
                x, w = base_distribution.quadrature(qtype=4, qparams=dict())
                solve_params['x'] = x
                solve_params['w'] = w
        else:
            self.logger.info("Reusing quadrature points from previous optimization")

        self.logger.info("Finished Refinement")
            
        # #plot stuff to take a look at the quadrature
        # # integrals = []
        # # for i in range(1,x.shape[0],round(x.shape[0]/100.)):
        # #     x_mc,w_mc = base_distribution.quadrature(qtype=0, qparams=i)
        # #     scatter_tuple = (['x'], [x_mc])
        # #     reduce_tuple = (['w'], [w_mc])
        # #     reduce_obj = ExpectationReduce()

        # #     integrals.append(mpi_map("grad_a_log_pdf", scatter_tuple=scatter_tuple,
        # #                     obj=pull_tar, reduce_obj=reduce_obj,
        # #                     reduce_tuple=reduce_tuple,
        # #                     mpi_pool=solve_params.get('mpi_pool'))) #grad_a_ [0]
        # import matplotlib
        # matplotlib.use('Qt5Agg')
        # import matplotlib.pyplot as plt
        # # plt.plot(np.arange(1,x.shape[0],round(x.shape[0]/100.)),
        # #          integrals,label="MC, by # pts",c='orange')
        # plt.plot(adapter.num_grid_pts_history,
        #          adapter.vector_valued_integrals,label="SG, by # pts",c='blue')
        # plt.title("Refinement: Vector integral, E_rho[-grad log T^* pi]")
        # plt.xlabel("# samples")
        # plt.ylabel("integral")
        # plt.legend()
        # plt.show()
        
        return solve_params['x'].shape[0]

   
