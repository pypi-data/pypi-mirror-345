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
import numpy.random as npr
from scipy.spatial.distance import pdist, squareform

from .... import Maps
from ....External import DOLFIN_SUPPORT
from .... import Distributions as DIST
from ....Distributions import Inference as DISTINF
from .... import Likelihoods as LKL
from ....Misc import counted, cached, get_sub_cache

if DOLFIN_SUPPORT:
    import dolfin as dol
    # import dolfin_adjoint as doladj
    if dol.__version__ == '2017.2.0':
        import mpi4py.MPI as MPI
        from petsc4py import PETSc
    dol.set_log_level(30)


__all__ = [
    'Covariance',
    'OrnsteinUhlenbeckCovariance',
    'SquaredExponentialCovariance',
    'IdentityCovariance',
    'GaussianFieldPoissonDistribution',
    'GaussianFieldIndependentLikelihoodPoissonDistribution'
]           

nax = np.newaxis

class Covariance(object):
    def __call__(self, coord):
        dists = squareform( pdist(coord) )
        return self._evaluate( dists )
    def _evaluate(self, dists):
        raise NotImplementedError("To be implemented in subclasses")

class OrnsteinUhlenbeckCovariance(Covariance):
    def __init__(self, var, l):
        self.var = var
        self.l = l
    def _evaluate(self, dists):
        return self.var * np.exp( - dists / self.l )

class SquaredExponentialCovariance(Covariance):
    def __init__(self, var, l):
        self.var = var
        self.l = l
    def _evaluate(self, dists):
        d0 = np.isclose(dists, 0.)
        dn0 = np.logical_not(d0)
        d0 = np.where(d0)
        dn0 = np.where(dn0)
        out = np.zeros(dists.shape)
        out[d0] = self.var + 1e-13
        out[dn0] = self.var * np.exp( - dists[dn0]**2 / self.l**2 / 2 )
        return out

class IdentityCovariance(Covariance):
    def __init__(self, var):
        self.var = var
    def _evaluate(self, dists):
        return self.var * np.eye( len(dists) )
    
