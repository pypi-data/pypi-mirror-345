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

import SpectralToolbox.Spectral1D as S1D

from ...Misc import \
    cached, counted, get_sub_cache,\
    deprecate
from .ParametricFunctionalBase import ParametricFunctionApproximation
from .ParametricMonotoneFunctionalBase import ParametricMonotoneFunctional
from .LinearSpanTensorizedParametricFunctionalBase import LinearSpanTensorizedParametricFunctional

__all__ = [
    'IntegratedExponentialParametricMonotoneFunctional',
    # Deprecated
    'MonotonicIntegratedExponentialApproximation'
]

nax = np.newaxis

    
class IntegratedExponentialParametricMonotoneFunctional(ParametricMonotoneFunctional):
    r""" Integrated Exponential approximation.

    For :math:`{\bf x} \in \mathbb{R}^d` The approximation takes the form:

    .. math::
       :label: integ-exp
       
       f_{\bf a}({\bf x}) = c({\bf x};{\bf a}^c) + \int_0^{{\bf x}_d} \exp\left( h({\bf x}_{1:d-1},t;{\bf a}^e) \right) dt

    where

    .. math::
    
       c({\bf x};{\bf a}^c) = \Phi({\bf x}) {\bf a}^c = \sum_{{\bf i}\in \mathcal{I}_c} \Phi_{\bf i}({\bf x}) {\bf a}^c_{\bf i} \qquad \text{and} \qquad h({\bf x}_{1:d-1},t;{\bf a}^e) = \Psi({\bf x}_{1:d-1},t) {\bf a}^e = \sum_{{\bf i}\in \mathcal{I}_e} \Psi_{\bf i}({\bf x}_{1:d-1},t) {\bf a}^e_{\bf i}

    for the set of basis :math:`\Phi` and :math:`\Psi` with cardinality :math:`\sharp \mathcal{I}_c = N_c` and :math:`\sharp \mathcal{I}_e = N_e`. In the following :math:`N=N_c+N_e`.

    Args:
       c (:class:`LinearSpanTensorizedParametricFunctional`): :math:`d-1` dimensional
         approximation of :math:`c({\bf x}_{1:d-1};{\bf a}^c)`.
       h (:class:`LinearSpanTensorizedParametricFunctional`): :math:`d` dimensional
         approximation of :math:`h({\bf x}_{1:d-1},t;{\bf a}^e)`.
       integ_ord_mult (int): multiplier for the number of Gauss points to be used
         in the approximation of :math:`\int_0^{{\bf x}_d}`. The resulting number of
         points is given by the product of the order in the :math:`d` direction
         and ``integ_ord_mult``.
    """

    def __init__(self, c, h, integ_ord_mult=6):
        if c.dim_in != h.dim_in:
            raise ValueError("The dimension of the constant part and the " +
                             "exponential part of the approximation must be " +
                             "the same.")
        if c.directional_orders[-1] != 0:
            raise ValueError("The order along the last direction of the constant " +
                             "part of the approximation must be zero")
        self.c = c
        self.h = h
        super(IntegratedExponentialParametricMonotoneFunctional, self).__init__(h.dim_in)
        self.P_JAC = S1D.JacobiPolynomial(0.,0.)
        self.integ_ord_mult = integ_ord_mult

    def init_coeffs(self):
        r""" Initialize the coefficients :math:`{\bf a}`
        """
        self.c.init_coeffs()
        self.h.init_coeffs()

    def get_ncalls_tree(self, indent=""):
        out = super(IntegratedExponentialParametricMonotoneFunctional, self).get_ncalls_tree(indent)
        out += self.c.get_ncalls_tree(indent + " c - ")
        out += self.h.get_ncalls_tree(indent + " h - ")
        return out

    def get_nevals_tree(self, indent=""):
        out = super(IntegratedExponentialParametricMonotoneFunctional, self).get_nevals_tree(indent)
        out += self.c.get_nevals_tree(indent + " c - ")
        out += self.h.get_nevals_tree(indent + " h - ")
        return out

    def get_teval_tree(self, indent=""):
        out = super(IntegratedExponentialParametricMonotoneFunctional, self).get_teval_tree(indent)
        out += self.c.get_teval_tree(indent + " c - ")
        out += self.h.get_teval_tree(indent + " h - ")
        return out

    def update_ncalls_tree(self, obj):
        super(IntegratedExponentialParametricMonotoneFunctional, self).update_ncalls_tree(obj)
        self.c.update_ncalls_tree( obj.c )
        self.h.update_ncalls_tree( obj.h )

    def update_nevals_tree(self, obj):
        super(IntegratedExponentialParametricMonotoneFunctional, self).update_nevals_tree(obj)
        self.c.update_nevals_tree( obj.c )
        self.h.update_nevals_tree( obj.h )

    def update_teval_tree(self, obj):
        super(IntegratedExponentialParametricMonotoneFunctional, self).update_teval_tree(obj)
        self.c.update_teval_tree( obj.c )
        self.h.update_teval_tree( obj.h )

    def reset_counters(self):
        super(IntegratedExponentialParametricMonotoneFunctional, self).reset_counters()
        self.c.reset_counters()
        self.h.reset_counters()

    @property
    def n_coeffs(self):
        r""" Get the number :math:`N` of coefficients :math:`{\bf a}`

        Returns:
          (:class:`int<int>`) -- number of coefficients
        """
        return self.c.n_coeffs + self.h.n_coeffs

    @property
    def coeffs(self):
        r""" Get the coefficients :math:`{\bf a}`

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients
        """
        return np.hstack( (self.c.coeffs, self.h.coeffs) )

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients :math:`{\bf a}`.

        Args:
          coeffs (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
        """
        if len(coeffs) != self.n_coeffs:
            raise ValueError("Wrong number of coefficients provided.")
        nc = self.c.n_coeffs
        self.c.coeffs = coeffs[:nc]
        self.h.coeffs = coeffs[nc:]

    def precomp_evaluate(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary containing the necessary structures
        """
        if precomp is None: precomp = {}
        # Constant part
        try: precomp_const = precomp['const']
        except KeyError as e: precomp['const'] = {}
        if precomp_type == 'uni':
            self.c.precomp_evaluate(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_evaluate(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Integrated exponential part
        try: precomp_intexp = precomp['intexp']
        except KeyError as e: precomp['intexp'] = {}
        try:
            xjsc_list = precomp['intexp']['xjsc_list']
            wjsc_list = precomp['intexp']['wjsc_list']
        except KeyError as e:
            precomp['intexp']['xjsc_list'] = []
            precomp['intexp']['wjsc_list'] = []
            xd_order = (self.h.directional_orders)[-1]
            (xj,wj) = self.P_JAC.Quadrature( self.integ_ord_mult * xd_order, norm=True )
            xj = xj / 2. + 0.5  # Mapped to [0,1]
            for idx in range(x.shape[0]):
                wjsc = wj * x[idx,-1]
                xjsc = xj * x[idx,-1]
                xother = np.tile( x[idx,:-1], (len(xjsc), 1) )
                xeval = np.hstack( (xother, xjsc[:,nax]) )
                # Append values
                precomp['intexp']['xjsc_list'].append( xeval )
                precomp['intexp']['wjsc_list'].append( wjsc )
        try: precomp_intexp_list = precomp['intexp']['prec_list']
        except KeyError as e:
            precomp['intexp']['prec_list'] = [{} for i in range(x.shape[0])]
        for idx, (xeval, p) in enumerate(zip(precomp['intexp']['xjsc_list'],
                                             precomp['intexp']['prec_list'])):
            if precomp_type == 'uni':
                self.h.precomp_evaluate(xeval, p)
            elif precomp_type == 'multi':
                self.h.precomp_Vandermonde_evaluate(xeval, p)
            else: raise ValueError("Unrecognized precomp_type")
        return precomp

    def precomp_Vandermonde_evaluate(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary containing the necessary structures
        """
        return self.precomp_evaluate(x, precomp, precomp_type='multi')

    @cached([('c',None)])
    @counted
    def evaluate(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1`]) -- function evaluations
        """
        try:
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intexp = precomp['intexp']
            prec_intexp_xjsc_list = prec_intexp['xjsc_list']
            prec_intexp_wjsc_list = prec_intexp['wjsc_list']
            prec_intexp_prec_list = prec_intexp['prec_list']
            for p in prec_intexp_prec_list:
                if 'V_list' not in p: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intexp = precomp['intexp']
        prec_intexp_xjsc_list = prec_intexp['xjsc_list']
        prec_intexp_wjsc_list = prec_intexp['wjsc_list']
        prec_intexp_prec_list = prec_intexp['prec_list']
        # Retrieve sub-cache
        c_cache = get_sub_cache(cache, ('c',None))
        try:
            h_cache_list = cache['h_cache_list']
        except TypeError:
            h_cache_list = [None]*len(prec_intexp_xjsc_list)
        except KeyError:
            h_cache_list = [{'tot_size': xx.shape[0]}
                            for xx in prec_intexp_xjsc_list]
            cache['h_cache_list'] = h_cache_list
        # Convert slice to range
        if idxs_slice.start is None: start = 0
        else: start = idxs_slice.start
        if idxs_slice.stop is None: stop = x.shape[0]
        else: stop = idxs_slice.stop
        idxs_list = range(start, stop)
        # Evaluate
        out = self.c.evaluate(x, prec_const, idxs_slice=idxs_slice, cache=c_cache)
        for i, idx in enumerate(idxs_list):# other_idxs:
            h_eval = self.h.evaluate(prec_intexp_xjsc_list[idx],
                                     precomp=prec_intexp_prec_list[idx],
                                     cache=h_cache_list[idx])[:,0]
            exp = np.exp( h_eval )
            out[i,0] += np.dot( exp, prec_intexp_wjsc_list[idx] )
        return out

    def precomp_grad_x(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`\nabla_{\bf x} f_{\bf a}` at ``x``

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary containing the necessary structures
        """
        if precomp is None: precomp = {}
        # precomp_evaluate part
        self.precomp_evaluate(x, precomp, precomp_type)
        # Constant part
        if precomp_type == 'uni':
            self.c.precomp_grad_x(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_grad_x(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Integrated exponential part
        for xeval, p in zip(precomp['intexp']['xjsc_list'],
                            precomp['intexp']['prec_list']):
            if precomp_type == 'uni':
                self.h.precomp_grad_x(xeval, p)
            elif precomp_type == 'multi':
                self.h.precomp_Vandermonde_grad_x(xeval, p)
            else: raise ValueError("Unrecognized precomp_type")
        # precomp_partial_xd part
        self.precomp_partial_xd(x, precomp, precomp_type)
        return precomp

    def precomp_Vandermonde_grad_x(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`\nabla_{\bf x} f_{\bf a}` at ``x``

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary containing the necessary structures
        """
        return self.precomp_grad_x(x, precomp, precomp_type='multi')

    @counted
    def grad_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,d`]) --
            :math:`\nabla_{\bf x} f_{\bf a}({\bf x})`
        """
        try: # precomp_evaluate structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intexp = precomp['intexp']
            prec_intexp_xjsc_list = prec_intexp['xjsc_list']
            prec_intexp_wjsc_list = prec_intexp['wjsc_list']
            prec_intexp_prec_list = prec_intexp['prec_list']
            for p in prec_intexp_prec_list:
                if 'V_list' not in p: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intexp = precomp['intexp']
        prec_intexp_xjsc_list = prec_intexp['xjsc_list']
        prec_intexp_wjsc_list = prec_intexp['wjsc_list']
        prec_intexp_prec_list = prec_intexp['prec_list']
        try: # precomp_grad_x structures
            if 'partial_x_V_list' not in prec_const: raise KeyError()
            for p in prec_intexp_prec_list:
                if 'partial_x_V_list' not in p: raise KeyError()
        except KeyError as e:
            precomp = self.precomp_grad_x(x, precomp)
        # Evaluation
        out = self.c.grad_x(x, prec_const)
        for idx in range(x.shape[0]):
            exp = np.exp( self.h.evaluate( prec_intexp_xjsc_list[idx],
                                           precomp=prec_intexp_prec_list[idx] ) )
            grad_x_exp = self.h.grad_x( prec_intexp_xjsc_list[idx],
                                        precomp=prec_intexp_prec_list[idx] ) \
                         * exp[:,:,nax]
            out[idx,0,:] += np.dot( prec_intexp_wjsc_list[idx], grad_x_exp[:,0,:] )
        out[:,:,-1] = self.partial_xd(x, precomp)
        return out

    @counted
    def grad_a_grad_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf a} \nabla_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,d`]) --
            :math:`\nabla_{\bf a} \nabla_{\bf x} f_{\bf a}({\bf x})`
        """
        try: # precomp_evaluate structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intexp = precomp['intexp']
            prec_intexp_xjsc_list = prec_intexp['xjsc_list']
            prec_intexp_wjsc_list = prec_intexp['wjsc_list']
            prec_intexp_prec_list = prec_intexp['prec_list']
            for p in prec_intexp_prec_list:
                if 'V_list' not in p: raise KeyError()
        except (TypeError, KeyError) as e:
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intexp = precomp['intexp']
        prec_intexp_xjsc_list = prec_intexp['xjsc_list']
        prec_intexp_wjsc_list = prec_intexp['wjsc_list']
        prec_intexp_prec_list = prec_intexp['prec_list']
        try: # precomp_grad_x structures
            if 'partial_x_V_list' not in prec_const: raise KeyError()
            for p in prec_intexp_prec_list:
                if 'partial_x_V_list' not in p: raise KeyError()
        except KeyError as e:
            precomp = self.precomp_grad_x(x, precomp)
        # Evaluation
        out = np.zeros((x.shape[0], self.n_coeffs, x.shape[1]))
        N_cc = self.c.n_coeffs
        out[:,:N_cc,:] = self.c.grad_a_grad_x(x, prec_const)[:,0,:,:]
        for idx in range(x.shape[0]):
            exp = np.exp( self.h.evaluate(
                prec_intexp_xjsc_list[idx],
                precomp=prec_intexp_prec_list[idx] )[:,0] )
            grad_x_h = self.h.grad_x(
                prec_intexp_xjsc_list[idx],
                precomp=prec_intexp_prec_list[idx] )[:,0,:]
            grad_a_h = self.h.grad_a(
                prec_intexp_xjsc_list[idx],
                precomp=prec_intexp_prec_list[idx] )[:,0,:]
            grad_a_grad_x_h = self.h.grad_a_grad_x(
                prec_intexp_xjsc_list[idx],
                precomp=prec_intexp_prec_list[idx] )[:,0,:,:]
            grad_a_grad_x_exp = grad_a_grad_x_h * exp[:,nax,nax] + grad_x_h[:,nax,:] * grad_a_h[:,:,nax] * exp[:,nax,nax]
            out[idx,N_cc:,:] += np.einsum('i,ijk->jk', prec_intexp_wjsc_list[idx], grad_a_grad_x_exp )
        out[:,:,-1] = self.grad_a_partial_xd(x, precomp)[:,0,:]
        return out[:,nax,:,:]

    def precomp_hess_x(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`\nabla^2_{\bf x} f_{\bf a}` at ``x``

        Enriches the ``precomp`` dictionary if necessary.
        
        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary containing the necessary structures
        """
        if precomp is None: precomp = {}
        # precomp_grad_x part (and precomp_evaluate)
        self.precomp_grad_x(x, precomp, precomp_type)
        # Constant part
        if precomp_type == 'uni':
            self.c.precomp_hess_x(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_hess_x(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Exponential part
        for xeval, p in zip(precomp['intexp']['xjsc_list'],
                            precomp['intexp']['prec_list']):
            if precomp_type == 'uni':
                self.h.precomp_hess_x(xeval, p)
            elif precomp_type == 'multi':
                self.h.precomp_Vandermonde_hess_x(xeval, p)
            else: raise ValueError("Unrecognized precomp_type")
        # precomp_grad_x_partial_xd part
        self.precomp_grad_x_partial_xd(x, precomp, precomp_type)
        return precomp

    def precomp_Vandermonde_hess_x(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`\nabla^2_{\bf x} f_{\bf a}` at ``x``

        Enriches the ``precomp`` dictionary if necessary.
        
        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary containing the necessary structures
        """
        return self.precomp_hess_x(x, precomp, precomp_type='multi')

    @counted
    def hess_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Evaluate :math:`\nabla^2_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,d,d`]) --
            :math:`\nabla^2_{\bf x} f_{\bf a}({\bf x})`
        """
        try: # precomp_evaluate structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intexp = precomp['intexp']
            prec_intexp_xjsc_list = prec_intexp['xjsc_list']
            prec_intexp_wjsc_list = prec_intexp['wjsc_list']
            prec_intexp_prec_list = prec_intexp['prec_list']
            for p in prec_intexp_prec_list:
                if 'V_list' not in p: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intexp = precomp['intexp']
        prec_intexp_xjsc_list = prec_intexp['xjsc_list']
        prec_intexp_wjsc_list = prec_intexp['wjsc_list']
        prec_intexp_prec_list = prec_intexp['prec_list']
        try: # precomp_grad_x structures
            if 'partial_x_V_list' not in prec_const: raise KeyError()
            for p in prec_intexp_prec_list:
                if 'partial_x_V_list' not in p: raise KeyError()
        except KeyError as e:
            precomp = self.precomp_grad_x(x, precomp)
        try: # precomp_hess_x structures
            if 'partial2_x_V_list' not in prec_const: raise KeyError()
            for p in prec_intexp_prec_list:
                if 'partial2_x_V_list' not in p: raise KeyError()
        except KeyError as e:
            precomp = self.precomp_hess_x(x, precomp)
        # Evaluation
        out = self.c.hess_x(x, prec_const)[:,0,:,:]
        for idx in range(x.shape[0]):
            exp = np.exp( self.h.evaluate( prec_intexp_xjsc_list[idx],
                                           precomp=prec_intexp_prec_list[idx] ) )[:,0]
            hess_x_h = self.h.hess_x(prec_intexp_xjsc_list[idx],
                                     precomp=prec_intexp_prec_list[idx])[:,0,:,:]
            grad_x_h = self.h.grad_x(prec_intexp_xjsc_list[idx],
                                     precomp=prec_intexp_prec_list[idx])[:,0,:]
            integrand = (hess_x_h + grad_x_h[:,:,nax] * grad_x_h[:,nax,:]) * exp[:,nax,nax]
            out[idx,:,:] += np.einsum( 'i,ijk->jk', prec_intexp_wjsc_list[idx], integrand )
        out[:,-1,:] = self.grad_x_partial_xd(x, precomp)[:,0,:]
        out[:,:,-1] = out[:,-1,:]
        return out[:,nax,:,:]

    @counted
    def grad_a_hess_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf a} \nabla^2_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,d,d`]) --
            :math:`\nabla_{\bf a} \nabla^2_{\bf x} f_{\bf a}({\bf x})`
        """
        try: # precomp_evaluate structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intexp = precomp['intexp']
            prec_intexp_xjsc_list = prec_intexp['xjsc_list']
            prec_intexp_wjsc_list = prec_intexp['wjsc_list']
            prec_intexp_prec_list = prec_intexp['prec_list']
            for p in prec_intexp_prec_list:
                if 'V_list' not in p: raise KeyError()
        except (TypeError, KeyError) as e:
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intexp = precomp['intexp']
        prec_intexp_xjsc_list = prec_intexp['xjsc_list']
        prec_intexp_wjsc_list = prec_intexp['wjsc_list']
        prec_intexp_prec_list = prec_intexp['prec_list']
        try: # precomp_grad_x structures
            if 'partial_x_V_list' not in prec_const: raise KeyError()
            for p in prec_intexp_prec_list:
                if 'partial_x_V_list' not in p: raise KeyError()
        except KeyError as e:
            precomp = self.precomp_grad_x(x, precomp)
        try: # precomp_hess_x structures
            if 'partial2_x_V_list' not in prec_const: raise KeyError()
            for p in prec_intexp_prec_list:
                if 'partial2_x_V_list' not in p: raise KeyError()
        except KeyError as e:
            precomp = self.precomp_hess_x(x, precomp)
        # Evaluation
        out = np.zeros((x.shape[0], self.n_coeffs, x.shape[1], x.shape[1]))
        N_cc = self.c.n_coeffs
        out[:,:N_cc,:,:] = self.c.grad_a_hess_x(x, prec_const)[:,0,:,:,:]
        for idx in range(x.shape[0]):
            exp = np.exp( self.h.evaluate(
                prec_intexp_xjsc_list[idx],
                precomp=prec_intexp_prec_list[idx] )[:,0] )
            hess_x_h = self.h.hess_x(
                prec_intexp_xjsc_list[idx],
                precomp=prec_intexp_prec_list[idx])[:,0,:,:]
            grad_x_h = self.h.grad_x(
                prec_intexp_xjsc_list[idx],
                precomp=prec_intexp_prec_list[idx])[:,0,:]
            grad_a_hess_x_h = self.h.grad_a_hess_x(
                prec_intexp_xjsc_list[idx],
                precomp=prec_intexp_prec_list[idx])[:,0,:,:,:]
            grad_a_h = self.h.grad_a(
                prec_intexp_xjsc_list[idx],
                precomp=prec_intexp_prec_list[idx])[:,0,:]
            grad_a_grad_x_h = self.h.grad_a_grad_x(
                prec_intexp_xjsc_list[idx],
                precomp=prec_intexp_prec_list[idx])[:,0,:,:]
            integrand = (grad_a_hess_x_h + hess_x_h[:,nax,:,:] * grad_a_h[:,:,nax,nax] 
                         + grad_a_grad_x_h[:,:,:,nax] * grad_x_h[:,nax,nax,:]
                         + grad_x_h[:,nax,:,nax] * grad_a_grad_x_h[:,:,nax,:] 
                         + grad_x_h[:,nax,:,nax] * grad_x_h[:,nax,nax,:] * grad_a_h[:,:,nax,nax]) * exp[:,nax,nax,nax]
            out[idx,N_cc:,:,:] += np.einsum( 'i,ijkl->jkl', prec_intexp_wjsc_list[idx], integrand )
        out[:,:,-1,:] = self.grad_a_grad_x_partial_xd(x, precomp) [:,0,:,:]
        out[:,:,:,-1] = out[:,:,-1,:]
        return out[:,nax,:,:,:]

    @cached([('c',None)])
    @counted
    def grad_a(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla_{\bf a} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N`]) --
            :math:`\nabla_{\bf a} f_{\bf a}({\bf x})`
        """
        try:
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intexp = precomp['intexp']
            prec_intexp_xjsc_list = prec_intexp['xjsc_list']
            prec_intexp_wjsc_list = prec_intexp['wjsc_list']
            prec_intexp_prec_list = prec_intexp['prec_list']
            for p in prec_intexp_prec_list:
                if 'V_list' not in p: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intexp = precomp['intexp']
        prec_intexp_xjsc_list = prec_intexp['xjsc_list']
        prec_intexp_wjsc_list = prec_intexp['wjsc_list']
        prec_intexp_prec_list = prec_intexp['prec_list']
        # Retrieve sub-cache
        c_cache = get_sub_cache(cache, ('c',None))
        try:
            h_cache_list = cache['h_cache_list']
        except TypeError:
            h_cache_list = [None]*len(prec_intexp_xjsc_list)
        except KeyError:
            h_cache_list = [{'tot_size': xx.shape[0]}
                            for xx in prec_intexp_xjsc_list]
            cache['h_cache_list'] = h_cache_list
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0], self.n_coeffs))
        # Convert slice to range
        if idxs_slice.start is None: start = 0
        else: start = idxs_slice.start
        if idxs_slice.stop is None: stop = x.shape[0]
        else: stop = idxs_slice.stop
        idxs_list = range(start, stop)
        # Evaluate
        # Constant part
        out[:,:ncc] = self.c.grad_a(x, prec_const, idxs_slice=idxs_slice, cache=c_cache)[:,0,:]
        # Integrated exponential part
        for i, idx in enumerate(idxs_list):
            xjsc = prec_intexp_xjsc_list[idx]
            wjsc = prec_intexp_wjsc_list[idx]
            precomp_exp = prec_intexp_prec_list[idx]
            exp = np.exp( self.h.evaluate(xjsc, precomp_exp, cache=h_cache_list[idx])[:,0] )
            VIexp = self.h.grad_a(xjsc, precomp_exp, cache=h_cache_list[idx])[:,0,:] * exp[:,nax]
            out[i,ncc:] = np.dot( wjsc, VIexp )
        return out[:,nax,:]

    @cached([('c',None)],False)
    @counted
    def hess_a(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla^2_{\bf a} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,N`]) --
            :math:`\nabla^2_{\bf a} f_{\bf a}({\bf x})`
        """
        try:
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intexp = precomp['intexp']
            prec_intexp_xjsc_list = prec_intexp['xjsc_list']
            prec_intexp_wjsc_list = prec_intexp['wjsc_list']
            prec_intexp_prec_list = prec_intexp['prec_list']
            for p in prec_intexp_prec_list:
                if 'V_list' not in p: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intexp = precomp['intexp']
        prec_intexp_xjsc_list = prec_intexp['xjsc_list']
        prec_intexp_wjsc_list = prec_intexp['wjsc_list']
        prec_intexp_prec_list = prec_intexp['prec_list']
        # Retrieve sub-cache
        c_cache = get_sub_cache(cache, ('c',None))
        try:
            h_cache_list = cache['h_cache_list']
        except TypeError:
            h_cache_list = [None]*len(prec_intexp_xjsc_list)
        except KeyError:
            h_cache_list = [{'tot_size': xx.shape[0]}
                            for xx in prec_intexp_xjsc_list]
            cache['h_cache_list'] = h_cache_list
        nc = self.n_coeffs
        ncc = self.c.n_coeffs
        nce = nc - ncc
        out = np.zeros((x.shape[0],nc,nc))
        # Convert slice to range
        if idxs_slice.start is None: start = 0
        else: start = idxs_slice.start
        if idxs_slice.stop is None: stop = x.shape[0]
        else: stop = idxs_slice.stop
        idxs_list = range(start, stop)
        # Evaluate
        # Constant part
        if not isinstance(self.c, LinearSpanTensorizedParametricFunctional):
            out[:,:ncc,:ncc] = self.c.hess_a(
                x, prec_const,
                idxs_slice=idxs_slice, cache=c_cache)[:,0,:,:]
        # Integrated exponential part
        for i, idx in enumerate(idxs_list):
            xjsc = prec_intexp_xjsc_list[idx]
            wjsc = prec_intexp_wjsc_list[idx]
            precomp_exp = prec_intexp_prec_list[idx]
            exp = np.exp( self.h.evaluate( xjsc, precomp_exp, cache=h_cache_list[idx] )[:,0] )
            if isinstance(self.h, LinearSpanTensorizedParametricFunctional):
                grad_a_h_t = self.h.grad_a( xjsc, precomp_exp, cache=h_cache_list[idx] )[:,0,:].T
                exp *= wjsc
                sqrt_exp_abs = np.sqrt(np.abs(exp))
                exp_sign = np.sign(exp)
                grad_a_h_t_1 = grad_a_h_t * sqrt_exp_abs[nax,:]
                grad_a_h_t_2 = grad_a_h_t * (exp_sign*sqrt_exp_abs)[nax,:]
                np.einsum('ik,jk->ij', grad_a_h_t_1, grad_a_h_t_2,
                          out=out[i,ncc:,ncc:], casting='unsafe')
            else:
                hess_a_h = self.h.hess_a( xjsc, precomp_exp, cache=h_cache_list[idx] )[:,0,:,:] # Always zero if h LinSpanApprox
                grad_a_h = self.h.grad_a( xjsc, precomp_exp, cache=h_cache_list[idx] )[:,0,:]
                hess_exp = (hess_a_h + grad_a_h[:,:,nax] * grad_a_h[:,nax,:]) * exp[:,nax,nax]
                np.einsum('i...,i', hess_exp, wjsc, out=out[i,ncc:,ncc:])
        return out[:,nax,:,:]

    def precomp_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary with necessary structures
        """
        if precomp is None: precomp = {}
        # Constant part
        try: precomp_const = precomp['const']
        except KeyError as e: precomp['const'] = {}
        if precomp_type == 'uni':
            self.c.precomp_partial_xd(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_partial_xd(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Integrated exponential part
        try: precomp_exp = precomp['exp']
        except KeyError as e: precomp['exp'] = {}
        if precomp_type == 'uni':
            self.h.precomp_evaluate(x, precomp['exp'])
        elif precomp_type == 'multi':
            self.h.precomp_Vandermonde_evaluate(x, precomp['exp'])
        else: raise ValueError("Unrecognized precomp_type")
        return precomp

    def precomp_Vandermonde_partial_xd(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary with necessary structures
        """
        return self.precomp_partial_xd(x, precomp, precomp_type='multi')

    @cached([('c',None),('h',None)])
    @counted
    def partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1`]) --
            :math:`\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            if 'partial_xd_V_last' not in prec_const: raise KeyError()
            prec_exp = precomp['exp']
            if 'V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_exp = precomp['exp']
        # Retrieve sub-cache
        c_cache, h_cache = get_sub_cache(cache, ('c',None), ('h',None))
        if idxs_slice is None: idxs_slice = range(x.shape[0])
        # Evaluation
        out = self.c.partial_xd(x, prec_const, idxs_slice=idxs_slice, cache=c_cache) + \
              np.exp( self.h.evaluate(x, prec_exp, idxs_slice=idxs_slice, cache=h_cache) )
        return out

    def precomp_grad_x_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary with the necessary structures
        """
        if precomp is None: precomp = {}
        # precomp_partial_xd
        self.precomp_partial_xd(x, precomp, precomp_type)
        # Constant part
        if precomp_type == 'uni':
            self.c.precomp_grad_x_partial_xd(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_grad_x_partial_xd(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Exponential part
        if precomp_type == 'uni':
            self.h.precomp_grad_x(x, precomp['exp'])
        elif precomp_type == 'multi':
            self.h.precomp_Vandermonde_grad_x(x, precomp['exp'])
        else: raise ValueError("Unrecognized precomp_type")
        return precomp

    def precomp_Vandermonde_grad_x_partial_xd(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary with the necessary structures
        """
        return self.precomp_grad_x_partial_xd(x, precomp, precomp_type='multi')

    @counted
    def grad_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,d`]) --
            :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            if 'partial_xd_V_last' not in prec_const: raise KeyError()
            prec_exp = precomp['exp']
            if 'V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_exp = precomp['exp']
        try: # precomp_grad_x_partial_xd structures
            if 'partial_x_V_list' not in prec_const: raise KeyError()
            if 'partial2_xd_V_last' not in prec_const: raise KeyError()
            if 'partial_x_V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            precomp = self.precomp_grad_x_partial_xd(x, precomp)
        # Evaluation
        exp = np.exp( self.h.evaluate(x, precomp=prec_exp) )
        out = self.c.grad_x_partial_xd(x, precomp=prec_const) + \
              self.h.grad_x(x, precomp=prec_exp) * exp[:,nax]
        return out

    @counted
    def grad_a_grad_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None),
                                 *args, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf a} \nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,d`]) --
            :math:`\nabla_{\bf a} \nabla_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            if 'partial_xd_V_last' not in prec_const: raise KeyError()
            prec_exp = precomp['exp']
            if 'V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_exp = precomp['exp']
        try: # precomp_grad_x_partial_xd structures
            if 'partial_x_V_list' not in prec_const: raise KeyError()
            if 'partial2_xd_V_last' not in prec_const: raise KeyError()
            if 'partial_x_V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            precomp = self.precomp_grad_x_partial_xd(x, precomp)
        # Evaluation 
        nc = self.n_coeffs
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0],1,nc,x.shape[1]))
        
        exp = np.exp( self.h.evaluate(x, precomp=prec_exp) )
        grad_x = self.h.grad_x(x, precomp=prec_exp)  
        grad_a = self.h.grad_a(x, precomp=prec_exp) 
        out[:,:,:ncc,:] = self.c.grad_a_grad_x_partial_xd(x, precomp=prec_const) 
        out[:,:,ncc:,:] = self.h.grad_a_grad_x(x, precomp=prec_exp) * exp[:,:,nax,nax] + \
              grad_x[:,:,nax,:] * grad_a[:,:,:,nax] * exp[:,:,nax,nax]
        return out

    def precomp_hess_x_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary with the necessary structures
        """
        if precomp is None: precomp = {}
        # precomp_grad_x_partial_xd (and precomp_partial_xd)
        self.precomp_grad_x_partial_xd(x, precomp, precomp_type)
        # Constant part
        if precomp_type == 'uni':
            self.c.precomp_hess_x_partial_xd(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_hess_x_partial_xd(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Exponential part
        if precomp_type == 'uni':
            self.h.precomp_hess_x(x, precomp['exp'])
        elif precomp_type == 'multi':
            self.h.precomp_Vandermonde_hess_x(x, precomp['exp'])
        else: raise ValueError("Unrecognized precomp_type")
        return precomp

    def precomp_Vandermonde_hess_x_partial_xd(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary with the necessary structures
        """
        return self.precomp_hess_x_partial_xd(x, precomp, precomp_type='multi')

    @counted
    def hess_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Evaluate :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,d,d`]) --
            :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            if 'partial_xd_V_last' not in prec_const: raise KeyError()
            prec_exp = precomp['exp']
            if 'V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_exp = precomp['exp']
        try: # precomp_grad_x_partial_xd structures
            if 'partial_x_V_list' not in prec_const: raise KeyError()
            if 'partial2_xd_V_last' not in prec_const: raise KeyError()
            if 'partial_x_V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            precomp = self.precomp_grad_x_partial_xd(x, precomp)
        try: # precomp_hess_x_partial_xd structures
            if 'partial2_x_V_list' not in prec_const: raise KeyError()
            if 'partial3_xd_V_last' not in prec_const: raise KeyError()
            if 'partial2_x_V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            precomp = self.precomp_hess_x_partial_xd(x, precomp)
        # Evaluation
        exp = np.exp( self.h.evaluate(x, prec_exp) )
        hx = self.h.hess_x(x, prec_exp)
        gx = self.h.grad_x(x, prec_exp)
        out = self.c.hess_x_partial_xd(x, prec_const) + \
              (hx + gx[:,:,:,nax] * gx[:,:,nax,:]) * exp[:,:,nax,nax]
        return out

    @counted
    def grad_a_hess_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None),
                                 *args, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf a}\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,d,d`]) --
            :math:`\nabla_{\bf a}\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            if 'partial_xd_V_last' not in prec_const: raise KeyError()
            prec_exp = precomp['exp']
            if 'V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_exp = precomp['exp']
        try: # precomp_grad_x_partial_xd structures
            if 'partial_x_V_list' not in prec_const: raise KeyError()
            if 'partial2_xd_V_last' not in prec_const: raise KeyError()
            if 'partial_x_V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            precomp = self.precomp_grad_x_partial_xd(x, precomp)
        try: # precomp_hess_x_partial_xd structures
            if 'partial2_x_V_list' not in prec_const: raise KeyError()
            if 'partial3_xd_V_last' not in prec_const: raise KeyError()
            if 'partial2_x_V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            precomp = self.precomp_hess_x_partial_xd(x, precomp)
        # Evaluation
        nc = self.n_coeffs
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0],1,nc,x.shape[1],x.shape[1]))

        exp  = np.exp( self.h.evaluate(x, prec_exp) )
        hx   = self.h.grad_x(x, prec_exp)
        hxx  = self.h.hess_x(x, prec_exp)
        ha   = self.h.grad_a(x, prec_exp)
        haxx = self.h.grad_a_hess_x(x, prec_exp)
        hax  = self.h.grad_a_grad_x(x, prec_exp)

        out[:,:,:ncc,:,:] = self.c.grad_a_hess_x_partial_xd(x, precomp=prec_const) 
        out[:,:,ncc:,:,:] = ha[:,:,:,nax,nax] * hxx[:,:,nax,:,:] * exp[:,:,nax,nax,nax] + \
                            haxx * exp[:,:,nax,nax,nax] + \
                            ha[:,:,:,nax,nax] * hx[:,:,nax,:,nax] * hx[:,:,nax,nax,:] *exp[:,:,nax,nax,nax] + \
                            hax[:,:,:,:,nax] * hx[:,:,nax,nax,:] * exp[:,:,nax,nax,nax] + \
                            hx[:,:,nax,:,nax] * hax[:,:,:,nax,:] * exp[:,:,nax,nax,nax]
        return out

    def precomp_partial2_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`\partial^2_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary with necessary structures
        """
        if precomp is None: precomp = {}
        # Constant part
        try: precomp_const = precomp['const']
        except KeyError as e: precomp['const'] = {}
        if precomp_type == 'uni':
            self.c.precomp_partial2_xd(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_partial2_xd(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Exponential part
        try: exp = precomp['exp']
        except KeyError as e: precomp['exp'] = {}
        if precomp_type == 'uni':
            self.h.precomp_partial_xd(x, precomp['exp'])
        elif precomp_type == 'multi':
            self.h.precomp_Vandermonde_partial_xd(x, precomp['exp'])
        else: raise ValueError("Unrecognized precomp_type")
        return precomp

    def precomp_Vandermonde_partial2_xd(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`\partial^2_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary with necessary structures
        """
        return self.precomp_partial2_xd(x, precomp, precomp_type='multi')

    @counted
    def partial2_xd(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Evaluate :math:`\partial^2_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1`]) --
            :math:`\partial^2_{x_d} f_{\bf a}({\bf x})`
        """
        try: # precomp_partial2_xd structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            if 'partial2_xd_V_last' not in prec_const: raise KeyError()
            prec_exp = precomp['exp']
            if 'V_list' not in prec_exp: raise KeyError()
            if 'partial_xd_V_last' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial2_xd(x, precomp)
        prec_const = precomp['const']
        prec_exp = precomp['exp']
        # Evaluation
        exp = np.exp( self.h.evaluate(x, prec_exp) )
        out = self.c.partial2_xd(x, prec_const) + \
              self.h.partial_xd(x, prec_exp) * exp
        return out

    @cached([('c',None),('h',None)])
    @counted
    def grad_a_partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla_{\bf a}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N`]) --
            :math:`\nabla_{\bf a}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            if 'partial_xd_V_last' not in prec_const: raise KeyError()
            prec_exp = precomp['exp']
            if 'V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_exp = precomp['exp']
        # Retrieve sub-cache
        c_cache, h_cache = get_sub_cache(cache, ('c',None), ('h',None))
        # Evaluation
        if idxs_slice is None: idxs_slice = range(x.shape[0])
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0], 1, self.n_coeffs))
        out[:,:,:ncc] = self.c.grad_a_partial_xd(
            x, prec_const, idxs_slice=idxs_slice, cache=c_cache)
        exp = np.exp( self.h.evaluate(
            x, prec_exp, idxs_slice=idxs_slice, cache=h_cache) )
        out[:,:,ncc:] = self.h.grad_a(
            x, prec_exp, idxs_slice=idxs_slice, cache=h_cache) * exp[:,nax]
        return out

    @cached([('c',None),('h',None)], False)
    @counted
    def hess_a_partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla^2_{\bf a}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,N`]) --
            :math:`\nabla^2_{\bf a}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            if 'partial_xd_V_last' not in prec_const: raise KeyError()
            prec_exp = precomp['exp']
            if 'V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_exp = precomp['exp']
        # Retrieve sub-cache
        c_cache, h_cache = get_sub_cache(cache, ('c',None), ('h',None))
        # Evaluation
        if idxs_slice is None: idxs_slice = range(x.shape[0])
        ncc = self.c.n_coeffs
        nc = self.n_coeffs
        out = np.zeros((x.shape[0], nc, nc))
        if not isinstance(self.c, LinearSpanTensorizedParametricFunctional):
            out[:,:ncc,:ncc] = self.c.hess_a_partial_xd(
                x, prec_const, idxs_slice=idxs_slice, cache=c_cache)[:,0,:,:]
        exp = np.exp( self.h.evaluate(
            x, prec_exp, idxs_slice=idxs_slice, cache=h_cache)[:,0] )
        grad_a_h = self.h.grad_a(
            x, prec_exp, idxs_slice=idxs_slice, cache=h_cache)[:,0,:]
        if isinstance(self.h, LinearSpanTensorizedParametricFunctional):
            sqrt_exp = np.sqrt(exp)
            grad_a_h_sq_exp = grad_a_h * sqrt_exp[:,nax]
            np.einsum('ki,kj->kij', grad_a_h_sq_exp, grad_a_h_sq_exp,
                      out=out[:,ncc:,ncc:], casting='unsafe')
        else:
            hess_a_h = self.h.hess_a(x, prec_exp, idxs_slice=idxs_slice, cache=h_cache)[:,0,:,:]
            out[:,ncc:,ncc:] = (hess_a_h + grad_a_h[:,:,nax] * grad_a_h[:,nax,:]) * \
                               exp[:,nax,nax]
        return out[:,nax,:,:]

    def get_identity_coeffs(self):
        return np.zeros(self.n_coeffs)

    def precomp_regression(self, x, precomp=None, *args, **kwargs):
        r""" Precompute necessary structures for the speed up of :func:`regression`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary to be updated

        Returns:
           (:class:`dict<dict>`) -- dictionary of necessary strucutres
        """
        if precomp is None:
            precomp = {}
        precomp.update( self.precomp_evaluate(x) )
        return precomp


##############
# DEPRECATED #
##############


class MonotonicIntegratedExponentialApproximation(
        IntegratedExponentialParametricMonotoneFunctional
):
    @deprecate(
        'MonotonicIntegratedExponentialApproximation',
        '3.0',
        'Use Functionals.IntegratedExponentialParametricMonotoneFunctional instead'
    )
    def __init__(self, *args, **kwargs):
        super(MonotonicIntegratedExponentialApproximation, self).__init__(
            *args, **kwargs
        )
