#!/usr/bin/env python

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
import scipy.linalg as scila

from ..Misc import deprecate
from .AffineMapBase import AffineMap

__all__ = [
    'AffineTriangularMap',
    # Deprecated
    'LinearTriangularMap'
]


class AffineTriangularMap(AffineMap):
    r""" Affine map :math:`T({\bf x})={\bf c} + {\bf L}{\bf x}` where :math:`L` is triangular
    """
    def __init__(self, **kwargs):
        r"""
        Optional Kwargs:
          dim (int): dimension :math:`d`. If provided the map is set to the identity.
          c (:class:`ndarray<numpy.ndarray>` [:math:`d`]): term :math:`{\bf c}`
          L (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]): term :math:`{\bf L}`
          lower (bool): whether the map is lower triangular (``True``)
            or upper triangular (``False``). Default: ``True``

        Raises:
          ValueError: if ``dim`` and (``c``, ``L``) are provided
            at the same time.
        """
        dim   = kwargs.get('dim')
        c     = kwargs.get('c')
        L     = kwargs.get('L')
        lower = kwargs.get('lower', True)
        if dim is not None and (c is not None or L is not None):
            raise ValueError(
                "The arguments dim and (c, L) are mutually exclusive.")
        if dim is not None:
            c = np.zeros(dim)
            L = np.eye(dim)
        L = np.tril(L) if lower else np.triu(L)
        kwargs['c'] = c
        kwargs['L'] = L
        super(AffineTriangularMap, self).__init__(**kwargs)


class LinearTriangularMap(AffineTriangularMap):
    @deprecate(
        'LinearTriangularMap',
        '3.0',
        'Use Maps.AffineTriangularMap instead.'
    )
    def __init__(self, dim=None, constantTerm=None, linearTerm=None, lower=True):
        super(LinearTriangularMap, self).__init__(
            dim   = dim,
            c     = constantTerm,
            L     = linearTerm,
            lower = lower
        )