class GaussianFieldPoissonDistribution(DISTINF.BayesPosteriorDistribution):
    r""" Posterior distribution of the conductivity field of a Poisson problem.

    The system is observed through the operator :math:`\mathcal{O}[{\bf c}]`
    defined by
    
    .. math::

       \mathcal{O}[{\bf c}](u) = \int u({\bf x}) \frac{1}{2\pi\sigma_y^2} \exp\left(-\frac{\Vert{\bf x} - {\bf c}\Vert^2}{2\sigma_y^2} \right) d{\bf x} \;,

    where :math:`u` is the solution associated to an underlying field :math:`\kappa`.

    Given the sensor locations :math:`\{{\bf c}_i\}_{i=1}^s`,
    the Bayesian problem is defined as follows:

    .. math::

       {\bf y}_i = \mathcal{O}[{\bf c}_i](u) + \varepsilon \;, \qquad \varepsilon \sim \mathcal{GP}(0, \mathcal{C}_y({\bf x},{\bf x}^\prime)) \\
       \kappa({\bf x}) \sim \log\mathcal{GP}(\mu_\kappa({\bf x}), \mathcal{C}_\kappa({\bf x},{\bf x}^\prime))

    Args:
      solver (PoissonSolver): Poisson solver for a particular problem setting
      sens_pos_list (:class:`list` of :class:`tuple`): list of sensor locations
      sens_geo_std (float): observation kernel width :math:`\sigma_y`
      real_observations (:class:`ndarray<numpy.ndarray>`): observations :math:`\{{\bf y}_i\}_{i=1}^s`
      field_vals (:class:`ndarray<numpy.ndarray>`): generating field
        (default is ``None``, generating a synthetic field)
      prior_mean_field_vals (:class:`ndarray<numpy.ndarray>`): values :math:`\mu_\kappa({\bf x})`
        (default is ``None``, which corresponds to :math:`\mu_\kappa({\bf x})=0`)
      prior_cov (Covariance): covariance function :math:`\mathcal{C}_\kappa({\bf x},{\bf x}^\prime)`
      lkl_cov (Covariance): covariance function :math:`\mathcal{C}_y({\bf x},{\bf x}^\prime)`
    """
    def __init__(
            self,
            # Physics
            solver,
            # Sensors definition
            sens_pos_list, sens_geo_std,
            # Prior settings
            prior_mean_field_vals=None,
            prior_cov=OrnsteinUhlenbeckCovariance(1.,1.),
            # Likelihood settings
            lkl_cov=IdentityCovariance(1.),
            # Generating field
            field_vals=None,
            # Observations
            real_observations=None):

        if not DOLFIN_SUPPORT:
            raise ImportError("Please install FENICS (dolfin) in order to use this class")

        self.solver = solver
        self.sens_pos_list = sens_pos_list
        self.sens_geo_std = sens_geo_std
        self.prior_mean_field_vals = prior_mean_field_vals
        self.prior_cov = prior_cov
        self.lkl_cov = lkl_cov
        self.field_vals = field_vals
        self.real_observations = real_observations
        
        # List of attributes to be excluded in get/set params
        self.exclude_state_param_list = set()

        # Build the field to data maps
        self.field_to_data_map = GaussianFieldPoissonFieldToDataMap(
            solver=self.solver,
            sens_pos_list=self.sens_pos_list,
            sens_geo_std=self.sens_geo_std )

        # Build prior (log-GP)
        if self.prior_mean_field_vals is not None:
            mean = self.prior_mean_field_vals
        else:
            mean = np.zeros(self.solver.ndofs)
        cov = self.prior_cov( self.solver.coord )
        prior = DIST.PushForwardTransportMapDistribution(
            Maps.FrozenExponentialDiagonalTransportMap(self.solver.ndofs),
            DIST.NormalDistribution(mean, cov) )

        # Build the slowness field if no-observation was provided
        if self.real_observations is None:
            if self.field_vals is None:
                self.field_vals = prior.rvs(1)[0,:]
            self.set_true_field()

        # Generate the observations
        if self.real_observations is None:
            y = self.field_to_data_map(self.field_vals[np.newaxis,:])[0,:]
        else:
            y = self.real_observations
            
        # Generate likelihoods
        cov = self.lkl_cov( self.sens_pos_list )
        pi_noise = DIST.NormalDistribution(
            np.zeros(len(self.sens_pos_list)), cov)
        if self.real_observations is None:    
            # If observations are synthetic, corrupt them with noise
            y += pi_noise.rvs(1)[0,:]
        # Build likelihood
        lkl = LKL.AdditiveLogLikelihood(y, pi_noise, self.field_to_data_map)

        # Call super to assemble posterior distribution
        super(GaussianFieldPoissonDistribution, self).__init__(lkl, prior)

    def __getstate__(self):
        out = {}
        for key, val in vars(self).items():
            if key not in self.exclude_state_param_list:
                out[key] = val
        return out

    def __setstate__(self, state):
        vars(self).update(state)
        self.solver.set_up()
        if self.real_observations is None:
            self.set_true_field()

    def set_true_field(self):
        self.true_field = self.solver.dof_to_fun(
            self.field_vals)
        self.exclude_state_param_list.add( 'true_field' )

