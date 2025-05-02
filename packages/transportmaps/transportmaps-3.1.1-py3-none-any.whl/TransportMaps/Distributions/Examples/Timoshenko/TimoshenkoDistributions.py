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
import numpy.linalg as npla
from scipy.spatial.distance import pdist, squareform

from .... import Maps
from ....Misc import counted
from ....External import DOLFIN_SUPPORT
from .... import Distributions as DIST
from ....Distributions import Inference as DISTINF
from .... import Likelihoods as LKL

__all__ = [
    'OrnsteinUhlenbeckCovariance',
    'SquaredExponentialCovariance',
    'IdentityCovariance',
    'TimoshenkoYoungModulusPosteriorDistribution'
]

class Covariance(object):
    def __call__(self, coord):
        dists = squareform( pdist(coord[:,np.newaxis]) )
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

class TimoshenkoYoungModulusPosteriorDistribution(
        DISTINF.BayesPosteriorDistribution
):
    r"""
    Args:
      solver (AdjointTimoshenkoSolver): provides the evaluation of the cost functional
        :math:`J(u) = \sum_{i=1}^{n_\text{obs}} w_i \left( y_i - \int u s_i dx \right)^2`
        and its gradients.
    """
    def __init__(
            self,
            # Physics
            solver,
            # Sensors definition
            sens_pos_list, sens_geo_eps,
            # Prior settings (mean and covariances are in GPa)
            piecewise=None,
            young_prior_mean_field_vals=None,
            young_prior_cov=OrnsteinUhlenbeckCovariance(1.,1.),
            # Likelihood settings
            lkl_std=1e-2,
            # Generating field
            young_field_vals=None,
            # Observations
            real_observations=None
    ):
        if not DOLFIN_SUPPORT:
            raise ImportError("Please install FENICS (dolfin) in order to use this class")

        self.solver = solver
        self.sens_pos_list = sens_pos_list
        self.sens_geo_eps = sens_geo_eps
        self.piecewise = piecewise
        self.young_prior_mean_field_vals = young_prior_mean_field_vals
        self.young_prior_cov = young_prior_cov
        self.lkl_std = lkl_std
        self.young_field_vals = young_field_vals
        self.real_observations = real_observations

        if self.piecewise is None:
            dim = self.solver.aux_ndofs
        else:
            dim = self.piecewise
        
        # List of attributes to be excluded in get/set params
        self.exclude_state_param_list = set()

        # Build prior map for Young modulus (Gaussian process)
        if self.young_prior_mean_field_vals is not None:
            mean = self.young_prior_mean_field_vals
        else:
            mean = np.zeros(dim)
        if self.piecewise is None:
            cov = self.young_prior_cov( self.solver.aux_coord )
        else:
            ends = np.linspace(0., solver.length, dim+1)
            cntrs = (ends[:-1] + ends[1:]) / 2
            cov = self.young_prior_cov( cntrs )
        u, s, v = npla.svd(cov)
        if not np.allclose(np.dot(v.T * s, v), cov, rtol=1e-8, atol=1e-8):
            raise ValueError("Covariance matrix is not symmetric positive definite")
        young_prior_map = Maps.AffineTransportMap(
            c=mean, L=np.dot(v.T * np.sqrt(s), v) )

        # Assemble prior map
        self.prior_map = young_prior_map

        # Assemble prior
        prior = DIST.PushForwardTransportMapDistribution(
            self.prior_map,
            DIST.StandardNormalDistribution(dim)
        )

        # Assemble piecewise map
        if self.piecewise is None:
            self.piecewise_map = Maps.IdentityTransportMap(dim)
        else:
            ends = np.linspace(0., solver.length, dim+1)
            L = np.zeros((solver.aux_ndofs, dim))
            coord = solver.aux_coord
            L[coord==0.,0] = 1.
            for i in range(dim):
                idxs = np.logical_and(ends[i] < coord, coord <= ends[i+1])
                L[idxs,i] = 1.
            self.piecewise_map = Maps.AffineMap(
                c = np.zeros(solver.aux_ndofs), L=L
            )

        # Build Young and shear modulus fields if no-observations
        if self.real_observations is None:
            if self.young_field_vals is None:
                self.young_field_vals = self.piecewise_map.evaluate(
                    prior.rvs(1)
                )[0,:]

        # Generate observations
        if self.real_observations is None:
            self.solver.set_sensors_list(self.sens_pos_list, self.sens_geo_eps)
            self.obs_without_noise = self.solver.observe(self.young_field_vals)
            y = self.obs_without_noise + self.lkl_std * npr.randn(len(self.obs_without_noise))
        else:
            y = self.real_observations

        # Build likelihood
        lkl = TimoshenkoYoungModulusLogLikelihood(
            solver  = self.solver,
            piecewise_map = self.piecewise_map,
            lkl_std = self.lkl_std,
            sens_pos_list = self.sens_pos_list,
            sens_geo_eps = self.sens_geo_eps,
            data = y
        )

        # Assemble posterior
        super(TimoshenkoYoungModulusPosteriorDistribution, self).__init__(lkl, prior)

