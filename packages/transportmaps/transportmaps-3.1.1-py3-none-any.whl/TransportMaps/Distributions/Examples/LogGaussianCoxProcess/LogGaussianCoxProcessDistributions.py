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
import scipy.linalg as scila
import scipy.stats as stats

from ....Misc import counted
from .... import Distributions, Maps

__all__ = [
    'StationaryKernel',
    'IsotropicStationaryKernel',
    'OrnsteinUhlenbeck',
    'SquaredExponentialKernel',
    'GaussianProcess',
    'PoissonPointProcessDistribution',
    'PoissonPointProcessLogLikelihood',
    'LogGaussianCoxProcessPosterior'
]

class Kernel(object):
    pass

class StationaryKernel(Kernel):
    def distance(self, x1, x2):
        return x1 - x2

class IsotropicStationaryKernel(StationaryKernel):
    def distance(self, x1, x2):
        return np.sqrt(np.sum((x1 - x2)**2., axis=1))

class OrnsteinUhlenbeck(IsotropicStationaryKernel):
    def __init__(self, l=1.):
        self.l = l
    def __call__(self, x1, x2):
        d = self.distance(x1, x2)
        return np.exp( - d / self.l )

class SquaredExponentialKernel(IsotropicStationaryKernel):
    def __init__(self, l=1.):
        self.l = l
    def __call__(self, x1, x2):
        d = self.distance(x1, x2)
        return np.exp( - d**2. / (2. * self.l**2.) )
    
class GaussianProcess(Distributions.PushForwardTransportMapDistribution):
    def __init__(self, pts, kernel, mu=None):
        self.proc_dim = pts.shape[1]
        self.pts = pts
        self.kernel = kernel
        if mu is None:
            mu = np.zeros(self.pts.shape[0])
        # Evaluate covariance
        npts = self.pts.shape[0]
        x1 = np.zeros((npts**2, self.proc_dim))
        x2 = np.zeros((npts**2, self.proc_dim))
        for i in range(pts.shape[1]):
            p1, p2 = np.meshgrid( self.pts[:,i], self.pts[:,i] )
            x1[:,i] = p1.flatten()
            x2[:,i] = p2.flatten()
        sigma = self.kernel(x1, x2).reshape((npts,npts))
        chol = scila.cholesky(sigma, lower=True)
        tm = Maps.AffineTransportMap(c=mu, L=chol)
        base = Distributions.StandardNormalDistribution(mu.shape[0])
        # Set the distribution
        super(GaussianProcess, self).__init__(tm, base)

class PoissonPointProcessDistribution(Distributions.Distribution):
    def __init__(self, lmb):
        self.lmb = lmb
        self.dim = len(lmb)
    def rvs(self, n):
        out = np.zeros((n, self.dim),dtype=int)
        for i in range(self.dim):
            rv = stats.poisson(mu=self.lmb[i])
            out[:,i] = rv.rvs(n)
        return out
    def pdf(self, x, *args, **kwargs):
        r""" Evaluate the pdf. ``x`` is integer
        """
        return np.exp( self.log_pdf(x) )
    def log_pdf(self, x, *args, **kwargs):
        r""" Evaluate the log_pdf. ``x`` is integer
        """
        if x.shape[1] != self.dim:
            raise ValueError("Incompatible dimensions")
        out = x * np.log(self.lmb)
        # Add the log(x!)
        oshape = out.shape
        out = out.reshape(out.size)
        xmax = np.max(x)
        idxs = np.arange(out.size)
        for i in range(2,xmax+1):
            (ii,) = np.where(out[idxs] >= i)
            idxs = idxs[ii]
            out[idxs] += np.log(i)
        out = out.reshape(oshape)
        # Add last term
        out -= self.lmb
        return out

class PoissonPointProcessLogLikelihood(Maps.Map):
    def __init__(self, obs, dim_in):
        super(PoissonPointProcessLogLikelihood, self).__init__(
            dim_in=dim_in, dim_out=1)
        self.obs = obs
        self.nobs = len(obs)
        # Pre-compute the log(obs!) term
        self.log_obs_fact = np.zeros( len(obs) )
        omax = np.max(self.obs)
        idxs = np.arange(len(self.obs))
        for i in range(2,omax+1):
            (ii,) = np.where(self.log_obs_fact[idxs] >= i)
            idxs = idxs[ii]
            self.log_obs_fact[idxs] += np.log(i)
    def evaluate(self, x, *args, **kwargs):
        r""" Evaluate the log_pdf. ``x`` is integer
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("Incompatible dimensions")
        out = np.zeros((x.shape[0], 1, self.dim_in))
        out[:,0,:self.nobs] = self.obs * np.log(x[:,:self.nobs])
        # Add log(obs!) term
        out[:,0,:self.nobs] -= self.log_obs_fact
        # Add last term
        out[:,0,:self.nobs] -= x[:,:self.nobs]
        return np.sum(out, axis=2) # Returns m x 1 
    def grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("Incompatible dimensions")
        out = np.zeros((x.shape[0], 1, self.dim_in))
        out[:,0,:self.nobs] = self.obs / x[:,:self.nobs] - 1.
        return out # Returns m x 1 x d 
    def hess_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("Incompatible dimensions")
        out = np.zeros( (x.shape[0], 1, self.dim_in, self.dim_in) )
        diag_out = np.einsum('...ii->...i', out) # Read/write from Numpy 1.10
        diag_out[:,0,:self.nobs] = - self.obs / x[:,:self.nobs]**2.
        return out

class LogGaussianCoxProcessPosterior(Distributions.Distribution):
    # This is the posterior restricted to the observation positions
    def __init__(self, reduced_gp, obs,
                 full_N, full_obs_idxs, full_gp, full_lmb):
        self.obs = obs  # ndarray of size (1,nobs)
        self.nobs = len(obs)
        self.reduced_gp = reduced_gp
        self.dim = reduced_gp.dim
        self.full_N = full_N
        self.full_obs_idxs = full_obs_idxs
        self.full_gp = full_gp
        self.full_lmb = full_lmb
        ##### PRIOR ######
        self.prior = Distributions.StandardNormalDistribution(self.dim)
        ##### LIKELIHOOD #####
        pppll = PoissonPointProcessLogLikelihood(self.obs, self.dim)
        exp_map = Maps.FrozenExponentialDiagonalTransportMap(self.dim)
        self.log_likelihood = Maps.ListCompositeMap(
            map_list=[pppll, exp_map, reduced_gp.transport_map] )
    @counted
    def pdf(self, x, *args, **kwargs):
        return np.exp(self.log_pdf(x))
    @counted
    def log_pdf(self, x, *args, **kwargs):
        out = self.prior.log_pdf(x)
        out += self.log_likelihood.evaluate(x)[:,0]
        return out
    @counted
    def grad_x_log_pdf(self, x, *args, **kwargs):
        out = self.prior.grad_x_log_pdf(x)
        out += self.log_likelihood.grad_x(x)[:,0,:]
        return out
    @counted
    def hess_x_log_pdf(self, x, *args, **kwargs):
        out = self.prior.hess_x_log_pdf(x)
        out += self.log_likelihood.hess_x(x)[:,0,:,:]
        return out