class GaussianFieldPoissonFieldToDataMap(Maps.Map):
    r""" Defines the observation mapping :math:`\kappa \mapsto \mathcal{O}[{\bf c}](u)` between the underlyling field and the sensors' obervations.

    Args:
      solver (PoissonSolver): Poisson solver for a particular problem setting
      sens_pos_list (:class:`list` of :class:`tuple`): list of sensor locations
      sens_geo_std (float): observation kernel width :math:`\sigma_y`
    """
    def __init__(self, solver, sens_pos_list, sens_geo_std):
        if not DOLFIN_SUPPORT:
            raise ImportError("Please install FENICS (dolfin) in order to use this class")
        self.solver = solver
        self.sens_pos_list = sens_pos_list
        self.sens_geo_std = sens_geo_std
        
        # List of exluded parameters
        self.exclude_state_param_list = set()
        
        # Set up experiment
        self.set_up()
        # Init super
        super(GaussianFieldPoissonFieldToDataMap, self).__init__(
            dim_in=self.solver.ndofs,
            dim_out=len(self.sens_pos_list))

    def __getstate__(self):
        out = {}
        for key, val in vars(self).items():
            if key not in self.exclude_state_param_list:
                out[key] = val
        return out

    def __setstate__(self, state):
        vars(self).update(state)
        self.solver.set_up()
        self.set_up()

    def set_up(self):
        nrm_list = []
        one = dol.project(dol.Constant(1.), self.solver.VEFS)
        for c0, c1 in self.sens_pos_list:
            expr = dol.Expression(
                'exp(-.5 * (pow(c0 - x[0],2) + pow(c1 - x[1],2)) / pow(std,2))',
                std=self.sens_geo_std,
                c0=c0, c1=c1, element=self.solver.VE)
            nrm_list.append( dol.assemble(expr * one * dol.dx) )
        self.sensors_list = [
            dol.Expression(
                '1./nrm * exp(-.5 * (pow(c0 - x[0],2) + pow(c1 - x[1],2)) / pow(std,2))',
                std=self.sens_geo_std,
                c0=c0, c1=c1, nrm=nrm, element=self.solver.VE)
            for (c0, c1), nrm in zip(self.sens_pos_list, nrm_list) ]
        self.exclude_state_param_list |= set(['sensors_list'])

    @cached([('solve', None)])
    @counted
    def evaluate(self, x, *args, **kwargs):
        # rank = MPI.COMM_WORLD.Get_rank()
        # print("rank %d: evaluate" % rank)
        x = np.asarray(x, order='C')
        m = x.shape[0]
        fx = np.zeros((m,self.dim_out))
        if 'cache' in kwargs and kwargs['cache'] is not None:
            sol_cache = get_sub_cache( kwargs['cache'], ('solve', None) )
            sol_from_cache = 'solve_list' in sol_cache
            if not sol_from_cache:
                sol_cache['solve_list'] = []
            sol_cache = sol_cache['solve_list']
        for i in range(m):
            kappa = self.solver.dof_to_fun(x[i,:])
            # Solve
            # print("rank %d: solving" % rank)
            if 'cache' in kwargs and \
               kwargs['cache'] is not None and \
               sol_from_cache:
                u = self.solver.dof_to_fun(sol_cache[i])
            else:
                u = self.solver.solve(kappa)
                if 'cache' in kwargs and kwargs['cache'] is not None:
                    sol_cache.append( u.vector().get_local() )
            for j, sensor in enumerate(self.sensors_list):
                fx[i,j] = dol.assemble(sensor * u * dol.dx)
        return fx

    @cached([('solve',None),('adjoints',None)])
    @counted
    def grad_x(self, x, *args, **kwargs):
        x = np.asarray(x, order='C')
        m = x.shape[0]
        fx = np.zeros((m,self.dim_out))
        gfx = np.zeros((m,self.dim_out,self.dim_in))
        if 'cache' in kwargs and kwargs['cache'] is not None:
            sol_cache, adj_cache = get_sub_cache(
                kwargs['cache'], ('solve', None), ('adjoints',None) )
            sol_from_cache = 'solve_list' in sol_cache
            if not sol_from_cache:
                sol_cache['solve_list'] = []
            sol_cache = sol_cache['solve_list']
            adj_from_cache = 'adjoints_list' in adj_cache
            if not adj_from_cache:
                adj_cache['adjoints_list'] = [[] for i in range(m)]
            adj_cache = adj_cache['adjoints_list']
        for i in range(m):
            kappa = self.solver.dof_to_fun(x[i,:])
            # Solve
            if 'cache' in kwargs and \
               kwargs['cache'] is not None and \
               sol_from_cache:
                u = self.solver.dof_to_fun(sol_cache[i])
            else:
                u = self.solver.solve(kappa)
                if 'cache' in kwargs and kwargs['cache'] is not None:
                    sol_cache.append( u.vector().get_local() )
            v = dol.TestFunction(self.solver.VEFS)
            for j, sensor in enumerate(self.sensors_list):
                # Gradient
                if 'cache' in kwargs and \
                   kwargs['cache'] is not None and \
                   adj_from_cache:
                    adj = self.solver.dof_to_fun(adj_cache[i][j])
                else:
                    adj = self.solver.solve_adjoint(sensor, kappa)
                    if 'cache' in kwargs and kwargs['cache'] is not None:
                        adj_cache[i].append( adj.vector().get_local() )
                grd = - dol.inner(dol.grad(adj), dol.grad(u))
                gfx[i,j,:] = dol.assemble( grd * v * dol.dx )
        return gfx

    @cached(caching=False)
    @counted
    def action_hess_x(self, x, dx, *args, **kwargs):
        x = np.asarray(x, order='C')
        dx = np.asarray(dx, order='C')
        m = x.shape[0]
        ahx = np.zeros((m,self.dim_out,self.dim_in))
        if 'cache' in kwargs and kwargs['cache'] is not None:
            sol_cache, adj_cache = get_sub_cache(
                kwargs['cache'], ('solve', None), ('adjoints',None) )
            sol_cache = sol_cache['solve_list']
            adj_cache = adj_cache['adjoints_list']
        for i in range(m):
            kappa_fun = self.solver.dof_to_fun(x[i,:])
            dx_fun = self.solver.dof_to_fun(dx[i,:])
            # Solve
            if 'cache' in kwargs and kwargs['cache'] is not None:
                u = self.solver.dof_to_fun(sol_cache[i])
            else:
                u = self.solver.solve(kappa_fun)
            v = dol.TestFunction(self.solver.VEFS)
            for j, sensor in enumerate(self.sensors_list):
                if 'cache' in kwargs and kwargs['cache'] is not None:
                    adj = self.solver.dof_to_fun(adj_cache[i][j])
                else:
                    adj = self.solver.solve_adjoint(sensor, kappa_fun)
                A1Mu = self.solver.solve_action_hess_adjoint(
                    dx_fun, u, kappa_fun)
                A1Madj = self.solver.solve_action_hess_adjoint(
                    dx_fun, adj, kappa_fun)
                ahess = dol.inner( dol.grad(adj), dol.grad(A1Mu) ) + \
                        dol.inner( dol.grad(A1Madj), dol.grad(u) )
                ahx[i,j,:] = dol.assemble( ahess * v * dol.dx )
        return ahx

