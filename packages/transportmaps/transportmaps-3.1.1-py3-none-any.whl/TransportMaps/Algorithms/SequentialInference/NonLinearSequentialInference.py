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

from ...MPI import mpi_map
from ..Adaptivity.KullbackLeiblerAdaptivity import KullbackLeiblerBuilder
from ..Adaptivity.RegressionAdaptivity import L2RegressionBuilder
from ...Distributions import StandardNormalDistribution, \
    PushForwardTransportMapDistribution, PullBackTransportMapDistribution
from ...Maps import \
    ComponentwiseMap, \
    TriangularComponentwiseTransportMap, \
    ListCompositeTransportMap, \
    CompositeMap, ListCompositeMap, PermutationTransportMap, \
    TriangularListStackedTransportMap, IdentityTransportMap, \
    InverseTransportMap, LinearTransportMap
from ...Diagnostics.Routines import variance_approx_kl
from ...Maps.Decomposable import SequentialInferenceMapFactory, LiftedTransportMap
from ...L2 import L2_misfit

from .SequentialInferenceBase import *

__all__ = [
    'TransportMapsSmoother',
    'FilteringPreconditionedTransportMapsSmoother',
    'LowRankTransportMapsSmoother',
    'LowRankFilteringPreconditionedTransportMapSmoother',
]


