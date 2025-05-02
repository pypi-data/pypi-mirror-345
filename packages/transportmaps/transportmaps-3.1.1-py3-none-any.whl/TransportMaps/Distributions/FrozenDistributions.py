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
import itertools

import numpy as np
import numpy.linalg as npla
import scipy.stats as stats

import SpectralToolbox.Spectral1D as S1D
import SpectralToolbox.SpectralND as SND

from ..Maps import FrozenBananaMap, CompositeTransportMap
from ..External import DARKSPARK_SUPPORT
from ..Misc import \
    counted, cached, deprecate
from ..LinAlg import \
    square_root, inverse_square_root, matrix_inverse, \
    solve_linear_system, solve_square_root_linear_system, log_det
from ..Maps import AffineTransportMap

from .DistributionBase import Distribution
from .ProductDistributionBase import ProductDistribution
from .Deprecated import GaussianDistribution

from .TransportMapDistributions import \
    PushForwardTransportMapDistribution

if DARKSPARK_SUPPORT:
    from DARKSparK.sparseGridProblem import DimAdaptiveSparseGridProblem, \
        ParametersDimAdaptiveSparseGridProblem
    from DARKSparK.quadratureRules import GaussHermite
    from DARKSparK.sparseGridRules import SparseGridRule


__all__ = ['FrozenDistribution_1d',
           'StandardNormalDistribution',
           'NormalDistribution',
           'ChainGraphGaussianDistribution',
           'StarGraphGaussianDistribution',
           'GridGraphGaussianDistribution',
           'LogNormalDistribution', 'LogisticDistribution',
           'GammaDistribution', 'BetaDistribution', 'UniformDistribution',
           'WeibullDistribution', 'CauchyDistribution',
           'GumbelDistribution', 'BananaDistribution',
           'StudentTDistribution']

nax = np.newaxis

