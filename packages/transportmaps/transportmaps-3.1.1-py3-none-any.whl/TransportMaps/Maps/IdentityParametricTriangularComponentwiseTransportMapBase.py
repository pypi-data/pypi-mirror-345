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

from ..Misc import \
    required_kwargs

from .Functionals import \
    IdentityParametricMonotoneFunctional

from .ParametricTriangularComponentwiseTransportMapBase import \
    ParametricTriangularComponentwiseTransportMap

__all__ = [
    'IdentityParametricTriangularComponentwiseTransportMap',
]


class IdentityParametricTriangularComponentwiseTransportMap(
        ParametricTriangularComponentwiseTransportMap
):
    r""" Identity transport map with interface for optimization.
    """
    @required_kwargs('dim')
    def __init__(self, **kwargs):
        approx_list = [IdentityParametricMonotoneFunctional()] * kwargs['dim']
        active_vars = [ [i] for i in range(kwargs['dim']) ]
        super(IdentityParametricTriangularComponentwiseTransportMap,
              self).__init__(
                  approx_list=approx_list,
                  active_vars=active_vars
              )

    def get_identity_coeffs(self):
        return np.zeros(0)
        
    def get_default_init_values_minimize_kl_divergence(self):
        return np.zeros(0)
    










