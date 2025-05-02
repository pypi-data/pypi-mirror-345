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

from ..Misc import \
    required_kwargs, \
    counted

from .TransportMapBase import TransportMap
from .InverseMapBase import InverseMap

__all__ = [
    'InverseTransportMap'
]


class InverseTransportMap(InverseMap, TransportMap):
    r""" Given the transport map :math:`T`, define :math:`S=T^{-1}`.
    """
    @required_kwargs('base_map')
    def __init__(self, **kwargs):
        r"""
        Kwags:
          base_map (:class:`TransportMap`): map :math:`T`
        """
        base_map = kwargs['base_map']
        if not isinstance(base_map, TransportMap):
            raise ValueError(
                "The provided base_map is not a TransportMap"
            )
        kwargs['dim'] = base_map.dim
        super(InverseTransportMap, self).__init__(**kwargs)
        
    @counted
    def log_det_grad_x(self, x, *args, **kwargs):
        return self.base_map.log_det_grad_x_inverse(x, *args, **kwargs)

    @counted
    def grad_x_log_det_grad_x(self, x, *args, **kwargs):
        return self.base_map.grad_x_log_det_grad_x_inverse(x, *args, **kwargs)

    @counted
    def hess_x_log_det_grad_x(self, x, *args, **kwargs):
        return self.base_map.hess_x_log_det_grad_x_inverse(x, *args, **kwargs)

    @counted
    def log_det_grad_x_inverse(self, x, *args, **kwargs):
        return self.base_map.log_det_grad_x(x, *args, **kwargs)

    @counted
    def grad_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        return self.base_map.grad_x_log_det_grad_x(x, *args, **kwargs)

    @counted
    def hess_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        return self.base_map.hess_x_log_det_grad_x(x, *args, **kwargs)
