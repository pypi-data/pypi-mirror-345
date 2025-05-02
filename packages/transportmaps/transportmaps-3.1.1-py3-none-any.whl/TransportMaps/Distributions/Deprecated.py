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
import scipy.stats as stats
import scipy.linalg as scila

import SpectralToolbox.Spectral1D as S1D
import SpectralToolbox.SpectralND as SND

from TransportMaps.Misc import counted, cached, deprecate
from TransportMaps.Distributions.DistributionBase import Distribution

__all__ = ['GaussianDistribution']

nax = np.newaxis

class GaussianDistribution(Distribution):
    r""" Multivariate Gaussian distribution :math:`\pi`

    Args:
      mu (:class:`ndarray<numpy.ndarray>` [:math:`d`]): mean vector
      sigma (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]): covariance matrix
      precision (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]): precision matrix
    """

    @deprecate("GaussianDistribution", "3.0",
               "Use NormalDistribution instead.")
    def __init__(self, mu, sigma=None, precision=None, square_root=None):
        if (sigma is not None) and (precision is not None) and \
           (square_root is not None):
            raise ValueError("The fields sigma and precision are mutually " +
                             "exclusive")
        super(GaussianDistribution,self).__init__(mu.shape[0])
        self._mu = None
        self._sigma = None
        self._precision = None
        self.mu = mu
        if sigma is not None:
            self.sigma = sigma
        if precision is not None:
            self.precision = precision
        if square_root is not None:
            self.square_root = square_root

    @property
    def mu(self):
        return self._mu

    @mu.setter
    def mu(self, mu):
        if (self._sigma is not None and mu.shape[0] != self._sigma.shape[0]) or \
           (self._precision is not None and mu.shape[0] != self._precision.shape[0]):
            raise ValueError("Dimension d of mu and sigma/precision must be the same")
        self._mu = mu

    @property
    def square_root(self):
        return self.sampling_mat

    @square_root.setter
    def square_root(self, sqrt):
        self.sampling_mat = sqrt
        self._sigma = np.dot(sqrt, sqrt.T)
        _, self.log_det_sigma = npla.slogdet(sqrt)
        self.det_sigma = np.exp( self.log_det_sigma )
        self.inv_sigma = npla.solve(self.sigma, np.eye(self.dim))

    @property
    def sigma(self):
        return self._sigma

    @sigma.setter
    def sigma(self, sigma):
        if self.mu.shape[0] != sigma.shape[0] or self.mu.shape[0] != sigma.shape[1]:
            raise ValueError("Dimension d of mu and sigma must be the same")
        if self._sigma is None or np.any(self._sigma != sigma):
            self._sigma = sigma
            try:
                chol = scila.cho_factor(self._sigma, True) # True: lower triangular
            except scila.LinAlgError:
                # Obtain the square root from svd
                u,s,v = scila.svd(self._sigma)
                self.log_det_sigma = np.sum(np.log(s))
                self.det_sigma = np.exp( self.log_det_sigma )
                self.sampling_mat = u * np.sqrt(s)[np.newaxis,:]
                self.inv_sigma = np.dot(u * (1./s)[np.newaxis,:], v.T)
            else:
                self.det_sigma = np.prod(np.diag(chol[0]))**2.
                self.log_det_sigma = 2. * np.sum( np.log( np.diag(chol[0]) ) )
                self.sampling_mat = np.tril(chol[0])
                self.inv_sigma = scila.cho_solve(chol, np.eye(self.dim))

    @property
    def precision(self):
        return self._precision

    @precision.setter
    def precision(self, precision):
        if self.mu.shape[0] != precision.shape[0] or self.mu.shape[0] != precision.shape[1]:
            raise ValueError("Dimension d of mu and precision must be the same")
        if self._precision is None or np.any(self.inv_sigma != precision):
            self._precision = precision
            self.inv_sigma = precision
            try:
                chol = scila.cho_factor(self.inv_sigma, False) # False: upper triangular
            except  scila.LinAlgError:
                u,s,v = scila.svd(self.inv_sigma)
                self.log_det_sigma = - np.sum( np.log(s) )
                self.det_sigma = np.exp( self.log_det_sigma )
                self._sigma = np.dot(u * (1./s)[np.newaxis,:], v.T)
                self.sampling_mat = scila.solve(
                    u * np.sqrt(s)[np.newaxis,:], np.eye(self.dim) )
            else:
                self._sigma = scila.cho_solve(chol, np.eye(self.dim))
                self.det_sigma = 1. / np.prod(np.diag(chol[0]))**2.
                self.log_det_sigma = - 2. * np.sum( np.log( np.diag(chol[0]) ) )
                self.sampling_mat = scila.solve_triangular(
                    np.triu(chol[0]), np.eye(self.dim), lower=False)
            
    def rvs(self, m, *args, **kwargs):
        r""" Generate :math:`m` samples from the distribution.

        Args:
          m (int): number of samples

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- samples

        .. seealso:: :func:`Distribution.rvs`
        """
        x, w = self.quadrature(0, m, **kwargs)
        return x
        
        # z = stats.norm().rvs(m*self.dim).reshape((m,self.dim))
        # samples = self._mu + np.dot( self.sampling_mat, z.T ).T
        # return samples

    def quadrature(
            self,
            qtype,
            qparams: int,
            mass=1.,
            batch_size=np.inf,
            **kwargs
    ):
        r""" Generate quadrature points and weights.

        Types of quadratures:

        Monte-Carlo (``qtype==0``)
           ``qparams``: (:class:`int`) -- number of samples

        Quasi-Monte-Carlo (``qtype==1``)
           ``qparams``: (:class:`int`) -- number of samples

        Latin-Hypercube-Sampling (``qtype==2``)
           ``qparams``: (:class:`int`) -- number of samples

        Gauss-quadrature (``qtype==3``)
           ``qparams``: (:class:`list<list>` [:math:`d`]) -- orders for
           each dimension
        """
        # Generate Standard Normal
        if qtype == 0:
            # Monte Carlo sampling (may be batched)
            batch_size = kwargs.get('batch_size', qparams)
            x = np.zeros((qparams, self.dim))
            niter = qparams // batch_size + (1 if qparams % batch_size > 0 else 0)
            for it in range(niter):
                nnew = min(qparams-it*batch_size, batch_size)
                samp_start = it * batch_size
                samp_stop = samp_start + nnew
                # Sample
                x[samp_start:samp_stop,:] = \
                    stats.norm().rvs(nnew*self.dim).reshape((nnew, self.dim))
            w = np.ones(qparams)/float(qparams)
        elif qtype == 1:
            # Quasi-Monte Carlo sampling
            raise NotImplementedError("Not implemented")
        elif qtype == 2:
            # Latin-Hyper cube sampling
            raise NotImplementedError("Todo")
        elif qtype == 3:
            # Gaussian quadrature
            # Generate first a standard normal quadrature
            # then apply the Cholesky transform
            P = SND.PolyND( [S1D.HermiteProbabilistsPolynomial()] * self.dim )
            (x,w) = P.GaussQuadrature(qparams, norm=True)
            # For stability sort in ascending order of w
            srt_idxs = np.argsort(w)
            w = w[srt_idxs]
            x = x[srt_idxs,:]
        else:
            raise ValueError("Quadrature type not recognized")
        # Transform to Gaussian
        x = np.dot( self.sampling_mat, x.T ).T
        x += self._mu
        # Transform mass
        w *= mass
        return (x,w)

    @counted
    def pdf(self, x, *args, **kwargs):
        r""" Evaluate :math:`\pi(x)`

        .. seealso:: :func:`Distribution.pdf`
        """
        return np.exp( self.log_pdf(x) )

    @cached()
    @counted
    def log_pdf(self, x, *args, **kwargs):
        r""" Evaluate :math:`\log\pi(x)`

        .. seealso:: :func:`Distribution.log_pdf`
        """
        b = x - self._mu
        sol = np.dot( self.inv_sigma, b.T ).T
        out = - .5 * np.einsum('...i,...i->...', b, sol) \
              - self.dim * .5 * np.log(2.*np.pi) \
              - .5 * self.log_det_sigma
        return out.flatten()

    @cached()
    @counted
    def grad_x_log_pdf(self, x, *args, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf x}\log\pi(x)`

        .. seealso:: :func:`Distribution.grad_x_log_pdf`
        """
        b = x - self._mu
        return - np.dot( self.inv_sigma, b.T ).T

    @counted
    def hess_x_log_pdf(self, x, *args, **kwargs):
        r""" Evaluate :math:`\nabla^2_{\bf x}\log\pi(x)`

        .. seealso:: :func:`Distribution.hess_x_log_pdf`
        """
        return - np.ones(x.shape[0])[:,nax,nax] * self.inv_sigma[nax,:,:]

    @counted
    def action_hess_x_log_pdf(self, x, dx, *args, **kwargs):
        r""" Evaluate :math:`\langle \nabla^2_{\bf x} \log \pi({\bf x}), \delta{\bf x}\rangle`

        .. seealso:: :func:`Distribution.action_hess_x_log_pdf`
        """
        return - np.dot( dx, self.inv_sigma )

    def mean_log_pdf(self):
        r""" Evaluate :math:`\mathbb{E}_{\pi}[\log \pi]`.

        .. seealso:: :func:`Distribution.mean_log_pdf`
        """
        return - .5 * ( self.dim * np.log(2*np.pi) + self.dim + self.log_det_sigma )
