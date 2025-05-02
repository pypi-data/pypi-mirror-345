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

from ..Misc import \
    required_kwargs, \
    counted, cached
from .MapBase import Map

__all__ = [
    'SlicedMap'
]

nax = np.newaxis


class SlicedMap(Map):
    r""" Takes the map :math:`T({\bf x})` and construct the map :math:`S_{\bf y}({\bf x}) := [T({\bf y}_{\bf i} \cup {\bf x}_{\neg{\bf i}})]_{\bf j}`, where :math:`S_{\bf y}:\mathbb{R}^{\sharp(\neg{\bf i})}\rightarrow\mathbb{R}^{\sharp{\bf j}}`.
    """
    @required_kwargs('base_map', 'y', 'idxs_fix', 'idxs_out')
    def __init__(self, **kwargs):
        r"""
        Args:
          base_map (:class:`Map`): map :math:`T`
          y (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): values of :math:`{\bf y}_{\bf i}`
          idxs_fix (:class:`list`): list of indices :math:`{\bf i}`
          idxs_out (:class:`list`): list of indeices :math:`{\bf j}`
        """
        base_map = kwargs['base_map']
        y = kwargs['y']
        idxs_fix = kwargs['idxs_fix']
        idxs_out = kwargs['idxs_out']
        
        if len(y) != len(idxs_fix):
            raise ValueError("The length of y and idxs_fix must be the same")
        if len(set(idxs_fix)) != len(idxs_fix):
            raise ValueError("idxs_fix must contain unique values")
        if len(idxs_fix) > base_map.dim_in:
            raise ValueError("idxs_fix must be a subset of the input dimensions of base_map")
        self.base_map = base_map
        self.y = y
        self.idxs_fix = idxs_fix
        self.idxs_var = [ i for i in range(base_map.dim_in) if i not in idxs_fix ]
        self.idxs_out = idxs_out

        kwargs['dim_in'] = len(self.idxs_var)
        kwargs['dim_out'] = len(self.idxs_out)
        super(SlicedMap, self).__init__( **kwargs )

    def _xin(self, x):
        xin = np.zeros((x.shape[0], self.base_map.dim))
        xin[:,self.idxs_fix] = self.y[nax,:]
        xin[:,self.idxs_var] = x
        return xin
        
    @cached()
    @counted
    def evaluate(self, x, **kwargs): 
        return self.base_map.evaluate(
            self._xin(x), **kwargs)[:,self.idxs_out]

    @cached()
    @counted
    def grad_x(self, x, **kwargs):
        return self.base_map.grad_x(
            self._xin(x), **kwargs)[:,self.idxs_out,self.idxs_var]
        

    @cached(caching=False)
    @counted
    def hess_x(self, x, **kwargs):
        return self.base_map.hess_x(
            self._xin(x), **kwargs)[
                :,self.idxs_out,self.idxs_var, self.idxs_var]

    @cached(caching=False)
    @counted
    def action_hess_x(self, x, dx, **kwargs):
        return self.base_map.action_hess_x( # There may be a problem here with dx
            self._xin(x), dx, **kwargs)[
                :,self.idxs_out,self.idxs_var]
