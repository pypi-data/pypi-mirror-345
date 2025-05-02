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
    LinearSpanTensorizedParametricFunctional

from .ParametricTriangularComponentwiseMapBase import ParametricTriangularComponentwiseMap

__all__ = [
    'LinearSpanParametricTriangularComponentwiseMap',
    'CommonBasisLinearSpanParametricTriangularComponentwiseMap',
]


class LinearSpanParametricTriangularComponentwiseMap(
        ParametricTriangularComponentwiseMap
):
    r""" Triangular map :math:`T[{\bf a}_{1:d_y}]({\bf x})= [T_1[{\bf a}_1],\ldots,T_{d_y}[{\bf a}_{d_y}]]^\top` where :math:`T_i[{\bf a}_i](x_{1:i}) := {\bf a}_i^\top \, \Phi(x_{1:i}) `.
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
        approx_list = kwargs['approx_list']
        
        if not all( [ isinstance(a, LinearSpanTensorizedParametricFunctional)
                      for a in approx_list ] ):
            raise ValueError("All the approximation functions must be instances " +
                             "of the class LinearSpanTensorizedParametricFunctional")
        super(LinearSpanParametricTriangularComponentwiseMap,
              self).__init__(**kwargs)
        self.full_basis_list = kwargs.get('full_basis_list')

    def get_identity_coeffs(self):
        r""" Returns the coefficients corresponding to the identity map

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
        """
        # Define the identity map
        coeffs = []
        for a in self.approx_list:
            cc = np.zeros(a.n_coeffs)
            idx = next(i for i,x in enumerate(a.multi_idxs)
                       if x == tuple([0]*(a.dim_in-1)+[1]))
            cc[idx] = 1.
            coeffs.append(cc)
        return np.hstack(coeffs)

class CommonBasisLinearSpanParametricTriangularComponentwiseMap(
        LinearSpanParametricTriangularComponentwiseMap
):
    r""" Triangular map :math:`T[{\bf a}_{1:d_y}]({\bf x})= [T_1[{\bf a}_1],\ldots,T_{d_y}[{\bf a}_{d_y}]]^\top` where :math:`T_i[{\bf a}_i](x_{1:i}) := {\bf a}_i^\top \, \Phi(x_{1:i})`, and for each dimension :math:`i`, every component :math:`T_k` share the same basis type.

    This is leads to some more efficient evaluation operations.
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
        super(CommonBasisLinearSpanParametricTriangularComponentwiseMap,
              self).__init__(**kwargs)
        # Checks
        self.basis_list = [None for i in range(self.dim)]
        for a,avars in zip(self.approx_list, self.active_vars):
            for b, avar in zip(a.basis_list,avars):
                if self.basis_list[avar] is None:
                    self.basis_list[avar] = b
                if not( self.basis_list[avar] is b ):
                    raise ValueError("Fixed a dimension, all the basis for " +
                                     "this dimension must be of the same object " +
                                     "for all T_i")
        # Init
        self.logger.warning(
            "Be advised that in the current implementation " + \
            "of the \"CommonBasis\" componentwise maps, " + \
            "max_orders does not get updated when underlying " + \
            "directional orders change!!! (e.g. adaptivity)"
        )
        self.max_orders = np.zeros(self.dim, dtype=int)
        for a,avar in zip(self.approx_list, self.active_vars):
            a_max_ord = a.directional_orders
            idxs = tuple( np.where( self.max_orders[avar] < a_max_ord )[0] )
            for i in idxs: self.max_orders[avar[i]] = a_max_ord[i]

    def precomp_evaluate(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`T({\bf x},{\bf a})`

        This returns a list of uni-variate Vandermonde matrices with order maximum among the components :math:`T_i`.

        Enriches the dictionaries in the ``precomp`` list if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): list of dictionaries of precomputed values
          precomp_type (str): only option 'uni' is allowed for this TransportMap

        Returns:
           (:class:`dict<dict>` of :class:`list<list>` [:math:`d`]
             :class:`ndarray<numpy.ndarray>`) -- necessary structures
        """
        if precomp_type != 'uni':
            raise ValueError("Only option 'uni' is allowed for CommonBasisTransportMaps")
        if precomp is None:
            precomp = {'components': [{} for i in range(self.dim)]}
        to_compute_flag = False
        for i,(avar,p) in enumerate(zip(self.active_vars, precomp['components'])):
            try: tmp = p['V_list']
            except KeyError:
                to_compute_flag = True
                break
        if to_compute_flag:
            vand = [ b.GradVandermonde(x[:,i], int(o)) for i,(o,b) in
                     enumerate(zip(self.max_orders,self.basis_list)) ]
            for i,(avar,p) in enumerate(zip(self.active_vars, precomp['components'])):
                # Vandermonde matrices
                p['V_list'] = [ vand[var] for var in avar ]
        return precomp

    def precomp_grad_x(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`\nabla_{\bf x}T({\bf x},{\bf a})`

        Enriches the dictionaries in the ``precomp`` list if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): list of dictionaries of precomputed values
          precomp_type (str): only option 'uni' is allowed for this TransportMap

        Returns:
           (:class:`dict<dict>` of :class:`list<list>` [:math:`d`]
            :class:`ndarray<numpy.ndarray>`) -- necessary structures
        """
        if precomp_type != 'uni':
            raise ValueError("Only option 'uni' is allowed for CommonBasisTransportMaps")
        if precomp is None:
            precomp = {'components': [{} for i in range(self.dim)]}
        # precomp_evaluate part
        self.precomp_evaluate(x, precomp)
        # precomp_grad_x part
        to_compute_flag = False
        for i,(avar,p) in enumerate(zip(self.active_vars, precomp['components'])):
            try: tmp = p['partial_x_V_list']
            except KeyError:
                to_compute_flag = True
                break
        if to_compute_flag:
            vand = [ b.GradVandermonde(x[:,i], int(o), k=1) for i,(o,b) in
                     enumerate(zip(self.max_orders,self.basis_list)) ]
            for i,(avar,p) in enumerate(zip(self.active_vars, precomp['components'])):
                p['partial_x_V_list'] = [ vand[var] for var in avar ]
        return precomp

    def precomp_hess_x(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`\nabla^2_{\bf x}T({\bf x},{\bf a})`

        Enriches the dictionaries in the ``precomp`` list if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): list of dictionaries of precomputed values
          precomp_type (str): only option 'uni' is allowed for this TransportMap

        Returns:
           (:class:`dict<dict>` of :class:`list<list>` [:math:`d`]
             :class:`ndarray<numpy.ndarray>`) -- necessary structures
        """
        if precomp_type != 'uni':
            raise ValueError("Only option 'uni' is allowed for CommonBasisTransportMaps")
        if precomp is None:
            precomp = {'components': [{} for i in range(self.dim)]}
        # precomp_evaluate and precomp_grad_x parts
        self.precomp_evaluate(x, precomp)
        self.precomp_grad_x(x, precomp)
        # precomp_hess_x part
        to_compute_flag = False
        for i,(avar,p) in enumerate(zip(self.active_vars, precomp['components'])):
            try: tmp = p['partial2_x_V_list']
            except KeyError:
                to_compute_flag = True
                break
        if to_compute_flag:
            vand = [ b.GradVandermonde(x[:,i], int(o), k=2) for i,(o,b) in
                     enumerate(zip(self.max_orders,self.basis_list)) ]
            for i,(avar,p) in enumerate(zip(self.active_vars, precomp['components'])):
                p['partial2_x_V_list'] = [ vand[var] for var in avar ]
        return precomp

    def precomp_nabla3_x(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`\nabla^3_{\bf x}T({\bf x},{\bf a})`

        Enriches the dictionaries in the ``precomp`` list if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): list of dictionaries of precomputed values
          precomp_type (str): only option 'uni' is allowed for this TransportMap

        Returns:
           (:class:`dict<dict>` of :class:`list<list>` [:math:`d`]
             :class:`ndarray<numpy.ndarray>`) -- necessary structures
        """
        if precomp_type != 'uni':
            raise ValueError("Only option 'uni' is allowed for CommonBasisTransportMaps")
        if precomp is None:
            precomp = {'components': [{} for i in range(self.dim)]}
        # precomp_evaluate precomp_grad_x precomp_hess_x parts
        self.precomp_evaluate(x, precomp)
        self.precomp_grad_x(x, precomp)
        self.precomp_hess_x(x, precomp)
        # precomp_nabla3_x
        to_compute_flag = False
        for i,(avar,p) in enumerate(zip(self.active_vars, precomp['components'])):
            try: tmp = p['partial3_x_V_list']
            except KeyError:
                to_compute_flag = True
                break
        if to_compute_flag:
            vand = [ b.GradVandermonde(x[:,i], int(o), k=3) for i,(o,b) in
                     enumerate(zip(self.max_orders, self.basis_list)) ]
            for i,(avar,p) in enumerate(zip(self.active_vars, precomp['components'])):
                p['partial3_x_V_list'] = [ vand[var] for var in avar ]
        return precomp

    def precomp_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`\partial_{x_k}T_k({\bf x},{\bf a})` for :math:`k=1,\ldots,d`

        Enriches the dictionaries in the ``precomp`` list if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): list of dictionaries of precomputed values
          precomp_type (str): only option 'uni' is allowed for this TransportMap

        Returns:
           (:class:`dict<dict>` of :class:`list<list>` [:math:`d`]
             :class:`ndarray<numpy.ndarray>`) -- necessary structures
        """
        if precomp_type != 'uni':
            raise ValueError("Only option 'uni' is allowed for CommonBasisTransportMaps")
        if precomp is None:
            precomp = {'components': [{} for i in range(self.dim)]}
        # precomp_evaluate and precomp_grad_x parts
        self.precomp_evaluate(x, precomp)
        self.precomp_grad_x(x, precomp)
        # Generate partial_xd_V_last fields
        for p in precomp['components']:
            p['partial_xd_V_last'] = p['partial_x_V_list'][-1]
        return precomp

    def precomp_grad_x_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`\nabla_{\bf x}\partial_{x_k}T_k({\bf x},{\bf a})` for :math:`k=1,\ldots,d`

        Enriches the dictionaries in the ``precomp`` list if necessary.
        
        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): list of dictionaries of precomputed values
          precomp_type (str): only option 'uni' is allowed for this TransportMap

        Returns:
           (:class:`dict<dict>` of :class:`list<list>` [:math:`d`]
             :class:`dict<dict>`) -- necessary structures
        """
        if precomp_type != 'uni':
            raise ValueError("Only option 'uni' is allowed for CommonBasisTransportMaps")
        if precomp is None:
            precomp = {'components': [{} for i in range(self.dim)]}
        # precomp_evaluate, precomp_grad_x and precomp_hess_x parts
        self.precomp_evaluate(x, precomp)
        self.precomp_grad_x(x, precomp)
        self.precomp_hess_x(x, precomp)
        # Generate partial2_xd_V_last fields
        for p in precomp['components']:
            p['partial2_xd_V_last'] = p['partial2_x_V_list'][-1]
        return precomp

    def precomp_hess_x_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`\nabla^2_{\bf x}\partial_{x_k}T_k({\bf x},{\bf a})` for :math:`k=1,\ldots,d`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): list of dictionaries of precomputed values
          precomp_type (str): only option 'uni' is allowed for this TransportMap

        Returns:
           (:class:`dict<dict>` of :class:`list<list>` [:math:`d`]
             :class:`dict<dict>`) -- necessary structures
        """
        if precomp_type != 'uni':
            raise ValueError("Only option 'uni' is allowed for CommonBasisTransportMaps")
        if precomp is None:
            precomp = {'components': [{} for i in range(self.dim)]}
        # precomp_evaluate, precomp_grad_x, precomp_hess_x, precomp_nabla3_x parts
        self.precomp_evaluate(x, precomp)
        self.precomp_grad_x(x, precomp)
        self.precomp_hess_x(x, precomp)
        self.precomp_nabla3_x(x, precomp)
        # Generate partial3_xd_V_last fields
        for p in precomp['components']:
            p['partial3_xd_V_last'] = p['partial3_x_V_list'][-1]
        return precomp

