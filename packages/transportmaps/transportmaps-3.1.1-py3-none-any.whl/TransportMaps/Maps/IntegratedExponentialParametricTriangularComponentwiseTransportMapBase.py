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
    IntegratedExponentialParametricMonotoneFunctional

from .ParametricTriangularComponentwiseTransportMapBase import \
    ParametricTriangularComponentwiseTransportMap

__all__ = [
    'IntegratedExponentialParametricTriangularComponentwiseTransportMap',
    'CommonBasisIntegratedExponentialParametricTriangularComponentwiseTransportMap',
    # Deprecated
    'IntegratedExponentialTriangularTransportMap',
    'CommonBasisIntegratedExponentialTriangularTransportMap',
]

nax = np.newaxis


class IntegratedExponentialParametricTriangularComponentwiseTransportMap(
        ParametricTriangularComponentwiseTransportMap
):
    r""" Triangular transport map where each component is represented by an :class:`IntegratedExponentialParametricMonotoneFunctional<TransportMaps.Maps.Functionals.IntegratedExponentialParametricMonotoneFunctional>`.
    """
    @required_kwargs('active_vars', 'approx_list')
    def __init__(self, **kwargs):
        r"""
        Kwargs:
          active_vars (:class:`list<list>` [:math:`d`] of :class:`list<list>`): for
            each dimension lists the active variables.
          approx_list (:class:`list<list>` [:math:`d`] of :class:`IntegratedExponentialParametricMonotoneFunctional<TransportMaps.Maps.Functionals.IntegratedExponentialParametricMonotoneFunctional>`):
            list of monotonic functional approximations for each dimension
          full_c_basis_list (:class:`list` of :class:`list`): list of basis for each input
            of the constant part of each component for a full triangular map
            (this is needed for some adaptivity algorithm)
          full_h_basis_list (:class:`list` of :class:`list`): list of basis for each input
            of the constant part of each component for a full triangular map
            (this is needed for some adaptivity algorithm)
        """
        approx_list = kwargs['approx_list']
        if not all( [ isinstance(a, IntegratedExponentialParametricMonotoneFunctional)
                      for a in approx_list ] ):
            raise ValueError("All the approximation functions must be instances " +
                             "of the class IntegratedExponentialParametricMonotoneFunctional")
        super(IntegratedExponentialParametricTriangularComponentwiseTransportMap,
              self).__init__(**kwargs)
        self.full_c_basis_list = kwargs.get('full_c_basis_list')
        self.full_h_basis_list = kwargs.get('full_h_basis_list')

    def get_identity_coeffs(self):
        r""" Returns the coefficients corresponding to the identity map

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
        """
        return np.zeros( self.n_coeffs )

    def get_default_init_values_minimize_kl_divergence(self):
        return self.get_identity_coeffs()

