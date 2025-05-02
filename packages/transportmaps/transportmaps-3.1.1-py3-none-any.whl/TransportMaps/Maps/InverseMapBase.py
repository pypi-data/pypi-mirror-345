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
from .MapBase import Map

__all__ = [
    'InverseMap'
]


class InverseMap(Map):
    r""" Defines the map :math:`S := T^{\dagger}`
    """
    @required_kwargs('base_map')
    def __init__(self, **kwargs):
        r"""
        Kwargs:
          base_map (:class:`Map`): map :math:`T`
        """
        base_map = kwargs['base_map']
        if not isinstance(base_map, Map):
            raise ValueError(
                "The provided base_map is not a Map"
            )
        self.base_map = base_map
        kwargs['dim_in']  = base_map.dim_out
        kwargs['dim_out'] = base_map.dim_in
        super(InverseMap, self).__init__(**kwargs)

    @property
    def base_map(self):
        try:
            return self._base_map
        except AttributeError:
            # Backward compatibility v < 3.0
            return self.tm

    @base_map.setter
    def base_map(self, base_map):
        self._base_map = base_map
        
    def get_ncalls_tree(self, indent=""):
        out = super(InverseMap, self).get_ncalls_tree(indent)
        out += self.base_map.get_ncalls_tree(indent + "  ")
        return out

    def get_nevals_tree(self, indent=""):
        out = super(InverseMap, self).get_nevals_tree(indent)
        out += self.base_map.get_nevals_tree(indent + "  ")
        return out

    def get_teval_tree(self, indent=""):
        out = super(InverseMap, self).get_teval_tree(indent)
        out += self.base_map.get_teval_tree(indent + "  ")
        return out

    def update_ncalls_tree(self, obj):
        super(InverseMap, self).update_ncalls_tree(obj)
        self.base_map.update_ncalls_tree( obj.tm )

    def update_nevals_tree(self, obj):
        super(InverseMap, self).update_nevals_tree(obj)
        self.base_map.update_nevals_tree( obj.tm )

    def update_teval_tree(self, obj):
        super(InverseMap, self).update_teval_tree(obj)
        self.base_map.update_teval_tree( obj.tm )

    def reset_counters(self):
        super(InverseMap, self).reset_counters()
        self.base_map.reset_counters()

    @counted
    def evaluate(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Evaluate the map :math:`T^{-1}` at the points :math:`{\bf x} \in \mathbb{R}^{m \times d}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- transformed points

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        return self.base_map.inverse(x)

    @counted
    def grad_x(self, x, *args, **kwargs):
        return self.base_map.grad_x_inverse(x, *args, **kwargs)

    @counted
    def tuple_grad_x(self, x, *args, **kwargs):
        return self.base_map.tuple_grad_x_inverse(x, *args, **kwargs)

    @counted
    def hess_x(self, x, *args, **kwargs):
        return self.base_map.hess_x_inverse(x, *args, **kwargs)

    @counted
    def action_hess_x(self, x, *args, **kwargs):
        return self.base_map.action_hess_x_inverse(x, *args, **kwargs)

    @counted
    def inverse(self, x, *args, **kwargs):
        r""" Evaluates :math:`T`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`T({\bf x})` for every evaluation point
        """
        return self.base_map.evaluate(x)

    @counted
    def grad_x_inverse(self, x, *args, **kwargs):
        r""" Evaluates :math:`\nabla_{\bf x}T`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           gradient matrices for every evaluation point.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        return self.base_map.grad_x(x)

    @counted
    def tuple_grad_x_inverse(self, x, *args, **kwargs):
        return self.base_map.tuple_grad_x(x)

    @counted
    def hess_x_inverse(self, x, *args, **kwargs):
        r""" Evaluates :math:`\nabla^2_{\bf x}T`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d,d`]) --
           Hessian matrices for every evaluation point and every dimension.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        return self.base_map.hess_x(x)

    @counted
    def action_hess_x_inverse(self, x, *args, **kwargs):
        return self.base_map.action_hess_x(x)
