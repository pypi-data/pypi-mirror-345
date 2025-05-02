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

import copy
from typing import List

import pickle
import numpy as np

import semilattices as SL

from .RegressionAdaptivity import L2RegressionBuilder

from ...Misc import \
    cmdinput, \
    read_and_cast_input, \
    argsort, \
    state_loader
from ...External import PLOT_SUPPORT
from ...Builders import \
    KullbackLeiblerBuilder
from ...Distributions import \
    PullBackTransportMapDistribution, Distribution
from ...KL import \
    grad_t_kl_divergence
from ...LaplaceApproximationRoutines import laplace_approximation
from ...MPI import mpi_map, mpi_bcast_dmem, mpi_scatter_dmem, mpi_map_alloc_dmem
from ...Maps import \
    assemble_LinearSpanTriangularMap, ParametricTransportMap
from ...Diagnostics.Routines import variance_approx_kl
from ...Maps import \
    AffineTransportMap, \
    AffineTriangularMap
from ...Maps.Functionals import \
    LinearSpanTensorizedParametricFunctional

__all__ = [
    'SequentialKullbackLeiblerBuilder',
    'ToleranceSequentialKullbackLeiblerBuilder',
    'FirstVariationKullbackLeiblerBuilder'
]

nax = np.newaxis

class SequentialKullbackLeiblerBuilder(KullbackLeiblerBuilder):
    r""" Solve over a list of maps, using the former to warm start the next one

    Given distribution :math:`\nu_\rho` and :math:`\nu_\pi`,
    and the list of parametric transport maps
    :math:`[T_1[{\bf a}_1,\ldots,T_n[{\bf a}_n]`,
    provides the functionalities to solve the problems

    .. math::

       \arg\min_{{\bf a}_i}\mathcal{D}_{\rm KL}\left(
       T_i[{\bf a}_i]_\sharp\rho \Vert \pi\right)

    up to a chosen tolerance, where the numerical solution for map
    :math:`T_{i+1}` is started at :math:`T_i`

    """
    def __init__(
            self,
            validator=None,
            regression_params_list=None,
            callback=None,
            callback_kwargs={},
            verbosity=0):
        r"""
        Args:
          validator (:class:`Validator<TransportMaps.Diagnostic.Validator>`):
            validator to be used to check stability of the solution
          regression_params_list (:class:`list` of :class:`dict`):
            list of dictionaries of parameters for the regression between :math:`T_i` and
            :math:`T_{i+1}`
          verbosity (int): level of verbosity of the builder
        """
        self.solve_counter = 0
        self.regression_params_list = regression_params_list
        super(SequentialKullbackLeiblerBuilder,
              self).__init__(
                  validator,
                  callback=callback,
                  callback_kwargs=callback_kwargs,
                  verbosity=verbosity )

    @state_loader(
        keys = [
            'transport_map',
            'base_distribution',
            'target_distribution',
            'solve_params' ]
    )
    def solve(
            self,
            transport_map: List[ParametricTransportMap] = None,
            base_distribution: Distribution = None,
            target_distribution: Distribution = None,
            solve_params: List[dict] = None,
            state=None,
            mpi_pool=None
    ):
        r"""    
        Args
          transport_map (:class:`list` of :class:`TransportMap<TransportMaps.Maps.TransportMap>`):
            transport maps :math:`T`
          base_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            distribution :math:`\nu_\rho`
          target_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            distribution :math:`\nu_\pi`
          solve_params (:class:`list` of :class:`dict`):
            list of dictionaries of parameters for solution
          state (:class:`TransportMaps.DataStorageObject`): 
            if provided, it must contain all the information needed for reloading,
            or a handle to an empty storage object which can be externally stored.
            If ``state`` contains the keys corresponding to arguments to this function, 
            they will be used instead of the input themselves.
      
        Returns:
          (:class:`TransportMaps.Maps.TransportMap`) -- the transport map fitted.
        """

        # Internal states
        state.solve_counter = getattr(state, 'solve_counter', 0)
        
        if len(state.transport_map_list) != len(state.solve_params_list):
            raise ValueError(
                "Unconsistent number of transport maps."
            )
        if state.solve_counter == 0:
            transport_map = state.transport_map_list[0]
            solve_params = state.solve_params_list[0]
            tm, log = super(SequentialKullbackLeiblerBuilder, self).solve(
                transport_map,
                state.base_distribution,
                state.target_distribution,
                solve_params,
                mpi_pool=mpi_pool
            )
            if not log['success']:
                tm.coeffs = x0
                return tm, log
            state.solve_counter += 1
        tm_old = state.transport_map_list[state.solve_counter-1]
        for transport_map, solve_params in zip(
                state.transport_map_list[state.solve_counter:],
                state.solve_params_list[state.solve_counter:]):
            # Here we are assuming nested basis
            for c1, c2 in zip(tm_old.approx_list, transport_map.approx_list):
                # Constant part
                for i1, midx1 in enumerate(c1.c.multi_idxs):
                    for i2, midx2 in enumerate(c2.c.multi_idxs):
                        if midx1 == midx2:
                            break
                    c2.c.coeffs[i2] = c1.c.coeffs[i1]
                # Integrated part
                for i1, midx1 in enumerate(c1.h.multi_idxs):
                    for i2, midx2 in enumerate(c2.h.multi_idxs):
                        if midx1 == midx2:
                            break
                    c2.h.coeffs[i2] = c1.h.coeffs[i1]
            # solve for the new map using regressed starting point
            solve_params['x0'] = transport_map.coeffs
            tm, log = super(SequentialKullbackLeiblerBuilder, self).solve(
                transport_map,
                base_distribution,
                target_distribution,
                solve_params,
                mpi_pool=mpi_pool
            )
            if not log['success']:
                return tm_old, log
            tm_old = tm
            state.solve_counter += 1
        return tm, log