class TransportMapsSmoother(Smoother):
    r""" Perform the on-line assimilation of a sequential Hidded Markov chain.

    Given the prior distribution on the hyper-parameters :math:`\pi(\Theta)`,
    provides the functions neccessary to assimilate new pieces of data or
    missing data 
    (defined in terms of transition densities
    :math:`\pi\left({\bf Z}_{k+1} \middle\vert {\bf Z}_k, \Theta \right)`
    and log-likelihoods
    :math:`\log \mathcal{L}\left({\bf y}_{k+1}\middle\vert {\bf Z}_{k+1}, \Theta\right)`),
    to return the map pushing forward :math:`\mathcal{N}(0,{\bf I})`
    to the smoothing distribution
    :math:`\pi\left(\Theta, {\bf Z}_\Lambda \middle\vert {\bf y}_\Xi \right)`
    and to return the maps pushing forward :math:`\mathcal{N}(0,{\bf I})`
    to the filtering/forecast distributions
    :math:`\{\pi\left(\Theta, {\bf Z}_k \middle\vert {\bf y}_{0:k} \right)\}_k`.

    For more details see also :cite:`Spantini2017` and the
    `tutorial <example-sequential-stocvol-6d.html>`_.

    Optional Args:
      pi_hyper (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        prior distribution on the hyper-parameters :math:`\pi(\Theta)`
    """
    def __init__(self, *args, **kwargs):
        super(TransportMapsSmoother, self).__init__(*args, **kwargs)
        self._var_diag_convergence = []
        self._regression_convergence = []
        self._markov_component_nevals = {}

    @property
    def var_diag_convergence(self):
        return self._var_diag_convergence

    @property
    def regression_convergence(self):
        return self._regression_convergence

    @property
    def markov_component_nevals(self):
        return self._markov_component_nevals
    
    def _terminate_kl(self, log, continue_on_error):
        if not log['success']:
            if continue_on_error:
                self.logger.warning(
                    log.get('msg', '') + \
                    "Reverted to last converged map. " + \
                    "This may lead to overall loss of accuracy.")
            else:
                self.logger.error(
                    log.get('msg', '') + " Terminating."
                )
                return True
        return False

    def _permuting_map(self, pi):
        hdim = self.pi.hyper_dim
        sdim = self.pi.state_dim
        if self.nsteps == 0:
            permtm = IdentityTransportMap(pi.dim)
        else:
            if not hasattr(self, 'Q'):
                self.Q = PermutationTransportMap(
                    list(range(hdim)) + \
                    list(range(hdim+sdim, hdim+2*sdim)) + \
                    list(range(hdim, hdim+sdim)) )
            permtm = self.Q
        return permtm
        
    def _preconditioning_map(self, pi, mpi_pool=None):
        r""" Returns the preconditioning map as well as the sub-components: the hyper-parameters and filtering preconditioning maps.
        """        
        hdim = self.pi.hyper_dim
        sdim = self.pi.state_dim
        if self.nsteps == 0:
            ptm = IdentityTransportMap(hdim+sdim)
        else:
            ptm = IdentityTransportMap(hdim+2*sdim)
        hptm = IdentityTransportMap(hdim)
        fptm = IdentityTransportMap(sdim)
        hfptm = IdentityTransportMap(sdim+hdim)
        map_factory_kwargs = {
            'sdim': sdim, 'hdim': hdim}
        return ptm, hptm, fptm, hfptm, map_factory_kwargs
        
    def _learn_map(
            self,
            rho,
            pi,
            tm,
            solve_params,
            builder_extra_kwargs,
            builder_class,
            continue_on_error,
            mpi_pool=None,
            **kwargs
    ):
        r""" Returns the transport map found and the preconditioning maps.
        """
        hdim = self.pi.hyper_dim
        sdim = self.pi.state_dim
        
        # Permute coordinates
        permtm = self._permuting_map(pi)
        tar_pi = PullBackTransportMapDistribution(permtm, pi)
        
        # Regular Preconditioning (optional rotations if active)
        ptm, hptm, fptm, hfptm, map_factory_kwargs = self._preconditioning_map(
            tar_pi, mpi_pool=mpi_pool)
        if issubclass(type(tm), SequentialInferenceMapFactory):
            nn = 0 if self.nsteps == 0 else 1
            tm = tm.generate(nsteps=nn, **map_factory_kwargs)
        tar_pi = PullBackTransportMapDistribution(ptm, tar_pi)
        ref_rho = PushForwardTransportMapDistribution(
            InverseTransportMap(base_map=ptm), rho )

        # Solve
        builder = builder_class(**builder_extra_kwargs)
        tm, log = builder.solve(
            tm,
            ref_rho, 
            tar_pi,
            solve_params,
            mpi_pool=mpi_pool)
        if self._terminate_kl(log, continue_on_error):
            raise RuntimeError(log['msg'] + " Terminating.")

        # Compose hyper-parameter map
        htm = None if hdim == 0 else \
              ListCompositeTransportMap(
                  map_list = [
                      hptm,
                      TriangularComponentwiseTransportMap(
                          active_vars=tm.active_vars[:hdim],
                          approx_list=tm.approx_list[:hdim] ),
                      InverseTransportMap( base_map=hptm )
                  ]
              )

        # Compose filtering map
        ftm = ListCompositeMap(
            map_list = [
                fptm,
                ComponentwiseMap(
                    active_vars=tm.active_vars[hdim:hdim+sdim],
                    approx_list=tm.approx_list[hdim:hdim+sdim] ),
                InverseTransportMap( base_map = hfptm )
            ]
        )

        # Compose smoothing map
        stm = ListCompositeTransportMap(
            map_list = [
                permtm,
                ptm,
                tm,
                InverseTransportMap( base_map=ptm ),
                InverseTransportMap( base_map=permtm )
            ]
        )

        dd = {
            'tm': tm,
            'hyper_tm': htm,
            'filt_tm': ftm,
            'smooth_tm': stm
        }
        
        return dd
        
    def _assimilation_step(
            self,
            # KL-minimization parameters
            tm,
            solve_params,
            builder_extra_kwargs={},
            builder_class=None,
            var_diag_convergence_params=None,
            # Hyper-parameters regression parameters
            hyper_tm=None,
            regression_params=None,
            regression_builder=None,
            regression_convergence_params=None,
            # Other parameters
            continue_on_error=True,
            # Additional parameters to be passed to learn_map
            learn_map_extra_kwargs={},
            mpi_pool=None
    ):
        r""" Assimilate one piece of data :math:`\left( \pi\left({\bf Z}_{k+1} \middle\vert {\bf Z}_k, \Theta \right), \log \mathcal{L}\left({\bf y}_{k+1}\middle\vert {\bf Z}_{k+1}, \Theta\right) \right)`.

        Given the new piece of data
        :math:`\left( \pi\left({\bf Z}_{k+1} \middle\vert {\bf Z}_k, \Theta \right), \log \mathcal{L}\left({\bf y}_{k+1}\middle\vert {\bf Z}_{k+1}, \Theta\right) \right)`,
        retrieve the :math:`k`-th Markov component :math:`\pi^k` of :math:`\pi`,
        determine the transport map

        .. math::

           \mathfrak{M}_k({\boldsymbol \theta}, {\bf z}_k, {\bf z}_{k+1}) = \left[
           \begin{array}{l}
           \mathfrak{M}^\Theta_k({\boldsymbol \theta}) \\
           \mathfrak{M}^0_k({\boldsymbol \theta}, {\bf z}_k, {\bf z}_{k+1}) \\
           \mathfrak{M}^1_k({\boldsymbol \theta}, {\bf z}_{k+1})
           \end{array}
           \right] = Q \circ R_k \circ Q

        that pushes forward :math:`\mathcal{N}(0,{\bf I})` to :math:`\pi^k`, and
        embed it into the linear map which will remove the desired conditional
        dependencies from :math:`\pi`.
        
        Optionally, it will also compress the maps
        :math:`\mathfrak{M}_{0}^\Theta \circ \ldots \circ \mathfrak{M}_{k-1}^\Theta`
        into the map :math:`\mathfrak{H}_{k-1}` in order to speed up the
        evaluation of the :math:`k`-th Markov component :math:`\pi^k`.

        Args:
          tm (:class:`TransportMap<TransportMaps.Maps.TransportMap>`):
            transport map :math:`R_k`
          builder_extra_kwargs (dict): parameters to be passed to the builder
            :func:`minimize_kl_divergence<TransportMaps.Maps.TransportMap.minimize_kl_divergence>`
          solve_params (dict): dictionary of options to be passed to
            :func:`minimize_kl_divergence`.
          builder_class (class): sub-class of
            :class:`KullbackLeiblerBuilder<TransportMaps.Algorithms.Adaptivity.KullbackLieblerBuilder>` describing the particular builder used for the minimization of the kl-divergence. Default is :class:`KullbackLeiblerBuilder<TransportMaps.Algorithms.Adaptivity.KullbackLieblerBuilder>` itself.
          hyper_tm (:class:`TransportMap<TransportMaps.Maps.TransportMap>`):
            transport map :math:`\mathfrak{H}_{k-1}`
          regression_params (dict): parameters to be passed to
            :func:`regression<TransportMaps.Maps.TransportMap.regression>` during
            the determination of :math:`\mathfrak{H}_{k-1}`
          regression_builder (:class:`L2RegressionBuilder`): builder for the regression of the
            hyper-parameters map.
          var_diag_convergence_params (dict): parameters to be used to monitor the
            convergence of the map approximation. If ``None`` the conevergence is not monitored.
          regression_convergence_params (dict): parameters to be used to monitor the
            convergence of the regression step on the hyper-parameters map.
            If ``None`` the conevergence is not monitored.
          continue_on_error (bool): whether to continue when the KL-minimization step or the
            regression step fails with back-up plans
          learn_map_extra_kwargs (dict): extra keyword arguments to be passed to
            the :func:`_learn_map`.
          mpi_pool (:class:`mpi_map.MPI_Pool`): pool of processes to be used for additional evaluations

        Raises:
          RunTimeError: an convergence error occurred during the assimilation

        .. see:: :func:`Smoother.assimilate`
        """
        hdim = self.pi.hyper_dim
        sdim = self.pi.state_dim        

        if builder_class is None:
            builder_class = KullbackLeiblerBuilder
        if regression_builder is None:
            regression_builder = L2RegressionBuilder({})
        # Approximation
        if self.nsteps == 0:
            # If step zero, then just approximate self.pi
            ref_rho = StandardNormalDistribution(self.pi.dim)
            tar_pi = self.pi
            ddlm = self._learn_map(
                ref_rho, tar_pi, tm, solve_params,
                builder_extra_kwargs, builder_class, continue_on_error,
                mpi_pool=mpi_pool,
                **learn_map_extra_kwargs )
            self.H_list = [ ddlm['hyper_tm'] ]
            self.R_list = [ ddlm['tm'] ]
            self.M_list = [ ddlm['smooth_tm'] ]
            self.L_list = [
                LiftedTransportMap(-1, self.M_list[0], self.pi.dim, hdim) ]
        elif self.nsteps > 0:
            # If step k, then approximate the (k-1)-th Markov component
            # Regression of the hyper-parameters maps
            if self.nsteps > 1 and hyper_tm is not None:
                x0 = None
                if self.nsteps > 2 and isinstance(regression_builder, L2RegressionBuilder):
                    x0 = self.H_list[-1].t1.coeffs
                hyper_tm, log_list = regression_builder.solve(
                    hyper_tm, self.H_list[-1], x0=x0, **regression_params)
                if not log_list[-1]['success']:
                    if not continue_on_error:
                        self.logger.error("Regression did not converge. Terminating.")
                        raise RuntimeError("Regression did not converge. Terminating.")
                else:
                    if regression_convergence_params is not None:
                        self._regression_convergence.append(
                            L2_misfit(
                                self.H_list[-1], hyper_tm,
                                **regression_convergence_params) )
                    else:
                        self._regression_convergence.append( None )
                    self.H_list[-1] = hyper_tm
            else:
                self._regression_convergence.append( 0. )
            Mkm1 = self.F_list[-1] if hdim == 0 else self.F_list[-1].map_list[1]
            tar_pi = self.pi.get_MarkovComponent(
                self.nsteps-1, state_map=Mkm1, hyper_map=self.H_list[-1] )
            ref_rho = StandardNormalDistribution(tar_pi.dim)
            ddlm = self._learn_map(
                ref_rho, tar_pi, tm, solve_params,
                builder_extra_kwargs, builder_class,
                continue_on_error,
                mpi_pool=mpi_pool,
                **learn_map_extra_kwargs )
            self.R_list.append( ddlm['tm'] )
            self.M_list.append( ddlm['smooth_tm'] )
            # Update dimension of all lifted maps
            for L in self.L_list:
                L.dim_in = L.dim_out = self.pi.dim
            L = LiftedTransportMap( self.nsteps-1, self.M_list[-1], self.pi.dim, hdim)
            self.L_list.append(L)
            # Store next hyper map composition
            self.H_list.append(
                CompositeMap(
                    self.H_list[-1],
                    ddlm['hyper_tm']
                )
                if hdim > 0 else None )

        # Prepare the filtering maps
        H = self.H_list[-1]
        R = self.R_list[-1]
        Rkp1 = ddlm['filt_tm']
        if hdim > 0:
            F = TriangularListStackedTransportMap(
                map_list=[H, Rkp1],
                active_vars=[list(range(hdim)), list(range(hdim+sdim))]
            )
        else:
            F = Rkp1    
        self.F_list.append( F )

        # Monitor kl convergence
        if var_diag_convergence_params is not None:
            pull_tar = PullBackTransportMapDistribution(
                self.M_list[-1], tar_pi )
            var = variance_approx_kl(
                ref_rho, pull_tar,
                mpi_pool_tuple=(None, mpi_pool),
                **var_diag_convergence_params)
            self.logger.info("Variance diagnostic: %e" % var)
        else:
            var = None
        
        self._var_diag_convergence.append( var )

        for cmd in [ 'log_pdf', 'grad_x_log_pdf', 'tuple_grad_x_log_pdf',
                     'hess_x_log_pdf', 'action_hess_x_log_pdf' ]:
            if cmd in tar_pi.nevals:
                if self.nsteps == 0:
                    self._markov_component_nevals[cmd] = []
                self._markov_component_nevals[cmd].append(
                    tar_pi.nevals[cmd] )

    def trim(self, ntrim):
        r""" Trim the integrator to ``ntrim``
        """
        nback = self.nsteps - ntrim
        ns = TransportMapsSmoother(self.pi.pi_hyper)
        # Trim smoother lists
        ns.H_list = self.H_list[:ntrim-1]
        ns.R_list = self.R_list[:ntrim-1]
        ns.M_list = self.M_list[:ntrim-1]
        ns.L_list = self.L_list[:ntrim-1]
        for L in ns.L_list:
            L.dim = L.dim_in = L.dim_out = \
                    ntrim * self.pi.state_dim  + self.pi.hyper_dim
        ns.F_list = self.F_list[:ntrim]
        ns._var_diag_convergence = self.var_diag_convergence[:ntrim-1]
        ns._regression_convergence = self.regression_convergence[:ntrim-1]
        # Trim target distribution
        for pi, ll in zip(self.pi.prior.pi_list[:ntrim], self.pi.ll_list[:ntrim]):
            ns.pi.append(pi, ll)
        # Update nsteps
        ns._nsteps = ntrim
        return ns

