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

from ..Misc import counted
from .ParametricMapBase import ParametricMap

__all__ = [
    'ConstantMap'
]


class ConstantMap(ParametricMap):
    r""" Map :math:`T({\bf x})={\bf c}`

    Args:
       dim_in (int): input dimension :math:`d_x`
       const (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): constant :math:`{\bf c}`
    """
    def __init__(self, dim_in, const):
        if const.dims > 1:
            raise ValueError(
                "The constant should be 1d array."
            )
        self._const = const
        super(ConstantMap, self).__init__(dim_in, len(const))
        
    @property
    def coeffs(self):
        return self._const

    @coeffs.setter
    def coeffs(self, coeffs):
        self._const = coeffs

    @counted
    def evaluate(self, x, precomp=None, idxs_slice=slice(None)):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        return self._const[:]

    @counted
    def grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        # shp = (1,) + self._const.shape + (self.dim_in,)
        shp = self._const.shape + (self.dim_in,)
        return np.zeros(shp)

    @counted
    def hess_x(self, x, precomp=None, idxs_slice=slice(None)):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        # shp = (1,) + self._const.shape + (self.dim_in,self.dim_in)
        shp = self._const.shape + (self.dim_in,self.dim_in)
        return np.zeros(shp)