class ToleranceSequentialKullbackLeiblerBuilder(KullbackLeiblerBuilder):
    r""" Solve over a list of maps, using the former to warm start the next one, until a target tolerance is met

    Given distribution :math:`\nu_\rho` and :math:`\nu_\pi`,
    and the list of parametric transport maps
    :math:`[T_1[{\bf a}_1,\ldots,T_n[{\bf a}_n]`,
    provides the functionalities to solve the problems

    .. math::

       \arg\min_{{\bf a}_i}\mathcal{D}_{\rm KL}\left(
       T_i[{\bf a}_i]_\sharp\rho \Vert \pi\right)

    up to a chosen tolerance, where the numerical solution for map
    :math:`T_{i+1}` is started at :math:`T_i`

    """
    def __init__(
            self,
            validator=None,
            tol=1e-2,
            laplace_pull=False, 
            callback=None,
            callback_kwargs={},
            verbosity=0):
        r"""
        Args:
          validator (:class:`Validator<TransportMaps.Diagnostic.Validator>`):
            validator to be used to check stability of the solution
          tol (float): target variance diagnostic tolerance
          callback (function): function taking a map and optional additional arguments
            which is called whenever it is deemed necessary by the chosen algorithm
            (e.g. for storing purposes)
          callback_kwargs (dict): additional arguments to be provided to the function
            ``callback``.
          verbosity (int): level of verbosity of the builder
        """
        self.solve_counter = 0
        self.tol = tol
        self.laplace_pull = laplace_pull
        super(ToleranceSequentialKullbackLeiblerBuilder,
              self).__init__(
                  validator,
                  callback=callback,
                  callback_kwargs=callback_kwargs,
                  verbosity=verbosity)

    @state_loader(
        keys = [
            'transport_map_list',
            'base_distribution',
            'target_distribution',
            'solve_params_list',
            'var_diag_params'
        ]
    )
    def solve(
            self,
            transport_map: List[ParametricTransportMap],
            base_distribution: Distribution,
            target_distribution: Distribution,
            solve_params: List[dict],
            var_diag_params: dict,
            state=None,
            mpi_pool=None,
    ):
        r"""    
        Args
          transport_map (:class:`list` of :class:`TransportMap<TransportMaps.Maps.TransportMap>`):
            transport maps :math:`T`
          base_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            distribution :math:`\nu_\rho`
          target_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            distribution :math:`\nu_\pi`
          solve_params (:class:`list` of :class:`dict`):
            list of dictionaries of parameters for solution
          var_diag_params (dict): parameters to be used in the variance diagnostic approximation
          state (:class:`TransportMaps.DataStorageObject`): 
            if provided, it must contain all the information needed for reloading,
            or a handle to an empty storage object which can be externally stored.
            If ``state`` contains the keys corresponding to arguments to this function, 
            they will be used instead of the input themselves.
      
        Returns:
          (:class:`TransportMaps.Maps.TransportMap`) -- the transport map fitted.
        """

        # Internal states
        state.solve_counter = getattr(state, 'solve_counter', 0)

        transport_map_list = transport_map
        solve_params_list = solve_params
        
        if len(state.transport_map_list) != len(state.solve_params_list):
            raise ValueError(
                "Unconsistent number of transport maps."
            )
        if state.solve_counter == 0:
            if state.var_diag_params is None:
                state.var_diag_params = {
                    'qtype': solve_params_list[-1]['qtype'],
                    'qparams': solve_params_list[-1]['qparams']}

            transport_map = state.transport_map_list[0]
            solve_params = state.solve_params_list[0]
            
            if self.laplace_pull:
                # First find Laplace point and center to it
                lap = laplace_approximation(state.target_distribution)
                lap_map = AffineTransportMap.build_from_Gaussian(lap)

                # Set initial conditions to Laplace approximation
                transport_map.regression(
                    lap_map, d=state.base_distribution,
                    qtype=3, qparams=[3]*state.base_distribution.dim,
                    regularization={'alpha': 1e-4, 'type': 'L2'})

                solve_params['x0'] = transport_map.coeffs

            tm, log = super(ToleranceSequentialKullbackLeiblerBuilder, self).solve(
                transport_map,
                state.base_distribution,
                state.target_distribution,
                solve_params,
                mpi_pool=mpi_pool
            )
            if not log['success']:
                tm.coeffs = x0
                return tm, log
            pull_tar = PullBackTransportMapDistribution(
                tm, state.target_distribution)
            var = variance_approx_kl(
                state.base_distribution,
                pull_tar,
                **state.var_diag_params)
            self.logger.info("Variance diagnostic: %e" % var)
            if var <= self.tol:
                return tm, log
            state.solve_counter += 1
        tm_old = state.transport_map_list[state.solve_counter-1]
        for transport_map, solve_params in zip(
                state.transport_map_list[state.solve_counter:],
                state.solve_params_list[state.solve_counter:]):
            # Here we are assuming nested basis
            for c1, c2 in zip(tm_old.approx_list, transport_map.approx_list):
                # Constant part
                for i1, midx1 in enumerate(c1.c.multi_idxs):
                    for i2, midx2 in enumerate(c2.c.multi_idxs):
                        if midx1 == midx2:
                            break
                    c2.c.coeffs[i2] = c1.c.coeffs[i1]
                # Integrated part
                for i1, midx1 in enumerate(c1.h.multi_idxs):
                    for i2, midx2 in enumerate(c2.h.multi_idxs):
                        if midx1 == midx2:
                            break
                    c2.h.coeffs[i2] = c1.h.coeffs[i1]
            
            # solve for the new map using regressed starting point
            solve_params['x0'] = transport_map.coeffs
            tm, log = super(ToleranceSequentialKullbackLeiblerBuilder, self).solve(
                transport_map,
                state.base_distribution,
                state.target_distribution,
                solve_params,
                mpi_pool=mpi_pool
            )
            if not log['success']:
                return tm_old, log
            pull_tar = PullBackTransportMapDistribution(tm, state.target_distribution)
            var = variance_approx_kl(
                state.base_distribution,
                pull_tar,
                **state.var_diag_params)
            self.logger.info("Variance diagnostic: %e" % var)
            if var <= self.tol:
                return tm, log
            tm_old = tm
            state.solve_counter += 1
        # Variance was not met
        log['success'] = False
        log['msg'] = "Desired tolerance was no met by the map adaptivity. " + \
                     "Target variance: %e - Variance: %e " % (self.tol, var)
        return tm, log

