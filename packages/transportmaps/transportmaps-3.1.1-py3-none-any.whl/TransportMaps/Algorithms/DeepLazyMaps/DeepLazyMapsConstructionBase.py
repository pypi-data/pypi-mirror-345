import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

import numpy as np
import numpy.random as npr
import numpy.linalg as npla

from ...ObjectBase import TMO
from ...MPI import mpi_map
from ...Misc import cmdinput, state_loader, counted
from ...Maps import AffineTransportMap, CompositeTransportMap, IdentityEmbeddedTransportMap
from ... import Distributions as DIST
from ... import Diagnostics as DIAG

__all__ = [
    'DeepLazyMapsAssembler',
]

nax = np.newaxis
        
class DeepLazyMapsAssembler(TMO):
    def __init__(
            self,
            # Builder of transport maps for each step
            builder,
            # Factory for the maps
            map_factory,
            # Overall convergence criterion
            eps,
            maxit     = 20,
            # Random rotations
            random_rotations       = False,
            random_rotations_step  = 1,
            # Low-rank approximation paramters
            rank_max     = 3,
            rank_eps     = 1e-2,
            rank_qtype   = 0,
            rank_qparams = 20,
            # Hard truncation (pi^\star algorithm)
            hard_truncation = False,
            ht_qtype = 0,
            ht_qparams = 100,
            # Variance diagnostic parameters
            var_diag_qtype   = 0,
            var_diag_qparams = 100,
            # Callback functions for, e.g., storing
            callback=None,
            callback_kwargs={},
    ):
        super().__init__()
        
        self.builder               = builder
        self.map_factory           = map_factory
        self.eps                   = eps
        self.maxit                 = maxit
        self.random_rotations      = random_rotations
        self.random_rotations_step = random_rotations_step
        self.rank_max              = rank_max
        self.rank_eps              = rank_eps
        self.rank_qtype            = rank_qtype
        self.rank_qparams          = rank_qparams
        self.hard_truncation       = hard_truncation
        self.ht_qtype              = ht_qtype
        self.ht_qparams            = ht_qparams
        self.var_diag_qtype        = var_diag_qtype
        self.var_diag_qparams      = var_diag_qparams
        self.callback              = callback
        self.callback_kwargs       = callback_kwargs

    #@staticmethod
    def _compute_subspace(
            self,
            x, w, rho, pi, eps, max_rank,
            step, mpi_pool=None, plotting=False
    ):
        gx = mpi_map(
            'grad_x_log_pdf',
            scatter_tuple = (['x'], [x]),
            obj = pi,
            mpi_pool=mpi_pool )
        gx -= rho.grad_x_log_pdf(x)
        H = np.dot( gx.T, w[:,nax] * gx )
        val, vec = npla.eigh( H )
        val = val[::-1]
        vec = vec[:,::-1]
        self.logger.info("Step %d - Power: %e" % (step, np.sum(val)))
        if isinstance(eps, float):
            cum_err = 0.
            for i in range(len(val)-1,-1,-1):
                cum_err += val[i]
                if cum_err > eps:
                    break
            trunc_i = min(i+1, max_rank)
        elif eps == 'manual':
            # Plot the normalized cumulative spectrum
            cum_spect = np.cumsum( val )
            cum_spect /= cum_spect[-1]
            self.logger.info(
                "Step %d - " % step + \
                "Missing normalized cumulative spectrum (1-c): " + \
                ", ".join( "%.2e" % (1.-c) for c in cum_spect[:max_rank] )
            )
            if plotting:
                fig = plt.figure()
                plt.plot( cum_spect[:max_rank], '-o' )
                plt.ylim([-0.1, 1.1])
                plt.grid(True)
                plt.show(False)
            trunc_i = None
            while not isinstance(trunc_i, int):
                instr = cmdinput(
                    "Step %d - " % step + \
                    "Select the truncation threshold [>0]: "
                )
                try:
                    trunc_i = int(instr)
                    if trunc_i < 1: trunc_i = None
                except ValueError:
                    pass
        U = vec[:,:trunc_i]
        Up = vec[:,trunc_i:]
        return U, Up, val

    #@staticmethod
    def _compute_subspace_overlap(self, u1, u2, step):
        umin = u1 if u1.shape[1] <= u2.shape[1] else u2
        umax = u2 if u1.shape[1] <= u2.shape[1] else u1
        # Project smaller space into bigger one
        umint = np.dot(umax, np.dot(umax.T, umin))
        umint = umint / npla.norm(umint, axis=0)[np.newaxis,:]    
        # Overlap
        ovlap = np.abs(npla.det(np.dot(umint.T, umin)))
        self.logger.info(
            "Step %d - " % step + \
            "Overlap of active subspaces: %.2f - " % ovlap
        )

    @state_loader(
        keys = [
            'target_distribution',
            'builder_solve_params'
        ]
    )
    def assemble(
            self,
            target_distribution=None,
            builder_solve_params=None,
            # Reloading state
            state=None,
            # Parallelization
            mpi_pool=None,
            # Whether to plot along the way
            plotting=False
    ):
        r"""    
        Args
          target_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            distribution :math:`\nu_\pi`
          builder_solve_params (:class:`dict`): parameters to be passed to the builder
          state (:class:`TransportMaps.DataStorageObject`): 
            if provided, it must contain all the information needed for reloading,
            or a handle to an empty storage object which can be externally stored.
            If ``state`` contains the keys corresponding to arguments to this function, 
            they will be used instead of the input themselves.
      
        Returns:
          (:class:`TransportMaps.Maps.TransportMap`) -- the transport map fitted.
        """

        # Internal states
        state.iter_counter   = getattr(state, 'iter_counter', 0)
        state.var_diag_list  = getattr(state, 'var_diag_list', [])
        state.power_list     = getattr(state, 'power_list', [])
        state.eig_val_list   = getattr(state, 'eig_val_list', [])
        state.pull_pi        = getattr(state, 'pull_pi', state.target_distribution)
        state.active_subspace_list = getattr(state, 'active_subspace_list', [])

        rho = DIST.StandardNormalDistribution( state.pull_pi.dim )

        var_diag = DIAG.variance_approx_kl(
            rho,
            state.pull_pi,
            qtype=self.var_diag_qtype,
            qparams=self.var_diag_qparams,
            mpi_pool_tuple=(None,mpi_pool) )
        if len(state.var_diag_list) == 0: # Only if not reloading
            state.var_diag_list.append( var_diag )
        self.logger.info(
            "Step %d " % state.iter_counter + \
            "- Variance diagnostic: %e" % var_diag )

        if plotting:
            fig_var_diag = plt.figure()
            ax_var_diag = fig_var_diag.add_subplot(111)
            handle_power, = ax_var_diag.semilogy(
                [.5 * p for p in state.power_list],
                'o-k', label=r'$\frac{1}{2}\operatorname{Tr}(H_\ell)$')
            handle_var_diag, = ax_var_diag.semilogy(
                state.var_diag_list, 'v-r', label=r'$\frac{1}{2}V[\log \rho/T^\sharp\pi]$')
            ax_var_diag.xaxis.set_major_locator(MaxNLocator(integer=True))
            ax_var_diag.grid()
            ax_var_diag.legend()
            plt.xlabel(r"Lazy iteration $\ell$")
            plt.show(False)
            plt.pause(0.1)

            def update_fig_var_diag(
                    ax_var_diag,
                    handle_var_diag, handle_power,
                    var_diag_list, power_list):
                handle_var_diag.set_xdata(np.arange(len(var_diag_list)))
                handle_var_diag.set_ydata(np.asarray(var_diag_list))
                handle_power.set_xdata(np.arange(len(power_list)))
                handle_power.set_ydata(np.asarray([.5*p for p in power_list]))
                ax_var_diag.set_xlim([-1, len(var_diag_list)])
                ax_var_diag.set_ylim([
                    min(np.min(var_diag_list), np.min(power_list)),
                    max(np.min(var_diag_list), np.max(power_list))
                ])

        if self.random_rotations:
            rand_rot_counter = 0
                
        while var_diag > self.eps and state.iter_counter < self.maxit:
            
            x, w = rho.quadrature(
                qtype   = self.rank_qtype,
                qparams = self.rank_qparams )

            if self.random_rotations:
                rand_rot_counter += 1
                
            if self.random_rotations and rand_rot_counter == self.random_rotations_step:
                # Compute random rotation
                rand_rot_counter = 0
                A = npr.randn(rho.dim**2).reshape((rho.dim,rho.dim))
                UUp,_ = npla.qr(A)
                U = UUp[:,:self.rank_max]
                Up = UUp[:,self.rank_max:]
                val = np.ones(rho.dim)/float(rho.dim)
            else:
                # Compute active and inactive subspaces
                U, Up, val = DeepLazyMapsAssembler._compute_subspace(
                    x, w,
                    rho,
                    state.pull_pi,
                    self.rank_eps,
                    self.rank_max,
                    state.iter_counter,
                    mpi_pool=mpi_pool,
                    plotting=plotting
                )
                
            if state.iter_counter > 0:
                self._compute_subspace_overlap(
                    U, state.active_subspace_list[-1],
                    state.iter_counter
                )
            state.active_subspace_list.append( U )
            dim_k = U.shape[1]
            power = np.sum(val)
            state.power_list.append( power )
            state.eig_val_list.append(val)
            self.logger.info(
                "Step %d - Truncation rank: %d" % (state.iter_counter, dim_k))
            
            if plotting:
                # Plot eigen values
                if 'fig_eig_vals' in locals():
                    new_fig = False
                else:
                    new_fig = True
                    fig_eig_vals = plt.figure()
                    ax_eig_vals = fig_eig_vals.add_subplot(111)
                    plt.title("Decay of eigenvalues")
                    plt.grid(True)
                ax_eig_vals.semilogy(val[:self.rank_max], 'o-')#, label='step %d' % i)
                ax_eig_vals.xaxis.set_major_locator(MaxNLocator(integer=True))
                if new_fig:
                    plt.show(False)

                # Update convergence plot
                update_fig_var_diag(
                    ax_var_diag,
                    handle_var_diag, handle_power,
                    state.var_diag_list, state.power_list)

                plt.draw()
                plt.pause(0.1)

            # Define the rotation map U|U_\perp
            UUp = np.hstack((U, Up))
            UUp_map = AffineTransportMap(
                c=np.zeros(state.pull_pi.dim),
                L=UUp
            )

            if self.hard_truncation:
                # Define low-dimensional target
                pi_star_k = LowDimensionalTargetDistribution(
                    state.pull_pi, UUp_map, dim_k,
                    qtype=self.ht_qtype,
                    qparams=self.ht_qparams
                )

                # Prepare low-dimensional map and reference
                tau = self.map_factory.generate(dim_k)
                self.logger.info("Step %d - Number of map coefficients: %d" % (
                    state.iter_counter, tau.n_coeffs))
                rho_k = DIST.StandardNormalDistribution( dim_k )
                if state.builder_solve_params['qtype'] == 3:
                    state.builder_solve_params['qparams'] = \
                        [ state.builder_solve_params['qparams'][0] ] * dim_k

                # Fit map tau
                state.builder_solve_params.pop('x', None)
                state.builder_solve_params.pop('w', None)
                state.builder_solve_params.pop('x0', None)
                _, log = self.builder.solve(
                    tau,
                    rho_k,
                    pi_star_k,
                    state.builder_solve_params,
                    mpi_pool=mpi_pool )
                
                # Compute star_k variance diagnostic
                pull_tau_pi_star_k = DIST.PullBackTransportMapDistribution(
                    tau, pi_star_k)
                var_diag_star_k = DIAG.variance_approx_kl(
                    rho_k, pull_tau_pi_star_k,
                    qtype=state.builder_solve_params['qtype'],
                    qparams=state.builder_solve_params['qparams'],
                    mpi_pool_tuple=(None,mpi_pool))
                # var_diag_list_star_k.append( var_diag_star_k )
                self.logger.info(
                    "Step %d - " % state.iter_counter + \
                    "Variance diagnostic low-dimensional sub-problem: %e" % var_diag_star_k)

                # Embed tau in an identity map
                tm_lazy = IdentityEmbeddedTransportMap(
                    tm=tau, idxs=list(range(dim_k)), dim=state.pull_pi.dim )

            else:
                # Define pullback target
                pi_star_k = DIST.PullBackTransportMapDistribution(UUp_map, state.pull_pi)

                # Construct nearly linear map tau_emb
                tm_lazy = self.map_factory.generate(
                    state.pull_pi.dim, dim_k )

                self.logger.info(
                    "Step %d - " % state.iter_counter + \
                    "Number of map coefficients: %d" % tm_lazy.n_coeffs )

                # Fit map T
                state.builder_solve_params.pop('x0', None)
                _, log = self.builder.solve(
                    tm_lazy,
                    rho,
                    pi_star_k,
                    state.builder_solve_params,
                    mpi_pool=mpi_pool )

            if not log['success']:
                print(
                    "WARNING: The minimization algorithm failed. " + \
                    "In some situations, e.g. if maximum number of iterations have " + \
                    "been exceeded, some progress have been done " + \
                    "and one could try to continue."
                )
                instr = None
                while instr not in ['c','q']:
                    instr = cmdinput(
                        "Select whether to [c]ontinue or [q]uit: ")
                if instr == 'q':
                    self.logger.info("Algorithm manually terminated.")
                    return state.deep_lazy_map, var_diag
                
            
            # Compose U|U_\perp with tau_emb
            Ti = CompositeTransportMap(UUp_map, tm_lazy)

            # Update pull_pi and T
            state.pull_pi = DIST.PullBackTransportMapDistribution(
                Ti, state.pull_pi)
            if state.iter_counter == 0:
                state.deep_lazy_map = Ti
            else:
                state.deep_lazy_map = CompositeTransportMap(
                    state.deep_lazy_map, Ti)

            # Compute variance diagnostic
            var_diag = DIAG.variance_approx_kl(
                rho,
                state.pull_pi,
                qtype=self.var_diag_qtype,
                qparams=self.var_diag_qparams,
                mpi_pool_tuple=(None,mpi_pool) )
            state.var_diag_list.append( var_diag )
            self.logger.info(
                "Step %d - " % state.iter_counter + \
                "Variance diagnostic: %e" % var_diag )

            if plotting:
                # DIAG.plotAlignedConditionals(
                #     pull_pi, do_diag=False,
                #     range_vec=[[-5,5]]*pi.dim,
                #     title='Aligned conditonals - step %d' % i)

                # DIAG.plotRandomConditionals(
                #     pull_pi, title='Random conditonals - step %d' % i)

                update_fig_var_diag(
                    ax_var_diag,
                    handle_var_diag, handle_power,
                    state.var_diag_list, state.power_list)

                plt.draw()
                plt.pause(0.1)

            state.iter_counter += 1
                
            if self.callback is not None:
                self.logger.info("Calling callback function...")
                self.callback( state.deep_lazy_map, **self.callback_kwargs )
                
            instr = None
            while instr not in ['c','q']:
                instr = cmdinput(
                    "Select whether to [c]ontinue or [q]uit: ")
            if instr == 'q':
                self.logger.info("Algorithm manually terminated.")
                return state.deep_lazy_map, var_diag

        return state.deep_lazy_map, var_diag


