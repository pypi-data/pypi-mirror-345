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

from .SequentialInferenceDistributions import Lag1TransitionDistribution
from TransportMaps.Distributions.FrozenDistributions import \
    NormalDistribution
from TransportMaps.Distributions.ConditionalDistributions import \
    ConditionallyNormalDistribution
from TransportMaps.Maps import \
    ConditionallyLinearMap, AffineMap

__all__ = [
    'LinearNormalAR1TransitionDistribution',
    'LinearGaussianAR1TransitionDistribution',
    'ConditionallyLinearNormalAR1TransitionDistribution',
    'ConditionallyLinearGaussianAR1TransitionDistribution']


class LinearNormalAR1TransitionDistribution(Lag1TransitionDistribution):
    r""" Transition probability distribution :math:`g({\bf x}_{k-1},{\bf x}_k) = \pi_{{\bf X}_k \vert {\bf X}_{k-1}={\bf x}_{k-1}}({\bf x}_k) = \pi({\bf x}_k - F_k {\bf x}_{k-1} - {\bf c}_k)` where :math:`\pi \sim \mathcal{N}(\mu_k,Q_k)`.

    This represents the following Markov transition model:

    .. math::

       {\bf x}_k = c_k + F_k {\bf x}_{k-1} + {\bf w}_k \\
       {\bf w}_k \sim \mathcal{N}(\mu,Q_k)

    where the control :math:`{\bf c}_k := B_k {\bf u}_k` can be used for control purposes
    
    Args:
      ck (:class:`ndarray<numpy.ndarray>` [:math:`d`] or :class:`Map<TransportMaps.Maps.Map>`): constant part or map returning the constant part given some parameters
      Fk (:class:`ndarray<numpy.ndarray>` [:math:`d,d`] or :class:`Map<TransportMaps.Maps.Map>`): state transition matrix (dynamics) or map returning the linear part given some parametrs
      mu (:class:`ndarray<numpy.ndarray>` [:math:`d`] or :class:`Map<TransportMaps.Maps.Map>`): mean :math:`\mu_k` or parametric map for :math:`\mu_k(\theta)`
      covariance (:class:`ndarray<numpy.ndarray>` [:math:`d,d`] or :class:`Map<TransportMaps.Maps.Map>`): covariance :math:`Q_k` or parametric map for :math:`Q_k(\theta)`
      precision (:class:`ndarray<numpy.ndarray>` [:math:`d,d`] or :class:`Map<TransportMaps.Maps.Map>`): precision :math:`Q_k^{-1}` or parametric map for :math:`Q_k^{-1}(\theta)`
    """
    def __init__(self, ck, Fk, mu, covariance=None, precision=None,
                 coeffs=None):
        Fmap = AffineMap(c=ck, L=Fk)
        pi = NormalDistribution(mu, covariance=covariance, precision=precision)
        super(LinearNormalAR1TransitionDistribution, self).__init__(
            pi, Fmap)


LinearGaussianAR1TransitionDistribution = LinearNormalAR1TransitionDistribution


class ConditionallyLinearNormalAR1TransitionDistribution(Lag1TransitionDistribution):
    r""" Transition probability distribution :math:`g(\theta,{\bf x}_{k-1},{\bf x}_k) = \pi_{{\bf X}_k \vert {\bf X}_{k-1}={\bf x}_{k-1}}({\bf x}_k, \Theta=\theta) = \pi({\bf x}_k - F_k(\theta) {\bf x}_{k-1} - {\bf c}_k(\theta))` where :math:`\pi \sim \mathcal{N}(\mu_k(\theta),Q_k(\theta))`.

    This represents the following Markov transition model:

    .. math::

       {\bf x}_k = c_k + F_k {\bf x}_{k-1} + {\bf w}_k \\
       {\bf w}_k \sim \mathcal{N}(\mu,Q_k)

    where the control :math:`{\bf c}_k := B_k {\bf u}_k` can be used for control purposes
    
    Args:
      ck (:class:`ndarray<numpy.ndarray>` [:math:`d`] or :class:`Map<TransportMaps.Maps.Map>`): constant part or map returning the constant part given some parameters
      Fk (:class:`ndarray<numpy.ndarray>` [:math:`d,d`] or :class:`Map<TransportMaps.Maps.Map>`): state transition matrix (dynamics) or map returning the linear part given some parametrs
      mu (:class:`ndarray<numpy.ndarray>` [:math:`d`] or :class:`Map<TransportMaps.Maps.Map>`): mean :math:`\mu_k` or parametric map for :math:`\mu_k(\theta)`
      covariance (:class:`ndarray<numpy.ndarray>` [:math:`d,d`] or :class:`Map<TransportMaps.Maps.Map>`): covariance :math:`Q_k` or parametric map for :math:`Q_k(\theta)`
      precision (:class:`ndarray<numpy.ndarray>` [:math:`d,d`] or :class:`Map<TransportMaps.Maps.Map>`): precision :math:`Q_k^{-1}` or parametric map for :math:`Q_k^{-1}(\theta)`
      coeffs (:class:`ndarray<numpy.ndarray>`): fixing the coefficients :math:`\theta`
    """
    def __init__(self, ck, Fk, mu, covariance=None, precision=None, coeffs=None):
        # DISTRIBUTION
        if isinstance(mu, np.ndarray) and (
                (covariance is not None and isinstance(covariance, np.ndarray)) or
                (precision is not None and isinstance(precision, np.ndarray)) ):
            pi = NormalDistribution(mu, covariance=covariance, precision=precision)
        else:
            pi = ConditionallyNormalDistribution(mu, sigma=covariance, precision=precision)
        Fmap = ConditionallyLinearMap(ck, Fk)
        super(ConditionallyLinearNormalAR1TransitionDistribution, self).__init__(
            pi, Fmap)
        self.coeffs = coeffs

    @property
    def n_coeffs(self):
        return self._n_coeffs
        
    @property
    def coeffs(self):
        return self._coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        if coeffs is not None:
            self.T.coeffs = coeffs
            if self.isPiCond:
                self.pi.coeffs = coeffs
            self._coeffs = coeffs


ConditionallyLinearGaussianAR1TransitionDistribution = ConditionallyLinearNormalAR1TransitionDistribution
            
