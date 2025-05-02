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

from TransportMaps.DerivativesChecks import \
    fd_gradient_check, \
    action_hess_check
from TransportMaps.Misc import counted, cached, cached_tuple

from .DistributionBase import Distribution

__all__ = [
    'ProductDistribution'
]

class ProductDistribution(Distribution):
    r""" Abstract distribution :math:`\nu(A_1\times\cdots\times A_n) = \nu_1(A_1)\cdots\nu_n(A_n)`
    """
    def get_component(self, avars):
        r""" [Abstract] return the measure :math:`\nu_{a_1}\times\cdots\times\nu_{a_k}`

        Args:
          avars (list): list of coordinates to extract from :math:`\nu`
        """
        raise NotImplementedError("To be implemented in subclasses")
