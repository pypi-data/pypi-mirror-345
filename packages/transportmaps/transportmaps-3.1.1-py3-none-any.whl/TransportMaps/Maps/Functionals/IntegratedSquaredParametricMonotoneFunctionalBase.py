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

from ...Misc import \
    cached, counted, get_sub_cache, \
    deprecate
from .ParametricFunctionalBase import ParametricFunctionApproximation
from .ParametricMonotoneFunctionalBase import ParametricMonotoneFunctional
from .AnchoredIntegratedSquaredParametricFunctionalBase import AnchoredIntegratedSquaredParametricFunctional
from .LinearSpanTensorizedParametricFunctionalBase import LinearSpanTensorizedParametricFunctional

__all__ = [
    'IntegratedSquaredParametricMonotoneFunctional',
    # Deprecated
    'MonotonicIntegratedSquaredApproximation'
]


class IntegratedSquaredParametricMonotoneFunctional(ParametricMonotoneFunctional):
    r""" Integrated Squared approximation.

    For :math:`{\bf x} \in \mathbb{R}^d` The approximation takes the form:

    .. math::
       :label: integ-sq
       
       f_{\bf a}({\bf x}) = c({\bf x};{\bf a}^c) + \int_0^{{\bf x}_d} \left( h({\bf x}_{1:d-1},t;{\bf a}^e) \right)^2 dt

    where

    .. math::
    
       c({\bf x};{\bf a}^c) = \Phi({\bf x}) {\bf a}^c = \sum_{{\bf i}\in \mathcal{I}_c} \Phi_{\bf i}({\bf x}) {\bf a}^c_{\bf i} \qquad \text{and} \qquad h({\bf x}_{1:d-1},t;{\bf a}^e) = \Psi({\bf x}_{1:d-1},t) {\bf a}^e = \sum_{{\bf i}\in \mathcal{I}_e} \Psi_{\bf i}({\bf x}_{1:d-1},t) {\bf a}^e_{\bf i}

    for the set of basis :math:`\Phi` and :math:`\Psi` with cardinality :math:`\sharp \mathcal{I}_c = N_c` and :math:`\sharp \mathcal{I}_e = N_e`. In the following :math:`N=N_c+N_e`.

    Args:
       c (:class:`LinearSpanTensorizedParametricFunctional`): :math:`d-1` dimensional
         approximation of :math:`c({\bf x}_{1:d-1};{\bf a}^c)`.
       h (:class:`LinearSpanTensorizedParametricFunctional`): :math:`d` dimensional
         approximation of :math:`h({\bf x}_{1:d-1},t;{\bf a}^e)`.
    """

    def __init__(self, c, h):
        if c.dim_in != h.dim_in:
            raise ValueError("The dimension of the constant part and the " +
                             "squared part of the approximation must be " +
                             "the same.")
        if c.directional_orders[-1] != 0:
            raise ValueError("The order along the last direction of the constant " +
                             "part of the approximation must be zero")
        self.c = c
        self.h = AnchoredIntegratedSquaredParametricFunctional( h )
        super(IntegratedSquaredParametricMonotoneFunctional, self).__init__(h.dim_in)

    def get_ncalls_tree(self, indent=""):
        out = super(IntegratedSquaredParametricMonotoneFunctional, self).get_ncalls_tree(indent)
        out += self.c.get_ncalls_tree(indent + " c - ")
        out += self.h.get_ncalls_tree(indent + " h - ")
        return out

    def get_nevals_tree(self, indent=""):
        out = super(IntegratedSquaredParametricMonotoneFunctional, self).get_nevals_tree(indent)
        out += self.c.get_nevals_tree(indent + " c - ")
        out += self.h.get_nevals_tree(indent + " h - ")
        return out

    def get_teval_tree(self, indent=""):
        out = super(IntegratedSquaredParametricMonotoneFunctional, self).get_teval_tree(indent)
        out += self.c.get_teval_tree(indent + " c - ")
        out += self.h.get_teval_tree(indent + " h - ")
        return out

    def update_ncalls_tree(self, obj):
        super(IntegratedSquaredParametricMonotoneFunctional, self).update_ncalls_tree(obj)
        self.c.update_ncalls_tree( obj.c )
        self.h.update_ncalls_tree( obj.h )

    def update_nevals_tree(self, obj):
        super(IntegratedSquaredParametricMonotoneFunctional, self).update_nevals_tree(obj)
        self.c.update_nevals_tree( obj.c )
        self.h.update_nevals_tree( obj.h )

    def update_teval_tree(self, obj):
        super(IntegratedSquaredParametricMonotoneFunctional, self).update_teval_tree(obj)
        self.c.update_teval_tree( obj.c )
        self.h.update_teval_tree( obj.h )
        
    def reset_counters(self):
        super(IntegratedSquaredParametricMonotoneFunctional, self).reset_counters()
        self.c.reset_counters()
        self.h.reset_counters()
        
    def init_coeffs(self):
        r""" Initialize the coefficients :math:`{\bf a}`
        """
        self.c.init_coeffs()
        self.h.init_coeffs()

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
        # Integrated squared part
        try: precomp_intsq = precomp['intsq']
        except KeyError as e: precomp['intsq'] = {}
        self.h.precomp_evaluate(x, precomp['intsq'], precomp_type)
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

    @cached([('c',None),('h',None)])
    @counted
    def evaluate(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1`]) -- function evaluations
        """
        try:
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intsq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        # Retrieve sub-cache
        c_cache, h_cache = get_sub_cache(cache, ('c',None), ('h',None))
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        # Evaluate
        out = self.c.evaluate(x, prec_const, idxs_slice=idxs_slice, cache=c_cache)
        out += self.h.evaluate(x, prec_intsq, idxs_slice=idxs_slice, cache=h_cache)
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
        # Integrated squared part
        self.h.precomp_grad_x(x, precomp['intsq'], precomp_type=precomp_type)
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

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,d`]) --
            :math:`\nabla_{\bf x} f_{\bf a}({\bf x})`
        """
        try: # precomp_evaluate structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intsq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_grad_x(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        # Evaluation
        out = self.c.grad_x(x, prec_const)
        out += self.h.grad_x(x, prec_intsq)
        return out

    @counted
    def grad_a_grad_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Evaluate :math:`\nabla{\bf a} \nabla_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,d`]) --
            :math:`\nabla{\bf a} \nabla_{\bf x} f_{\bf a}({\bf x})`
        """
        try: # precomp_evaluate structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intsq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0], 1, self.n_coeffs, self.dim_in))
        # Evaluation
        out[:,:,:ncc,:] = self.c.grad_a_grad_x(x, prec_const)
        out[:,:,ncc:,:] = self.h.grad_a_grad_x(x, prec_intsq)
        return out

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
        # Squared part
        self.h.precomp_hess_x(x, precomp['intsq'], precomp_type=precomp_type)
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
            prec_intsq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_hess_x(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        # Evaluation
        out = self.c.hess_x(x, prec_const)
        out += self.h.hess_x(x, prec_intsq)
        return out

    @counted
    def grad_a_hess_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Evaluate :math:`\nabla{\bf a} \nabla^2_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,d,d`]) --
            :math:`\nabla{\bf a} \nabla^2_{\bf x} f_{\bf a}({\bf x})`
        """
        try: # precomp_evaluate structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intsq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0], 1, self.n_coeffs, self.dim_in, self.dim_in))
        # Evaluation
        out[:,:,:ncc,:,:] = self.c.grad_a_hess_x(x, prec_const)
        out[:,:,ncc:,:,:] = self.h.grad_a_hess_x(x, prec_intsq)
        return out

    @cached([('c',None),('h',None)])
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
            prec_intsq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        # Retrieve sub-cache
        c_cache, h_cache = get_sub_cache(cache, ('c',None), ('h',None))
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0], 1, self.n_coeffs))
        # Constant part
        out[:,:,:ncc] = self.c.grad_a(x, prec_const, idxs_slice=idxs_slice, cache=c_cache)
        # Integrated squared part
        out[:,:,ncc:] = self.h.grad_a(x, prec_intsq, idxs_slice=idxs_slice, cache=h_cache)
        return out

    @cached([('c',None),('h',None)])
    @counted
    def hess_a(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla^2_{\bf a} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,N`]) --
            :math:`\nabla^2_{\bf a} f_{\bf a}({\bf x})`
        """
        try:
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intsq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        # Retrieve sub-cache
        c_cache, h_cache = get_sub_cache(cache, ('c',None), ('h',None))
        nc = self.n_coeffs
        ncc = self.c.n_coeffs
        nce = nc - ncc
        out = np.zeros((x.shape[0],1,nc,nc))
        # Constant part
        if not isinstance(self.c, LinearSpanTensorizedParametricFunctional):
            out[:,:,:ncc,:ncc] = self.c.hess_a(
                x, prec_const, idxs_slice=idxs_slice, cache=c_cache)
        # Integrated squared part
        out[:,:,ncc:,ncc:] = self.h.hess_a(
            x, prec_intsq, idxs_slice=idxs_slice, cache=h_cache)
        return out
        
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
        # Integrated squared part
        try: precomp_sq = precomp['intsq']
        except KeyError as e: precomp['intsq'] = {}
        self.h.precomp_partial_xd(x, precomp['intsq'], precomp_type)
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
            prec_sq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        # Retrieve sub-cache
        c_cache, h_cache = get_sub_cache(cache, ('c',None), ('h',None))
        prec_const = precomp['const']
        prec_sq = precomp['intsq']
        if idxs_slice is None: idxs_slice = range(x.shape[0])
        # Evaluation
        out = self.c.partial_xd(x, prec_const, idxs_slice=idxs_slice, cache=c_cache) + \
              self.h.partial_xd(x, prec_sq, idxs_slice=idxs_slice, cache=h_cache)
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
        # Squared part
        self.h.precomp_grad_x_partial_xd(x, precomp['intsq'], precomp_type)
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
            prec_sq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_grad_x_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_sq = precomp['intsq']
        # Evaluation
        out = self.c.grad_x_partial_xd(x, precomp=prec_const) + \
              self.h.grad_x_partial_xd(x, precomp=prec_sq)
        return out

    @counted
    def grad_a_grad_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None),
                                 *args, **kwargs):
        r""" Evaluate :math:`\nabla{\bf a} \nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,d`]) --
            :math:`\nabla{\bf a} \nabla_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            prec_sq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_grad_x_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_sq = precomp['intsq']
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0], 1, self.n_coeffs, self.dim_in))
        # Evaluation
        out[:,:,:ncc,:] = self.c.grad_a_grad_x_partial_xd(x, precomp=prec_const)
        out[:,:,ncc:,:] = self.h.grad_a_grad_x_partial_xd(x, precomp=prec_sq)
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
        # Squared part
        self.h.precomp_hess_x_partial_xd(x, precomp['intsq'], precomp_type)
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
            prec_sq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        # Evaluation
        out = self.c.hess_x_partial_xd(x, prec_const) + \
              self.h.hess_x_partial_xd(x, prec_intsq)
        return out

    @counted
    def grad_a_hess_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None),
                                 *args, **kwargs):
        r""" Evaluate :math:`\nabla{\bf a} \nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,d,d`]) --
            :math:`\nabla{\bf a} \nabla^2_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            prec_sq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0], 1, self.n_coeffs, self.dim_in, self.dim_in))
        # Evaluation
        out[:,:,:ncc,:,:] = self.c.grad_a_hess_x_partial_xd(x, prec_const)
        out[:,:,ncc:,:,:] = self.h.grad_a_hess_x_partial_xd(x, prec_intsq)
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
        # Squared part
        try: sq = precomp['intsq']
        except KeyError as e: precomp['intsq'] = {}
        self.h.precomp_partial2_xd(x, precomp['intsq'], precomp_type)
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
            prec_sq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial2_xd(x, precomp)
        prec_const = precomp['const']
        prec_sq = precomp['intsq']
        # Evaluation
        out = self.c.partial2_xd(x, prec_const) + \
              self.h.partial2_xd(x, prec_sq)
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
            prec_sq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        # Retrieve sub-cache
        c_cache, h_cache = get_sub_cache(cache, ('c',None), ('h',None))
        # Evaluation
        if idxs_slice is None: idxs_slice = range(x.shape[0])
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0], 1, self.n_coeffs))
        out[:,:,:ncc] = self.c.grad_a_partial_xd(
            x, prec_const, idxs_slice=idxs_slice, cache=c_cache)
        out[:,:,ncc:] = self.h.grad_a_partial_xd(
            x, prec_intsq, idxs_slice=idxs_slice, cache=h_cache)
        return out

    @cached([('c',None),('h',None)],False)
    @counted
    def hess_a_partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla^2_{\bf a}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict<dict>`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,N`]) --
            :math:`\nabla^2_{\bf a}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            prec_intsq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        # Retrieve sub-cache
        c_cache, h_cache = get_sub_cache(cache, ('c',None), ('h',None))
        # Evaluation
        if idxs_slice is None: idxs_slice = range(x.shape[0])
        ncc = self.c.n_coeffs
        nc = self.n_coeffs
        out = np.zeros((x.shape[0], 1, nc, nc))
        if not isinstance(self.c, LinearSpanTensorizedParametricFunctional):
            out[:,:,:ncc,:ncc] = self.c.hess_a_partial_xd(
                x, prec_const, idxs_slice=idxs_slice, cache=c_cache)
        out[:,:,ncc:,ncc:] = self.h.hess_a_partial_xd(
            x, prec_intsq, idxs_slice=idxs_slice, cache=h_cache)
        return out

    def get_identity_coeffs(self):
        # Define the identity map
        coeffs = np.zeros(self.n_coeffs)
        idx = next(i for i,x in enumerate(self.h.multi_idxs)
                   if x == tuple([0]*self.h.dim_in))
        coeffs[self.c.n_coeffs + idx] = 1.
        return coeffs
        
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


class MonotonicIntegratedSquaredApproximation(
        IntegratedSquaredParametricMonotoneFunctional
):
    @deprecate(
        'MonotonicIntegratedSquaredApproximation',
        '3.0',
        'IntegratedSquaredParametricMonotoneFunctional'
    )
    def __init__(self, *args, **kwars):
        super(MonotonicIntegratedSquaredApproximation, self).__init__(
            *args, **kwars)