class FilteringPreconditionedTransportMapsSmoother( TransportMapsSmoother ):
    def __init__(self, **kwargs):
        super(FilteringPreconditionedTransportMapsSmoother, self).__init__(**kwargs)
        self._precondition_regression_convergence = []

    @property
    def precondition_regression_convergence(self):
        return self._precondition_regression_convergence 

    def _learn_map(
            self,
            rho,
            pi,
            tm,
            solve_params,
            builder_extra_kwargs,
            builder_class,
            continue_on_error,
            mpi_pool=None,
            filt_prec_regression_builder=None,
            filt_prec_regression_tm=None,
            filt_prec_regression_params={},
            filt_prec_regression_convergence_params=None
    ):
        r""" Returns the transport map found and the preconditioning maps.

        This routines first precondition the target with the previous filtering map
        along the marginal regarding the next step.
        This means that the map to be found will be a perturbation of the identity
        representing the update of the previous filtering.
        To understand this one can think that, had the transition operator
        been the identity (and assuming no observation at this step),
        the identity map would be suitable.
        """
        if self.nsteps <= 0:
            dd = super(FilteringPreconditionedTransportMapsSmoother, self)._learn_map(
                rho, pi, tm, solve_params,
                builder_extra_kwargs, builder_class,
                continue_on_error,
                mpi_pool=mpi_pool)

        else:
            hdim = self.pi.hyper_dim
            sdim = self.pi.state_dim

            # Permute coordinates
            permtm = self._permuting_map(pi)
            tar_pi = PullBackTransportMapDistribution(permtm, pi)

            # Precondition prediction/assimilation step through latest filtering
            hyper_filt_prec = TriangularListStackedTransportMap(
                [ IdentityTransportMap( hdim ) ] if hdim > 0 else [] + \
                [ pi.state_map ],
                [ list(range(hdim)) ] if hdim > 0 else [] + \
                [ list(range(hdim+sdim)) ] )
            filt_prec = TriangularListStackedTransportMap(
                [ hyper_filt_prec,
                  IdentityTransportMap(sdim) ],
                [ list(range(hdim+sdim)),
                  list(range(hdim+sdim, hdim+2*sdim)) ] )
            tar_pi = PullBackTransportMapDistribution(
                filt_prec, tar_pi )
            
            # Regular preconditioning (optional rotations if active)
            ptm, hptm, fptm, map_factory_kwargs = self._preconditioning_map(
                tar_pi, mpi_pool=mpi_pool)
            if issubclass(type(tm), SequentialInferenceMapFactory):
                nn = 0 if self.nsteps == 0 else 1
                tm = tm.generate(nsteps=nn, **map_factory_kwargs)
            tar_pi = PullBackTransportMapDistribution(ptm, tar_pi)
            ref_rho = PushForwardTransportMapDistribution(
                InverseTransportMap(ptm), rho )    
            
            builder = builder_class(
                ref_rho, tar_pi, tm,
                solve_params, **builder_extra_kwargs)
            tm, log = builder.solve(mpi_pool=mpi_pool)
            if self._terminate_kl(log, continue_on_error):
                raise RuntimeError(log['msg'] + " Terminating.")

            # Regression
            if issubclass(type(filt_prec_regression_tm), SequentialInferenceMapFactory):
                hftm = filt_prec_regression_tm.generate(nsteps=0, sdim=sdim, hdim=hdim)
            if filt_prec_regression_builder is None:
                filt_prec_regression_builder = L2RegressionBuilder({})
            hfptm = TriangularListStackedTransportMap(
                ([ hptm ] if hdim>0 else []) + \
                [ fptm ],
                ([list(range(hdim))] if hdim>0 else []) + \
                [list(range(hdim,hdim+sdim))] )
            tar_tm = ListCompositeMap(
                [
                    hyper_filt_prec,
                    hfptm,
                    TriangularComponentwiseTransportMap(
                        tm.active_vars[:hdim+sdim],
                        tm.approx_list[:hdim+sdim]),
                    InverseTransportMap( hfptm )
                ]
            )
            hftm, log_reg = filt_prec_regression_builder.solve(
                hftm, tar_tm, **filt_prec_regression_params)
            if not log_reg[-1]['success']:
                if not continue_on_error:
                    msg = "Regression of filtering preconditioned map did not converge. " + \
                          "Terminating."
                    self.logger.error( msg )
                    raise RuntimeError( msg )
            else:
                self._precondition_regression_convergence.append(
                    L2_misfit( hftm, tar_tm, **filt_prec_regression_convergence_params ) )

            # Extract hyper-parameter map
            htm = None if hdim == 0 else \
                  TriangularComponentwiseTransportMap(
                      hftm.active_vars[:hdim],
                      hftm.approx_list[:hdim] )

            # Extract filtering map
            ftm = TriangularComponentwiseTransportMap(
                hftm.active_vars[hdim:hdim+sdim],
                hftm.approx_list[hdim:hdim+sdim] )

            # Assemble transport map
            stm = ListCompositeMap(
                [
                    permtm,
                    filt_prec,
                    ptm,
                    tm,
                    InverseTransportMap( ptm ),
                    InverseTransportMap( permtm )
                ]
            )

            dd = {
                'tm': tm,
                'hyper_tm': htm,
                'filt_tm': ftm,
                'smooth_tm': stm
            }
                
        return dd
        