class LowDimensionalTargetDistribution(DIST.PullBackTransportMapDistribution):
    def __init__(self, pi, UUp_map, dim_k, qtype=0, qparams=0):
        super(LowDimensionalTargetDistribution, self).__init__(UUp_map, pi)
        # The dimension of the low-dimensional distribution
        self.dim = dim_k
        # The sample used for averaging the conditional expectation
        if self.dim < pi.dim:
            self.pi_null = DIST.StandardNormalDistribution( pi.dim - dim_k )
            self.qtype = qtype
            self.qparams = qparams
            if self.qparams == 0:
                self.x_null = np.zeros((1, pi.dim - dim_k))
                self.w_null = np.array([1.])
            else:
                self.x_null, self.w_null = self.pi_null.quadrature(
                    qtype=self.qtype, qparams=self.qparams)
        else:
            self.x_null = np.zeros((1,0))
            self.w_null = np.array([1.])
        self.m = self.x_null.shape[0]

    @counted
    def log_pdf(self, x, params=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim:
            raise ValueError("Dimension mismatch.")
        # avg_pts_cache = TM.get_sub_cache(cache, ('avg_pts', self.m))
        out = np.zeros(x.shape[0])
        for i in range(self.m):
            x_null = self.x_null[[i],:]
            w_null = self.w_null[i]
            xin = np.hstack( (x, np.tile( x_null,(x.shape[0],1)) ) )
            out += w_null * \
                   super(LowDimensionalTargetDistribution,self).log_pdf(
                       xin, params=params, idxs_slice=idxs_slice# ,
                       # cache=avg_pts_cache[i]
                   )
        return out

    @counted
    def grad_x_log_pdf(self, x, params=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim:
            raise ValueError("Dimension mismatch.")
        # avg_pts_cache = TM.get_sub_cache(cache, ('avg_pts', self.m))
        out = np.zeros( (x.shape[0], self.dim) )
        for i in range(self.m):
            x_null = self.x_null[[i],:]
            w_null = self.w_null[i]
            xin = np.hstack( (x, np.tile( x_null,(x.shape[0],1)) ) )
            out += w_null * \
                   super(LowDimensionalTargetDistribution,self).grad_x_log_pdf(
                       xin, params=params, idxs_slice=idxs_slice,
                       # cache=avg_pts_cache[i]
                   )[:,:self.dim]
        return out

    @counted
    def tuple_grad_x_log_pdf(self, x, params=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim:
            raise ValueError("Dimension mismatch.")
        lpdf = np.zeros( x.shape[0] )
        gxlpdf = np.zeros( (x.shape[0], self.dim) )    
        for i in range(self.m):
            x_null = self.x_null[[i],:]
            w_null = self.w_null[i]
            xin = np.hstack( (x, np.tile( x_null,(x.shape[0],1)) ) )
            tmp_lpdf, tmp_gxlpdf = super(LowDimensionalTargetDistribution,self).tuple_grad_x_log_pdf(
                xin, params=params, idxs_slice=idxs_slice)
            lpdf += w_null * tmp_lpdf
            gxlpdf += w_null * tmp_gxlpdf[:,:self.dim]
        return lpdf, gxlpdf