class GaussianFieldIndependentLikelihoodPoissonDistribution(DISTINF.BayesPosteriorDistribution):
    r""" Posterior distribution of the conductivity field of a Poisson problem.

    The system is observed through the operator :math:`\mathcal{O}[{\bf c}]`
    defined by
    
    .. math::

       \mathcal{O}[{\bf c}](u) = \int u({\bf x}) \frac{1}{2\pi\sigma_y^2} \exp\left(-\frac{\Vert{\bf x} - {\bf c}\Vert^2}{2\sigma_y^2} \right) d{\bf x} \;,

    where :math:`u` is the solution associated to an underlying field :math:`\kappa`.

    Given the sensor locations :math:`\{{\bf c}_i\}_{i=1}^s`,
    the Bayesian problem is defined as follows:

    .. math::

       {\bf y}_i = \mathcal{O}[{\bf c}_i](u) + \varepsilon \;, \qquad \varepsilon \sim \mathcal{N}(0, \sigma^2 {\bf I}) \\
       \kappa({\bf x}) \sim \log\mathcal{GP}(\mu_\kappa({\bf x}), \mathcal{C}_\kappa({\bf x},{\bf x}^\prime))

    Args:
      solver (PoissonSolver): Poisson solver for a particular problem setting
      sens_pos_list (:class:`list` of :class:`tuple`): list of sensor locations
      sens_geo_std (float): observation kernel width :math:`\sigma_y`
      real_observations (:class:`ndarray<numpy.ndarray>`): observations :math:`\{{\bf y}_i\}_{i=1}^s`
      field_vals (:class:`ndarray<numpy.ndarray>`): generating field
        (default is ``None``, generating a synthetic field)
      prior_mean_field_vals (:class:`ndarray<numpy.ndarray>`): values :math:`\mu_\kappa({\bf x})`
        (default is ``None``, which corresponds to :math:`\mu_\kappa({\bf x})=0`)
      prior_cov (Covariance): covariance function :math:`\mathcal{C}_\kappa({\bf x},{\bf x}^\prime)`
      lkl_std (floag): standard deviation :math:`\sigma`
    """
    def __init__(
            self,
            # Physics
            solver,
            # Sensors definition
            sens_pos_list, sens_geo_std,
            # Prior settings
            prior_mean_field_vals=None,
            prior_cov=OrnsteinUhlenbeckCovariance(1.,1.),
            # Likelihood settings
            lkl_std=1.,
            # Generating field
            field_vals=None,
            # Observations
            real_observations=None):

        if not DOLFIN_SUPPORT:
            raise ImportError("Please install FENICS (dolfin) in order to use this class")

        self.solver = solver
        self.sens_pos_list = sens_pos_list
        self.sens_geo_std = sens_geo_std
        self.prior_mean_field_vals = prior_mean_field_vals
        self.prior_cov = prior_cov
        self.lkl_std = lkl_std
        self.field_vals = field_vals
        self.real_observations = real_observations
        
        # List of attributes to be excluded in get/set params
        self.exclude_state_param_list = set()

        # Build the field to data maps
        self.field_to_data_map = GaussianFieldPoissonFieldToDataMap(
            solver=self.solver,
            sens_pos_list=self.sens_pos_list,
            sens_geo_std=self.sens_geo_std )

        # Build prior (log-GP)
        if self.prior_mean_field_vals is not None:
            mean = self.prior_mean_field_vals
        else:
            mean = np.zeros(self.solver.ndofs)
        cov = self.prior_cov( self.solver.coord )
        prior = DIST.PushForwardTransportMapDistribution(
            Maps.FrozenExponentialDiagonalTransportMap(self.solver.ndofs),
            DIST.NormalDistribution(mean, cov) )

        # Build the slowness field if no-observation was provided
        if self.real_observations is None:
            if self.field_vals is None:
                self.field_vals = prior.rvs(1)[0,:]
            self.set_true_field()

        # Generate the observations
        if self.real_observations is None:
            y = self.field_to_data_map(self.field_vals[np.newaxis,:])[0,:]
            y += self.lkl_std * npr.randn(len(self.sens_pos_list))
        else:
            y = self.real_observations

        # Build likelihood
        lkl = DiagonalLogLikelihoodPoisson(
            solver  = self.solver,
            lkl_std = self.lkl_std,
            sens_pos_list = self.sens_pos_list,
            sens_geo_std = self.sens_geo_std,
            data = y,
            field_to_data_map = self.field_to_data_map
        )
    
        # Call super to assemble posterior distribution
        super(GaussianFieldIndependentLikelihoodPoissonDistribution, self).__init__(lkl, prior)

    def __getstate__(self):
        out = {}
        for key, val in vars(self).items():
            if key not in self.exclude_state_param_list:
                out[key] = val
        return out

    def __setstate__(self, state):
        vars(self).update(state)
        self.solver.set_up()
        if self.real_observations is None:
            self.set_true_field()

    def set_true_field(self):
        self.true_field = self.solver.dof_to_fun(
            self.field_vals)
        self.exclude_state_param_list.add( 'true_field' )

