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

from .DistributionBase import Distribution
from .ParametricDistributionBase import ParametricDistribution
from .TransportMapDistributionBase import TransportMapDistribution
from ..Maps import ParametricTransportMap

__all__ = [
    'ParametricTransportMapDistribution',
]


class ParametricTransportMapDistribution(
        ParametricDistribution,
        TransportMapDistribution
):
    r""" Abstract class for distribution defined by parametric transport maps (:math:`T^\sharp \pi` or :math:`T_\sharp \pi`)

    Args:
      transport_map (:class:`TransportMap<TransportMaps.Maps.ParametricTransportMap>`): transport map :math:`T`
      base_distribution (:class:`Distribution`): distribution :math:`\pi``

    .. seealso:: :class:`PushForwardTransportMapDistribution` and :class:`PullBackTransportMapDistribution`.
    """

    def __init__(
            self,
            transport_map: ParametricTransportMap,
            base_distribution: Distribution
    ):
        super(ParametricTransportMapDistribution, self).__init__(
            transport_map=transport_map,
            base_distribution=base_distribution
        )

    @property
    def coeffs(self):
        r""" Get the coefficients :math:`{\bf a}` of the distribution

        .. seealso:: :func:`ParametricDistribution.coeffs`
        """
        return self.transport_map.coeffs

    @property
    def n_coeffs(self):
        r""" Get the number :math:`N` of coefficients
        
        .. seealso:: :func:`ParametricDistribution.n_coeffs`
        """
        return self.transport_map.n_coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients :math:`{\bf a}` of the distribution

        .. seealso:: :func:`ParametricDistribution.coeffs`
        """
        self.transport_map.coeffs = coeffs

    def _evaluate_grad_a_log_pullback(self, gxlpdf, ga_list, galdgx):
        out = np.zeros((gxlpdf.shape[0], self.transport_map.n_coeffs))
        start = 0
        for k, grad in enumerate(ga_list):
            stop = start + grad.shape[1]
            out[:, start:stop] = gxlpdf[:, k, np.newaxis] * grad
            start = stop
        out += galdgx
        return out
