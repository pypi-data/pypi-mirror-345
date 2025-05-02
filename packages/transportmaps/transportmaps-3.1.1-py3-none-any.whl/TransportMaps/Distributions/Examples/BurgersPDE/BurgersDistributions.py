#!/usr/bin/env python

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
# Author: Transport Map Team
# Website: transportmaps.mit.edu
# Support: transportmaps.mit.edu/qa/
#

import numpy as np
import numpy.linalg as npla
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF

from ....External import DOLFIN_SUPPORT
from ....Misc import counted
from .... import Distributions as DIST
from ....Distributions import Inference as DISTINF
from .... import Likelihoods as LKL
from .... import Maps

__all__ = [
    "ViscosityInitialConditionsBurgersPosteriorDistribution"
]

class ViscosityInitialConditionsBurgersPosteriorDistribution(
        DISTINF.BayesPosteriorDistribution
):
    def __init__(
            self,
            # Physics
            solver,
            # Prior settings
            u0_length_scale = 1.,
            nu_mean = -3,
            nu_std  = 3,
            # Likelihood setting
            obs_sigma = 1e-2,
            # Observations (must be defined on the FunctionSpace of the solver)
            obs = None
    ):
        
        if not DOLFIN_SUPPORT:
            raise ImportError("Please install FENICS (dolfin) in order to use this class")

        self.solver = solver
        self.u0_length_scale = u0_length_scale
        self.nu_mean = nu_mean
        self.nu_std = nu_std
        self.obs_sigma = obs_sigma
        self.obs = obs

        # List of attributes to be excluded in get/set params
        self.exclude_state_param_list = set()

        ###################
        # Building priors 
        # The prior will be built as the push-forward of a
        # Standard normal through maps delivering the right
        # marginals. We'll do it this way so that it will be
        # easy to whiten the prior.
        
        # Build the prior for the viscosity:
        # log \nu \sim N(\mu_\nu, \sigma_\nu)
        L = Maps.FrozenLinearDiagonalTransportMap([nu_mean], [nu_std])
        E = Maps.FrozenExponentialDiagonalTransportMap(1)
        nu_map = Maps.CompositeTransportMap(E, L)
        # prior_nu = DIST.PushForwardTransportMapDistribution(
        #     nu_map,
        #     DIST.StandardNormalDistribution(1)
        # )
        
        # Build the GP prior for the initial conditions
        # To this end fit a GP with RBF covariance to the Boundary
        # conditions of the problem, then extract its mean and covariance
        # at the coordinates of the discretization.
        # The prior is defined for the interior of the interval,
        # as on the boundaries the values are fixed.
        a = (solver.ul * solver.xr - solver.ur * solver.xl) / (solver.xr - solver.xl)
        b = (solver.ur - solver.ul) / (solver.xr - solver.xl)
        gpr = GaussianProcessRegressor(
            # kernel = Matern(nu=self.u0_matern_smoothness)
            kernel = RBF(length_scale=1.)
        )
        gpr.fit( np.array([[solver.xl],[solver.xr]]), np.array([0.,0.]) )
        _, cov = gpr.predict( solver.coord.reshape((solver.ndofs, 1)), return_cov=True )
        mean = a + b * solver.coord
        self.mean_boundaries = [mean[0], mean[-1]]
        mean = mean[1:-1]
        cov = cov[1:-1,1:-1]
        u, s, v = npla.svd(cov)
        if not np.allclose(np.dot(v.T * s, v), cov, rtol=1e-8, atol=1e-8):
            raise ValueError("Covariance matrix is not symmetric positive definite")
        u0_map = Maps.AffineTransportMap(c=mean, L=np.dot(v.T * np.sqrt(s), v))
        # prior_u0 = DIST.PushForwardTransportMapDistribution(
        #     u0_map, DIST.StandardNormalDistribution(solver.ndofs-2))
        
        # Assemble the prior map (keep it around for whitening)
        self.prior_map = Maps.TriangularListStackedTransportMap(
            map_list = [nu_map, u0_map],
            active_vars = [[0], list(range(1,solver.ndofs-1))]
        )

        prior = DIST.PushForwardTransportMapDistribution(
            self.prior_map,
            DIST.StandardNormalDistribution(solver.ndofs-1)
        )
        
        # # Assemble the prior distribution as a factorized one (nu,u0)
        # prior = DIST.FactorizedDistribution([
        #     (prior_nu, [0], []),
        #     (prior_u0, list(range(1,solver.ndofs-1)), [])
        # ])

        # Define the log-likelihood
        lkl = ViscosityInitialConditionsBurgersLogLikelihood(
            solver = solver,
            bvs = self.mean_boundaries,
            obs = obs,
            obs_sigma = obs_sigma
        )

        # Call super
        super(ViscosityInitialConditionsBurgersPosteriorDistribution, self).__init__(lkl, prior)

