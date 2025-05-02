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

import logging
import pickle
import numpy as np
import numpy.linalg as npla
import scipy.optimize as sciopt

from ..Misc import \
    required_kwargs, \
    deprecate
from ..MPI import mpi_map, mpi_map_alloc_dmem, mpi_bcast_dmem

from .LinearSpanParametricTriangularComponentwiseMapBase import \
    LinearSpanParametricTriangularComponentwiseMap, \
    CommonBasisLinearSpanParametricTriangularComponentwiseMap
from .ParametricTriangularComponentwiseTransportMapBase import \
    ParametricTriangularComponentwiseTransportMap

__all__ = [
    'NonMonotoneParametricTriangularComponentwiseTransportMap',
    'NonMonotoneLinearSpanParametricTriangularComponentwiseTransportMap',
    'NonMonotoneCommonBasisLinearSpanParametricTriangularComponentwiseTransportMap',
    # Deprecated
    'LinearSpanTriangularTransportMap',
    'CommonBasisLinearSpanTriangularTransportMap',
    'MonotonicLinearSpanTriangularTransportMap',
    'MonotonicCommonBasisLinearSpanTriangularTransportMap'
]

nax = np.newaxis


class NonMonotoneParametricTriangularComponentwiseTransportMap(
        ParametricTriangularComponentwiseTransportMap
):
    pass


class NonMonotoneLinearSpanParametricTriangularComponentwiseTransportMap(
        LinearSpanParametricTriangularComponentwiseMap,
        NonMonotoneParametricTriangularComponentwiseTransportMap
):
    r""" :class:`LinearSpanParametricTriangularComponentwiseMap` which allows for kl-minimization by enforcing pointwise constraints
    """
    @required_kwargs('active_vars', 'approx_list')
    def __init__(self, **kwargs):
        r"""
        Kwargs:
          active_vars (:class:`list<list>` [:math:`d`] of :class:`list<list>`): for
            each dimension lists the active variables.
          approx_list (:class:`list<list>` [:math:`d`] of :class:`LinearSpanTensorizedParametricFunctional<TransportMaps.Maps.Functionals.LinearSpanTensorizedParametricFunctional`):
            list of parametric functionals for each dimension
          full_basis_list (:class:`list` of :class:`list`): list of basis for each input
            of each component for a full triangular map
            (this is needed for some adaptivity algorithm)
        """
        super(NonMonotoneLinearSpanParametricTriangularComponentwiseTransportMap,
              self).__init__(**kwargs)

    def get_default_init_values_minimize_kl_divergence(self):
        return self.get_identity_coeffs()


class NonMonotoneCommonBasisLinearSpanParametricTriangularComponentwiseTransportMap(
        CommonBasisLinearSpanParametricTriangularComponentwiseMap,
        NonMonotoneParametricTriangularComponentwiseTransportMap
):
    r""" :class:`CommonBasisLinearSpanParametricTriangularComponentwiseMap` which allows for kl-minimization by enforcing pointwise constraints
    """
    @required_kwargs('active_vars', 'approx_list')
    def __init__(self, **kwargs):
        r"""
        Kwargs:
          active_vars (:class:`list<list>` [:math:`d`] of :class:`list<list>`): for
            each dimension lists the active variables.
          approx_list (:class:`list<list>` [:math:`d`] of :class:`LinearSpanTensorizedParametricFunctional<TransportMaps.Maps.Functionals.LinearSpanTensorizedParametricFunctional`):
            list of parametric functionals for each dimension
          full_basis_list (:class:`list` of :class:`list`): list of basis for each input
            of each component for a full triangular map
            (this is needed for some adaptivity algorithm)
        """
        super(NonMonotoneCommonBasisLinearSpanParametricTriangularComponentwiseTransportMap,
              self).__init__(**kwargs)

    def get_default_init_values_minimize_kl_divergence(self):
        return self.get_identity_coeffs()

##############
# DEPRECATED #
##############
    
class MonotonicLinearSpanTriangularTransportMap(
        NonMonotoneLinearSpanParametricTriangularComponentwiseTransportMap
):
    @deprecate(
        'MonotonicLinearSpanTriangularTransportMap',
        '3.0',
        'Use Maps.NonMonotoneLinearSpanParametricTriangularComponentwiseTransportMap instead.'
    )
    def __init__(self, active_vars, approx_list):
        super(MonotonicLinearSpanTriangularTransportMap, self).__init__(
            active_vars=active_vars,
            approx_list=approx_list
        )

class MonotonicCommonBasisLinearSpanTriangularTransportMap(
        NonMonotoneCommonBasisLinearSpanParametricTriangularComponentwiseTransportMap
):
    @deprecate(
        'MonotonicCommonBasisLinearSpanTriangularTransportMap',
        '3.0',
        'Use Maps.NonMonotoneCommonBasisLinearSpanParametricTriangularComponentwiseTransportMap instead.'
    )
    def __init__(self, active_vars, approx_list):
        super(MonotonicCommonBasisLinearSpanTriangularTransportMap,
              self).__init__(
            active_vars=active_vars,
            approx_list=approx_list
        )

class LinearSpanTriangularTransportMap(
        NonMonotoneLinearSpanParametricTriangularComponentwiseTransportMap
):
    @deprecate(
        'LinearSpanTriangularTransportMap',
        '3.0',
        'Use Maps.NonMonotoneLinearSpanParametricTriangularComponentwiseTransportMap instead.'
    )
    def __init__(self, active_vars, approx_list):
        super(LinearSpanTriangularTransportMap, self).__init__(
            active_vars=active_vars,
            approx_list=approx_list
        )

class CommonBasisLinearSpanTriangularTransportMap(
        NonMonotoneCommonBasisLinearSpanParametricTriangularComponentwiseTransportMap
):
    @deprecate(
        'CommonBasisLinearSpanTriangularTransportMap',
        '3.0',
        'Use Maps.NonMonotoneCommonBasisLinearSpanParametricTriangularComponentwiseTransportMap instead.'
    )
    def __init__(self, active_vars, approx_list):
        super(CommonBasisLinearSpanTriangularTransportMap, self).__init__(
            active_vars=active_vars,
            approx_list=approx_list
        )
