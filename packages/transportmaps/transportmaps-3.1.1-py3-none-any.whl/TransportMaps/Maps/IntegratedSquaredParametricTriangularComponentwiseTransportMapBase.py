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
    required_kwargs, \
    deprecate

from .Functionals import \
    IntegratedSquaredParametricMonotoneFunctional

from .ParametricTriangularComponentwiseTransportMapBase import \
    ParametricTriangularComponentwiseTransportMap

__all__ = [
    'IntegratedSquaredParametricTriangularComponentwiseTransportMap',
    # Deprecated
    'IntegratedSquaredTriangularTransportMap',
]

nax = np.newaxis


class IntegratedSquaredParametricTriangularComponentwiseTransportMap(
        ParametricTriangularComponentwiseTransportMap
):
    r""" Triangular transport map where each component is represented by a :class:`IntegratedSquaredParametricMonotoneFunctional<TransportMaps.Maps.Functionals.IntegratedSquaredParametricMonotoneFunctional>`.
    """
    @required_kwargs('active_vars', 'approx_list')
    def __init__(self, **kwargs):
        r"""
        Kwargs:
          active_vars (:class:`list<list>` [:math:`d`] of :class:`list<list>`): for
            each dimension lists the active variables.
          approx_list (:class:`list<list>` [:math:`d`] of :class:`IntegratedSquaredParametricMonotoneFunctional<TransportMaps.Maps.Functionals.IntegratedSquaredParametricMonotoneFunctional>`):
            list of parametric monotone functionals for each dimension
          full_c_basis_list (:class:`list` of :class:`list`): list of basis for each input
            of the constant part of each component for a full triangular map
            (this is needed for some adaptivity algorithm)
          full_h_basis_list (:class:`list` of :class:`list`): list of basis for each input
            of the constant part of each component for a full triangular map
            (this is needed for some adaptivity algorithm)
        """
        approx_list = kwargs['approx_list']
        if not all( [
                isinstance(a, IntegratedSquaredParametricMonotoneFunctional)
                for a in approx_list
        ] ):
            raise ValueError("All the approximation functions must be instances " +
                             "of the class IntegratedSquaredParametricMonotoneFunctional")
        super(IntegratedSquaredParametricTriangularComponentwiseTransportMap,
              self).__init__(**kwargs)
        self.full_c_basis_list = kwargs.get('full_c_basis_list')
        self.full_h_basis_list = kwargs.get('full_h_basis_list')
        

    def get_identity_coeffs(self):
        r""" Returns the coefficients corresponding to the identity map

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
        """
        # Define the identity map
        coeffs = []
        for a in self.approx_list:
            coeffs.append( np.zeros(a.c.n_coeffs) )
            ch = np.zeros(a.h.n_coeffs)
            idx = next(i for i,x in enumerate(a.h.multi_idxs) if x == tuple([0]*a.h.dim_in))
            ch[idx] = 1.
            coeffs.append(ch)
        return np.hstack(coeffs)

    def get_default_init_values_minimize_kl_divergence(self):
        return self.get_identity_coeffs()

##############
# DEPRECATED #
##############

class IntegratedSquaredTriangularTransportMap(
        IntegratedSquaredParametricTriangularComponentwiseTransportMap
):
    @deprecate(
        'IntegratedSquaredTriangularTransportMap',
        '3.0',
        'Use Maps.IntegratedSquaredParametricTriangularComponentwiseTransportMap instead'
    )
    def __init__(self, active_vars, approx_list):
        super(IntegratedSquaredTriangularTransportMap,
              self).__init__(
                  active_vars=active_vars,
                  approx_list=approx_list
              )