class FrozenDistribution_1d(Distribution):
    r""" [Abstract] Generic frozen distribution 1d
    """
    def __init__(self):
        super(FrozenDistribution_1d,self).__init__(1)
        self.base = StandardNormalDistribution(1)
        self.scipy_base = stats.norm()

    def rvs(self, n, *args, **kwargs):
        return self.dist.rvs(n).reshape((n,1))

    def quadrature(self, qtype, qparams, mass=1, **kwargs):
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

        Sparse Grid Gauss-Hermite quadrature (``qtype==4``)
           ``qparams``: (:class:`list<list>` [:math:`d`]) -- orders for
           each dimension
        .. seealso:: :func:`Distribution.quadrature`
        """
        if qtype == 0:
            # Monte Carlo sampling
            x = self.rvs(qparams)
            w = np.ones(qparams)/float(qparams)
        elif qtype == 1:
            # Quasi-Monte Carlo sampling
            raise NotImplementedError("Not implemented")
        elif qtype == 2:
            # Latin-Hyper cube sampling
            raise NotImplementedError("Todo")
        elif qtype == 3:
            # Gaussian quadrature
            (x1,w) = self.base.quadrature(3, qparams, mass=mass)
            x = self.dist.ppf( self.scipy_base.cdf(x1[:,0]) )[:,nax]
        else:
            raise ValueError("Quadrature type not recognized")
        return (x,w)

    @counted
    def tuple_grad_x_log_pdf(self, x, *args, **kwargs):
        return ( self.log_pdf(x, *args, **kwargs),
                 self.grad_x_log_pdf(x, *args, **kwargs) )
        
    @cached(caching=False)
    @counted
    def action_hess_x_log_pdf(self, x, dx, *args, **kwargs):
        return np.einsum('...ij,...j->...i',
                         self.hess_x_log_pdf(x, *args, **kwargs), dx )


################################################
# Definitions of Standard and Normal densities #
################################################
class StandardNormalDistribution(ProductDistribution):
    r""" Multivariate Standard Normal distribution :math:`\pi`.

    Args:
      d (int): dimension
    """

    def __init__(self, dim):
        super(StandardNormalDistribution,self).__init__(dim)

    @property
    def mu(self):
        return np.zeros(self.dim)

    @property
    def sigma(self):
        return np.eye(self.dim)

    covariance = sigma
        
    @property
    def precision(self):
        return np.eye(self.dim)

    @property
    def square_root(self):
        return np.eye(self.dim)
        
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

    def quadrature(self, qtype, qparams, mass=1., batch_size=np.inf, **kwargs):
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

        Sparse Grid Gauss-Hermite quadrature (``qtype==4``)
           ``qparams``: (:class:`list<list>` [:math:`d`]) -- orders for
           each dimension
        .. seealso:: :func:`Distribution.quadrature`
        """
        if qtype == 0:
            if isinstance(qparams, list):
                if len(qparams) != 1:
                    raise ValueError('len(qparams) != 1')
                qparams = qparams[0]
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
        elif qtype == 4:
            if not DARKSPARK_SUPPORT:
                raise RuntimeError("Sparse Grid is not supported (install DARKSparK).")
            # Gauss Hermite quadrature
            ####################
            # Setting up parameters
            gaussHermiteSparseGridRule = SparseGridRule(
                self.dim,
                GaussHermite(growth_level = qparams.get('growth_level', 1) ),  
                num_levels_precomputed = qparams.get('num_levels_precomputed', 4),
                max_allowed_level_per_dim = qparams.get('max_allowed_level_per_dim', 15)
            )
            sparse_grid_params = ParametersDimAdaptiveSparseGridProblem()
            sparse_grid_params.start_num_dims = self.dim
            sparse_grid_params.num_dims_to_add_each_iter = qparams.get(
                'num_dims_to_add_each_iter', 1) #free to choose, probably keep at 1
            sparse_grid_params.rel_tol = qparams.get(
                'rel_tol', 1e-19) # rel_tol not used for this problem
            sparse_grid_params.min_allowed_num_grid_pts = qparams.get(
                'min_allowed_num_grid_pts', 1)  # this is arbitrary
            sparse_grid_params.min_level_per_dim = qparams.get(
                'min_level_per_dim', 1) # this is arbitrary
            sparse_grid_params.dim_adaptivity_degree = qparams.get(
                'dim_adaptivity_degree', 1.0) # this is arbitrary
            sparse_grid_params.max_allowed_grid_size = qparams.get(
                'max_allowed_grid_size', 1e6) # this is arbitrary
            sparse_grid_params.max_allowed_num_grid_pts = qparams.get(
                'max_allowed_num_grid_pts', 10000) # cost maximum?..... qparams['cost_max']?
            # Finished setting up parameters
            ####################
            
            if 'f' in kwargs:
                # Dimension Adaptive Gauss Hermite sparse grid based on integrand f
                sparse_grid_params.abs_tol = qparams['abs_tol'] # Mandatory parameter

                adapter = DimAdaptiveSparseGridProblem(
                    gaussHermiteSparseGridRule,
                    map=kwargs['f'],
                    parameters=sparse_grid_params)
                qparams['adapter'] = adapter
                
                adapter.integrate() 
                # If doesnt converge within tolerance, 
                # DARKSparK should user with warning, but not provide any error. 
                # If a warning is generated, user should have the option in TM to do something..
                x,w = adapter.get_all_unique_sparse_grid_pts_and_weights()

                if True:
                    import matplotlib.pyplot as plt
                    plt.plot(adapter.max_level_per_dim.keys(),
                             adapter.max_level_per_dim.values())
                    plt.title("Quadrature levels per dimension")
                    plt.show()
                    # print("Manually calculated quadrature",np.dot(kwargs['f'](x),w))
                    # plt.plot(adapter.num_grid_pts_history[len(adapter.num_grid_pts_history)//2:],
                    #          [integral[0]
                    #           for integral in adapter.vector_valued_integrals][len(adapter.num_grid_pts_history)//2:],
                    #          label="SG, by # pts")
                    # plt.title("Sparse Grid Quadrature Error Indicator")
                    # plt.xlabel("# samples")
                    # plt.ylabel("integral")
                    # plt.show()

            else:
                # Use the level 1 isotropic Gauss Hermite quadrature sparse grid instead
                initial_sparse_grid = DimAdaptiveSparseGridProblem(
                    gaussHermiteSparseGridRule,
                    parameters=sparse_grid_params)
                x, w = initial_sparse_grid.get_all_unique_sparse_grid_pts_and_weights()

            #Only perform this check in some debug mode:
            # xw_concat = np.append(x,w[:,np.newaxis],axis=1)
            # if (xw_concat.shape[0] - np.unique(xw_concat,axis=1).shape[0] > 0):
            #     ValueError("Non-unique x, w pairs! Check quadrature rule")

            # For stability sort in ascending order of w
            srt_idxs =  np.argsort([abs(x) for x in w])
            w = w[srt_idxs]
            x = x[srt_idxs,:]
        else:
            raise ValueError("Quadrature type not recognized")
        # Transform mass
        w *= mass
        return x, w

    def get_component(self, avars):
        r""" Return the measure :math:`\nu_{a_1}\times\cdots\times\nu_{a_k} = \mathcal{N}(0,{\bf I}_k)`

        Args:
          avars (list): list of coordinates to extract from :math:`\nu`
        """
        return StandardNormalDistribution(len(avars))

    @counted
    def log_pdf(self, x, *args, **kwargs):
        r""" Evaluate :math:`\log\pi({\bf x})`

        .. seealso:: :func:`Distribution.log_pdf`
        """
        return -.5 * npla.norm(x, axis=1)**2 \
            - self.dim * .5 * np.log(2.*np.pi)

    @counted
    def grad_x_log_pdf(self, x, *args, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf x}\log\pi({\bf x})`

        .. seealso:: :func:`Distribution.grad_x_log_pdf`
        """
        return - x.copy()

    @counted
    def tuple_grad_x_log_pdf(self, x, *args, **kwargs):
        r""" Evaluate :math:`(\log\pi({\bf x}), \nabla_{\bf x}\log\pi({\bf x}))`

        .. seealso:: :func:`Distribution.grad_x_log_pdf`
        """
        lpdf = self.log_pdf(x, *args, **kwargs)
        gxlpdf = self.grad_x_log_pdf(x, *args, **kwargs)
        return (lpdf, gxlpdf)
        
    @counted
    def hess_x_log_pdf(self, x, *args, **kwargs):
        r""" Evaluate :math:`\nabla^2_{\bf x}\log\pi({\bf x})`

        .. seealso:: :func:`Distribution.hess_x_log_pdf`
        """
        hx = np.zeros( (x.shape[0], self.dim, self.dim) )
        dhx = np.einsum('...ii->...i', hx)
        dhx[:] = -1.
        return hx

    @counted
    def action_hess_x_log_pdf(self, x, dx, *args, **kwargs):
        r""" Evaluate :math:`\langle \nabla^2_{\bf x}\log\pi({\bf x}), \delta{\bf x}\rangle`

        .. seealso:: :func:`Distribution.action_hess_x_log_pdf`
        """
        return - dx.copy()

    def solve_square_root(self, y):
        r""" Solve :math:`\Sigma^{\frac{1}{2}}{\bf x} = {\bf y}` (:math:`{\bf x}={\bf y}` for Standard Normal).
        """
        return y.copy()

    def solve_square_root_transpose(self, y):
        r""" Solve :math:`\Sigma^{\frac{\top}{2}}{\bf x} = {\bf y}` (:math:`{\bf x}={\bf y}` for Standard Normal).
        """
        return y.copy()

    def solve_sigma(self, y):
        r""" Solve :math:`\Sigma{\bf x} = {\bf y}` (:math:`{\bf x}={\bf y}` for Standard Normal).
        """
        return y.copy()

    def mean_log_pdf(self):
        r""" Evaluate :math:`\mathbb{E}_{\pi}[\log \pi]`.

        .. seealso:: :func:`Distribution.mean_log_pdf`
        """
        return -.5 * (self.dim * np.log(2*np.pi) + self.dim)

class NormalDistribution(PushForwardTransportMapDistribution):
    r""" Multivariate Gaussian distribution :math:`\mathcal{N}(\mu,\Sigma)`

    Args:
      mu (:class:`ndarray<numpy.ndarray>` [:math:`d`]): mean vector :math:`\mu`
      covariance (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]):
        covariance matrix :math:`\Sigma`
      precision (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]):
        precision matrix :math:`\Sigma^{-1}`
      square_root_covariance (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]):
        square root :math:`\Sigma^{\frac{1}{2}}`
      square_root_precision (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]):
        square root :math:`\Sigma^{-\frac{1}{2}}`
      square_root_type (str): type of square root to be used in case
        ``covariance`` or ``precision``were provided.
        For ``square_root_type=='sym'``, :math:`L=U\Lambda^{\frac{1}{2}}U^T`
        where :math:`\Sigma = U\Lambda U^T` is the eigenvalue decomposition
        of :math:`\Sigma`.
        For ``square_root_type=='tri'`` or ``square_root_type=='chol'``,
        :maht:`L=C` where :math:`\Sigma=CC^T` is
        the Cholesky decomposition of :math:`\Sigma`.
        For ``square_root_type=='kl'``, :math:`L=U\Lambda^{\frac{1}{2}}`
        where :math:`\Sigma = U\Lambda U^T` is the eigenvalue decomposition
        of :math:`\Sigma` (this corresponds to the Karuenen-Loeve expansion).
        The eigenvalues and eigenvectors are ordered with :math:`\lambda_i\geq\lambda_{i+1}`.
        If the parameter ``square_root`` is provided, then the
        :py:attr:`square_root_type` attribute will be set ``user``.

    .. note:: The arguments ``covariance``, ``precision`` and ``square_root`` are mutually
       exclusive.
    """
    def __init__(
            self, mu,
            covariance=None,
            precision=None,
            square_root_covariance=None,
            square_root_precision=None,
            square_root_type='sym'
    ):
        if sum(inp is not None
               for inp in [covariance, precision, square_root_covariance, square_root_precision]) != 1:
            raise AttributeError(
                "The inputs covariance, precision, " + \
                "square_root_covariance and square_root_precision " + \
                "are mutually exclusive."
            )

        if covariance is not None:
            if not (mu.shape[0] == covariance.shape[0] == covariance.shape[1]):
                raise AttributeError("mu and covariance must have consistent dimensions")
            self._covariance = covariance
            self._square_root_type = square_root_type
            self._square_root_covariance = self._square_root_covariance_from_covariance(square_root_type)
            L = self._square_root_covariance
        elif precision is not None:
            if not (mu.shape[0] == precision.shape[0] == precision.shape[1]):
                raise AttributeError("mu and precision must have consistent dimensions")
            self._square_root_type = square_root_type
            self._precision = precision
            self._square_root_covariance = self._square_root_covariance_from_precision(square_root_type)
            L = self._square_root_covariance
        elif square_root_covariance is not None:
            if not (mu.shape[0] == square_root_covariance.shape[0] == square_root_covariance.shape[1]):
                raise AttributeError("mu and square_root_covariance must have consistent dimensions")
            self._square_root_type = 'user'
            self._square_root_covariance = square_root_covariance
            L = square_root_covariance
        elif square_root_precision is not None:
            if not (mu.shape[0] == square_root_precision.shape[0] == square_root_precision.shape[1]):
                raise AttributeError("mu and square_root_precision must have consistent dimensions")
            self.square_root_type = 'user'
            self.square_root_precision = square_root_precision
            L = matrix_inverse( square_root_precision )
        # Define the push-forward distribution
        tm = AffineTransportMap(c=mu, L=L)
        d = StandardNormalDistribution(mu.shape[0])
        super(NormalDistribution, self).__init__(tm, d)
        
    def _square_root_covariance_from_covariance(self, square_root_type='sym'):
        r""" Factorizes the covariance and returns its square root
        
        Kwargs:
          square_root_type (str): type of square root.
             For ``square_root_type=='sym'``, :math:`L=U\Lambda^{\frac{1}{2}}U^T`
             where :math:`\Sigma = U\Lambda U^T` is the eigenvalue decomposition
             of :math:`\Sigma`.
             For ``square_root_type=='tri'`` or ``square_root_type=='chol'``,
             :maht:`L=C` where :math:`\Sigma=CC^T` is
             the Cholesky decomposition of :math:`\Sigma`.
             For ``square_root_type=='kl'``, :math:`L=U\Lambda^{\frac{1}{2}}`
             where :math:`\Sigma = U\Lambda U^T` is the eigenvalue decomposition
             of :math:`\Sigma` (this corresponds to the Karuenen-Loeve expansion).
             The eigenvalues and eigenvectors are ordered with :math:`\lambda_i\geq\lambda_{i+1}`.
        
        Returns:
           :math:`L` -- square root of covariance
        """
        try:
            return square_root(self._covariance)
        except AttributeError:  # Back compatibility v3.0
            return square_root(self._sigma)

    def _square_root_precision_from_covariance(self, square_root_type='sym'):
        r""" Factorizes the covariance and returns the square root of the precision
        
        Kwargs:
          square_root_type (str): type of square root.
             For ``square_root_type=='sym'``, :math:`L=U\Lambda^{\frac{1}{2}}U^T`
             where :math:`\Sigma = U\Lambda U^T` is the eigenvalue decomposition
             of :math:`\Sigma`.
             For ``square_root_type=='tri'`` or ``square_root_type=='chol'``,
             :maht:`L=C` where :math:`\Sigma=CC^T` is
             the Cholesky decomposition of :math:`\Sigma`.
             For ``square_root_type=='kl'``, :math:`L=U\Lambda^{\frac{1}{2}}`
             where :math:`\Sigma = U\Lambda U^T` is the eigenvalue decomposition
             of :math:`\Sigma` (this corresponds to the Karuenen-Loeve expansion).
             The eigenvalues and eigenvectors are ordered with :math:`\lambda_i\geq\lambda_{i+1}`.
        
        Returns:
           :math:`L^{-1}` -- square root of precision
        """
        try:
            return inverse_square_root( self._covariance )
        except AttributeError: # Back compatibility v3.0
            return inverse_square_root( self._sigma )

    def _square_root_precision_from_precision(self, square_root_type='sym'):
        r""" Factorizes the precision and returns its square root

        Args:
          precision (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]): precision matrix :math:`\Sigma^{-1}`
        
        Kwargs:
          square_root_type (str): type of square root.
             For ``square_root_type=='sym'``, :math:`L=U\Lambda^{\frac{1}{2}}U^T`
             where :math:`\Sigma = U\Lambda U^T` is the eigenvalue decomposition
             of :math:`\Sigma`.
             For ``square_root_type=='tri'`` or ``square_root_type=='chol'``,
             :maht:`L=C` where :math:`\Sigma=CC^T` is
             the Cholesky decomposition of :math:`\Sigma`.
             For ``square_root_type=='kl'``, :math:`L=U\Lambda^{\frac{1}{2}}`
             where :math:`\Sigma = U\Lambda U^T` is the eigenvalue decomposition
             of :math:`\Sigma` (this corresponds to the Karuenen-Loeve expansion).
             The eigenvalues and eigenvectors are ordered with :math:`\lambda_i\geq\lambda_{i+1}`.
        
        Returns:
           :math:`L^{-1}` -- square root of the precision
        """
        return square_root( self._precision )

    def _square_root_covariance_from_precision(self, square_root_type='sym'):
        r""" Factorizes the precision and returns the square root of the covariance

        Args:
          precision (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]): precision matrix :math:`\Sigma^{-1}`
        
        Kwargs:
          square_root_type (str): type of square root.
             For ``square_root_type=='sym'``, :math:`L=U\Lambda^{\frac{1}{2}}U^T`
             where :math:`\Sigma = U\Lambda U^T` is the eigenvalue decomposition
             of :math:`\Sigma`.
             For ``square_root_type=='tri'`` or ``square_root_type=='chol'``,
             :maht:`L=C` where :math:`\Sigma=CC^T` is
             the Cholesky decomposition of :math:`\Sigma`.
             For ``square_root_type=='kl'``, :math:`L=U\Lambda^{\frac{1}{2}}`
             where :math:`\Sigma = U\Lambda U^T` is the eigenvalue decomposition
             of :math:`\Sigma` (this corresponds to the Karuenen-Loeve expansion).
             The eigenvalues and eigenvectors are ordered with :math:`\lambda_i\geq\lambda_{i+1}`.
        
        Returns:
           :math:`L` -- square root of the covariance
        """
        return inverse_square_root( self._precision )
    
    @property
    def mu(self):
        return self.transport_map.c

    @mu.setter
    def mu(self, mu):
        self.transport_map.c = mu

    @property
    def covariance(self):
        try:
            self._covariance
        except AttributeError: # Back compatibiliy
            try:
                self._covariance = self._sigma
            except AttributeError: # Use square root of covariance
                try:
                    self._covariance = np.dot(self._square_root_covariance, self._square_root_covariance.T)
                except AttributeError: # Use square root of precision
                    try:
                        self._square_root_covariance = matrix_inverse( self._square_root_precision )
                        self._covariance = np.dot(self._square_root_covariance, self._square_root_covariance.T)
                    except AttributeError: # Use precision
                        self._covariance = matrix_inverse(self._precision)
        return self._covariance

    @covariance.setter
    def covariance(self, cov):
        if not( self.dim == cov.shape[0] == cov.shape[1] ):
            raise AttributeError(
                "The dimensions of covariance must be consistent " + \
                "with the dimensions of the distribution")
        if self._square_root_type == 'user':
            raise AttributeError(
                "The square_root_type attribute is set to `user`. Please " + \
                "set this attribute to one of the available square root types " + \
                "`sym`, `kl`, `tri`.")
        if hasattr(self, '_precision'): delattr(self, '_precision')
        if hasattr(self, '_square_root_precision'): delattr(self, '_square_root_precision')
        self._covariance = cov
        self._square_root_covariance = self._square_root_covariance_from_covariance(self.square_root_type)
        self.transport_map.L = self._square_root_covariance

    @property
    @deprecate("sigma", "3.0",
               "Use property covariance instead.")
    def sigma(self):
        return self.covariance

    @sigma.setter
    @deprecate("sigma", "3.0",
               "Use setter covariance instead.")
    def sigma(self, sigma):
        self.covariance = sigma
        
    @property
    def precision(self):
        try:
            self._precision
        except AttributeError: # Use square root of precision
            try:
                self._precision = np.dot(self._square_root_precision, self._square_root_precision.T)
            except AttributeError: # Use square root of covariance
                try:
                    self._square_root_precision = matrix_inverse(self._square_root_covariance)
                    self._precision = np.dot(self._square_root_precision, self._square_root_precision.T)
                except AttributeError: # Use covariance
                    try:
                        self._precision = matrix_inverse(self._covariance)
                    except AttributeError: # Back compatibility v3.0
                        self._precision = matrix_inverse(self._sigma)
        return self._precision

    @precision.setter
    def precision(self, precision):
        if not( self.dim == precision.shape[0] == precision.shape[1] ):
            raise AttributeError(
                "The dimensions of precision must be consistent " + \
                "with the dimensions of the distribution")
        if self._square_root_type == 'user':
            raise AttributeError(
                "The square_root_type attribute is set to `user`. Please " + \
                "set this attribute to one of the available square root types " + \
                "`sym`, `kl`, `tri`.")
        if hasattr(self, '_covariance'): delattr(self, '_covariance')
        if hasattr(self, '_square_root_precision'): delattr(self, '_square_root_precision')
        self._precision = precision
        self._square_root_covariance = self._square_root_covariance_from_precision(self._square_root_type)
        self.transport_map.L = self._square_root_covariance

    @property
    @deprecate("inv_sigma", "3.0",
               "Use property precision instead.")
    def inv_sigma(self):
        return self.precision

    @inv_sigma.setter
    @deprecate("inv_sigma", "3.0",
               "Use setter precision instead.")
    def inv_sigma(self, inv_sigma):
        self.precision = inv_sigma

    @property
    def square_root_covariance(self):
        try:
            self._square_root_covariance
        except AttributeError: # Use square root precision
            try:
                self._square_root_covariance = matrix_inverse(self._square_root_precision)
            except AttributeError: # Factorize covariance
                try:
                    self._square_root_covariance = self._square_root_covariance_from_covariance(self._square_root_type)
                except AttributeError: # Factorize precision
                    self._square_root_covariance = self._square_root_covariance_from_precision(self._square_root_type)
        return self._square_root_covariance

    @square_root_covariance.setter
    def square_root_covariance(self, sqrt):
        if not( self.dim == sqrt.shape[0] == sqrt.shape[1] ):
            raise AttributeError(
                "The dimensions of the square root must be consistent " + \
                "with the dimensions of the distribution")
        if hasattr(self, '_covariance'): delattr(self, '_covariance')
        if hasattr(self, '_precision'): delattr(self, '_precision')
        if hasattr(self, '_square_root_precision'): delattr(self, '_square_root_precision')
        self._square_root_type = 'user'
        self._square_root_covariance = sqrt
        self.transport_map.L = self._square_root_covariance
        
    @property
    @deprecate("square_root", "3.0",
               "Use property square_root_covariance instead.")
    def square_root(self):
        return self._square_root_covariance
        
    @square_root.setter
    @deprecate("square_root", "3.0",
               "Use setter square_root_covariance instead.")
    def square_root(self, square_root):
        self.square_root_covariance = square_root

    @property
    @deprecate("sampling_mat", '3.0',
               "Use attribute square_root instead.")
    def sampling_mat(self):
        return self.square_root

    @property
    def square_root_precision(self):
        try:
            self._square_root_precision
        except AttributeError: # Use square root covariance
            try:
                self._square_root_precision = matrix_inverse(self._square_root_covariance)
            except AttributeError: # Factorize precision
                try:
                    self._square_root_precision = self._square_root_precision_from_precision(self._square_root_type)
                except AttributeError: # Factorize covariance
                    self._square_root_precision = self._square_root_precision_from_covariance(self._square_root_type)
        return self._square_root_precision

    @square_root_precision.setter
    def square_root_precision(self, sqrt):
        if not( self.dim == sqrt.shape[0] == sqrt.shape[1] ):
            raise AttributeError(
                "The dimensions of the square root must be consistent " + \
                "with the dimensions of the distribution")
        if hasattr(self, '_covariance'): delattr(self, '_covariance')
        if hasattr(self, '_precision'): delattr(self, '_precision')
        self._square_root_type = 'user'
        self._square_root_precision = sqrt
        self._square_root_covariance = matrix_inverse(sqrt)
        self.transport_map.L = self._square_root_covariance
    
    @property
    def square_root_type(self):
        return self._square_root_type

    @square_root_type.setter
    def square_root_type(self, square_root_type):
        if square_root_type not in ['sym', 'kl', 'tri','chol']:
            raise ValueError("Square root type not recognized")
        if square_root_type != self._square_root_type:
            L = self._square_root_covariance_from_covariance(square_root_type)
            self.transport_map.L = L
            self._square_root_type = square_root_type

    def solve_square_root_covariance(self, y):
        r""" Solve :math:`\Sigma^{\frac{1}{2}}{\bf x} = {\bf y}`.
        """
        return solve_linear_system(self._square_root_covariance, y)

    def solve_square_root_covariance_transposed(self, y):
        r""" Solve :math:`\Sigma^{\frac{\top}{2}}{\bf x} = {\bf y}`.
        """
        return solve_linear_system(
            self._square_root_covariance, y, transposed=True)

    @deprecate("solve_square_root", "3.0",
               "Use solve_square_root_covariance instead.")
    def solve_square_root(self, y):
        r""" Solve :math:`\Sigma^{\frac{1}{2}}{\bf x} = {\bf y}`.
        """
        return self.transport_map.solve_linear(y)

    @deprecate("solve_square_root_transpose", "3.0",
               "Use solve_square_root_covariance_transposed instead.")
    def solve_square_root_transpose(self, y):
        r""" Solve :math:`\Sigma^{\frac{\top}{2}}{\bf x} = {\bf y}`.
        """
        return self.transport_map.solve_linear_transpose(y)
        
    def solve_covariance(self, y):
        r""" Solve :math:`\Sigma{\bf x} = {\bf y}`
        """
        try:
            x = np.dot(self._precision, y)
        except AttributeError:
            x = solve_square_root_linear_system(self.square_root_covariance, y)
        return x

    @deprecate("solve_sigma", "3.0",
               "Use solve_covariance instead.")
    def solve_sigma(self, y):
        return self.solve_covariance(y)

    def solve_square_root_precision(self, y):
        r""" Solve :math:`\Sigma^{-\frac{1}{2}}{\bf x} = {\bf y}`.
        """
        return solve_linear_system(self._square_root_precision, y)

    def solve_square_root_precision_transposed(self, y):
        r""" Solve :math:`\Sigma^{-\frac{\top}{2}}{\bf x} = {\bf y}`.
        """
        return solve_linear_system(
            self._square_root_precision, y, transposed=True)

    def solve_precision(self, y):
        r""" Solve :math:`\Sigma^{-1}{\bf x} = {\bf y}`
        """
        try:
            x = np.dot(self._covariance, y)
        except AttributeError:
            x = solve_square_root_linear_system(self.square_root_precision, y)
        return x

    @property
    def log_det_covariance(self):
        return 2 * self.log_det_square_root_covariance

    @property
    def log_det_square_root_covariance(self):
        try:
            self._log_det_square_root_covariance
        except AttributeError:
            self._log_det_square_root_covariance = log_det( self.square_root_covariance )
        return self._log_det_square_root_covariance

    @property
    def log_det_precision(self):
        return 2 * self.log_det_square_root_precision()

    @property
    def log_det_square_root_precision(self):
        try:
            self._log_det_square_root_precision
        except AttributeError:
            self._log_det_square_root_precision = log_det( self.square_root_precision )
        return self._log_det_square_root_precision

    @property
    @deprecate("log_det_sigma", '3.0',
               'Use property log_det_covariance instead.')
    def log_det_sigma(self):
        return self.log_det_covariance
    
    def mean_log_pdf(self):
        r""" Evaluate :math:`\mathbb{E}_{\pi}[\log \pi]`.

        .. seealso:: :func:`Distribution.mean_log_pdf`
        """
        return self.base_distribution.mean_log_pdf() - \
            self.transport_map.log_det_grad_x( np.zeros((1,self.dim)) )[0]

class ChainGraphGaussianDistribution(GaussianDistribution):
    def __init__(self, dim, edge_strength=.45):
        self.dim = dim
        self.edge_strength = edge_strength
        mu = np.zeros(dim)
        precision = self.omega()
        super(ChainGraphGaussianDistribution, self).__init__(mu, precision=precision)

    def omega(self):
        # create tridiagonal matrix 
        omega = np.eye(self.dim) + self.edge_strength*np.eye(self.dim,k=-1) + self.edge_strength*np.eye(self.dim,k=+1)
        # compute unnormalized sigma (covariance matrix)
        sigma_temp = np.linalg.inv(omega)
        # extract standard deviations from sigma_temp
        std_temp = np.diag(np.sqrt(np.diag(sigma_temp)))
        # scale omega by std_temp
        omega = np.dot(np.dot(std_temp, omega), std_temp)
        return omega

    def sigma(self):
        # return inverse of omega
        sigma = np.linalg.inv(self.omega)
        return sigma

    def rvs(self, m):
        # compute K, where K K^T = sigma
        K = np.linalg.cholesky(self.sigma)
        # generate 'base' samples from standard normal
        x = stats.norm().rvs(m*self.dim).reshape((m,self.dim))
        # return m realizations
        samples = np.dot(K, x.T).T
        return samples

    @property
    def nonzero_idxs(self):
        # find zero elements in omega to determine active_vars
        omegaLower = np.tril(self.omega())
        active_vars = []
        for i in range(self.dim):
            actives = np.where(omegaLower[i,:] != 0)
            active_list = list(set(actives[0]) | set([i]))
            active_list.sort(key=int)
            active_vars.append(active_list)
        return active_vars

    @property
    def graph(self):
        graph = np.zeros([self.dim,self.dim])
        graph[self.omega() != 0] = 1
        return graph

    @property
    def n_edges(self):
        return self.dim-1

class StarGraphGaussianDistribution(GaussianDistribution):
    def __init__(self, dim, edge_strength=.45):
        self.dim = dim
        self.edge_strength = edge_strength
        mu = np.zeros(dim)
        precision = self.omega()
        super(StarGraphGaussianDistribution, self).__init__(mu, precision=precision)

    def omega(self):
        # create star matrix 
        omega = np.eye(self.dim)
        omega[0,0] = self.dim
        omega[0,1:] = self.edge_strength
        omega[1:,0] = self.edge_strength
        # compute unnormalized sigma (covariance matrix)
        sigma_temp = np.linalg.inv(omega)
        # extract standard deviations from sigma_temp
        std_temp = np.diag(np.sqrt(np.diag(sigma_temp)))
        # scale omega by std_temp
        omega = np.dot(np.dot(std_temp, omega), std_temp)
        return omega

    def sigma(self):
        # return inverse of omega
        sigma = np.linalg.inv(self.omega)
        return sigma

    def rvs(self, m):
        # compute K, where K K^T = sigma
        K = np.linalg.cholesky(self.sigma)
        # generate 'base' samples from standard normal
        x = stats.norm().rvs(m*self.dim).reshape((m,self.dim))
        # return m realizations
        samples = np.dot(K, x.T).T
        return samples

    @property
    def nonzero_idxs(self):
        # find zero elements in omega to determine active_vars
        omegaLower = np.tril(self.omega())
        active_vars = []
        for i in range(self.dim):
            actives = np.where(omegaLower[i,:] != 0)
            active_list = list(set(actives[0]) | set([i]))
            active_list.sort(key=int)
            active_vars.append(active_list)
        return active_vars

    @property
    def graph(self):
        graph = np.zeros([self.dim,self.dim])
        graph[self.omega() != 0] = 1
        return graph

    @property
    def n_edges(self):
        return self.dim-1

class GridGraphGaussianDistribution(GaussianDistribution):
    def __init__(self, dim, edge_strength= 1.0):
        if (np.sqrt(dim) - int(np.sqrt(dim))) != 0:
            raise ValueError('Input dimension must be a square number')
        self.dim = dim
        self.edge_strength = edge_strength
        mu = np.zeros(dim)
        precision = self.omega()
        super(GridGraphGaussianDistribution, self).__init__(mu, precision=precision)

    def omega(self):
        dim_sq_root = int(np.sqrt(self.dim))

        # declare grid coordinates
        coords = self.zigzag(dim_sq_root)
        n_coords = len(coords)
    
        # create zero matrix
        omega = np.zeros((n_coords, n_coords))

        # pull out all coordinates
        all_coords = list(coords.values())

        # add all edges for the grid graph
        for i in range(n_coords):
            coord_val = coords[i];
            new_coords = [(coord_val[0],coord_val[1]+1), 
                          (coord_val[0],coord_val[1]-1), 
                          (coord_val[0]+1,coord_val[1]),
                          (coord_val[0]-1,coord_val[1])]
            for j in range(len(new_coords)):
                if new_coords[j] in all_coords:
                    coord_idx = all_coords.index(new_coords[j])
                    omega[i, coord_idx] = self.edge_strength
                    omega[coord_idx, i] = self.edge_strength

        # set the diagonal appropriately
        max_val = np.ceil(np.max(np.sum(np.abs(omega), axis = 0))) + 1
        omega = omega + max_val*np.eye(n_coords)
        
        # compute unnormalized sigma (covariance matrix)
        sigma_temp = np.linalg.inv(omega)
        # extract standard deviations from sigma_temp
        std_temp = np.diag(np.sqrt(np.diag(sigma_temp)))
        # scale omega by std_temp
        omega = np.dot(np.dot(std_temp, omega), std_temp)
        return omega

    def zigzag(self,n):
        # zig-zag pattern returns bijection between graph coordinates and ordering
        indexorder = sorted(((x,y) for x in range(n) for y in range(n)),
                    key = lambda p: (p[0]+p[1], -p[1] if (p[0]+p[1]) % 2 else p[1]) )
        return dict((n,index) for n,index in enumerate(indexorder))

    def sigma(self):
        # return inverse of omega
        sigma = np.linalg.inv(self.omega)
        return sigma

    def rvs(self, m):
        # compute K, where K K^T = sigma
        K = np.linalg.cholesky(self.sigma)
        # generate 'base' samples from standard normal
        x = stats.norm().rvs(m*self.dim).reshape((m,self.dim))
        # return m realizations
        samples = np.dot(K, x.T).T
        return samples

    @property
    def nonzero_idxs(self):
        #dim_sq = np.power(self.dim,2)

        # extract lower triangular matrix
        omegaLower = np.tril(self.omega())

        # add edges by...
        # variable elimination moving from highest node (dim-1) to node 2 (at most)
        for i in range(self.dim-1,1,-1):
            non_zero_ind  = np.where(omegaLower[i,:i] != 0)[0]
            if len(non_zero_ind) > 1:
                co_parents = list(itertools.combinations(non_zero_ind,2))
                for j in range(len(co_parents)):
                    row_index = max(co_parents[j])
                    col_index = min(co_parents[j])
                    omegaLower[row_index, col_index] = 1.0

        # find zero elements in chordal omega to determine active_vars
        active_vars = []
        for i in range(self.dim):
            actives = np.where(omegaLower[i,:] != 0)
            active_list = list(set(actives[0]) | set([i]))
            active_list.sort(key=int)
            active_vars.append(active_list)

        return active_vars

    @property
    def graph(self):
        graph = np.zeros([self.dim,self.dim])
        graph[self.omega() != 0] = 1
        return graph

    @property
    def n_edges(self):
        return 2.*(np.sqrt(self.dim) - 1)**2

###############################################################
# Definition of miscellaneous densities (No sampling defined) #
###############################################################
class LogNormalDistribution(FrozenDistribution_1d):
    def __init__(self, s, mu, scale):
        super(LogNormalDistribution,self).__init__()
        self.s = s
        self.mu = mu
        self.scale = scale
        self.dist = stats.lognorm(s=s,
                                  loc=mu,
                                  scale=scale)
    def rvs(self, n, *args, **kwargs):
        return self.dist.rvs(n).reshape((n,1))
    @counted
    def pdf(self, x, *args, **kwargs):
        return self.dist.pdf( x ).flatten()
    @counted
    def grad_x_pdf(self, x, *args, **kwargs):
        s = self.s
        m = self.mu
        d = self.dist
        return - d.pdf(x) * ( 1./(x-m) + np.log(x-m)/(s**2.*(x-m)) )
    @counted
    def log_pdf(self, x, *args, **kwargs):
        return self.dist.logpdf( x ).flatten()
    @counted
    def grad_x_log_pdf(self, x, *args, **kwargs):
        s = self.s
        m = self.mu
        sc = self.scale
        return - 1./(x-m) * (np.log((x-m)/sc)/s**2. + 1)
    @counted
    def hess_x_log_pdf(self, x, *args, **kwargs):
        s = self.s
        m = self.mu
        sc = self.scale
        return (1./(x-m)**2. * ( (np.log((x-m)/sc) + s**2. - 1.)/s**2. ))[:,:,nax]

class LogisticDistribution(FrozenDistribution_1d):
    def __init__(self, mu, s):
        super(LogisticDistribution,self).__init__()
        self.mu = mu
        self.s = s
        self.dist = stats.logistic(loc=mu,scale=s)
    def rvs(self, n, *args, **kwargs):
        return self.dist.rvs(n).reshape((n,1))
    @counted
    def pdf(self, x, *args, **kwargs):
        return self.dist.pdf(x).flatten()
    @counted
    def log_pdf(self, x, *args, **kwargs):
        # Log pdf with modified asymptotic behavior
        out = np.zeros(x.shape)
        g20 = (x >= -20)
        l20 = (x < -20)
        out[g20] = self.dist.logpdf(x[g20]).flatten()
        out[l20] = (x[l20].flatten() - self.mu)/self.s
        return out.flatten()
    @counted
    def grad_x_log_pdf(self, x, *args, **kwargs):
        mu = self.mu
        s = self.s
        out = np.zeros(x.shape)
        g20 = (x >= -20)
        l20 = (x < -20)
        g = np.exp(-(x[g20]-mu)/s)
        out[g20] = -1./s + 2./s * g/(1+g)
        out[l20] = 1./s
        return out
    @counted
    def hess_x_log_pdf(self, x, *args, **kwargs):
        mu = self.mu
        s = self.s
        out = np.zeros(x.shape)
        g20 = (x >= -20)
        l20 = (x < -20)
        g = np.exp(-(x[g20]-mu)/s)
        out[g20] = (- 2./s**2. * g/(1+g)**2.)
        out[l20] = 0.
        return out[:,:,nax]
    # def nabla3_x_log_pdf(self, x, params=None):
    #     mu = self.mu
    #     s = self.s
    #     g = np.exp(-(x-mu)/s)
    #     return (2./s**3. * g*(1-g)/(1+g)**3.)[:,:,nax,nax]

class GammaDistribution(FrozenDistribution_1d):
    def __init__(self, kappa, theta):
        super(GammaDistribution,self).__init__()
        self.kappa = kappa
        self.theta = theta
        self.dist = stats.gamma(kappa, scale=theta)
    def rvs(self, n, *args, **kwargs):
        return self.dist.rvs(n).reshape((n,1))
    @counted
    def pdf(self, x, *args, **kwargs):
        return self.dist.pdf(x).flatten()
    @counted
    def log_pdf(self, x, *args, **kwargs):
        return self.dist.logpdf(x).flatten()
    @counted
    def grad_x_log_pdf(self, x, *args, **kwargs):
        k = self.kappa
        t = self.theta
        return (k-1.)/x - 1/t
    @counted
    def hess_x_log_pdf(self, x, *args, **kwargs):
        k = self.kappa
        return ((1.-k)/x**2.)[:,:,nax]
    @counted
    def nabla3_x_log_pdf(self, x, *args, **kwargs):
        k = self.kappa
        return (2.*(k-1.)/x**3.)[:,:,nax,nax]

class BetaDistribution(FrozenDistribution_1d):
    def __init__(self, alpha, beta):
        super(BetaDistribution,self).__init__()
        self.alpha = alpha
        self.beta = beta
        self.dist = stats.beta(alpha, beta)
    def rvs(self, n, *args, **kwargs):
        return self.dist.rvs(n).reshape((n,1))
    @counted
    def pdf(self, x, *args, **kwargs):
        return self.dist.pdf(x).flatten()
    @counted
    def log_pdf(self, x, *args, **kwargs):
        return self.dist.logpdf(x).flatten()
    @counted
    def grad_x_log_pdf(self, x, *args, **kwargs):
        a = self.alpha
        b = self.beta
        return (a-1.)/x + (b-1.)/(x-1.)
    @counted
    def hess_x_log_pdf(self, x, *args, **kwargs):
        a = self.alpha
        b = self.beta
        out = (1.-a)/x**2. + (1-b)/(x-1.)**2.
        return out[:,:,nax]
    @counted
    def nabla3_x_log_pdf(self, x, *args, **kwargs):
        a = self.alpha
        b = self.beta
        out = 2.*(a-1.)/x**3. + 2.*(b-1.)/(x-1.)**3.
        return out[:,:,nax,nax]

class UniformDistribution(Distribution):
    def __init__(self, dim=1):
        super(UniformDistribution, self).__init__(dim)
        self.dist = stats.uniform()
    def rvs(self, n, *args, **kwargs):
        return self.dist.rvs(n*self.dim).reshape((n,self.dim))
    @counted
    def pdf(self, x, *args, **kwargs):
        return np.prod(self.dist.pdf(x), axis=1)
    @counted
    def log_pdf(self, x, *args, **kwargs):
        return np.sum(self.dist.logpdf(x), axis=1)
    @counted
    def grad_x_log_pdf(self, x, *args, **kwargs):
        return np.zeros((x.shape[0],self.dim))
    @counted
    def hess_x_log_pdf(self, x, *args, **kwargs):
        return np.zeros((x.shape[0],self.dim,self.dim))
        
class GumbelDistribution(FrozenDistribution_1d):
    def __init__(self, mu, beta):
        super(GumbelDistribution,self).__init__()
        self.mu = mu
        self.beta = beta
        self.dist = stats.gumbel_r(loc=mu, scale=beta)
    def rvs(self, n, *args, **kwargs):
        return self.dist.rvs(n).reshape((n,1))
    @counted
    def pdf(self, x, *args, **kwargs):
        return self.dist.pdf(x).flatten()
    @counted
    def log_pdf(self, x, *args, **kwargs):
        return self.dist.logpdf(x).flatten()
    @counted
    def grad_x_log_pdf(self, x, *args, **kwargs):
        m = self.mu
        b = self.beta
        z = (x-m)/b
        return (np.exp(-z)-1.)/b
    @counted
    def hess_x_log_pdf(self, x, *args, **kwargs):
        m = self.mu
        b = self.beta
        z = (x-m)/b
        return (- np.exp(-z)/b**2.)[:,:,nax]
    @counted
    def nabla3_x_log_pdf(self, x, *args, **kwargs):
        m = self.mu
        b = self.beta
        z = (x-m)/b
        return (np.exp(-z)/b**3.)[:,:,nax,nax]

class WeibullDistribution(FrozenDistribution_1d):
    def __init__(self, c, mu=0., sigma=1.):
        super(WeibullDistribution,self).__init__()
        self.c = c
        self.mu = mu
        self.sigma=sigma
        self.dist = stats.weibull_min(c=self.c, loc=self.mu, scale=self.sigma)
    def rvs(self, n, *args, **kwargs):
        return self.dist.rvs(n).reshape((n,1))
    @counted
    def pdf(self, x, *args, **kwargs):
        return self.dist.pdf(x).flatten()
    @counted
    def log_pdf(self, x, *args, **kwargs):
        return self.dist.logpdf(x).flatten()
    @counted
    def grad_x_log_pdf(self, x, *args, **kwargs):
        c = self.c
        m = self.mu
        s = self.sigma
        out = (c-1.)/(x-m) - c/s * ((x-m)/s)**(c-1.)
        return out
    @counted
    def hess_x_log_pdf(self, x, *args, **kwargs):
        c = self.c
        m = self.mu
        s = self.sigma
        out = - (c-1.)/(x-m)**2. - (c*(c-1.))/s**2. * ((x-m)/s)**(c-2.)
        return out[:,:,nax]

class CauchyDistribution(FrozenDistribution_1d):
  def __init__(self, loc, scale):
    self.loc = loc
    self.scale = scale
  def pdf(self,x,params=None):
    out = stats.cauchy.pdf(x, loc = self.loc, scale = self.scale)
    return out.flatten()
  def log_pdf(self,x,params=None):
    out = stats.cauchy.logpdf(x, loc = self.loc, scale = self.scale)
    return out.flatten()
  def rvs(self,n):
    out = stats.cauchy.rvs(size=n)
    return out
  def quadrature(self,qtype,qparams):
    if qtype == 0:
      x = qparams
      l = qparams.shape[0]
      w = np.ones(l)/l
    else:
      raise NotImplementedError("Not implemented")
    return (x,w)

class StudentTDistribution(FrozenDistribution_1d):
    def __init__(self, df, mu=0., sigma=1.):
        super(StudentTDistribution,self).__init__()
        if df < 1:
            raise AttributeError("df must be >= 1")
        self.mu = mu
        self.sigma = sigma
        self.df = df
        self.dist = stats.t(df, loc=mu, scale=sigma)
    def rvs(self, n, *args, **kwargs):
        return self.dist.rvs(n).reshape((n,1))
    @counted
    def pdf(self, x, *args, **kwargs):
        return self.dist.pdf(x).flatten()
    @counted
    def log_pdf(self, x, *args, **kwargs):
        return self.dist.logpdf(x).flatten()
    @counted
    def grad_x_log_pdf(self, x, *args, **kwargs):
        m = self.mu
        s = self.sigma
        k = self.df
        return - (k+1)*(x-m)/(k*s**2 + (x-m)**2)
    @counted
    def hess_x_log_pdf(self, x, *args, **kwargs):
        m = self.mu
        s = self.sigma
        k = self.df
        out =  - (k+1)/(k*s**2 + (x-m)**2) + \
               2*(k+1)*(x-m)**2/(k*s**2 + (x-m)**2)**2
        return out[:,:,nax]
        
class BananaDistribution(PushForwardTransportMapDistribution):
    def __init__(self, a, b, mu, sigma2):
        import TransportMaps.Maps as MAPS
        gauss_map = AffineTransportMap(c=mu, L=npla.cholesky(sigma2))
        ban_map = FrozenBananaMap(a, b)
        tm = CompositeTransportMap(ban_map, gauss_map)
        base_distribution = StandardNormalDistribution(2)
        super(BananaDistribution, self).__init__(tm, base_distribution)

class RelaxedRademacherDistribution(Distribution):
    def __init__(self, dim):
        if dim%2 != 0:
            raise ValueError("Input dimension must be an even number")
        self.dim = dim

    def rvs(self, m):
        rvs = np.zeros([m, self.dim])
        for i in range(0,self.dim,2):
            rvs[:,i] = stats.norm.rvs(size=m)
            unif = 2*stats.uniform.rvs(size=m) - 1
            rvs[:,i+1] = rvs[:,i] * unif
        return rvs

    @property
    def graph(self):
        graph = np.eye(self.dim)
        for i in range(0,self.dim,2):
            graph[i,i+1] = 1
            graph[i+1,i] = 1
        return graph

    @property
    def nonzero_idxs(self):
        # find zero elements in omega to determine active_vars
        graphLower = np.tril(self.graph())
        active_vars = []
        for i in range(self.dim):
            actives = np.where(graphLower[i,:] != 0)
            active_list = list(set(actives[0]) | set([i]))
            active_list.sort(key=int)
            active_vars.append(active_list)
        return active_vars
        
    @property
    def n_edges(self):
        return self.dim/2.

class ButterflyDistribution(Distribution):
    def __init__(self, dim):
        if dim%2 != 0:
            raise ValueError("Input dimension must be an even number")
        self.dim = dim

    def rvs(self, m):
        rvs = np.zeros([m, self.dim])
        for i in range(0,self.dim,2):
            rvs[:,i] = stats.norm.rvs(size=m)
            norm = stats.norm.rvs(size=m)
            rvs[:,i+1] = rvs[:,i] * norm
        return rvs

    @property
    def graph(self):
        graph = np.eye(self.dim)
        for i in range(0,self.dim,2):
            graph[i,i+1] = 1
            graph[i+1,i] = 1
        return graph

    @property
    def nonzero_idxs(self):
        # find zero elements in omega to determine active_vars
        graphLower = np.tril(self.graph())
        active_vars = []
        for i in range(self.dim):
            actives = np.where(graphLower[i,:] != 0)
            active_list = list(set(actives[0]) | set([i]))
            active_list.sort(key=int)
            active_vars.append(active_list)
        return active_vars
        
    @property
    def n_edges(self):
        return self.dim/2.

