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

import logging
import numpy as np
import numpy.linalg as npla
import scipy.optimize as sciopt

from ...Misc import deprecate
from ...MPI import mpi_map, mpi_map_alloc_dmem, mpi_bcast_dmem, \
    SumChunkReduce

from .ParametricFunctionalBase import ParametricFunctional
from .MonotoneFunctionalBase import MonotoneFunctional

__all__ = [
    'ParametricMonotoneFunctional',
    'MonotonicFunctionApproximation'
]


class ParametricMonotoneFunctional(
        ParametricFunctional,
        MonotoneFunctional
):
    r""" Abstract class for the prametric functional :math:`f \approx f_{\bf a} = \sum_{{\bf i} \in \mathcal{I}} {\bf a}_{\bf i} \Phi_{\bf i}` assumed to be monotonic in :math:`x_d`
    """

    def get_default_init_values_regression(self):
        return self.get_identity_coeffs()
        
    def get_default_init_values_minimize_kl_divergence_component(self):
        return self.get_identity_coeffs()

    def precomp_minimize_kl_divergence_component(self, x, params, precomp_type='uni'):
        r""" Precompute necessary structures for the speed up of :func:`minimize_kl_divergence_component`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters to be updated
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'

        Returns:
           (:class:`tuple<tuple>` (None,:class:`dict<dict>`)) -- dictionary of necessary
              strucutres. The first argument is needed for consistency with 
        """
        self.precomp_evaluate(x, params['params_t'], precomp_type)
        self.precomp_partial_xd(x, params['params_t'], precomp_type)

    def allocate_cache_minimize_kl_divergence_component(self, x):
        r""" Allocate cache space for the KL-divergence minimization

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
        """
        cache = {'tot_size': x.shape[0]}
        return (cache, )

    def reset_cache_minimize_kl_divergence_component(self, cache):
        r""" Reset the objective part of the cache space for the KL-divergence minimization

        Args:
          params2 (dict): dictionary of precomputed values
        """
        tot_size = cache['tot_size']
        cache.clear()
        cache['tot_size'] = tot_size

    def minimize_kl_divergence_component_callback(self, xk):
        self.it_callback += 1
        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            self.logger.debug("Iteration %d" % self.it_callback)
        if self.ders_callback == 2:
            self.params_callback['hess_assembled'] = False


##############
# DEPRECATED #
##############

class MonotonicFunctionApproximation(ParametricMonotoneFunctional):
    @deprecate(
        'MonotonicFunctionApproximation',
        '3.0',
        'Use Funtionals.ParametricMonotoneFunctional instead.'
    )
    def __init__(self, *args, **kwars):
        super(MonotonicFunctionApproximation, self).__init__(*args, **kwars)