class TimoshenkoYoungModulusLogLikelihood( LKL.LogLikelihood ):
    r"""
    The ``solver`` :math:`S : E,G,{\bf y} \mapsto J(u(E,G),{\bf y})` is defined by

    .. math::
    
       J(u) = \sum_{i=1}^{n_\text{obs}} w_i \left( y_i - \int u s_i dx \right)^2 \;,

    with :math:`w_i = 1/(2 \sigma^2)` and :math:`\{s_i\} are observation functionals

    .. math::

       s_i({\bf x}) = \frac{\exp((p_i-x)^2/(2\varepsilon^2))}{\int \exp((p_i-x)^2/(2\varepsilon^2))}

    at locations :math:`\{p_i\}`. The Gaussian likelihood is then defined by

    .. math::

       \mathcal{L}({\bf y}\vert E, G) \propto \exp( - S(E, G, {\bf y}) )
    """
    def __init__(
            self,
            solver,
            piecewise_map,
            lkl_std,
            sens_pos_list,
            sens_geo_eps,
            data
    ):
        self.solver = solver
        self.piecewise_map = piecewise_map
        self.lkl_std = lkl_std
        self.sens_pos_list = sens_pos_list
        self.sens_geo_eps = sens_geo_eps
        self.solver.set_data(
            data, self.sens_pos_list, self.sens_geo_eps,
            [1/2/self.lkl_std**2] * len(self.sens_pos_list)
        )
        super(TimoshenkoYoungModulusLogLikelihood, self).__init__(
            data, self.piecewise_map.dim_in
        )
        
    @counted
    def evaluate(self, x, *args, **kwargs):
        r""" Inputs are in GPa
        """
        x = self.piecewise_map.evaluate(x)
        x = np.asarray(x, order='C')
        m = x.shape[0]
        ll = np.zeros((m,1))
        for i in range(m):
            E = x[i,:]
            ll[i,0] = self.solver.evaluate(E)
        return - ll

    @counted
    def grad_x(self, x, *args, **kwargs):
        r""" Inputs are in GPa
        """
        _, gxll = self.tuple_grad_x(x, *args, **kwargs)
        return gxll

    @counted
    def tuple_grad_x(self, x, *args, **kwargs):
        gx_pw = self.piecewise_map.grad_x(x)
        x = self.piecewise_map.evaluate(x)
        x = np.asarray(x, order='C')
        m = x.shape[0]
        ll = np.zeros((m,1))
        gxll = np.zeros((m,1,self.solver.aux_ndofs))
        for i in range(m):
            E = x[i,:]
            J, dJdE = self.solver.tuple_grad_x(E)
            ll[i,0] = J
            gxll[i,0,:] = dJdE
        gxll = np.einsum('...ji,...ik->...jk', gxll, gx_pw)
        return - ll, - gxll
