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

from TransportMaps import mpi_map
from TransportMaps.Samplers.SamplerBase import *

__all__ = ['ImportanceSampler', 'RejectionSampler']

class ImportanceSampler(Sampler):
    r""" Importance sampler of distribution ``d``, with biasing distribution ``d_bias``

    Args:
      d (Distributions.Distribution): distribution to sample from
      d_bias (Distributions.Distribution): biasing distribution
    """
    def __init__(self, d, d_bias):
        if d.dim != d_bias.dim:
            raise ValueError("Dimension of the densities ``d`` and ``d_bias`` must " + \
                             "be the same")
        super(ImportanceSampler, self).__init__(d)
        self.bias_distribution = d_bias

    def rvs(self, m, mpi_pool_tuple=(None, None)):
        r""" Generate :math:`m` samples and importance weights from the distribution

        Args:
          m (int): number of samples to generate

        Returns:
          (:class:`tuple` (:class:`ndarray<numpy.ndarray>` [:math:`m,d`], :class:`ndarray<numpy.ndarray>` [:math:`m`])) -- list of points and weights
        """
        samps = self.bias_distribution.rvs(m, mpi_pool=mpi_pool_tuple[1])
        scatter_tuple = (['x'], [samps])
        num = mpi_map('pdf', obj=self.distribution, scatter_tuple=scatter_tuple,
                      mpi_pool=mpi_pool_tuple[0])
        den = mpi_map('pdf', obj=self.bias_distribution, scatter_tuple=scatter_tuple,
                      mpi_pool=mpi_pool_tuple[1])
        weights = num/den
        weights /= np.sum(weights)
        return (samps, weights)

class RejectionSampler(Sampler):
    r""" Rejection sampler of distribution ``d``, with biasing distribution ``d_bias``

    Args:
      d (Distributions.Distribution): distribution to sample from
      d_bias (Distributions.Distribution): biasing distribution
      factor (float): scaling factor to allow the biasing distribution to dominate
    """
    def __init__(self, d, d_bias, factor):
        if d.dim != d_bias.dim:
            raise ValueError("Dimension of the densities ``d`` and ``d_bias`` must " + \
                             "be the same")
        super(RejectionSampler, self).__init__(d)
        self.bias_distribution = d_bias
        self.factor = factor

    def rvs(self, m, *args, **kwargs):
        r""" Generate :math:`m` samples and importance weights from the distribution

        Args:
          m (int): number of samples to generate

        Optional Kwags:
          maxtrialmul (int): multiplicator of ``m`` giving the number of maximum trial samples.
            Default is 100.

        Returns:
          (:class:`tuple` (:class:`ndarray<numpy.ndarray>` [:math:`m,d`], :class:`ndarray<numpy.ndarray>` [:math:`m`])) -- list of points and weights
        """
        maxtrialmul = kwargs.get('maxtrialmul', 100)
        maxtrial = m * maxtrialmul
        smpls = np.zeros((m, self.distribution.dim))
        it = 0
        jj = 0
        while jj < m and it < maxtrial:
            # Compute acceptance probabilities in chunks
            rnd_smpls = self.bias_distribution.rvs(m-jj)
            rnd_bernoulli = npr.random(m-jj)
            accprob = self.distribution.pdf(rnd_smpls) / self.factor
            # Accept / reject
            acc = rnd_smpls[rnd_bernoulli<accprob,:][:m-jj,:]
            nacc = acc.shape[0]    
            smpls[jj:jj+nacc,:] = acc
            it += m-jj
            jj += nacc
        if it == maxtrial:
            raise RuntimeError(
                "Accept/reject maximum number of iterations reached"
            )
        return smpls