class ViscosityInitialConditionsBurgersMismatchMap(Maps.Map):
    def __init__(self, solver, bvs):
        self.solver = solver
        self.bvs = bvs
        super(ViscosityInitialConditionsBurgersMismatchMap, self).__init__(
            dim_in=solver.ndofs-1, dim_out=1)

    @counted
    def evaluate(self, x, *args, **kwargs):
        r"""        
        Args:
          x (array): the first column contains samples for :math:`\nu`,
            while the remaining columns contain values of the field :math:`u_0`.
        """
        f = np.zeros((x.shape[0],1))
        u0 = np.zeros(self.solver.ndofs)
        u0[0] = self.bvs[0]
        u0[-1] = self.bvs[1]
        for i in range(x.shape[0]):
            nu = x[i,0]
            u0[1:-1] = x[i,1:]
            f[i,0] = self.solver.evaluate(nu, u0)
        return f
        
    @counted
    def grad_x(self, x, *args, **kwargs):
        u0 = np.zeros(self.solver.ndofs)
        u0[0] = self.bvs[0]
        u0[-1] = self.bvs[1]
        gx = np.zeros((x.shape[0],1,x.shape[1]))
        for i in range(x.shape[0]):
            nu = x[i,0]
            u0[1:-1] = x[i,1:]
            dJdnu, dJdu = self.solver.grad_x(nu, u0)
            gx[i,0,0] = dJdnu
            gx[i,0,1:] = dJdu[1:-1]
        return gx
        
    @counted
    def tuple_grad_x(self, x, *args, **kwargs):
        u0 = np.zeros(self.solver.ndofs)
        u0[0] = self.bvs[0]
        u0[-1] = self.bvs[1]
        f = np.zeros((x.shape[0],1))
        gx = np.zeros((x.shape[0],1,x.shape[1]))
        for i in range(x.shape[0]):
            nu = x[i,0]
            u0[1:-1] = x[i,1:]
            J, dJdnu, dJdu = self.solver.tuple_grad_x(nu, u0)
            f[i,0] = J
            gx[i,0,0] = dJdnu
            gx[i,0,1:] = dJdu[1:-1]
        return f, gx

class ViscosityInitialConditionsBurgersLogLikelihood( LKL.LogLikelihood ):
    r"""
    Given the ``solver`` :math:`J:(u_0,\nu) \mapsto \int_a^b (u(x,T) - u_d)^2 dx`,
    where the mapping :math:`F:(u_0,\nu) \mapsto u(x,T)` is defined by the solution
    of the Burger's equation

    .. math::
    
       \begin{cases}
       \partial_t u(x,t) = \nu \partial_{xx} u - u \partial_x u & x \in [x_l, x_r] \\
       u(x,0) = u_0(x) & \\
       u(x_l,t) = u_l \quad u(x_r,t) = u_r &
       \end{cases} \;,

    the observation :math:`u_d := F_h(\hat{u}_0,\hat{\nu})` (where :math:`F_h` is the 
    data generating model for the coefficients :math:`\hat{u}_0,\hat{\nu}`) and 
    the observation noise :math:`sigma`, assembles the likelihood

    .. math::
    
       \mathcal{L}_{u_d}(u_0,\nu) := - \frac{1}{2\sigma^2} J(u_0,\nu)
    """
    def __init__(self, solver, bvs, obs, obs_sigma):
        r"""
        Args:
          solver (FinalL2MismatchBurgersProblem): solver providing function evaluation
            and function/gradient evaluation
          bvs (list): values to be appended to the boundaries of the initial conditions
          obs (:class:`ndarray<numpy.ndarray>`): coefficients representing the final condition
            in the :class:`FunctionSpace<dolfin.FunctionSpace>` used in the solver
          obs_sigma (float): observation noise :math:`\sigma`
        """
        if not DOLFIN_SUPPORT:
            raise ImportError("Please install FENICS (dolfin) in order to use this class")
        self.mismatch_map = ViscosityInitialConditionsBurgersMismatchMap(
            solver, bvs
        )
        self.T = self.mismatch_map
        self.obs_sigma = obs_sigma    
        super(ViscosityInitialConditionsBurgersLogLikelihood, self).__init__(obs, solver.ndofs-1)

    def _get_y(self):
        return super(ViscosityInitialConditionsBurgersLogLikelihood, self)._get_y()
        
    def _set_y(self, y):
        super(ViscosityInitialConditionsBurgersLogLikelihood, self)._set_y(y)
        self.set_up()

    y = property(_get_y, _set_y)

    def set_up(self):
        self.mismatch_map.solver.ud = self.y

    def __setstate__(self, state):
        super(ViscosityInitialConditionsBurgersLogLikelihood, self).__setstate__(state)
        self.set_up()

    @counted
    def evaluate(self, x, *args, **kwargs):
        r"""        
        Args:
          x (array): the first column contains samples for :math:`\nu`,
            while the remaining columns contain values of the field :math:`u_0`.
        """
        f = self.T.evaluate(x, *args, **kwargs)
        return - .5 * f[:,0] / self.obs_sigma**2

    @counted
    def grad_x(self, x, *args, **kwargs):
        s = self.obs_sigma
        gx = self.T.grad_x(x, *args, **kwargs)
        return - .5 * gx[:,0,:] / s**2

    @counted
    def tuple_grad_x(self, x, *args, **kwargs):
        s = self.obs_sigma
        f, gx = self.T.tuple_grad_x(x, *args, **kwargs)
        return - .5 * f[:,0] / s**2, - .5 * gx[:,0,:] / s**2