class CommonBasisIntegratedExponentialParametricTriangularComponentwiseTransportMap(
        IntegratedExponentialParametricTriangularComponentwiseTransportMap
):
    r""" Triangular transport map where each component is represented by an :class:`IntegratedExponentialParametricMonotoneFunctional<TransportMaps.Maps.Functionals.IntegratedExponentialParametricMonotoneFunctional>` and for each dimension :math:`i`, every component :math:`T_k` share the same basis type.

    This is leads to some more efficient evaluation operations.
    """
    @required_kwargs('active_vars', 'approx_list')
    def __init__(self, **kwargs):
        r"""
        Kwargs:
          active_vars (:class:`list<list>` [:math:`d`] of :class:`list<list>`): for
            each dimension lists the active variables.
          approx_list (:class:`list<list>` [:math:`d`] of :class:`IntegratedExponentialParametricMonotoneFunctional<TransportMaps.Maps.Functionals.IntegratedExponentialParametricMonotoneFunctional>`):
            list of monotonic functional approximations for each dimension
          full_c_basis_list (:class:`list` of :class:`list`): list of basis for each input
            of the constant part of each component for a full triangular map
            (this is needed for some adaptivity algorithm)
          full_h_basis_list (:class:`list` of :class:`list`): list of basis for each input
            of the constant part of each component for a full triangular map
            (this is needed for some adaptivity algorithm)
        """
        super(CommonBasisIntegratedExponentialParametricTriangularComponentwiseTransportMap,
              self).__init__(**kwargs)
        # Checks
        self.const_basis_list = [None for i in range(self.dim)]
        self.exp_basis_list = [None for i in range(self.dim)]
        for a,avars in zip(self.approx_list, self.active_vars):
            const_approx = a.c
            exp_approx = a.h
            for const_basis, exp_basis, avar in zip(const_approx.basis_list,
                                                    exp_approx.basis_list, avars):
                if self.const_basis_list[avar] is None:
                    self.const_basis_list[avar] = const_basis
                if self.exp_basis_list[avar] is None:
                    self.exp_basis_list[avar] = exp_basis
                if ( not( self.const_basis_list[avar] is const_basis ) or
                     not( self.exp_basis_list[avar] is exp_basis ) ):
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
        self.const_max_orders = np.zeros(self.dim, dtype=int)
        self.exp_max_orders = np.zeros(self.dim, dtype=int)
        for a,avar in zip(self.approx_list, self.active_vars):
            const_approx = a.c
            const_max_ord = const_approx.directional_orders
            const_idxs = tuple( np.where( self.const_max_orders[avar] < const_max_ord )[0] )
            for i in const_idxs: self.const_max_orders[avar[i]] = const_max_ord[i]
            exp_approx = a.h
            exp_max_ord = exp_approx.directional_orders
            exp_idxs = tuple( np.where( self.exp_max_orders[avar] < exp_max_ord )[0] )
            for i in exp_idxs: self.exp_max_orders[avar[i]] = exp_max_ord[i]
    
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
        # Constant part
        to_compute_flag = False
        for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
            try: prec_const = prec['const']
            except KeyError:
                to_compute_flag = True
                break
            try: prec_const_V_list = prec['const']['V_list']
            except KeyError:
                to_compute_flag = True
                break
        if to_compute_flag:
            const_vand = [ b.GradVandermonde(x[:,i], int(o)) for i,(o,b) in
                           enumerate(zip(self.const_max_orders,self.const_basis_list)) ]
            for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
                try: prec_const = prec['const']
                except KeyError: prec['const'] = {}
                # Vandermonde matrices
                try: prec_const_V_list = prec['const']['V_list']
                except KeyError:
                    prec['const']['V_list'] = [ const_vand[var] for var in avar ]
        # Integrated exponential part
        to_compute_flag = False
        for i,(approx,avar,prec) in enumerate(zip(self.approx_list, self.active_vars,
                                                  precomp['components'])):
            try: prec_intexp = prec['intexp']
            except KeyError:
                to_compute_flag = True
                break
            try:
                xjsc_list = prec['intexp']['xjsc_list']
                wjsc_list = prec['intexp']['wjsc_list']
            except KeyError:
                to_compute_flag = True
                break
            try: precomp_intexp_list = prec['intexp']['prec_list']
            except KeyError:
                to_compute_flag = True
                break
        if to_compute_flag:
            exp_vand = [ b.GradVandermonde(x[:,i], int(o)) for i,(o,b) in
                         enumerate(zip(self.exp_max_orders,self.exp_basis_list)) ]
            for i,(approx,avar,prec) in enumerate(zip(self.approx_list, self.active_vars,
                                                      precomp['components'])):
                try: prec_intexp = prec['intexp']
                except KeyError: prec['intexp'] = {}
                # Generate points and weights
                try:
                    xjsc_list = prec['intexp']['xjsc_list']
                    wjsc_list = prec['intexp']['wjsc_list']
                except KeyError:
                    prec['intexp']['xjsc_list'] = []
                    prec['intexp']['wjsc_list'] = []
                    xapprox = x[:,avar]
                    xd_order = (approx.h.directional_orders)[-1]
                    (xj,wj) = approx.P_JAC.Quadrature( approx.integ_ord_mult * xd_order, norm=True )
                    xj = xj / 2. + 0.5  # Mapped to [0,1]
                    for idx in range(x.shape[0]):
                        wjsc = wj * xapprox[idx,-1]
                        xjsc = xj * xapprox[idx,-1]
                        xother = np.tile( xapprox[idx,:-1], (len(xjsc), 1) )
                        xeval = np.hstack( (xother, xjsc[:,nax]) )
                        # Append values
                        prec['intexp']['xjsc_list'].append( xeval )
                        prec['intexp']['wjsc_list'].append( wjsc )
                # Generate Vandermonde matrices
                try: precomp_intexp_list = prec['intexp']['prec_list']
                except KeyError: prec['intexp']['prec_list'] = [{} for i in range(x.shape[0])]
                for idx, (xeval, pp) in enumerate(zip(prec['intexp']['xjsc_list'],
                                                      prec['intexp']['prec_list'])):
                    # Vandermonde matrices
                    try: prec_intexp_V_list = pp['V_list']
                    except KeyError:
                        pp['V_list'] = [ np.tile( exp_vand[var][idx,:], (xeval.shape[0],1) )
                                         for var in avar[:-1] ]
                        pp['V_list'].append(
                            self.exp_basis_list[avar[-1]].GradVandermonde(
                                xeval[:,-1], self.exp_max_orders[avar[-1]]) )
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
        # precomp_evaluate part
        precomp = self.precomp_evaluate(x, precomp, precomp_type)
        # Constant part
        to_compute_flag = False
        for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
            try: prec_const_partial_x_V_list = prec['const']['partial_x_V_list']
            except KeyError:
                to_compute_flag = True
                break
        if to_compute_flag:
            const_vand = [ b.GradVandermonde(x[:,i], int(o), k=1) for i,(o,b) in
                           enumerate(zip(self.const_max_orders,self.const_basis_list)) ]
            for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
                try: prec_const_partial_x_V_list = prec['const']['partial_x_V_list']
                except KeyError:
                    prec['const']['partial_x_V_list'] = [ const_vand[var] for var in avar ]
        # Integrated exponential part
        to_compute_flag = False
        for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
            for idx, (xeval, pp) in enumerate(zip(prec['intexp']['xjsc_list'],
                                                  prec['intexp']['prec_list'])):
                try: prec_intexp_partial_x_V_list = pp['partial_x_V_list']
                except KeyError:
                    to_compute_flag = True
                    break
            if to_compute_flag: break
        if to_compute_flag:
            partial_x_exp_vand = [ b.GradVandermonde(x[:,i], int(o), k=1) for i,(o,b) in
                                   enumerate(zip(self.exp_max_orders,self.exp_basis_list)) ]
            for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
                # Generate Vandermonde matrices
                for idx, (xeval, pp) in enumerate(zip(prec['intexp']['xjsc_list'],
                                                      prec['intexp']['prec_list'])):
                    try: prec_intexp_partial_x_V_list = pp['partial_x_V_list']
                    except KeyError:
                        pp['partial_x_V_list'] = [
                            np.tile( partial_x_exp_vand[var][idx,:], (xeval.shape[0],1) )
                            for var in avar[:-1] ]
                        pp['partial_x_V_list'].append(
                            self.exp_basis_list[avar[-1]].GradVandermonde(
                                xeval[:,-1], self.exp_max_orders[avar[-1]], k=1) )
        # precomp_partial_xd part
        to_compute_flag = False
        for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
            try: prec_exp = prec['exp']
            except KeyError:
                to_compute_flag = True
                break
            try: prec_exp_V_list = prec['exp']['V_list']
            except KeyError:
                to_compute_flag = True
                break
        if to_compute_flag:
            exp_vand = [ b.GradVandermonde(x[:,i], int(o)) for i,(o,b) in
                         enumerate(zip(self.exp_max_orders,self.exp_basis_list)) ]
            for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
                try: prec_exp = prec['exp']
                except KeyError: prec['exp'] = {}
                try: prec_exp_V_list = prec['exp']['V_list']
                except KeyError:
                    prec['exp']['V_list'] = [ exp_vand[var] for var in avar ]
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
        # precomp_grad_x part (and precomp_evaluate)
        precomp = self.precomp_grad_x(x, precomp, precomp_type)
        # Constant part
        to_compute_flag = False
        for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
            try: prec_const_partial2_x_V_list = prec['const']['partial2_x_V_list']
            except KeyError:
                to_compute_flag = True
                break
        if to_compute_flag:
            const_vand = [ b.GradVandermonde(x[:,i], int(o), k=2) for i,(o,b) in
                           enumerate(zip(self.const_max_orders,self.const_basis_list)) ]
            for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
                try: prec_const_partial2_x_V_list = prec['const']['partial2_x_V_list']
                except KeyError:
                    prec['const']['partial2_x_V_list'] = [ const_vand[var] for var in avar ]
        # Integrated exponential part
        to_compute_flag = False
        for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
            for idx, (xeval, pp) in enumerate(zip(prec['intexp']['xjsc_list'],
                                                  prec['intexp']['prec_list'])):
                try: prec_intexp_partial2_x_V_list = pp['partial2_x_V_list']
                except KeyError:
                    to_compute_flag = True
                    break
            if to_compute_flag: break
        if to_compute_flag:
            partial2_x_exp_vand = [ b.GradVandermonde(x[:,i], int(o), k=2) for i,(o,b) in
                                   enumerate(zip(self.exp_max_orders,self.exp_basis_list)) ]
            for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
                # Generate Vandermonde matrices
                for idx, (xeval, pp) in enumerate(zip(prec['intexp']['xjsc_list'],
                                                      prec['intexp']['prec_list'])):
                    try: prec_intexp_partial2_x_V_list = pp['partial2_x_V_list']
                    except KeyError:
                        pp['partial2_x_V_list'] = [
                            np.tile( partial2_x_exp_vand[var][idx,:], (xeval.shape[0],1) )
                            for var in avar[:-1] ]
                        pp['partial2_x_V_list'].append(
                            self.exp_basis_list[avar[-1]].GradVandermonde(
                                xeval[:,-1], self.exp_max_orders[avar[-1]], k=2) )
        # precomp_partial2_xd part
        to_compute_flag = False
        for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
            try: prec_exp_partial_xd_V_last = prec['exp']['partial_xd_V_last']
            except KeyError:
                to_compute_flag = True
                break
        if to_compute_flag:
            partial_x_exp_vand = [ b.GradVandermonde(x[:,i], int(o), k=1) for i,(o,b) in
                                   enumerate(zip(self.exp_max_orders,self.exp_basis_list)) ]
            for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
                try: prec_exp_partial_xd_V_last = prec['exp']['partial_xd_V_last']
                except KeyError:
                    prec['exp']['partial_xd_V_last'] = partial_x_exp_vand[avar[-1]]
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
        # precomp_hess_x part (and precomp_evaluate, precomp_grad_x)
        precomp = self.precomp_hess_x(x, precomp, precomp_type)
        # Constant part
        to_compute_flag = False
        for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
            try: prec_const_partial3_x_V_list = prec['const']['partial3_x_V_list']
            except KeyError:
                to_compute_flag = True
                break
        if to_compute_flag:
            const_vand = [ b.GradVandermonde(x[:,i], int(o), k=3) for i,(o,b) in
                           enumerate(zip(self.const_max_orders,self.const_basis_list)) ]
            for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
                try: prec_const_partial3_x_V_list = prec['const']['partial3_x_V_list']
                except KeyError:
                    prec['const']['partial3_x_V_list'] = [ const_vand[var] for var in avar ]
        # Integrated exponential part
        to_compute_flag = False
        for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
            for idx, (xeval, pp) in enumerate(zip(prec['intexp']['xjsc_list'],
                                                  prec['intexp']['prec_list'])):
                try: prec_intexp_partial3_x_V_list = pp['partial3_x_V_list']
                except KeyError:
                    to_compute_flag = True
                    break
        if to_compute_flag:
            partial3_x_exp_vand = [ b.GradVandermonde(x[:,i], int(o), k=3) for i,(o,b) in
                                   enumerate(zip(self.exp_max_orders,self.exp_basis_list)) ]
            for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
                # Generate Vandermonde matrices
                for idx, (xeval, pp) in enumerate(zip(prec['intexp']['xjsc_list'],
                                                      prec['intexp']['prec_list'])):
                    try: prec_intexp_partial3_x_V_list = pp['partial3_x_V_list']
                    except KeyError:
                        pp['partial2_x_V_list'] = [
                            np.tile( partial3_x_exp_vand[var][idx,:], (xeval.shape[0],1) )
                            for var in avar[:-1] ]
                        pp['partial2_x_V_list'].append(
                            self.exp_basis_list[avar[-1]].GradVandermonde(
                                xeval[:,-1], self.exp_max_orders[avar[-1]], k=3) )
        # precomp_partial3_xd part
        to_compute_flag = False
        for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
            try: prec_exp_partial2_xd_V_last = prec['exp']['partial2_xd_V_last']
            except KeyError:
                to_compute_flag = True
                break
        if to_compute_flag:
            partial2_x_exp_vand = [ b.GradVandermonde(x[:,i], int(o), k=2) for i,(o,b) in
                                    enumerate(zip(self.exp_max_orders,self.exp_basis_list)) ]
            for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
                try: prec_exp_partial2_xd_V_last = prec['exp']['partial2_xd_V_last']
                except KeyError:
                    prec['exp']['partial2_xd_V_last'] = partial2_x_exp_vand[avar[-1]]
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
        # Constant part
        to_compute_flag = False
        for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
            try: prec_const = prec['const']
            except KeyError:
                to_compute_flag = True
                break
            try: prec_const_V_list = prec['const']['V_list']
            except KeyError:
                to_compute_flag = True
                break
            try: prec_const_partial_xd_V_last = prec['const']['partial_xd_V_last']
            except KeyError:
                to_compute_flag = True
                break
        if to_compute_flag:
            const_vand = [ b.GradVandermonde(x[:,i], int(o)) for i,(o,b) in
                           enumerate(zip(self.const_max_orders,self.const_basis_list)) ]
            const_partial_x_vand = [ b.GradVandermonde(x[:,i], int(o), k=1) for i,(o,b) in
                                     enumerate(zip(self.const_max_orders,self.const_basis_list)) ]
            for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
                try: prec_const = prec['const']
                except KeyError: prec['const'] = {}
                try: prec_const_V_list = prec['const']['V_list']
                except KeyError: prec['const']['V_list'] = [ const_vand[var] for var in avar ]
                try: prec_const_partial_xd_V_last = prec['const']['partial_xd_V_last']
                except KeyError: prec['const']['partial_xd_V_last'] = const_partial_x_vand[avar[-1]]
        # Exponential part
        to_compute_flag = False
        for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
            try: prec_const = prec['exp']
            except KeyError:
                to_compute_flag = True
                break
            try: prec_exp_V_list = prec['exp']['V_list']
            except KeyError:
                to_compute_flag = True
                break
        if to_compute_flag:
            exp_vand = [ b.GradVandermonde(x[:,i], int(o)) for i,(o,b) in
                         enumerate(zip(self.exp_max_orders,self.exp_basis_list)) ]
            for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
                try: prec_const = prec['exp']
                except KeyError: prec['exp'] = {}
                try: prec_exp_V_list = prec['exp']['V_list']
                except KeyError: prec['exp']['V_list'] = [ exp_vand[var] for var in avar ]
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
        # precomp_partial_xd part
        precomp = self.precomp_partial_xd(x, precomp, precomp_type)
        # Constant part
        to_compute_flag = False
        for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
            try: prec_const_partial_xd_V_list = prec['const']['partial_xd_V_list']
            except KeyError:
                to_compute_flag = True
                break
            try: prec_const_partial2_xd_V_last = prec['const']['partial2_xd_V_last']
            except KeyError:
                to_compute_flag = True
                break
        if to_compute_flag:
            const_partial_x_vand = [ b.GradVandermonde(x[:,i], int(o), k=1) for i,(o,b) in
                                     enumerate(zip(self.const_max_orders,self.const_basis_list)) ]
            const_partial2_x_vand = [ b.GradVandermonde(x[:,i], int(o), k=2) for i,(o,b) in
                                      enumerate(zip(self.const_max_orders,self.const_basis_list)) ]
            for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
                try: prec_const_partial_xd_V_list = prec['const']['partial_xd_V_list']
                except KeyError:
                    prec['const']['partial_xd_V_list'] = [ const_partial_x_vand[var] for var in avar ]
                try: prec_const_partial2_xd_V_last = prec['const']['partial2_xd_V_last']
                except KeyError: prec['const']['partial2_xd_V_last'] = const_partial2_x_vand[avar[-1]]
        # Exponential part
        to_compute_flag = False
        for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
            try: prec_exp_partial_x_V_list = prec['exp']['partial_x_V_list']
            except KeyError:
                to_compute_flag = True
                break
        if to_compute_flag:
            partial_x_exp_vand = [ b.GradVandermonde(x[:,i], int(o), k=1) for i,(o,b) in
                                   enumerate(zip(self.exp_max_orders,self.exp_basis_list)) ]
            for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
                try: prec_exp_partial_x_V_list = prec['exp']['partial_x_V_list']
                except KeyError:
                    prec['exp']['partial_x_V_list'] = [ partial_x_exp_vand[var] for var in avar ]
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
        # precomp_grad_x_partial_xd (and precomp_partial_xd) parts
        precomp = self.precomp_grad_x_partial_xd(x, precomp, precomp_type)
        # Constant part
        to_compute_flag = False
        for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
            try: prec_const_partial2_xd_V_list = prec['const']['partial2_xd_V_list']
            except KeyError:
                to_compute_flag = True
                break
            try: prec_const_partial3_xd_V_last = prec['const']['partial3_xd_V_last']
            except KeyError:
                to_compute_flag = True
                break
        if to_compute_flag:
            const_partial2_x_vand = [ b.GradVandermonde(x[:,i], int(o), k=2) for i,(o,b) in
                                      enumerate(zip(self.const_max_orders,self.const_basis_list)) ]
            const_partial3_x_vand = [ b.GradVandermonde(x[:,i], int(o), k=3) for i,(o,b) in
                                      enumerate(zip(self.const_max_orders,self.const_basis_list)) ]
            for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
                try: prec_const_partial2_xd_V_list = prec['const']['partial2_xd_V_list']
                except KeyError:
                    prec['const']['partial2_xd_V_list'] = [ const_partial2_x_vand[var] for var in avar ]
                try: prec_const_partial3_xd_V_last = prec['const']['partial3_xd_V_last']
                except KeyError: prec['const']['partial3_xd_V_last'] = const_partial3_x_vand[avar[-1]]
        # Exponential part
        to_compute_flag = False
        for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
            try: prec_exp_partial2_x_V_list = prec['exp']['partial2_x_V_list']
            except KeyError:
                to_compute_flag = True
                break
        if to_compute_flag:
            partial2_x_exp_vand = [ b.GradVandermonde(x[:,i], int(o), k=2) for i,(o,b) in
                                    enumerate(zip(self.exp_max_orders,self.exp_basis_list)) ]
            for i,(avar,prec) in enumerate(zip(self.active_vars, precomp['components'])):
                try: prec_exp_partial2_x_V_list = prec['exp']['partial2_x_V_list']
                except KeyError:
                    prec['exp']['partial2_x_V_list'] = [ partial2_x_exp_vand[var] for var in avar ]
        return precomp

##############
# DEPRECATED #
##############

class IntegratedExponentialTriangularTransportMap(
        IntegratedExponentialParametricTriangularComponentwiseTransportMap
):
    @deprecate(
        'IntegratedExponentialTriangularTransportMap',
        '3.0',
        'Use Maps.IntegratedExponentialParametricTriangularComponentwiseTransportMap instead'
    )
    def __init__(self, active_vars, approx_list):
        super(IntegratedExponentialTriangularTransportMap,
              self).__init__(
                  active_vars=active_vars,
                  approx_list=approx_list
              )

class CommonBasisIntegratedExponentialTriangularTransportMap(
        CommonBasisIntegratedExponentialParametricTriangularComponentwiseTransportMap
):
    @deprecate(
        'CommonBasisIntegratedExponentialTriangularTransportMap',
        '3.0',
        'Use Maps.CommonBasisIntegratedExponentialParametricTriangularComponentwiseTransportMap instead'
    )
    def __init__(self, active_vars, approx_list):
        super(CommonBasisIntegratedExponentialTriangularTransportMap,
              self).__init__(
                  active_vars=active_vars,
                  approx_list=approx_list
              )

