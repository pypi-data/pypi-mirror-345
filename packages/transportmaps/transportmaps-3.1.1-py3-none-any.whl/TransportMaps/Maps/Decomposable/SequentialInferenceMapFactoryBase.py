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

from TransportMaps.Maps import \
    MapFactory, MapListFactory

__all__ = [
    'SequentialInferenceMapFactory',
    'SequentialInferenceMapListFactory',
    'IncreasingOrderSequentialInferenceMapListFactory',
    'FadingIncreasingOrderSequentialInferenceMapListFactory',
]

class SequentialInferenceMapFactory(MapFactory):
    def generate(self, nsteps, *args, **kwargs):
        r""" [abstract] generates maps.

        Args:
          nsteps (int): number of sequential steps the maps should for
        """
        raise NotImplementedError("To be implemented in sub-classes")

class SequentialInferenceMapListFactory(MapListFactory, SequentialInferenceMapFactory):
    def __init__(self, n_maps, *args, **kwargs):
        MapListFactory.__init__(self, n_maps, *args, **kwargs)
            
    def generate(self, nsteps, *args, **kwargs):
        r""" [abstract] generates maps.

        Args:
          nsteps (int): number of sequential steps the maps should for
        """
        raise NotImplementedError("To be implemented in sub-classes")

class IncreasingOrderSequentialInferenceMapListFactory(SequentialInferenceMapListFactory):
    r""" A factory for a list of maps with increasing order.
    """
    def __init__(self, max_order, btype='fun'):
        super(SequentialInferenceMapListFactory, self).__init__( max_order )
        self._max_order = max_order
        self._btype = btype

    @property
    def max_order(self):
        return self._max_order

    @property
    def btype(self):
        return self._btype
    
class FadingIncreasingOrderSequentialInferenceMapListFactory(
        IncreasingOrderSequentialInferenceMapListFactory):
    r"""
    The orders are scaled down using the following formula:

    .. math::

       q_d = \lfloor q^{1/(1+\alpha d)} \rceil

    where :math:`q` is the maximum order in the current map
    and :math:`\alpha` tunes the speed at which the order decrease
    to :math:`1` with respect to :math:`d`.
    With :math:`\alpha=0` the order is not decreased.

    Args:
      alpha (float): :math:`alpha`
    """
    def __init__(self, max_order, btype='fun', alpha=0.):
        super(FadingIncreasingOrderSequentialInferenceMapListFactory, self).__init__(
            max_order, btype=btype )
        self._alpha = alpha

    @property
    def alpha(self):
        return self._alpha

