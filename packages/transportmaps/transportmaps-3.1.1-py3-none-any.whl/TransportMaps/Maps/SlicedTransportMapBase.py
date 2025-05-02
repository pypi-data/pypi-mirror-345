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

from ..Misc import required_kwargs

from .SlicedMapBase import SlicedMap
from .TransportMapBase import TransportMap

__all__ = [
    'SlicedTransportMap'
]


class SlicedTransportMap(
        SlicedMap,
        TransportMap
):
    r""" Takes the transport map :math:`T({\bf x})` and construct the map :math:`S_{\bf y}({\bf x}) := [T({\bf y}_{\bf i} \cup {\bf x}_{\neg{\bf i}})]_{\bf j}`, where :math:`S_{\bf y}:\mathbb{R}^{\sharp(\neg{\bf i})}\rightarrow\mathbb{R}^{\sharp{\bf j}}` and :math:`\sharp(\neg{\bf i}) = \sharp{\bf j}`.
    """
    @required_kwargs('base_map', 'y', 'idxs_fix', 'idxs_out')
    def __init__(self, **kwargs):
        r"""
        Args:
          base_map (:class:`TransportMap`): map :math:`T`
          y (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): values of :math:`{\bf y}_{\bf i}`
          idxs_fix (:class:`list`): list of indices :math:`{\bf i}`
          idxs_out (:class:`list`): list of indeices :math:`{\bf j}`
        """
        # Check base_map is a TransportMap
        base_map = kwargs['base_map']
        if not isinstance(base_map, TransportMap):
            raise ValueError(
                "The base_map must be a TransportMap"
            )
        # Check for the number of variable indices and the number of outputs to be the same
        if base_map.dim - len(kwargs['idxs_fix']) != len(kwargs['idxs_out']):
            raise ValueError(
                "The number of variable indices and the number of output must match."
            )
        kwargs['dim'] = len(kwargs['idxs_out'])
        super(SlicedTransportMap, self).__init__(**kwargs)