class FirstVariationKullbackLeiblerBuilder(KullbackLeiblerBuilder):
    r""" Adaptive builder based on the first variation of the kl divergence

    Given distribution :math:`\nu_\rho` and :math:`\nu_\pi`,
    and the parametric transport map :math:`T[{\bf a}]`,
    provides the functionalities to solve the problem

    .. math::

       \arg\min_{\bf a}\mathcal{D}_{\rm KL}\left(
       T[{\bf a}]_\sharp\rho \Vert \pi\right) =
       \arg\min_{\bf a}\underbrace{\mathbb{E}_\rho\left[
       -\log T[{\bf a}]^\sharp\pi \right]}_{
       \mathcal{J}[T]({\bf x})}

    up to a chosen tolerance, by enriching the map using information
    from the first variation

    .. math::

       \nabla\mathcal{J}[T]({\bf x}) =
       (\nabla_{\bf x}T)^{-\top}
       \left(\log\frac{\rho({\bf x})}{T^\sharp\pi({\bf x})}\right)

    """
    def __init__(
            self,
            validator,
            eps_bull,
            regression_builder=L2RegressionBuilder(),
            line_search_params={},
            max_it=20,
            prune_trunc={'type': 'manual', 'val': None},
            avar_trunc={'type': 'manual', 'val': None},
            coeff_trunc={'type': 'manual', 'val': None},
            callback=None,
            callback_kwargs={},
            verbosity=0,
            interactive=False):
        r"""
        Args:
          validator (:class:`Validator<TransportMaps.Diagnostic.Validator>`):
            validator to be used to check stability of the solution
          eps_bull (float): target tolerance of variance diagnostic
          callback (function): function taking a map and optional additional arguments
            which is called whenever it is deemed necessary by the chosen algorithm
            (e.g. for storing purposes)
          callback_kwargs (dict): additional arguments to be provided to the function
            ``callback``.
          verbosity (int): level of verbosity of the builder
          interactive (bool): whether to ask for permission to proceed to the user
        """
        self.regression_builder = regression_builder
        self.eps_bull = eps_bull
        self.line_search_params = line_search_params
        self.max_it = max_it
        self.prune_trunc = prune_trunc
        self.avar_trunc = avar_trunc
        self.coeff_trunc = coeff_trunc

        super(FirstVariationKullbackLeiblerBuilder,
              self).__init__(
                  validator,
                  callback=callback,
                  callback_kwargs=callback_kwargs,
                  verbosity=verbosity,
                  interactive=interactive)

    def _validation(self, state, mpi_pool=None):
        spmet = False
        while not spmet and \
              not state.validation_log.get('validator_cost_exceeded', False) and \
              not state.validation_log.get('validator_fcast_cost_exceeded', False):
            self.logger.info("Validation...")
            _, state.validation_log = super(
                FirstVariationKullbackLeiblerBuilder,
                self).solve(
                    state.transport_map,
                    state.base_distribution,
                    state.target_distribution,
                    state.solve_params,
                    mpi_pool=mpi_pool
                )
            # Separate cache from log, so not to store it.
            cache = state.validation_log.pop('cache')
            if not state.validation_log.get('success', False) or \
               state.validation_log.get('validator_cost_exceeded', False) or \
               state.validation_log.get('validator_fcast_cost_exceeded', False):
                if not state.validation_log.get('success', True):
                    state.fv_adapt_status = 'Failed to converge'
                    self.logger.warning(
                        "KL-minimization failed to converge. " + \
                        "Reverting to the last available map.")
                else:
                    state.fv_adapt_status = 'Cost exceeded'
                    self.logger.warning(
                        "Maximum cost exceeded. Reverting to the last available map.")
                if len(state.transport_map_list) > 0:
                    state.transport_map = state.transport_map_list[-1]
                return False, cache
            state.transport_map_list.append( state.transport_map )
            state.qparams_list.append(
                {'n_samps': state.solve_params['x'].shape[0]} )
            state.target_ncalls_list.append(
                state.target_distribution.get_ncalls_tree() )
            state.target_nevals_list.append(
                state.target_distribution.get_nevals_tree() )
            if self.callback is not None:
                self.callback( state.transport_map, **self.callback_kwargs )
            state.validator_error_list.append(
                state.validation_log.get('validator_error', 0.) )
            spmet = state.validator_error_list[-1] < state.validation_log.get(
                'validator_target_error', np.inf)
            state.spmet_list.append(spmet)
            if not spmet:
                self.logger.info("Pruning...")
                # Prune
                tm_new, flag, prune_params = \
                    FirstVariationKullbackLeiblerBuilder._prune_map(
                        state.transport_map,
                        state.validation_log['validator_prune_params'],
                        self.prune_trunc,
                        method='active')
                state.prune_trunc_params_list.append( prune_params )
                self.logger.info(
                    "Map pruning. Map structure:\n" + \
                    map_structure_str(tm_new, indent='   ', verbosity=self.verbosity) + \
                    map_sparsity_str(tm_new, indent='   ', verbosity=self.verbosity))
                if tm_new.n_coeffs == state.transport_map.n_coeffs:
                    # The minimum number of coefficients has already been reached
                    state.fv_adapt_status = \
                        "The pruning of the map, did not lead to the removal of " + \
                        "any degree of freedom."
                    self.logger.warning(
                        state.fv_adapt_status
                    )
                    state.spmet = False
                    state.tolmet = False
                    if len(state.transport_map_list) > 0:
                        state.transport_map = state.transport_map_list[-1]
                    return False, cache
                else:
                    state.transport_map = tm_new
                    state.solve_params['x0'] = state.transport_map.coeffs
        return True, cache

    def _diagnostic(self, state, mpi_pool=None):
        self.logger.info("Computing variance diagnostic...")
        pb_distribution = PullBackTransportMapDistribution(
            state.transport_map, state.target_distribution)
        var_diag = variance_approx_kl(
            state.base_distribution, pb_distribution,
            qtype=state.solve_params['qtype'],
            qparams=state.solve_params.get('qparams', {'eps_bull': self.eps_bull}),
            mpi_pool_tuple=(None, mpi_pool)
        )
        self.logger.info("Variance diagnostic: %.3e (target %.3e)" % (
            var_diag,self.eps_bull))

        state.variance_diagnostic_list.append( var_diag )
        if len(state.variance_diagnostic_list) > 1 and \
           var_diag > state.variance_diagnostic_list[-2]:
            state.fv_adapt_status = \
                "The variance diagnostic is not decreasing. This can be due to " + \
                "several reasons:\n" + \
                "   1) the number of quadrature points is insufficient and/or\n" + \
                "   2) the validation tolerance is too low with respect to the " + \
                "target adaptivity tolerance and/or\n" + \
                "   3) a pruning step with too strict tolerance has occurred"
            if self.interactive:
                self.logger.warning(state.fv_adapt_status)
                instr = None
                while instr not in ['c', 'q']:
                    instr = cmdinput(
                        "Please specify whether to (c)ontinue or to (q)uit: ")
                if instr == 'q':
                    self.logger.warning(
                        "The algorithm has been manually terminated.")
                    return False # Terminate
            else:
                if var_diag > state.variance_diagnostic_list[-2] + state.validator_error_list[-1]:
                    state.fv_adapt_status += "\n" + \
                        "The algorithms is automatically terminating."
                    self.logger.warning(state.fv_adapt_status)
                    return False # Terminate
                else:
                    keep_going_msg = "\n" + \
                        "Even though not decreasing, the variance diagnostic is still within " + \
                        "the validation error."
                    state.fv_adapt_status += keep_going_msg
                    self.logger.warning(keep_going_msg)
        state.tolmet = var_diag <= self.eps_bull
        return True 

    def _refinement(self, state, cache=None, mpi_pool=None):
        self.logger.info("Computing first variation...")

        if state.solve_params['qtype'] == 4:
            self.logger.warning(
                "Using MC for first variation." + \
                "We should be able to use other quadratures as well.")
            (x, w) = state.base_distribution.quadrature(
                0, 10000)
        else:
            try:
                x = state.solve_params['x']
                w = state.solve_params['w']
            except KeyError:
                (x, w) = state.base_distribution.quadrature(
                    state.solve_params['qtype'], state.solve_params['qparams'])
          
        # Compute first variation (here we need to make use of the caching)
        pb_distribution = PullBackTransportMapDistribution(
            state.transport_map, state.target_distribution)
        gt = FirstVariationKullbackLeiblerBuilder._compute_first_variation(
            x, w, state.base_distribution, pb_distribution, cache=cache,
            batch_size=state.solve_params.get('batch_size'),
            mpi_pool=mpi_pool)

        # Generate candidate transport map for regression of first variation
        self.logger.info("Projection of first variation...")

        # Project first variation on linear map (to extract active variables)
        fv_tri_tm = AffineTriangularMap(dim=state.transport_map.dim)
        fv_tri_tm, log_reg1 = self.regression_builder.solve(
            fv_tri_tm, gt, x=x, w=w)
        abs_exp_gx_fv_tri_tm = np.abs(fv_tri_tm.L)

        # Construct first variation candidate map (and prune unnecessary variables)
        fv_tri_tm, flag, trunc_params = \
            FirstVariationKullbackLeiblerBuilder._first_variation_candidate_triangular_map(
                state.transport_map, abs_exp_gx_fv_tri_tm, self.avar_trunc)
        state.avars_trunc_params_list.append( trunc_params )
        if flag == 'quit':
            self.logger.info("Terminating.")
            state.fv_adapt_status = \
                "Simulation aborted by the user during " + \
                "the pruning of the first variation in the refinement step."
            return False

        # Apply regression again to learn only important coefficients
        fv_tri_tm, log_reg2 = self.regression_builder.solve(
            fv_tri_tm, gt, x=x, w=w)
        for log_entry in log_reg2:
            if not log_entry['success']:
                state.fv_adapt_status = \
                    "Some of the optimizations during the second regression did not converge."
                self.logger.warning(
                    "Terminating: " + state.fv_adapt_status)
                return False

        # Line search and evaluation of improved map
        self.logger.info("Line search...")
        tm_ev = state.transport_map.evaluate(x)
        fv_tri_tm_ev = fv_tri_tm.evaluate(x)
        tm_pxd = state.transport_map.partial_xd(x)
        fv_tri_tm_pxd = fv_tri_tm.partial_xd(x)
        delta, ls_success = \
            FirstVariationKullbackLeiblerBuilder._kl_divergence_fv_line_search(
                state.target_distribution, w,
                tm_ev, fv_tri_tm_ev, tm_pxd, fv_tri_tm_pxd,
                self.line_search_params,
                mpi_pool=mpi_pool,
                interactive=self.interactive)
        if not ls_success:
            state.fv_adapt_status = \
                "Line search did not converge (delta: %e" % delta + "). " + \
                "This may due to several causes:\n" + \
                "   1) the maximum number of line search iterations is too low\n" + \
                "   2) the validation tolerance is too low to " + \
                "be able to detect improving directions\n" + \
                "   3) the validation tolerance is too low to detect that " + \
                "there is no other improving direction\n" + \
                "   4) the validation tolerance is too low w.r.t the target " + \
                "adaptivity tolerance"
            self.logger.warning(state.fv_adapt_status)
            if self.interactive:
                instr = None
                while instr not in ['c', 'q']:
                    instr = cmdinput(
                        "Specify whether to " + \
                        "(c)ontinue with stricter validation tolerances, " + \
                        "or to (q)uit: ")
                    if instr == 'q':
                        self.logger.warning(
                            "The algorithm has been manually terminated.")
                        return False
                    elif instr == 'c':
                        flag = self.validator.update_tolerances()
                        return flag
            else:
                self.logger.warning("Terminating: " + state.fv_adapt_status)
                return False
        self.logger.info("Line search - delta: %e" % delta)

        # Generate candidate transport map for regression on improved map
        self.logger.info("Generating new candidate map...")
        tm_new = FirstVariationKullbackLeiblerBuilder._improved_candidate_map(
            state.transport_map, fv_tri_tm)
        x0 = tm_new.coeffs
        tm_new, log_reg3 = self.regression_builder.solve(
            tm_new, tm_ev - delta * fv_tri_tm_ev,
            x=x, w=w, x0=x0)

        for log_entry in log_reg3:
            if not log_entry['success']:
                state.fv_adapt_status = \
                    "Some of the optimizations during the third regression step did not converge."
                self.logger.warning(
                    "Terminating. " + state.fv_adapt_status)
                return False

        # Remove unnecessary coefficients
        tm_new, flag, trunc_params = \
            FirstVariationKullbackLeiblerBuilder._prune_map(
                tm_new, np.abs(tm_new.coeffs), self.coeff_trunc,
                method='childless')
        if flag == 'quit':
            self.logger.info("Terminating.")
            state.fv_adapt_status = \
                "Simulation aborted by the user during the prune in the refinement step."
            return False
        if is_equal_map(state.transport_map, tm_new):
            state.fv_adapt_status = \
                "The refinement step did not change the original map. " + \
                "This may be due to several factors:\n" + \
                "   1) the truncation tolerances are too strict w.r.t. " + \
                "the validation tolerances\n" + \
                "   2) the validation tolerance is too low w.r.t the target " + \
                "adaptivity tolerance"
            self.logger.warning("Terminating. " + state.fv_adapt_status)
            return False

        # Set the values of the new coefficients in the approximation to zero
        # and the values of the old coefficients to the ones obtained in the latest
        # optimization cycle.
        # If changing dimension we need to rescale the coefficients
        # with respect to the normalization constant.
        for comp, avars, avars_old in zip(
                tm_new.approx_list, tm_new.active_vars, state.transport_map.active_vars):
            sl = comp.c.semilattice
            factor = np.sqrt(
                np.prod( [comp.c.full_basis_list[var].Gamma(0) for var in avars_old[:-1] ]) \
                / np.prod( [comp.c.full_basis_list[var].Gamma(0) for var in avars[:-1] ])
            )
            for v in sl:
                if v.data['is_new']:
                    v.coeff = 0.
                else:
                    v.coeff = v.data['old_coeff'] / factor
                    del v.data['old_coeff']
                del v.data['is_new']
            sl = comp.h.semilattice
            factor = np.sqrt(
                np.prod( [comp.h.full_basis_list[var].Gamma(0) for var in avars_old[:-1] ] ) \
                / np.prod( [comp.h.full_basis_list[var].Gamma(0) for var in avars[:-1] ] )
            )
            for v in sl:
                if v.data['is_new']:
                    v.coeff = 0.
                else:
                    v.coeff = v.data['old_coeff'] / factor
                    del v.data['old_coeff']
                del v.data['is_new']    

        self.logger.info(
            "Map refinement. Map structure:\n" + \
            map_structure_str(tm_new, indent='   ', verbosity=self.verbosity) + \
            map_sparsity_str(tm_new, indent='   ', verbosity=self.verbosity))
                
        # Set up as the new transport map and new initial conditions
        state.transport_map = tm_new
        state.solve_params['x0'] = state.transport_map.coeffs
        return True

    @state_loader(
        keys = [
            'transport_map',
            'base_distribution',
            'target_distribution',
            'solve_params']
    )
    def solve(
            self,
            transport_map=None,
            base_distribution=None,
            target_distribution=None,
            solve_params=None,
            state=None,
            mpi_pool=None
    ):
        r"""
        Args:
          transport_map (:class:`TransportMap<TransportMaps.Maps.TransportMap>`):
            starting transport map :math:`T`
          base_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            distribution :math:`\nu_\rho`
          target_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            distribution :math:`\nu_\pi`
          solve_params (dict): dictionary of parameters for solutino
          state (:class:`TransportMaps.DataStorageObject`): 
            if provided, it must contain all the information needed for reloading,
            or a handle to an empty storage object which can be externally stored.
            If ``state`` contains the keys corresponding to arguments to this function, 
            they will be used instead of the input themselves.

        Returns:
          (:class:`TransportMaps.Maps.TransportMap`) -- the transport map fitted.
        """

        # Internal solve states
        state.iter_counter    = getattr(state, 'iter_counter', 0)
        state.adapt_stage     = getattr(state, 'adapt_stage', 'validation')
        state.tolmet          = getattr(state, 'tolmet', False)
        state.validation_log  = getattr(state, 'validation_log', {})
        state.refinement_log  = getattr(state, 'refinement_log', {})
        state.diagnostic_log  = getattr(state, 'diagnostic_log', {})
        state.fv_adapt_status = getattr(state, 'fv_adapt_status', 'success')
        state.transport_map_list       = getattr(state, 'transport_map_list', [])
        state.validator_error_list     = getattr(state, 'validator_error_list', [])
        state.spmet_list               = getattr(state, 'spmet_list', [])
        state.variance_diagnostic_list = getattr(state, 'variance_diagnostic_list', [])
        state.qparams_list             = getattr(state, 'qparams_list', [])
        state.target_ncalls_list       = getattr(state, 'target_ncalls_list', [])
        state.target_nevals_list       = getattr(state, 'target_nevals_list', [])
        state.avars_trunc_params_list  = getattr(state, 'avars_trunc_params_list', [])
        state.coeffs_trunc_params_list = getattr(state, 'coeffs_trunc_params_list', [])
        state.prune_trunc_params_list  = getattr(state, 'prune_trunc_params_list', [])
        
        continue_flag = True # Continue
        self.logger.info(
            "Starting. Map structure:\n" + \
            map_structure_str(
                state.transport_map, indent='   ', verbosity=self.verbosity) + \
            map_sparsity_str(
                state.transport_map, indent='   ', verbosity=self.verbosity))
        if state.solve_params.get('x0') is None:
            state.transport_map.coeffs = state.transport_map.get_identity_coeffs()
            state.solve_params['x0'] = state.transport_map.coeffs
        while state.iter_counter < self.max_it and not state.tolmet:
            self.logger.info("Iteration %d" % state.iter_counter)
            if state.adapt_stage == 'validation':
                continue_flag, cache = self._validation(state, mpi_pool)
                if not continue_flag:
                    break
                state.adapt_stage = 'diagnostic'
                if self.callback is not None:
                    self.callback( state.transport_map, **self.callback_kwargs )
            if state.adapt_stage == 'diagnostic':
                # Once the coefficients are determined we check whether the
                # variance diagnostic tolerance is met
                continue_flag = self._diagnostic(state, mpi_pool)
                if not continue_flag or state.tolmet:
                    break
                state.adapt_stage = 'refinement'
                if self.callback is not None:
                    self.callback( state.transport_map, **self.callback_kwargs )
            if state.adapt_stage == 'refinement':
                try:
                    cache
                except NameError:
                    cache = None
                if not state.tolmet: # Refinement
                    continue_flag = self._refinement(state, cache, mpi_pool)
                if not continue_flag:
                    break
                state.adapt_stage = 'validation'
                del cache # Free some memory...    
            state.iter_counter += 1
            if self.callback is not None:
                self.callback( state.transport_map, **self.callback_kwargs )
        if state.iter_counter == self.max_it:
            fv_adapt_status = 'Maximum number of iterations exceeded'
        if self.callback is not None:
            self.callback( state.transport_map, **self.callback_kwargs )
        log = {'fv_adapt_status': state.fv_adapt_status,
               'fv_adapt_tolmet': state.tolmet,
               'fv_adapt_it': state.iter_counter}
        return state.transport_map, log

    @staticmethod
    def _compute_first_variation(
            x, w, d1, d2, cache=None,
            batch_size=None, mpi_pool=None):
        # Distribute objects
        d2_distr = pickle.loads( pickle.dumps(d2) )
        d2_distr.reset_counters()
        mpi_bcast_dmem(d1=d1, d2=d2_distr, mpi_pool=mpi_pool)
        # Link tm to d2.transport_map
        def link_tm_d2(d2):
            return (d2.transport_map,)
        (tm,) = mpi_map_alloc_dmem(
            link_tm_d2, dmem_key_in_list=['d2'], dmem_arg_in_list=['d2'],
            dmem_val_in_list=[d2], dmem_key_out_list=['tm'],
            mpi_pool=mpi_pool)
        # Prepare cache
        if mpi_pool:
            if cache is not None:
                cache2 = [ cc['pi_cache'] for cc in cache ]
            else:
                cache2 = [ None ] * mpi_pool.nprocs
            mpi_scatter_dmem(cache2=cache2, mpi_pool=mpi_pool)
        else:
            cache2 = cache['pi_cache'] if cache else None
        # Prepare batch size
        if batch_size is None:
            bsize = x.shape[0]
        else:
            bsize = batch_size[1]

        # # Split data
        # if mpi_pool is None:
        #     x_list = [x]
        # else:
        #     split_dict = mpi_pool.split_data([x],['x'])
        #     x_list = [sd['x'] for sd in split_dict]
        # max_len = x_list[0].shape[0]
        # # Compute the number of iterations necessary for batching
        # niter = max_len // batch_size + (1 if max_len % batch_size > 0 else 0)
        # # Iterate
        # idx0_list = [ 0 ] * len(x_list)
        # grad_t = np.zeros((x.shape[0], d2.dim))
        # for it in range(niter):
        #     # Prepare batch-slicing for each chunk
        #     idxs_slice_list = []
        #     for i, (xs, idx0) in enumerate(zip(x_list, idx0_list)):
        #         incr = min(batch_size, xs.shape[0] - idx0)
        #         idxs_slice_list.append( slice(idx0, idx0+incr, None) )
        #         idx0_list[i] += incr
        #     # Prepare input x
        #     x_in = [ xs[idxs_slice,:] for xs, idxs_slice in zip(x_list, idxs_slice_list) ]
        #     # Compute grad_x and store in distributed memory
        #     (grad_x_tm,) = mpi_map_alloc_dmem(
        #         'grad_x',
        #         scatter_tuple=scatter_tuple,
        #         dmem_key_out_list=['grad_x_tm'],
        #         obj='tm',
        #         obj_val=tm,
        #         mpi_pool=mpi_pool)

        # Compute grad_x and store in distributed memory
        scatter_tuple = (['x'], [x])
        (grad_x_tm,) = mpi_map_alloc_dmem(
            'grad_x',
            scatter_tuple=scatter_tuple,
            dmem_key_out_list=['grad_x_tm'],
            obj='tm',
            obj_val=tm,
            mpi_pool=mpi_pool)
        # Compute first variation
        grad_t = mpi_map(
            grad_t_kl_divergence,
            scatter_tuple=scatter_tuple,
            bcast_tuple=(['batch_size'],[bsize]),
            dmem_key_in_list=['d1', 'd2', 'grad_x_tm', 'cache2'],
            dmem_arg_in_list=['d1', 'd2', 'grad_x_tm', 'cache2'],
            dmem_val_in_list=[d1, d2, grad_x_tm, cache2],
            mpi_pool=mpi_pool, concatenate=True )    
        
        # start = 0
        # grad_t = np.zeros((x.shape[0], d2.dim))
        # while start < x.shape[0]:
        #     stop = min(x.shape[0], start + bsize)
        #     # Compute grad_x and store in distributed memory
        #     scatter_tuple = (['x'], [x[start:stop,:]])
        #     (grad_x_tm,) = mpi_map_alloc_dmem(
        #         'grad_x',
        #         scatter_tuple=scatter_tuple,
        #         dmem_key_out_list=['grad_x_tm'],
        #         obj='tm',
        #         obj_val=tm,
        #         mpi_pool=mpi_pool)
        #     # Compute first variation
        #     (grad_t_batch,) = mpi_map(
        #         grad_t_kl_divergence,
        #         scatter_tuple=scatter_tuple,
        #         dmem_key_in_list=['d1', 'd2', 'grad_x_tm', 'cache2'],
        #         dmem_arg_in_list=['d1', 'd2', 'grad_x_tm', 'cache2'],
        #         dmem_val_in_list=[d1, d2, grad_x_tm, cache2],
        #         mpi_pool=mpi_pool, concatenate=True )
        #     grad_t[start:stop,:] = grad_t_batch
        #     start = stop

        # Update counters
        if mpi_pool is not None:
            d2_child_list = mpi_pool.get_dmem('d2')
            d2.update_ncalls_tree( d2_child_list[0][0] )
            for (d2_child,) in d2_child_list:
                d2.update_nevals_tree(d2_child)
                d2.update_teval_tree(d2_child)
        # Clear mpi_pool
        if mpi_pool is not None:
            mpi_pool.clear_dmem()
        return grad_t

    @staticmethod
    def _kl_divergence_fv_line_search(
            pi, w, tm_ev, fv_tri_tm_ev, tm_pxd, fv_tri_tm_pxd,
            line_search_params, mpi_pool, interactive=False):

        def objective(x, pi, w, U, pU, mpi_pool):
            # Here x = [T(x)+\delta U(x) | \partial_i T_i(x) + \delta \partial_i U_i(x) ]
            dim = x.shape[1]//2
            TdU = x[:,:dim]
            pTdU = x[:,dim:]
            if np.any(pTdU < 0):
                return np.nan
            lpTdU = np.log(pTdU)
            # Compute pi.log_pdf( T(x)-\delta U(x) )
            scatter_tuple = (['x'], [TdU])
            lpdf = mpi_map('log_pdf', scatter_tuple=scatter_tuple,
                           obj='pi', obj_val=pi, mpi_pool=mpi_pool)
            # Compute log determinant part
            log_det = np.sum(lpTdU, axis=1)
            # Compute output
            out = - np.dot( lpdf + log_det, w )
            return out

        # Distribute pi to the different cores if necessary
        pi_distr = pickle.loads( pickle.dumps(pi) )
        pi_distr.reset_counters()
        mpi_bcast_dmem(pi=pi, mpi_pool=mpi_pool)

        # Set up line search arguments
        T = tm_ev
        pT = tm_pxd
        U = fv_tri_tm_ev
        pU = fv_tri_tm_pxd
        args = (pi, w, U, pU, mpi_pool)
        Tstack = np.hstack( (T, pT) )
        Ustack = np.hstack( (U, pU) )

        # Perform steps of back tracking to find a good delta improving the objective
        # and preserving monotonicity
        maxit = line_search_params.get('maxiter', 20)
        delta = line_search_params.get('delta', 2.)
        isnan = True
        it = 0
        fval0 = objective(Tstack, *args)
        fval = np.inf
        done = False
        while not done:
            while (isnan or fval > fval0) and it < maxit:
                delta /= 2
                fval = objective(Tstack - delta * Ustack, *args)
                isnan = np.isnan(fval)
                it += 1
            if interactive:
                done = it < maxit
                if not done:
                    print("Line search did not converge.")
                    val, flag = read_and_cast_input(
                        "number of extra iterations [delta: %e]" % delta,
                        int)
                    if not flag:
                        done = True
                    else:
                        maxit += val
            else:
                done = True

        if mpi_pool is not None:
            pi_child_list = mpi_pool.get_dmem('pi')
            pi.update_ncalls_tree( pi_child_list[0][0] )
            for (pi_child,) in pi_child_list:
                pi.update_nevals_tree(pi_child)
                pi.update_teval_tree(pi_child)

        return delta, it < maxit

    @staticmethod
    def _first_variation_candidate_triangular_map(
            transport_map, sensitivities, avar_trunc): 
        r""" Construct the candidate map to be used in the regression of the first variation.

        It takes the multi-indices in ``transport_map`` and increases them by one,
        adding also active variables if needed.
        The active variables to add are detected using the information contained
        in ``sensitivities``.
        """
        active_vars = []
        sl_list = []
        scsens = sensitivities / np.max(sensitivities)
        if isinstance(avar_trunc, dict):
            if avar_trunc['type'] == 'manual':
                if not PLOT_SUPPORT:
                    raise ImportError(
                        "The 'manual' truncation type requires plotting, but " + \
                        "plotting is not supported on this machine. " + \
                        "The program will be terminated.")
                import matplotlib.pyplot as plt
                plt.figure()
                for d in range(transport_map.dim):
                    plt.semilogy(range(d+1), scsens[d,:d+1], 'o-')
                # plt.imshow(np.log10(scsens)) 
                # plt.colorbar()
                plt.grid(True)
                plt.show(False)
                trunc_val = None
                while trunc_val is None:
                    try:
                        istr = cmdinput(
                            "Provide an active variable truncation level [q to quit]: ")
                        trunc_val = float( istr )
                    except ValueError:
                        if istr == 'q':
                            return transport_map, 'quit', None
                        print("The value entered cannot be casted to a floating point number.")
            elif avar_trunc['type'] == 'constant':
                trunc_val = avar_trunc['val']
        else:
            trunc_val = avar_trunc
        log_params = {
            'avar_trunc': copy.deepcopy(avar_trunc),
            'trunc_val': trunc_val
        }
        for d, (tm_comp, tm_comp_avars) in enumerate(zip(
                transport_map.approx_list, transport_map.active_vars)):
            # Update active variables using second order information
            fv_avars = list(np.where(scsens[d,:d] > trunc_val)[0])
            add_avars = [ var for var in fv_avars if not var in tm_comp_avars ]
            avars = tm_comp_avars + add_avars
            perm_avars = argsort( avars )
            avars = [ avars[i] for i in perm_avars ]
            # Extract semilattices from constant and integrated squared part
            c_sl = tm_comp.c.semilattice
            h_sl = tm_comp.h.semilattice
            # Expand integrated squared semilattice by doubling the orders
            # and adding one to the trailing dimension
            h_sl_2 = h_sl * h_sl # double the orders
            h_dim = h_sl.dims
            lst = [ v for v in SL.BreadthFirstSemilatticeIterable( h_sl_2 ) ]
            for v in lst: # add one to the last dimension
                if h_dim-1 not in v.children:
                    h_sl_2.new_vertex( parent=v, edge=h_dim-1 )
            # Merge constant and integrated squared semilattices
            sl = c_sl | h_sl_2
            if len(add_avars) > 0:
                # Expand dimension to match new active variables
                sl.modify_dims(add_dims=len(add_avars))
                # Permute semilattice according to the order of the active variables
                sl = SL.permute(sl, perm_avars)
            # Expand along admissible frontier
            lst = [ v for v in sl.admissible_frontier ]
            for v in lst:
                edges = sl.potential_children_edges( v )
                for edge in edges:
                    sl.new_vertex(parent=v, edge=edge)
            # Update
            active_vars.append(avars)
            sl_list.append(sl)
        fv_approx = assemble_LinearSpanTriangularMap(
            transport_map.dim, sl_list, active_vars)
        return fv_approx, 'success', log_params

    @staticmethod
    def _improved_candidate_map(transport_map, fv_map):
        active_vars = []
        approx_list = []
        for d, (tm_avars, tm_comp,
                fv_avars, fv_comp) in enumerate(zip(
                    transport_map.active_vars, transport_map.approx_list,
                    fv_map.active_vars, fv_map.approx_list)):
            tm_full_c_blist = tm_comp.c.full_basis_list
            tm_full_h_blist = tm_comp.h.full_basis_list
            # Retrieve semilattices
            tmc_sl = tm_comp.c.semilattice.copy()
            tmh_sl = tm_comp.h.semilattice.copy()
            # Find missing active variables (tm_avars is a subset of fv_avars)
            add_avars = []
            j = 0
            for var in fv_avars:
                if var != tm_avars[j]:
                    add_avars.append( var )
                else:
                    j += 1
            # Add the active variables and find appropriate permutation
            avars = tm_avars + add_avars
            perm_avars = argsort( avars )
            avars = [ avars[i] for i in perm_avars ]
            # Expand dimensions (append) to match new active variables
            tmc_sl.modify_dims(add_dims=len(add_avars))
            tmh_sl.modify_dims(add_dims=len(add_avars))
            # Permute semilattice according to the order of the active variables
            tmc_sl = SL.permute(tmc_sl, perm_avars)
            tmh_sl = SL.permute(tmh_sl, perm_avars)
            # Mark all old vertices as old vertices and store coefficent values
            for v in tmc_sl:
                v.data['is_new'] = False
                v.data['old_coeff'] = v.coeff
            for v in tmh_sl:
                v.data['is_new'] = False
                v.data['old_coeff'] = v.coeff
            # Expand along admissible frontier (constant part)
            # and flag new vertices (using the data dictionary in vertices)
            lst = [ v for v in tmc_sl.admissible_frontier ]
            for v in lst:
                edges = tmc_sl.potential_children_edges( v )
                for edge in edges:
                    if edge != tmc_sl.dims - 1:
                        # Not allowed to increase in the last dimension
                        # for the constant part
                        new_v = tmc_sl.new_vertex(
                            parent=v, edge=edge)
                        new_v.data['is_new'] = True
            # Expand along admissible frontier (integrated squared part)
            # and flag new vertices (using the data dictionary in vertices)            
            lst = [ v for v in tmh_sl.admissible_frontier ]
            for v in lst:
                edges = tmh_sl.potential_children_edges( v )
                for edge in edges:
                    new_v = tmh_sl.new_vertex(
                        parent=v, edge=edge)
                    new_v.data['is_new'] = True
            # Build basis (using the full basis set provided by the transport map)
            c_basis = [ tm_full_c_blist[a] for a in avars ]
            h_basis = [ tm_full_h_blist[a] for a in avars ]
            # Build constant and integrated linear span functions
            c = LinearSpanTensorizedParametricFunctional(
                c_basis,
                semilattice=tmc_sl,
                full_basis_list=tm_full_c_blist)
            h = LinearSpanTensorizedParametricFunctional(
                h_basis,
                semilattice=tmh_sl,
                full_basis_list=tm_full_h_blist)
            # Assemble component
            comp = type(tm_comp)(c, h)
            # Append to list of components and active variables
            approx_list.append(comp)
            active_vars.append(avars)
        new_map = type(transport_map)(
            active_vars=active_vars,
            approx_list=approx_list,
            full_c_basis_list=transport_map.full_c_basis_list,
            full_h_basis_list=transport_map.full_h_basis_list)
        return new_map

    @staticmethod
    def _prune_map(
            tm, coeffs_weights, coeff_trunc,
            method='active'):
        r"""

        With the option ``method==active`` all the ``active`` 
        vertices will be considered for removal.
        With the option ``method==childless`` only the ``active`` 
        childless vertices of the semilattices 
        will be considered for removal.
        In both cases the roots will never be removed/inactivated.

        Args:
          coeffs_weights (list): weights for each degree of freedom.
            Must be ``len(coeffs_weights)==tm.n_coeffs``.
            Degrees of freedoms with lower coefficients will be removed.
          method (str): method for pruning.
            Available options are ``childless``, ``active``.
        """
        tm = copy.deepcopy(tm)

        # Identify coefficients that are allowed to be removed
        removable_flag_list = [] # List of booleans marking whether one dof may be removed (True)
        for comp in tm.approx_list:
            # Constant part
            sl = comp.c.semilattice 
            for v in sl.dof:
                if v is sl.root:
                    removable_flag_list.append( False )
                else:
                    if method == 'childless':
                        removable_flag_list.append( v in sl.childless )
                    elif method == 'active':
                        removable_flag_list.append( True )
                    else:
                        raise ValueError("Unrecognized pruning method")
            # Integrated squared part
            sl = comp.h.semilattice 
            for v in sl.dof:
                if v is sl.root:
                    removable_flag_list.append( False )
                else:
                    if method == 'childless':
                        removable_flag_list.append( v in sl.childless )
                    elif method == 'active':
                        removable_flag_list.append( True )
                    else:
                        raise ValueError("Unrecognized pruning method")

        # Identify the truncation value
        rem_coeffs_weights = sorted(
            [ cw for flag, cw in zip(removable_flag_list, coeffs_weights) if flag ] )
        if isinstance(coeff_trunc, float):
            coeff_trunc = {'type': 'value', 'val': coeff_trunc}
        elif not isinstance(coeff_trunc, dict):
            raise ValueError(
                "coeff_trunc must be either a float or a dictionary.")
        if coeff_trunc['type'] == 'constant':
            idx = coeff_trunc['val'] if coeff_trunc['val'] < len(rem_coeffs_weights) else -1
            trunc_val = rem_coeffs_weights[idx]
        elif coeff_trunc['type'] == 'percentage':
            idx = int( np.ceil( len(rem_coeffs_weights) * coeff_trunc['val'] ) )
            trunc_val = rem_coeffs_weights[idx]
        elif coeff_trunc['type'] == 'manual':
            if not PLOT_SUPPORT:
                raise ImportError(
                    "The 'manual' truncation type requires plotting, but " + \
                    "plotting is not supported on this machine. " + \
                    "The program will be terminated.")
            import matplotlib.pyplot as plt
            plt.figure()
            plt.semilogy( rem_coeffs_weights[::-1], 'o-' )
            plt.grid(which='major', linewidth=1.)
            plt.grid(which='minor', linewidth=.3)
            plt.show(False)
            trunc_val = None
            while trunc_val is None:
                try:
                    istr = cmdinput("Provide a truncation level [q to quit]: ")
                    trunc_val = float( istr )
                except ValueError:
                    if istr == 'q':
                        return tm, 'quit'
                    print("The value entered cannot be casted to a floating point number.")
        elif coeff_trunc['type'] == 'value':
            trunc_val = coeff_trunc['val']
        else:
            raise ValueError(
                "Unrecognized truncation type. Available options are: " + \
                "constant, percentage, manual.")
        log_params = {
            'coeff_trunc': copy.deepcopy(coeff_trunc),
            'trunc_val': trunc_val
        }
        
        # Run through the degrees of freedom and inactivate them
        j = 0
        for comp in tm.approx_list:
            # Constant part
            inactive_list = []
            sl = comp.c.semilattice
            for v in sl.dof:
                removable = removable_flag_list[j]
                if removable and abs(v.coeff) < trunc_val:
                    inactive_list.append( v )
                j += 1
            for v in inactive_list:
                sl.set_inactive( v )
            # Integrated squared part
            inactive_list = []
            sl = comp.h.semilattice
            for v in sl.dof:
                removable = removable_flag_list[j]
                if removable and abs(v.coeff) < trunc_val:
                    inactive_list.append( v )
                j += 1
            for v in inactive_list:
                sl.set_inactive( v )

        # Clean up the semilattices
        # Run through the childless vertices and if inactive, remove them
        nrem = 1 # Keep removing untill nothing can be removed (i.e. every childless is active)
        while nrem > 0:
            nrem = 0
            for comp in tm.approx_list:
                # Constant part
                rm_lst = []
                sl = comp.c.semilattice
                for v in sl.childless:
                    if v not in sl.dof:
                        rm_lst.append( v )
                for v in rm_lst:
                    sl.delete_vertex( v )
                nrem += len(rm_lst)
                # Integrated squared part
                rm_lst = []
                sl = comp.h.semilattice
                for v in sl.childless:
                    if v not in sl.dof:
                        rm_lst.append( v )
                for v in rm_lst:
                    sl.delete_vertex( v )
                nrem += len(rm_lst)

        # Remove dimensions that have been inactivated by the pruning
        for icomp, comp in enumerate(tm.approx_list):
            avars_old = tm.active_vars[icomp]
            c = comp.c
            h = comp.h.h
            # Figure out which active variables are not active anymore
            # One just needs to look at the children that the root has left.
            avars_idxs = set([ comp.dim_in-1 ])
            sl = c.semilattice  # Constant part
            avars_idxs |= sl.root.children.keys()
            sl = h.semilattice  # Integrated squared part
            avars_idxs |= sl.root.children.keys()
            avars_idxs_compl = set([ idx for idx in range(comp.dim_in) if idx not in avars_idxs ]) # Inactive variables indices
            avars_new = sorted([ avars_old[i] for i in avars_idxs ])
            # Re-sort the input dimensions of the semilattices to have
            # first the active indices (sorted) and then the inactive ones.
            # Then we can just trim the dimension of the semilattice
            # as all the trailing dimensions are inactive.
            perm_idxs = sorted(list(avars_idxs)) + list(avars_idxs_compl)
            c.semilattice = SL.permute(c.semilattice, perm_idxs)
            h.semilattice = SL.permute(h.semilattice, perm_idxs)
            c.semilattice.modify_dims(subtract_dims=len(avars_idxs_compl))
            h.semilattice.modify_dims(subtract_dims=len(avars_idxs_compl))
            # Modify basis list for the tensorized parametric functionals
            c.basis_list = [ c.basis_list[i] for i in sorted(list(avars_idxs)) ]
            h.basis_list = [ h.basis_list[i] for i in sorted(list(avars_idxs)) ]
            # Modify dimensions
            c.dim_in = len(avars_idxs)
            h.dim_in = len(avars_idxs)
            comp.dim_in = len(avars_idxs)
            # Modify active variables for the component
            tm.active_vars[icomp] = avars_new
                
        # Return
        return tm, 'success', log_params
    