class LowRankTransportMapsSmoother(TransportMapsSmoother):
    r""" Perform the on-line assimilation of a sequential Hidded Markov chain using low-rank information to precondition each assimilation problem.

    At each assimilation/prediction step computes the matrix

    .. math::

       H_x = \frac{1}{m-1} \sum_{k=1}^m \nabla_x \log \pi^i(z_i^{(k)},z_{i+1}^{(k)}) \otimes \nabla_x \log \pi^i(z_i^{(k)},z_{i+1}^{(k)})

    and extracts the rank-:math:`r` sub-spaces of
    :math:`H_{z_i}` and :math:`H_{z_{i+1}}`
    such that

    .. math::

       \sum_{i=0}^r \lambda_i > \alpha \sum_{i=0}^d \lambda_i \;.

    These are used to precondition the problem through non-symmetric square roots.

    Args:
      m (int): number of samples to be used in the estimation of :math:`H` (must be provided)
      alpha (float): truncation parameter :math:`\alpha` (default: 0.9)
      max_rank (int): maximum rank allowed (defalut: :math:`\infty`)

    Optional Kwargs:
      pi_hyper (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        prior distribution on the hyper-parameters :math:`\pi(\Theta)`
    """
    def __init__(self, **kwargs):
        self._lr_m = kwargs.pop('m', None)
        self._lr_alpha = kwargs.pop('alpha', 0.9)
        self._lr_max_rank = kwargs.pop('max_rank', float('inf'))
        if self._lr_m is None:
            raise ValueError("Parameter m must be provided.")
        super(LowRankTransportMapsSmoother, self).__init__(**kwargs)

    def _compute_sqrt(self, H):
        u, s, v = npla.svd(H)
        cmsm = np.cumsum(s)
        lim = self._lr_alpha * cmsm[-1]
        r = next( (i+1 for i in range(len(cmsm)) if cmsm[i] > lim),
                  len(s) )
        U = u * np.sqrt(s)[np.newaxis,:]
        Uinv = (u / np.sqrt(s)[np.newaxis,:]).T
        # U = np.dot(u * np.sqrt(s)[np.newaxis,:], u.T)
        # Uinv = np.dot(u / np.sqrt(s)[np.newaxis,:], u.T)
        # U = u
        # Uinv = u.T
        return U, Uinv, u, r

    def _preconditioning_map(self, pi, mpi_pool=None):
            
        # ptm, hptm, fptm, map_factory_kwargs = \
        #     super(LowRankTransportMapsSmoother,
        #           self)._preconditioning_map(pi)
        map_factory_kwargs = {}

        hdim = self.pi.hyper_dim
        sdim = self.pi.state_dim

        rlst = []

        # # Find Laplape approximation of pi to sample from
        # lap = laplace_approximation(pi, ders=1)
        # x = lap.rvs(self._lr_m)

        # Estimate H
        rho = StandardNormalDistribution(pi.dim)
        x = rho.rvs(self._lr_m)
        if self.nsteps > 1 and not isinstance(pi, PullBackTransportMapDistribution):
            # Better guess of where the bulk of pi is...
            x[:,hdim+sdim:] = pi.state_map.evaluate(x[:,hdim+sdim:])
        scatter_tuple = (['x'], [x])
        gxlpdf = mpi_map(
            'grad_x_log_pdf', obj=pi, scatter_tuple=scatter_tuple,
            mpi_pool=mpi_pool )
        gxlpdf -= rho.grad_x_log_pdf(x)
        H = np.dot( gxlpdf.T, gxlpdf ) / (self._lr_m-1)

        # Linear term
        L = np.zeros( (pi.dim, pi.dim) )
        Linv = np.zeros( (pi.dim, pi.dim) )

        # Compute square root hyper-parameters
        if hdim > 0:
            raise NotImplementedError(
                "Map factory is not coded to account for this case")
            LH, LHinv, rht = self._compute_sqrt(H[:hdim,:hdim])
            L[:hdim,:hdim] = LH
            Linv[:hdim,:hdim] = LHinv
            # hptm = CompositeMap(
            #     LinearTransportMap(np.zeros(hdim), LH, Linv=LHinv),
            #     hptm )
            hptm = LinearTransportMap(np.zeros(hdim), LH, Linv=LHinv)
            rh = min(rh, self._lr_max_rank)
            print("Rank hp: %d (%d) - " % (rh, rht), end="")
            rlst.append(rh)
        else:
            hptm = None
            
        # Compute square root first component (Z_i+1 if nsteps > 0)
        L1, L1inv, u1, r1t = self._compute_sqrt( H[hdim:hdim+sdim,hdim:hdim+sdim] )
        r1 = min(r1t, self._lr_max_rank)
        print("Rank 1: %d (%d) - " % (r1,r1t), end="")

        r2 = None
        if self.nsteps > 0: # Square root second component
            L2, L2inv, u2, r2t = self._compute_sqrt( H[hdim+sdim:,hdim+sdim:] )
            r2 = min(r2t, self._lr_max_rank)
            print("Rank 2: %d (%d) - " % (r2,r2t), end="")

            # Measure overlap (or that smaller space is contained in larger one)
            if r1 <= r2:
                umin = u1[:,:r1]
                umax = u2[:,:r2]
            else:
                umin = u2[:,:r2]
                umax = u1[:,:r1]
            # Project smaller space into bigger one
            umint = np.dot(umax, np.dot(umax.T, umin))
            umint = umint / npla.norm(umint, axis=0)[np.newaxis,:]    
            # Overlap
            ovlap = np.abs(npla.det(np.dot(umint.T, umin)))
            print("Overlap: %.2f - " % ovlap, end="")
            
            # # Merge the relenvant subspaces
            # Lm = np.hstack((u1[:,:r1], u2[:,:r2]))
            # Q, R = npla.qr(Lm)
            # NLL = np.eye(sdim) - np.dot(Q, Q.T)
            # B, s, v = npla.svd(NLL)
            # Qnll = B[:,:-(r1+r2)]
            # L1 = L2 = np.hstack((Q, Qnll))
            # L1inv =  L2inv = L1.T
            # r1 = r2 = r1+r2

        rlst.append(r1)
        if self.nsteps > 0:
            rlst.append(r2)
            
        L[hdim:hdim+sdim,hdim:hdim+sdim] = L1
        Linv[hdim:hdim+sdim,hdim:hdim+sdim] = L1inv
        fptm = CompositeMap(
            LinearTransportMap(np.zeros(sdim), L1, Linv=L1inv),
            fptm )
        
        if self.nsteps > 0:
            L[hdim+sdim:,hdim+sdim:] = L2
            Linv[hdim+sdim:,hdim+sdim:] = L2inv
            
        # Build the affine map
        P = LinearTransportMap(np.zeros(pi.dim), L, Linv=Linv)

        # Build the preconditioning map
        # ptm = CompositeMap(P, ptm)
        ptm = P

        map_factory_kwargs['sdim'] = sdim
        map_factory_kwargs['rlst'] = rlst

        return ptm, hptm, fptm, map_factory_kwargs


class LowRankFilteringPreconditionedTransportMapSmoother(
        FilteringPreconditionedTransportMapsSmoother, LowRankTransportMapsSmoother):
    pass
    