class DiagonalLogLikelihoodPoisson( LKL.AdditiveLogLikelihood ):
    r"""
    Given the ``solver`` :math:`\kappa \mapsto u[\kappa]({\bf x})` satisfying the
    Poisson differential equation, and given the data ``y`` collected
    at the ``sens_pos_list``, assemble the log-likelihood functional

    .. math::

       J[\kappa] = \frac{1}{2\sigma^2}
         \sum_{i=1}^n \left( y_i - \langle u[\kappa],\varphi_i \rangle \right)^2

    where :math:`\varphi_i` is the observation operator at sensor :math:`i`.
    """
    def __init__(
            self,
            solver,
            lkl_std,
            sens_pos_list,
            sens_geo_std,
            data,
            field_to_data_map
    ):
        self.solver = solver
        self.lkl_std = lkl_std
        self.sens_pos_list = sens_pos_list
        self.sens_geo_std = sens_geo_std
        # Facilitate compositions while allowing to have the filed_to_data_map
        pi_noise = DIST.NormalDistribution(
            np.zeros(len(data)), lkl_std**2 * np.eye(len(data))
        )
        super(DiagonalLogLikelihoodPoisson, self).__init__(
            data, pi_noise, field_to_data_map)
        self.composite_map = Maps.ListCompositeMap(map_list=[self])
        self.set_up()

    def __getstate__(self):
        d = super(DiagonalLogLikelihoodPoisson, self).__getstate__()
        del d['sensors_list']
        del d['assembled_sensors_list']
        return d
        
    def __setstate__(self, state):
        vars(self).update(state)
        self.solver.set_up()
        self.set_up()

    @property
    def dim_in(self):
        if hasattr(self,'composite_map'):
            return self.composite_map.dim_in
        else:
            return super(DiagonalLogLikelihoodPoisson, self).dim_in

    @dim_in.setter
    def dim_in(self, dim_in):
        if hasattr(self,'composite_map'):
            if self.composite_map.dim_in != dim_in:
                raise ValueError("Dimension mismatch between dimensions")
        else:
            super(DiagonalLogLikelihoodPoisson, self).dim_in = dim_in            

    def compose(self, mp):
        if hasattr(self,'composite_map'):
            self.composite_map.append( mp )
        else:
            self.composite_map = Maps.ListCompositeMap(map_list=[self, mp])
        if isinstance(self.T, Maps.ListCompositeMap):
            self.T.append( mp )
        else:
            self.T = Maps.ListCompositeMap(map_list=[self.T, mp])
        
    def set_up(self):
        nrm_list = []
        one = dol.project(dol.Constant(1.), self.solver.VEFS)
        for c0, c1 in self.sens_pos_list:
            expr = dol.Expression(
                'exp(-.5 * (pow(c0 - x[0],2) + pow(c1 - x[1],2)) / pow(std,2))',
                std=self.sens_geo_std,
                c0=c0, c1=c1, element=self.solver.VE)
            nrm_list.append( dol.assemble(expr * one * dol.dx) )
        self.sensors_list = [
            dol.Expression(
                '1./nrm * exp(-.5 * (pow(c0 - x[0],2) + pow(c1 - x[1],2)) / pow(std,2))',
                std=self.sens_geo_std,
                c0=c0, c1=c1, nrm=nrm, element=self.solver.VE)
            for (c0, c1), nrm in zip(self.sens_pos_list, nrm_list) ]
        v = dol.TestFunction(self.solver.VEFS)
        self.assembled_sensors_list = [
            dol.assemble( sensor * v * dol.dx )
            for sensor in self.sensors_list
        ]
        
    @counted
    def evaluate(self, x, *args, **kwargs):
        if not hasattr(self, 'composite_map'):
            # Backward compatibility
            return self._evaluate(x, *args, **kwargs)
        if getattr(self, 'composite_evaluate_flag', False):
            # If the composition has been rolled out already
            del self.composite_evaluate_flag
            return self._evaluate(x, *args, **kwargs)
        else:
            self.composite_evaluate_flag = True
            return self.composite_map.evaluate(x, *args, **kwargs)

    @cached([('solve', None)])
    @counted
    def _evaluate(self, x, *args, **kwargs):
        x = np.asarray(x, order='C')
        m = x.shape[0]
        ll = np.zeros(m)
        if 'cache' in kwargs and kwargs['cache'] is not None:
            sol_cache = get_sub_cache( kwargs['cache'], ('solve', None) )
            sol_from_cache = 'solve_list' in sol_cache
            if not sol_from_cache:
                sol_cache['solve_list'] = []
                sol_cache['mismatch_list'] = []
            solve_list = sol_cache['solve_list']
            mismatch_list = sol_cache['mismatch_list']
        for i in range(m):
            kappa = self.solver.dof_to_fun(x[i,:])
            # Solve
            if 'cache' in kwargs and \
               kwargs['cache'] is not None and \
               sol_from_cache:
                mismatch = mismatch_list[i]
            else:
                u = self.solver.solve(kappa)
                if 'cache' in kwargs and kwargs['cache'] is not None:
                    solve_list.append( u.vector().get_local() )
                # Compute mismatch
                mismatch = np.zeros(len(self.sensors_list))
                for j, sensor in enumerate(self.sensors_list):
                    mismatch[j] = dol.assemble(sensor * u * dol.dx) - self.y[j]
                if 'cache' in kwargs and kwargs['cache'] is not None:
                    mismatch_list.append( mismatch )
            # Compute log-likelihood
            for j, sensor in enumerate(self.sensors_list):
                ll[i] -= mismatch[j]**2
            ll[i] /= 2 * self.lkl_std**2
        return ll[:,nax]

    @counted
    def tuple_grad_x(self, x, *args, **kwargs):
        if not hasattr(self, 'composite_map'):
            # Backward compatibility
            return self._tuple_grad_x(x, *args, **kwargs)
        if getattr(self, 'composite_tuple_grad_x_flag', False):
            # If the composition has been rolled out already
            del self.composite_tuple_grad_x_flag
            return self._tuple_grad_x(x, *args, **kwargs)
        else:
            self.composite_tuple_grad_x_flag = True
            return self.composite_map.tuple_grad_x(x, *args, **kwargs)

    def _tuple_grad_x(self, x, *args, **kwargs):
        x = np.asarray(x, order='C')
        m = x.shape[0]
        ll = np.zeros(m)
        gxll = np.zeros(x.shape)
        v = dol.TestFunction(self.solver.VEFS)
        for i in range(m):
            kappa = self.solver.dof_to_fun(x[i,:])
            # Solve
            u = self.solver.solve(kappa)
            # Compute log-likelihood
            mismatch = np.zeros(len(self.sensors_list))
            # for j, sensor in enumerate(self.projected_sensors_list):
            for j, sensor in enumerate(self.sensors_list):
                mismatch[j] = dol.assemble(sensor * u * dol.dx) - self.y[j]
                ll[i] -= mismatch[j]**2
            ll[i] /= 2 * self.lkl_std**2
            
            # Use adjoint to compute gradient
            # Put together the assembled right hand side
            rhs = sum( mm * ss for mm, ss in zip(mismatch, self.assembled_sensors_list) )
            rhs /= - self.lkl_std**2
            
            # Solve adjoint
            adj = self.solver.solve_adjoint(rhs, kappa)
            grd = - dol.inner(dol.grad(adj), dol.grad(u))            
            gxll[i,:] = dol.assemble( grd * v * dol.dx )
        return ll[:,nax], gxll[:,nax,:]

    @counted
    def grad_x(self, x, *args, **kwargs):
        if not hasattr(self, 'composite_map'):
            # Backward compatibility
            return self._grad_x(x, *args, **kwargs)
        if getattr(self, 'composite_grad_x_flag', False):
            # If the composition has been rolled out already
            del self.composite_grad_x_flag
            return self._grad_x(x, *args, **kwargs)
        else:
            self.composite_grad_x_flag = True
            return self.composite_map.grad_x(x, *args, **kwargs)

    @cached([('solve', None)])
    @counted
    def _grad_x(self, x, *args, **kwargs):
        x = np.asarray(x, order='C')
        m = x.shape[0]
        gxll = np.zeros(x.shape)
        v = dol.TestFunction(self.solver.VEFS)
        if 'cache' in kwargs and kwargs['cache'] is not None:
            sol_cache = get_sub_cache( kwargs['cache'], ('solve', None) )
            sol_from_cache = 'solve_list' in sol_cache
            if not sol_from_cache:
                sol_cache['solve_list'] = []
                sol_cache['mismatch_list'] = []
            solve_list = sol_cache['solve_list']
            mismatch_list = sol_cache['mismatch_list']
        for i in range(m):
            kappa = self.solver.dof_to_fun(x[i,:])
            # Solve
            if 'cache' in kwargs and \
               kwargs['cache'] is not None and \
               sol_from_cache:
                u = self.solver.dof_to_fun(solve_list[i])
                mismatch = mismatch_list[i]
            else:
                u = self.solver.solve(kappa)
                if 'cache' in kwargs and kwargs['cache'] is not None:
                    solve_list.append( u.vector().get_local() )
                # Compute mismatch
                mismatch = np.zeros(len(self.sensors_list))
                for j, sensor in enumerate(self.sensors_list):
                    mismatch[j] = dol.assemble(sensor * u * dol.dx) - self.y[j]
                if 'cache' in kwargs and kwargs['cache'] is not None:
                    mismatch_list.append( mismatch )
            
            # Use adjoint to compute gradient
            # Put together the assembled right hand side
            rhs = sum( mm * ss for mm, ss in zip(mismatch, self.assembled_sensors_list) )
            rhs /= - self.lkl_std**2
            
            # Solve adjoint
            adj = self.solver.solve_adjoint(rhs, kappa)
            grd = - dol.inner(dol.grad(adj), dol.grad(u))            
            gxll[i,:] = dol.assemble( grd * v * dol.dx )
        return gxll[:,nax,:]