def map_structure_str(tm, indent, verbosity=0):
    out = indent + "Number of degrees of freedom: %d\n" % tm.n_coeffs
    cmp_str = "Component %%%dd" % len(str(tm.dim))
    if verbosity > 1:
        for d, (comp, avars) in enumerate(zip(tm.approx_list, tm.active_vars)):
            out += indent + cmp_str % d + " #D.o.F: %d - " % comp.n_coeffs + \
                   "Active variables: %s\n" % str(avars)
            out += indent + "   Const part - midxs: %s\n" % (comp.c.multi_idxs)
            if verbosity > 1:
                out += indent + "   Const part - coeffs: %s\n" % ([ "%.2e" % c for c in comp.c.coeffs])
            out += indent + "   Integ part - midxs: %s\n" % (comp.h.multi_idxs)
            if verbosity > 1:
                out += indent + "   Integ part - coeffs: %s\n" % ([ "%.2e" % c for c in comp.h.coeffs])
    return out

def map_sparsity_str(tm, indent, verbosity=0):
    navar = sum([len(avars) for avars in tm.active_vars])
    totvar = (tm.dim+1)*tm.dim / 2
    out = indent + "Map sparsity: %d/%d (%.4f%%)\n" % (
        navar, totvar, float(navar)/float(totvar)*100)
    if verbosity == 1:
        for d, (comp, avars) in enumerate(zip(tm.approx_list, tm.active_vars)):
            out += indent + \
                   '   comp %d - avars: %s ' % (d, str(avars)) + \
                   '- maxord: %d' % (max(
                       np.max(comp.c.multi_idxs), np.max(comp.h.multi_idxs))) + '\n'
    if verbosity > 1:
        for d, avars in enumerate(tm.active_vars):
            str_list = [' '] * tm.dim
            for var in avars:
                str_list[var] = 'x'
            out += indent + '   |' + ''.join(str_list) + '|' + '\n'
    return out

def is_equal_map(tm1, tm2): # TODO: update with semilattices
    match = True
    for d, (c1, a1, c2, a2) in enumerate(zip(
            tm1.approx_list, tm1.active_vars, tm2.approx_list, tm2.active_vars)):
        match = set(a1) == set(a2)
        if not match:
            break
        match = c1.c.semilattice == c2.c.semilattice
        if not match:
            break
        match = c1.h.semilattice == c2.h.semilattice
        if not match:
            break
    return match
