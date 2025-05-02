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
import scipy.stats as stats
import scipy.linalg as scila

from TransportMaps.Misc import counted, cached
from .ConditionalDistributionBase import ConditionalDistribution
from .FrozenDistributions import NormalDistribution

__all__ = [
    'ConditionallyNormalDistribution',
    'MeanConditionallyNormalDistribution',
    # Deprecated
    'ConditionallyGaussianDistribution',
    'MeanConditionallyGaussianDistribution',
]

nax = np.newaxis

class ConditionallyNormalDistribution(ConditionalDistribution):
    r""" Multivariate Gaussian distribution :math:`\pi({\bf x}\vert{\bf y}) \sim \mathcal{N}(\mu({\bf y}), \Sigma({\bf y}))`

    Args:
      mu (:class:`Map<TransportMaps.Maps.Map>`): mean vector map
      sigma (:class:`Map<TransportMaps.Maps.Map>`): covariance matrix map
      precision (:class:`Map<TransportMaps.Maps.Map>`): precision matrix map
      coeffs (:class:`ndarray<numpy.ndarray>`): fix the coefficients :math:`{\bf y}`
    """
    def __init__(self, mu, sigma=None, precision=None, coeffs=None):
        if (sigma is not None) and (precision is not None):
            raise ValueError("The fields sigma and precision are mutually " +
                             "exclusive")
        if sigma is not None and mu.dim_in != sigma.dim_in:
            raise ValueError("The number of parameters must be the same for both " + \
                             "the map mu and the map sigma")
        if precision is not None and mu.dim_in != precision.dim_in:
            raise ValueError("The number of parameters must be the same for both " + \
                             "the map mu and the map precision")
        self._muMap = mu
        self._sigmaMap = sigma
        self._precisionMap = precision
        if sigma is not None:
            self._isSigmaOn = True
        else:
            self._isSigmaOn = False
        self._mu = None
        self._sigma = None
        self._precision = None
        self._pi = NormalDistribution(np.zeros(mu.dim_out), np.eye(mu.dim_out))
        super(ConditionallyNormalDistribution,self).__init__(mu.dim_out, mu.dim_in)
        self._coeffs = None
        self.coeffs = coeffs
        # Gradients
        self._grad_a_mu = None
        self._grad_a_T = None
        self._grad_a_precision = None
        self._grad_a_sigma = None
        self._grad_a_c = None

    def get_ncalls_tree(self, indent=""):
        out = super(ConditionallyNormalDistribution, self).get_ncalls_tree(indent)
        out += self._pi.get_ncalls_tree(indent + '  ')
        out += self._muMap.get_ncalls_tree(indent + '  ')
        if self._sigmaMap is not None:
            out += self._sigmaMap.get_ncalls_tree(indent + '  ')
        if self._precisionMap is not None:
            out += self._precisionMap.get_ncalls_tree(indent + '  ')
        return out

    def get_nevals_tree(self, indent=""):
        out = super(ConditionallyNormalDistribution, self).get_nevals_tree(indent)
        out += self._pi.get_nevals_tree(indent + '  ')
        out += self._muMap.get_nevals_tree(indent + '  ')
        if self._sigmaMap is not None:
            out += self._sigmaMap.get_nevals_tree(indent + '  ')
        if self._precisionMap is not None:
            out += self._precisionMap.get_nevals_tree(indent + '  ')
        return out

    def get_teval_tree(self, indent=""):
        out = super(ConditionallyNormalDistribution, self).get_teval_tree(indent)
        out += self._pi.get_teval_tree(indent + '  ')
        out += self._muMap.get_teval_tree(indent + '  ')
        if self._sigmaMap is not None:
            out += self._sigmaMap.get_teval_tree(indent + '  ')
        if self._precisionMap is not None:
            out += self._precisionMap.get_teval_tree(indent + '  ')
        return out

    def update_ncalls_tree(self, obj):
        super(ConditionallyNormalDistribution, self).update_ncalls_tree(obj)
        self._pi.update_ncalls_tree(obj._pi)
        self._muMap.update_ncalls_tree(obj._muMap)
        if self._sigmaMap is not None:
            self._sigmaMap.update_ncalls_tree(obj._sigmaMap)
        if self._precisionMap is not None:
            self._precisionMap.update_ncalls_tree(obj._precisionMap)

    def update_nevals_tree(self, obj):
        super(ConditionallyNormalDistribution, self).update_nevals_tree(obj)
        self._pi.update_nevals_tree(obj._pi)
        self._muMap.update_nevals_tree(obj._muMap)
        if self._sigmaMap is not None:
            self._sigmaMap.update_nevals_tree(obj._sigmaMap)
        if self._precisionMap is not None:
            self._precisionMap.update_nevals_tree(obj._precisionMap)

    def update_teval_tree(self, obj):
        super(ConditionallyNormalDistribution, self).update_teval_tree(obj)
        self._pi.update_teval_tree(obj._pi)
        self._muMap.update_teval_tree(obj._muMap)
        if self._sigmaMap is not None:
            self._sigmaMap.update_teval_tree(obj._sigmaMap)
        if self._precisionMap is not None:
            self._precisionMap.update_teval_tree(obj._precisionMap)

    def reset_counters(self):
        super(ConditionallyNormalDistribution, self).reset_counters()
        self._pi.reset_counters()
        self._muMap.reset_counters()
        if self._sigmaMap is not None:
            self._sigmaMap.reset_counters()
        if self._precisionMap is not None:
            self._precisionMap.reset_counters()
            
    @property
    def pi(self):
        return self._pi
        
    @property
    def mu(self):
        return self._pi.mu
        
    @property
    def sigma(self):
        return self._pi.sigma

    @property
    def precision(self):
        return self._pi.precision
        
    @property
    def muMap(self):
        return self._muMap

    @property
    def sigmaMap(self):
        return self._sigmaMap

    @property
    def precisionMap(self):
        return self._precisionMap

    @property
    def coeffs(self):
        return self._coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        if coeffs is None:
            self._coeffs = None
        elif self._coeffs is None or np.any(self._coeffs != coeffs):
            # Set up Gaussian distribution
            mu = self._muMap.evaluate(coeffs[nax,:])[0,:]
            sigma = None
            precision = None
            if self._isSigmaOn:
                sigma = self._sigmaMap.evaluate(
                    coeffs[nax,:])[0,:,:] 
                self._precision = None
            else:
                precision = self._precisionMap.evaluate(
                    coeffs[nax,:])[0,:,:]
                self._sigma = None
            # Set up gradients
            try:
                self._grad_a_mu = self._muMap.grad_x(coeffs[nax,:])[0,:,:]
                if self._isSigmaOn:
                    self._grad_a_sigma = \
                        self._sigmaMap.grad_x(coeffs[nax,:])[0,:,:,:]
                    self._grad_a_precision = None
                else:
                    self._grad_a_precision = \
                        self._precisionMap.grad_x(coeffs[nax,:])[0,:,:,:]
                    self._grad_a_sigma = None
            except NotImplementedError:
                self._grad_a_c = None
                self._grad_a_T = None
            try:
                self._hess_a_mu = self._muMap.hess_x(
                    coeffs[nax,:])[0,:,:,:]
                if self._isSigmaOn:
                    self._hess_a_sigma = \
                        self._sigmaMap.hess_x(coeffs[nax,:])[0,:,:,:,:]
                    self._hess_a_precision = None
                else:
                    self._hess_a_precision = \
                        self._precisionMap.hess_x(coeffs[nax,:])[0,:,:,:,:]
                    self._hess_a_sigma = None
            except NotImplementedError:
                self._hess_a_c = None
                self._hess_a_T = None
            if self._pi is None:
                self._pi = NormalDistribution(mu, sigma=sigma, precision=precision)
            else:
                self._pi.mu = mu
                if self._isSigmaOn:
                    self._pi.sigma = sigma
                else:
                    self._pi.precision = precision
            self._coeffs = coeffs

    @property
    def grad_a_mu(self):
        return self._grad_a_mu

    @property
    def grad_a_sigma(self):
        return self._grad_a_sigma

    @property
    def grad_a_precision(self):
        return self._grad_a_precision

    def rvs(self, m, y=None, **kwargs):
        r""" Generate :math:`m` samples from the distribution.

        Args:
          m (int): number of samples to generate
          y (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- :math:`m`
             :math:`d`-dimensional samples

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        if self._coeffs is None:
            self.pi.mu = self._muMap.evaluate(y[nax,:])[0,:]
            if self._isSigmaOn:
                self.pi.sigma = self._sigmaMap.evaluate(y[nax,:])[0,:,:] 
            else:
                self.pi.precision = self._precisionMap.evaluate(y[nax,:])[0,:,:]
        return self.pi.rvs(m)

    @cached([("pi",None),("mu",None),("sigma",None),("precision",None)])
    @counted
    def log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None), cache=None):
        r""" Evaluate :math:`\log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`] or :class:`ndarray<numpy.ndarray>` [:math:`d_y`]):
            conditioning values :math:`{\bf Y}={\bf y}`. In the second case one
            conditioning value is used for all the :math:`m` points :math:`{\bf x}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\log\pi`
            at the ``x`` points.
        """
        if self._coeffs is None:
            m = x.shape[0]
            try:
                pi_cache = cache['pi_cache']
                mu_cache = cache['mu_cache']
                sigma_cache = cache['sigma_cache']
                precision_cache = cache['precision_cache']
            except TypeError:
                pi_cache = None
                mu_cache = None
                sigma_cache = None
                precision_cache = None
            mu = self._muMap.evaluate(y, cache=mu_cache)
            if self._isSigmaOn:
                sigma = self._sigmaMap.evaluate(y, cache=sigma_cache)
            else:
                precision = self._precisionMap.Evaluate(y, cache=precision_cache)
            out = np.zeros(m)
            for i in range(m):
                self.pi.mu = mu[i]
                if self._isSigmaOn:
                    self.pi.sigma = sigma[i]
                else:
                    self.pi.precision = precision[i]
                out[i] = self.pi.log_pdf(
                    x[[i],:], params=params, idxs_slice=idxs_slice,
                    cache=pi_cache)
        else:
            try:
                pi_cache = cache['pi_cache']
            except TypeError:
                pi_cache = None
            out = self.pi.log_pdf(x, params=params, idxs_slice=idxs_slice,
                                  cache=pi_cache)
        return out

    @cached([("pi",None),("mu",None),("sigma",None),("precision",None)])
    @counted
    def grad_x_log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None),
                       cache=None):
        r""" Evaluate :math:`\nabla_{\bf x,y} \log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\nabla_x\log\pi` at the ``x`` points.
        """
        if self._coeffs is None:
            try:
                pi_cache = cache['pi_cache']
                mu_cache = cache['mu_cache']
                sigma_cache = cache['sigma_cache']
                precision_cache = cache['precision_cache']
            except TypeError:
                pi_cache = None
                mu_cache = None
                sigma_cache = None
                precision_cache = None
            m = x.shape[0]
            mu_all = self._muMap.evaluate(y, cache=mu_cache)
            ga_mu_all = self._muMap.grad_x(y, cache=mu_cache)
            if self._isSigmaOn:
                sigma_all = self._sigmaMap.evaluate(y, cache=sigma_cache)
                ga_sigma_all = self._sigmaMap.evaluate(y, cache=sigma_cache)
            else:
                precision_all = self._precisionMap.Evaluate(y, cache=precision_cache)
                raise NotImplementedError("There are some parts missing for this gradient")
            out = np.zeros((m, x.shape[1]+y.shape[1]))
            for i in range(m):
                mu = mu_all[i]
                ga_mu = ga_mu_all[i]
                sigma = sigma_all[i]
                ga_sigma = ga_sigma_all[i]
                # Cholesky of sigma
                chol = scila.cho_factor(sigma)
                precision = scila.cho_solve(chol, np.eye(mu.shape))
                ga_precision = - np.einsum('ij,jkl,km->iml', precision, ga_sigma, precision)
                xmu = x[[i],:]-mu
                isgas = np.einsum('ij,jkl->ikl', precision, ga_precision)
                out[i,:x.shape[1]] = self.pi.grad_x_log_pdf(
                    x[[i],:], params=params, idxs_slice=idxs_slice,
                    cache=pi_cache)
                out[i,x.shape[1]:] = \
                    -.5 * ( np.einsum('ij,ik,...k->...j', -ga_mu, precision, xmu) + \
                            np.einsum('...i,ikl,...k->...l', xmu, ga_precision, xmu) + \
                            np.einsum('...i,ij,jk->...k', xmu, precision, -ga_mu) ) \
                    - .5 * np.einsum('iik->k', isgas) # Log determinant part
        else:
            raise NotImplementedError("To be done.")
        return out

ConditionallyGaussianDistribution = ConditionallyNormalDistribution


class MeanConditionallyNormalDistribution(ConditionalDistribution):
    r""" Multivariate Gaussian distribution :math:`\pi({\bf x}\vert{\bf y}) \sim \mathcal{N}(\mu({\bf y}), \Sigma)`

    Args:
      mu (:class:`Map<TransportMaps.Maps.Map>`): mean vector map
      sigma (:class:`ndarray<numpy.ndarray>`): covariance matrix map
      precision (:class:`ndarray<numpy.ndarray>`): precision matrix map
      coeffs (:class:`ndarray<numpy.ndarray>`): fix the coefficients :math:`{\bf y}`
    """
    def __init__(self, mu, sigma=None, precision=None, coeffs=None):
        if (sigma is not None) and (precision is not None):
            raise ValueError("The fields sigma and precision are mutually " +
                             "exclusive")
        self._muMap = mu
        self._mu = None
        self._pi = NormalDistribution(np.zeros(mu.dim_out), sigma)
        super(MeanConditionallyNormalDistribution,self).__init__(mu.dim_out, mu.dim_in)
        self._coeffs = None
        self.coeffs = coeffs

    def get_ncalls_tree(self, indent=""):
        out = super(MeanConditionallyNormalDistribution, self).get_ncalls_tree(indent)
        out += self._pi.get_ncalls_tree(indent + '  ')
        out += self._muMap.get_ncalls_tree(indent + '  ')
        return out

    def get_nevals_tree(self, indent=""):
        out = super(MeanConditionallyNormalDistribution, self).get_nevals_tree(indent)
        out += self._pi.get_nevals_tree(indent + '  ')
        out += self._muMap.get_nevals_tree(indent + '  ')
        return out

    def get_teval_tree(self, indent=""):
        out = super(MeanConditionallyNormalDistribution, self).get_teval_tree(indent)
        out += self._pi.get_teval_tree(indent + '  ')
        out += self._muMap.get_teval_tree(indent + '  ')
        return out

    def update_ncalls_tree(self, obj):
        super(MeanConditionallyNormalDistribution, self).update_ncalls_tree(obj)
        self._pi.update_ncalls_tree(obj._pi)
        self._muMap.update_ncalls_tree(obj._muMap)

    def update_nevals_tree(self, obj):
        super(MeanConditionallyNormalDistribution, self).update_nevals_tree(obj)
        self._pi.update_nevals_tree(obj._pi)
        self._muMap.update_nevals_tree(obj._muMap)

    def update_teval_tree(self, obj):
        super(MeanConditionallyNormalDistribution, self).update_teval_tree(obj)
        self._pi.update_teval_tree(obj._pi)
        self._muMap.update_teval_tree(obj._muMap)

    def reset_counters(self):
        super(MeanConditionallyNormalDistribution, self).reset_counters()
        self._pi.reset_counters()
        self._muMap.reset_counters()
        
    @property
    def pi(self):
        return self._pi
        
    @property
    def mu(self):
        return self._pi.mu
        
    @property
    def sigma(self):
        return self._pi.sigma

    @property
    def precision(self):
        return self._pi.precision
        
    @property
    def muMap(self):
        return self._muMap

    @property
    def coeffs(self):
        return self._coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        if coeffs is None:
            self._coeffs = None
        elif self._coeffs is None or np.any(self._coeffs != coeffs):
            # Set up Gaussian distribution
            mu = self._muMap.evaluate(coeffs[nax,:])[0,:]
            self._pi.mu = mu
            self._coeffs = coeffs

    @property
    def grad_a_mu(self):
        return self._grad_a_mu

    def rvs(self, m, y=None, **kwargs):
        r""" Generate :math:`m` samples from the distribution.

        Args:
          m (int): number of samples to generate
          y (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- :math:`m`
             :math:`d`-dimensional samples

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        if self._coeffs is None:
            if y.ndim == 1:
                self.pi.mu = self._muMap.evaluate(y[nax,:])[0,:]
                out = self.pi.rvs(m)
            else:
                mu = self._muMap.evaluate(y)
                z = stats.norm().rvs(m*self.dim).reshape((m,self.dim))
                out = mu + np.dot( self.pi.sampling_mat, z.T ).T
        else:
            out = self.pi.rvs(m)
        return out

    @cached([("pi",None),("mu",None)])
    @counted
    def log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None), cache=None):
        r""" Evaluate :math:`\log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`] or :class:`ndarray<numpy.ndarray>` [:math:`d_y`]):
            conditioning values :math:`{\bf Y}={\bf y}`. In the second case one
            conditioning value is used for all the :math:`m` points :math:`{\bf x}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\log\pi`
            at the ``x`` points.
        """
        if self._coeffs is None:
            try:
                pi_cache = cache['pi_cache']
                mu_cache = cache['mu_cache']
            except TypeError:
                pi_cache = None
                mu_cache = None
            m = x.shape[0]
            mu = self._muMap.evaluate(y, idxs_slice=idxs_slice, cache=mu_cache)
            b = x - mu
            sol = self.pi.solve_covariance( b.T ).T
            out = - .5 * np.einsum('...i,...i->...', b, sol) \
                  - self.pi.dim * .5 * np.log(2.*np.pi) \
                  - .5 * self.pi.log_det_covariance
        else:
            try:
                pi_cache = cache['pi_cache']
            except TypeError:
                pi_cache = None
            out = self.pi.log_pdf(x, params=params, idxs_slice=idxs_slice,
                                  cache=pi_cache)
        return out

    @cached([("pi",None),("mu",None)])
    @counted
    def grad_x_log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None),
                       cache=None):
        r""" Evaluate :math:`\nabla_{\bf x,y} \log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\nabla_x\log\pi` at the ``x`` points.
        """
        if self._coeffs is None:
            try:
                pi_cache = cache['pi_cache']
                mu_cache = cache['mu_cache']
            except TypeError:
                pi_cache = None
                mu_cache = None
            m = x.shape[0]
            mu = self._muMap.evaluate(y, idxs_slice=idxs_slice, cache=mu_cache)
            gx_mu = self._muMap.grad_x(y, idxs_slice=idxs_slice, cache=mu_cache)
            out = np.zeros((m, self.dim + self.dim_y))
            b = x - mu
            out[:,:self.pi.dim] = - np.dot( self.pi.precision, b.T ).T
            out[:,self.pi.dim:] = np.einsum(
                '...i,...ij->...j', - out[:,:self.pi.dim], gx_mu)
        else:
            try:
                pi_cache = cache['pi_cache']
                mu_cache = cache['mu_cache']
            except TypeError:
                pi_cache = None
                mu_cache = None
            m = x.shape[0]
            mu = self._muMap.evaluate(y, cache=mu_cache)
            gx_mu = self._muMap.grad_x(y, cache=mu_cache)
            out = np.zeros((m, self.dim + self.dim_y))
            b = x - mu
            out[:,:self.pi.dim] = - np.dot( self.pi.precision, b.T ).T
            out[:,self.pi.dim:] = np.einsum(
                '...i,ij->...j', - out[:,:self.pi.dim], gx_mu)
        return out

    @cached([("pi",None),("mu",None)], False)
    @counted
    def hess_x_log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None),
                       cache=None):
        r""" Evaluate :math:`\nabla^2_{\bf x,y} \log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\nabla^2_x\log\pi` at the ``x`` points.
        """
        if self._coeffs is None:
            try:
                pi_cache = cache['pi_cache']
                mu_cache = cache['mu_cache']
            except TypeError:
                pi_cache = None
                mu_cache = None
            m = x.shape[0]
            mu = self._muMap.evaluate(y, idxs_slice=idxs_slice, cache=mu_cache)
            gx_mu = self._muMap.grad_x(y, idxs_slice=idxs_slice, cache=mu_cache)
            hx_mu = self._muMap.hess_x(y, idxs_slice=idxs_slice, cache=mu_cache)
            out = np.zeros((m, self.dim + self.dim_y, self.dim + self.dim_y))
            b = x - mu
            dylpdf = np.dot( self.pi.precision, b.T ).T
            dy2lpdf = - self.pi.precision
            out[:,:self.pi.dim,:self.pi.dim] = - self.pi.precision[nax,:,:]
            out[:,:self.pi.dim,self.pi.dim:] = \
                np.einsum('ij,...jk->...ik', self.pi.precision, gx_mu)
            out[:,self.pi.dim:,:self.pi.dim] = \
                out[:,:self.pi.dim,self.pi.dim:].transpose((0,2,1))
            out[:,self.pi.dim:,self.pi.dim:] = \
                np.einsum('...ji,jk,...kl->...il',
                          gx_mu, dy2lpdf, gx_mu) + \
                np.einsum('...i,...ijk->...jk', dylpdf, hx_mu)
        else:
            try:
                pi_cache = cache['pi_cache']
                mu_cache = cache['mu_cache']
            except TypeError:
                pi_cache = None
                mu_cache = None
            m = x.shape[0]
            mu = self._muMap.evaluate(y, cache=mu_cache)
            gx_mu = self._muMap.grad_x(y, cache=mu_cache)
            hx_mu = self._muMap.hess_x(y, cache=mu_cache)
            out = np.zeros((m, self.dim + self.dim_y, self.dim + self.dim_y))
            b = x - mu
            dylpdf = np.dot( self.pi.precision, b.T ).T
            dy2lpdf = - self.pi.precision
            out[:,:self.pi.dim,:self.pi.dim] = - self.pi.precision[nax,:,:]
            out[:,:self.pi.dim,self.pi.dim:] = \
                np.einsum('ij,jk->ik', self.pi.precision, gx_mu)[nax,:,:]
            out[:,self.pi.dim:,:self.pi.dim] = \
                out[:,:self.pi.dim,self.pi.dim:].transpose((0,2,1))
            out[:,self.pi.dim:,self.pi.dim:] = \
                np.einsum('ji,jk,kl->il',
                          gx_mu, dy2lpdf, gx_mu)[nax,:,:] + \
                np.einsum('...i,ijk->...jk', dylpdf, hx_mu)
        return out

MeanConditionallyGaussianDistribution = MeanConditionallyNormalDistribution
