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

from TransportMaps.Misc import counted, cached, get_sub_cache, deprecate
from .ParametricFunctionalBase import ParametricFunctional
from .LinearSpanTensorizedParametricFunctionalBase import LinearSpanTensorizedParametricFunctional

__all__ = [
    'AnchoredIntegratedSquaredParametricFunctional',
    # Deprecated
    'IntegratedSquaredParametricFunctionApproximation'
]

nax = np.newaxis

class AnchoredIntegratedSquaredParametricFunctional(ParametricFunctional):
    r""" Parameteric function :math:`f_{\bf a}({\bf x}) = \int_0^{x_d} h_{\bf a}^2(x_1,\ldots,x_{d-1},t) dt`

    Args:
      h (:class:`ParametricFunctionApproximation`): parametric function :math:`h`
      integ_ord_mult (int): multiplier for the number of Gauss points to be used
         in the approximation of :math:`\int_0^{{\bf x}_d}`. The resulting number of
         points is given by the product of the order in the :math:`d` direction
         and ``integ_ord_mult``.
    """
    def __init__(self, h, integ_ord_mult=6):
        self.h = h
        self.coeffs = self.h.coeffs
        super(AnchoredIntegratedSquaredParametricFunctional, self).__init__(self.h.dim_in)
        # Initialize the squared base
        if isinstance(self.h, LinearSpanTensorizedParametricFunctional) and \
           isinstance(self.h.basis_list[-1], S1D.OrthogonalPolynomial):
            self.sq_basis = S1D.SquaredOrthogonalPolynomial(self.h.basis_list[-1])
        elif isinstance(self.h, LinearSpanTensorizedParametricFunctional) and \
             isinstance(self.h.basis_list[-1],
                        S1D.ConstantExtendedHermiteProbabilistsFunction):
            self.sq_basis = S1D.SquaredConstantExtendedHermiteProbabilistsFunction()
        # elif isinstance(self.h, LinearSpanTensorizedParametricFunctional) and \
        #      isinstance(self.h.basis_list[-1],
        #                 S1D.ConstantExtendedHermitePhysicistsFunction):
        #     self.sq_basis = S1D.PositiveDefiniteSquaredConstantExtendedHermitePhysicistsFunction()
        else:
            self.logger.warn("""
                             The basis provided is not an orthogonal polynomial or
                             a ConstantExtendedHermitePhysicistsFunction.
                             Quadratures are used for the
                             IntegratedSquaredParametricFunctionApproximation.
                             This will lead to slower computation times and
                             higher memory usage.
                             """)
            self.sq_basis = None
            self.integ_ord_mult = integ_ord_mult
            self.P_JAC = S1D.JacobiPolynomial(0.,0.)

    def init_coeffs(self):
        r""" Initialize the coefficients :math:`{\bf a}`
        """
        self.h.init_coeffs()
        
    @property
    def dim_in(self):
        return self.h.dim_in

    @dim_in.setter
    def dim_in(self, dim):
        self.h.dim_in = dim

    @property
    def n_coeffs(self):
        r""" Get the number :math:`N` of coefficients :math:`{\bf a}`

        Returns:
          (:class:`int<int>`) -- number of coefficients
        """
        return self.h.n_coeffs

    @property
    def coeffs(self):
        r""" Get the coefficients :math:`{\bf a}`

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients
        """
        return self.h.coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients :math:`{\bf a}`.

        Args:
          coeffs (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
        """
        self.h.coeffs = coeffs

    @deprecate("IntegratedSquaredParametricFunctionApproximation.get_multi_idxs()",
               "2.0",
               "Use property IntegratedSquaredParametricFunctionApproximation.multi_idxs")
    def get_multi_idxs(self):
        r""" Get the list of multi indices

        Return:
          (:class:`list` of :class:`tuple`) -- multi indices
        """
        return self.h.get_multi_idxs()

    @deprecate("IntegratedSquaredParametricFunctionApproximation.set_multi_idxs()",
               "2.0",
               "Use property IntegratedSquaredParametricFunctionApproximation.multi_idxs")
    def set_multi_idxs(self, multi_idxs):
        r""" Set the list of multi indices

        Args:
          multi_idxs (:class:`list` of :class:`tuple`): multi indices
        """
        self.h.set_multi_idxs()

    @property
    def multi_idxs(self):
        return self.h.multi_idxs

    @multi_idxs.setter
    def multi_idxs(self, midxs):
        self.h.multi_idxs = midxs

    @property
    def semilattice(self):
        return self.h.semilattice

    @semilattice.setter
    def semilattice(self, semilattice):
        self.h.semilattice = semilattice

    @property
    def basis_list(self):
        return self.h.basis_list

    @basis_list.setter
    def basis_list(self, basis_list):
        self.h.basis_list = basis_list

    @property
    def full_basis_list(self):
        return self.h.full_basis_list

    @full_basis_list.setter
    def full_basis_list(self, blist):
        self.h.full_basis_list = blist

    def precomp_evaluate(self, x, precomp=None, precomp_type='uni'):
        if precomp is None: precomp = {}
        if self.sq_basis is None:
            try:
                xjsc_list = precomp['xjsc_list']
                wjsc_list = precomp['wjsc_list']
            except KeyError as e:
                precomp['xjsc_list'] = []
                precomp['wjsc_list'] = []
                xd_order = (self.h.directional_orders)[-1]
                (xj,wj) = self.P_JAC.Quadrature( self.integ_ord_mult * xd_order, norm=True )
                xj = xj / 2. + 0.5  # Mapped to [0,1]
                for idx in range(x.shape[0]):
                    wjsc = wj * x[idx,-1]
                    xjsc = xj * x[idx,-1]
                    xother = np.tile( x[idx,:-1], (len(xjsc), 1) )
                    xeval = np.hstack( (xother, xjsc[:,nax]) )
                    # Append values
                    precomp['xjsc_list'].append( xeval )
                    precomp['wjsc_list'].append( wjsc )
            try: precomp_intsq_list = precomp['prec_list']
            except KeyError as e:
                precomp['prec_list'] = [{} for i in range(x.shape[0])]
            for idx, (xeval, p) in enumerate(zip(precomp['xjsc_list'],
                                                 precomp['prec_list'])):
                if precomp_type == 'uni':
                    self.h.precomp_evaluate(xeval, p)
                elif precomp_type == 'multi':
                    self.h.precomp_Vandermonde_evaluate(xeval, p)
                else: raise ValueError("Unrecognized precomp_type")
        else:
            # Vandermonde matrices
            try:
                V_list = precomp['V_list']
            except KeyError as e:
                precomp['V_list'] = [ b.GradVandermonde(x[:,i], o)
                                      for i,(b,o) in
                                      enumerate(zip(self.h.basis_list[:-1],
                                                    self.h.directional_orders[:-1])) ]
            # Integrated squared Vandermonde matrix
            try:
                IntSqV1d = precomp['IntSqV1d']
            except KeyError as e:
                o = self.h.directional_orders[-1]
                precomp['IntSqV1d'] = self.sq_basis.GradVandermonde(x[:,-1], o, k=-1)
            if precomp_type == 'multi' and 'V' not in precomp:
                # Compute general Vandermonde matrix (m x N x N)
                # Unroll only the first sum
                V_list = precomp['V_list']
                IntSqV1d = precomp['IntSqV1d']
                IntSqVmd = np.ones((IntSqV1d.shape[0], self.n_coeffs, self.n_coeffs))
                # Fill upper triangular part
                for i in range(self.n_coeffs):
                    for j in range(i+1, self.n_coeffs):
                        midx_i = self.h.multi_idxs[i]
                        midx_j = self.h.multi_idxs[j]
                        for idx, V1d in zip(midx_i[:-1], V_list):
                            IntSqVmd[:,i,j] *= V1d[:,idx]
                        for idx, V1d in zip(midx_j[:-1], V_list):
                            IntSqVmd[:,i,j] *= V1d[:,idx]
                        IntSqVmd[:,i,j] *= IntSqV1d[:,midx_i[-1],midx_j[-1]]
                # Fill diagonal
                for i, midx in enumerate(self.h.multi_idxs):
                    for idx, V1d in zip(midx[:-1], V_list):
                        IntSqVmd[:,i,i] *= V1d[:,idx]**2.
                    IntSqVmd[:,i,i] *= IntSqV1d[:,midx[-1],midx[-1]]
                # Fill lower triangular part (symmetrize)
                for i in range(1,self.n_coeffs):
                    for j in range(i):
                        IntSqVmd[:,i,j] = IntSqVmd[:,j,i]
                precomp['IntSqVmd'] = IntSqVmd
        return precomp

    @cached()
    @counted
    def evaluate(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict<dict>`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1`]) -- function evaluations
        """
        if self.sq_basis is None:
            try:
                prec_intsq_xjsc_list = precomp['xjsc_list']
                prec_intsq_wjsc_list = precomp['wjsc_list']
                prec_intsq_prec_list = precomp['prec_list']
                for p in prec_intsq_prec_list:
                    if 'V_list' not in p: raise KeyError()
            except (TypeError, KeyError) as e:
                idxs_slice = slice(None)
                precomp = self.precomp_evaluate(x, precomp)
            prec_intsq_xjsc_list = precomp['xjsc_list']
            prec_intsq_wjsc_list = precomp['wjsc_list']
            prec_intsq_prec_list = precomp['prec_list']
            # Convert slice to range
            if idxs_slice.start is None: start = 0
            else: start = idxs_slice.start
            if idxs_slice.stop is None: stop = x.shape[0]
            else: stop = idxs_slice.stop
            idxs_list = range(start, stop)
            # Evaluate
            out = np.zeros(len(idxs_list))
            for i, idx in enumerate(idxs_list):# other_idxs:
                h_eval = self.h.evaluate(
                    prec_intsq_xjsc_list[idx],
                    precomp=prec_intsq_prec_list[idx])[:,0]
                out[i] += np.dot( h_eval**2., prec_intsq_wjsc_list[idx] )
        else:
            try:
                precomp['IntSqVmd']
            except (TypeError, KeyError) as e:
                try:
                    precomp['V_list']
                    precomp['IntSqV1d']
                    self.precomp_evaluate(x, precomp, precomp_type='multi')
                except (TypeError, KeyError) as e:
                    precomp = self.precomp_evaluate(x, precomp, precomp_type='multi')
                    idxs_slice = slice(None)
            IntSqVmd = precomp['IntSqVmd']
            out = np.dot( np.tensordot(IntSqVmd[idxs_slice,:,:], self.h.coeffs, axes=(2,0)),
                          self.h.coeffs )
        return out[:,nax]

    def precomp_grad_x(self, x, precomp, precomp_type='uni'):
        if precomp is None: precomp = {}
        if self.sq_basis is None:
            self.precomp_evaluate(x, precomp, precomp_type)
            self.precomp_partial_xd(x, precomp, precomp_type)
            for xeval, p in zip(precomp['xjsc_list'],
                                precomp['prec_list']):
                if precomp_type == 'uni':
                    self.h.precomp_grad_x(xeval, p)
                elif precomp_type == 'multi':
                    self.h.precomp_Vandermonde_grad_x(xeval, p)
                else: raise ValueError("Unrecognized precomp_type")
        else:
            self.precomp_evaluate(x, precomp, precomp_type='uni')
            self.precomp_partial_xd(x, precomp, precomp_type)
            # Vandermonde matrices
            try:
                partial_x_V_list = precomp['partial_x_V_list']
            except KeyError as e:
                partial_x_V_list = [ b.GradVandermonde(x[:,i], o, k=1)
                                     for i,(b,o) in enumerate(zip(
                                             self.h.basis_list[:-1],
                                             self.h.directional_orders[:-1])) ]
                precomp['partial_x_V_list'] = partial_x_V_list
            if precomp_type == 'multi' and 'grad_x_IntSqVmd_list' not in precomp:
                V_list = precomp['V_list']
                IntSqV1d = precomp['IntSqV1d']
                grad_x_IntSqVmd_list = []
                for d in range(self.dim_in-1):
                    grad_x_V = np.ones((x.shape[0], self.n_coeffs, self.n_coeffs))
                    # Fill upper triangular part (including diagonal)
                    for i in range(self.n_coeffs):
                        for j in range(self.n_coeffs):
                            midx_i = self.h.multi_idxs[i]
                            midx_j = self.h.multi_idxs[j]
                            for k, (idx, V1d, pxV1d) in enumerate(zip(
                                    midx_i[:-1], V_list, partial_x_V_list)):
                                if k != d:
                                    grad_x_V[:,i,j] *= V1d[:,idx]
                                else:
                                    grad_x_V[:,i,j] *= pxV1d[:,idx]
                            for idx, V1d in zip(midx_j[:-1], V_list):
                                grad_x_V[:,i,j] *= V1d[:,idx]
                            grad_x_V[:,i,j] *= IntSqV1d[:,midx_i[-1],midx_j[-1]]
                    grad_x_IntSqVmd_list.append(grad_x_V)
                precomp['grad_x_IntSqVmd_list'] = grad_x_IntSqVmd_list
        return precomp

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
        if self.sq_basis is None:
            try:
                prec_intsq_xjsc_list = precomp['xjsc_list']
                prec_intsq_wjsc_list = precomp['wjsc_list']
                prec_intsq_prec_list = precomp['prec_list']
                for p in prec_intsq_prec_list:
                    if 'V_list' not in p: raise KeyError()
            except (TypeError, KeyError) as e:
                idxs_slice = slice(None)
                precomp = self.precomp_grad_x(x, precomp)
            prec_intsq_xjsc_list = precomp['xjsc_list']
            prec_intsq_wjsc_list = precomp['wjsc_list']
            prec_intsq_prec_list = precomp['prec_list']
            # Convert slice to range
            if idxs_slice.start is None: start = 0
            else: start = idxs_slice.start
            if idxs_slice.stop is None: stop = x.shape[0]
            else: stop = idxs_slice.stop
            idxs_list = range(start, stop)
            # Evaluate
            out = np.zeros((len(idxs_list),self.dim_in))
            for i, idx in enumerate(idxs_list):
                ev = self.h.evaluate( prec_intsq_xjsc_list[idx],
                                      precomp=prec_intsq_prec_list[idx] )[:,0]
                grad_x = self.h.grad_x( prec_intsq_xjsc_list[idx],
                                        precomp=prec_intsq_prec_list[idx] )[:,0,:]
                out[i,:] += np.dot( prec_intsq_wjsc_list[idx], 2. * ev[:,nax] * grad_x )
            out[:,-1] = self.partial_xd(x, precomp)[:,0]
        else:
            try:
                precomp['grad_x_IntSqVmd_list']
            except (TypeError, KeyError) as e:
                precomp = self.precomp_grad_x(x, precomp, precomp_type='multi')
                idxs_slice = slice(None)
            grad_x_IntSqVmd_list = precomp['grad_x_IntSqVmd_list']
            # Convert slice to range
            if idxs_slice.start is None: start = 0
            else: start = idxs_slice.start
            if idxs_slice.stop is None: stop = x.shape[0]
            else: stop = idxs_slice.stop
            idxs_list = range(start, stop)
            # Evaluate
            out = np.zeros((len(idxs_list),self.dim_in))
            for d, grad_x_IntSqVmd in enumerate(grad_x_IntSqVmd_list):
                out[:,d] = 2. * np.dot( np.tensordot(grad_x_IntSqVmd[idxs_slice,:,:],
                                                     self.h.coeffs, axes=(2,0)), self.h.coeffs )
            out[:,-1] = self.partial_xd(x, precomp, idxs_slice=idxs_slice)[:,0]
        return out[:,nax,:]

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
            :math:`\nabla_{\bf a}\nabla_{\bf x} f_{\bf a}({\bf x})`
        """
        if self.sq_basis is None:
            try:
                prec_intsq_xjsc_list = precomp['xjsc_list']
                prec_intsq_wjsc_list = precomp['wjsc_list']
                prec_intsq_prec_list = precomp['prec_list']
                for p in prec_intsq_prec_list:
                    if 'V_list' not in p: raise KeyError()
            except (TypeError, KeyError) as e:
                idxs_slice = slice(None)
                precomp = self.precomp_grad_x(x, precomp)
            prec_intsq_xjsc_list = precomp['xjsc_list']
            prec_intsq_wjsc_list = precomp['wjsc_list']
            prec_intsq_prec_list = precomp['prec_list']
            # Convert slice to range
            if idxs_slice.start is None: start = 0
            else: start = idxs_slice.start
            if idxs_slice.stop is None: stop = x.shape[0]
            else: stop = idxs_slice.stop
            idxs_list = range(start, stop)
            # Evaluate
            out = np.zeros((len(idxs_list), self.n_coeffs, self.dim_in))
            for i, idx in enumerate(idxs_list):
                ev = self.h.evaluate(
                    prec_intsq_xjsc_list[idx],
                    precomp=prec_intsq_prec_list[idx] )[:,0]
                grad_x = self.h.grad_x(
                    prec_intsq_xjsc_list[idx],
                    precomp=prec_intsq_prec_list[idx] )[:,0,:]
                grad_a = self.h.grad_a(
                    prec_intsq_xjsc_list[idx],
                    precomp=prec_intsq_prec_list[idx] )[:,0,:]
                grad_a_grad_x = self.h.grad_a_grad_x(
                    prec_intsq_xjsc_list[idx],
                    precomp=prec_intsq_prec_list[idx] )[:,0,:,:]
                out[i,:,:] += np.tensordot(
                    prec_intsq_wjsc_list[idx], 2. * ev[:,nax,nax] * grad_a_grad_x + \
                    2. * grad_x[:,nax,:] * grad_a[:,:,nax], axes=(0,0) )
            out[:,:,-1] = self.grad_a_partial_xd(x, precomp)[:,0,:]
        else:
            try:
                precomp['grad_x_IntSqVmd_list']
            except (TypeError, KeyError) as e:
                precomp = self.precomp_grad_x(x, precomp, precomp_type='multi')
                idxs_slice = slice(None)
            grad_x_IntSqVmd_list = precomp['grad_x_IntSqVmd_list']
            # Convert slice to range
            if idxs_slice.start is None: start = 0
            else: start = idxs_slice.start
            if idxs_slice.stop is None: stop = x.shape[0]
            else: stop = idxs_slice.stop
            idxs_list = range(start, stop)
            # Evaluate
            out = np.zeros((len(idxs_list), self.n_coeffs, self.dim_in))
            # Q: What about factor of 2(necessary in grad_x)?
            for d, grad_x_IntSqVmd in enumerate(grad_x_IntSqVmd_list):
                out[:,:,d] = 2. * np.tensordot(
                    grad_x_IntSqVmd[idxs_slice,:,:], self.h.coeffs, axes=(2,0))
                out[:,:,-1] = self.grad_a_partial_xd(x, precomp, idxs_slice=idxs_slice)[:,0,:]
        return out[:,nax,:,:]

    def precomp_hess_x(self, x, precomp, precomp_type='uni'):
        if precomp is None: precomp = {}
        if self.sq_basis is None:
            self.precomp_grad_x(x, precomp, precomp_type)
            self.precomp_grad_x_partial_xd(x, precomp, precomp_type)
            for xeval, p in zip(precomp['xjsc_list'],
                                precomp['prec_list']):
                if precomp_type == 'uni':
                    self.h.precomp_hess_x(xeval, p)
                elif precomp_type == 'multi':
                    self.h.precomp_Vandermonde_hess_x(xeval, p)
                else: raise ValueError("Unrecognized precomp_type")
        else:
            self.precomp_grad_x(x, precomp, precomp_type='uni')
            self.precomp_grad_x_partial_xd(x, precomp, precomp_type=precomp_type)
            try:
                partial2_xd_V_list = precomp['partial2_xd_V_list']
            except KeyError as e:
                partial2_x_V_list = [ b.GradVandermonde(x[:,i], o, k=2)
                                      for i,(b,o) in enumerate(zip(
                                              self.h.basis_list[:-1],
                                              self.h.directional_orders[:-1])) ]
                precomp['partial2_x_V_list'] = partial2_x_V_list
            if precomp_type == 'multi' and 'hess_x_IntSqVmd_mat' not in precomp:
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
                IntSqV1d = precomp['IntSqV1d']
                hess_x_IntSqVmd_mat = np.empty((self.dim_in-1, self.dim_in-1), dtype=object)
                for d1 in range(self.dim_in-1):
                    for d2 in range(self.dim_in-1):
                        # PART 1: \partial_x^2 \phi \Phi \phi
                        hess_x_V1 = np.ones((x.shape[0], self.n_coeffs, self.n_coeffs))
                        # Fill all (non symmetric)
                        for i in range(self.n_coeffs):
                            for j in range(self.n_coeffs):
                                midx_i = self.h.multi_idxs[i]
                                midx_j = self.h.multi_idxs[j]
                                for k, (idx, V1d, pxV1d, p2xV1d) in enumerate(zip(
                                        midx_i[:-1], V_list, partial_x_V_list, partial2_x_V_list)):
                                    if d1 == d2 and k == d1:
                                        hess_x_V1[:,i,j] *= p2xV1d[:,idx]
                                    elif k == d1 or k == d2:
                                        hess_x_V1[:,i,j] *= pxV1d[:,idx]
                                    else:
                                        hess_x_V1[:,i,j] *= V1d[:,idx]
                                for idx, V1d in zip(midx_j[:-1], V_list):
                                    hess_x_V1[:,i,j] *= V1d[:,idx]
                                hess_x_V1[:,i,j] *= IntSqV1d[:,midx_i[-1],midx_j[-1]]
                        # PART 2: \partial_x \phi \Phi \partial_x \phi
                        hess_x_V2 = np.ones((x.shape[0], self.n_coeffs, self.n_coeffs))
                        # Fill upper triangular and diagonal
                        for i in range(self.n_coeffs):
                            for j in range(i,self.n_coeffs):
                                midx_i = self.h.multi_idxs[i]
                                midx_j = self.h.multi_idxs[j]
                                for k, (idx, V1d, pxV1d) in enumerate(zip(
                                        midx_i[:-1], V_list, partial_x_V_list)):
                                    if k != d1:
                                        hess_x_V2[:,i,j] *= V1d[:,idx]
                                    else:
                                        hess_x_V2[:,i,j] *= pxV1d[:,idx]
                                for k, (idx, V1d, pxV1d) in enumerate(zip(
                                        midx_j[:-1], V_list, partial_x_V_list)):
                                    if k != d2:
                                        hess_x_V2[:,i,j] *= V1d[:,idx]
                                    else:
                                        hess_x_V2[:,i,j] *= pxV1d[:,idx]
                                hess_x_V2[:,i,j] *= IntSqV1d[:,midx_i[-1],midx_j[-1]]
                        # Fill lower triangular (symmetrize)
                        for i in range(1,self.n_coeffs):
                            for j in range(i):
                                hess_x_V2[:,i,j] = hess_x_V2[:,j,i]
                        # SUM PART 1 + PART 2
                        hess_x_IntSqVmd_mat[d1,d2] = hess_x_V1 + hess_x_V2
                precomp['hess_x_IntSqVmd_mat'] = hess_x_IntSqVmd_mat
        return precomp

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
        if self.sq_basis is None:
            try:
                prec_intsq_xjsc_list = precomp['xjsc_list']
                prec_intsq_wjsc_list = precomp['wjsc_list']
                prec_intsq_prec_list = precomp['prec_list']
                for p in prec_intsq_prec_list:
                    if 'V_list' not in p: raise KeyError()
            except (TypeError, KeyError) as e:
                idxs_slice = slice(None)
                precomp = self.precomp_hess_x(x, precomp)
            prec_intsq_xjsc_list = precomp['xjsc_list']
            prec_intsq_wjsc_list = precomp['wjsc_list']
            prec_intsq_prec_list = precomp['prec_list']
            # Convert slice to range
            if idxs_slice.start is None: start = 0
            else: start = idxs_slice.start
            if idxs_slice.stop is None: stop = x.shape[0]
            else: stop = idxs_slice.stop
            idxs_list = range(start, stop)
            # Evaluate
            out = np.zeros((len(idxs_list),self.dim_in,self.dim_in))
            for i, idx in enumerate(idxs_list):
                ev = self.h.evaluate( prec_intsq_xjsc_list[idx],
                                      precomp=prec_intsq_prec_list[idx] )[:,0]
                hess_x = self.h.hess_x(prec_intsq_xjsc_list[idx],
                                       precomp=prec_intsq_prec_list[idx])[:,0,:,:]
                grad_x = self.h.grad_x(prec_intsq_xjsc_list[idx],
                                       precomp=prec_intsq_prec_list[idx])[:,0,:]
                integrand = 2. * (ev[:,nax,nax] * hess_x + grad_x[:,:,nax] * grad_x[:,nax,:])
                out[i,:,:] += np.einsum( 'i,ijk->jk', prec_intsq_wjsc_list[idx], integrand )
            out[:,-1,:] = self.grad_x_partial_xd(x, precomp)[:,0,:]
            out[:,:,-1] = out[:,-1,:]
        else:
            try:
                precomp['hess_x_IntSqVmd_mat']
            except (TypeError, KeyError) as e:
                precomp = self.precomp_hess_x(x, precomp, precomp_type='multi')
                idxs_slice = slice(None)
            hess_x_IntSqVmd_mat = precomp['hess_x_IntSqVmd_mat']
            # Convert slice to range
            if idxs_slice.start is None: start = 0
            else: start = idxs_slice.start
            if idxs_slice.stop is None: stop = x.shape[0]
            else: stop = idxs_slice.stop
            idxs_list = range(start, stop)
            # Evaluate
            out = np.zeros((len(idxs_list), self.dim_in, self.dim_in))
            # Upper triangular part and diagonal
            for d1 in range(self.dim_in-1):
                for d2 in range(d1, self.dim_in-1):
                    hess_x_V = hess_x_IntSqVmd_mat[d1,d2]
                    out[:,d1,d2] = 2. * np.dot( np.tensordot(
                        hess_x_V[idxs_slice,:,:], self.h.coeffs, axes=(2,0)), self.h.coeffs )
            # Symmetrize
            for d1 in range(1,self.dim_in-1):
                for d2 in range(d1):
                    out[:,d1,d2] = out[:,d2,d1]
            # Complete last col and row
            out[:,-1,:] = self.grad_x_partial_xd(x, precomp)[:,0,:]
            out[:,:,-1] = out[:,-1,:]
        return out[:,nax,:,:]

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
        if self.sq_basis is None:
            try:
                prec_intsq_xjsc_list = precomp['xjsc_list']
                prec_intsq_wjsc_list = precomp['wjsc_list']
                prec_intsq_prec_list = precomp['prec_list']
                for p in prec_intsq_prec_list:
                    if 'V_list' not in p: raise KeyError()
            except (TypeError, KeyError) as e:
                idxs_slice = slice(None)
                precomp = self.precomp_hess_x(x, precomp)
            prec_intsq_xjsc_list = precomp['xjsc_list']
            prec_intsq_wjsc_list = precomp['wjsc_list']
            prec_intsq_prec_list = precomp['prec_list']
            # Convert slice to range
            if idxs_slice.start is None: start = 0
            else: start = idxs_slice.start
            if idxs_slice.stop is None: stop = x.shape[0]
            else: stop = idxs_slice.stop
            idxs_list = range(start, stop)
            # Evaluate
            out = np.zeros((len(idxs_list), self.n_coeffs, self.dim_in,self.dim_in))
            for i, idx in enumerate(idxs_list):
                ev = self.h.evaluate(
                    prec_intsq_xjsc_list[idx],
                    precomp=prec_intsq_prec_list[idx] )[:,0]
                hess_x = self.h.hess_x(
                    prec_intsq_xjsc_list[idx],
                    precomp=prec_intsq_prec_list[idx])[:,0,:,:]
                grad_x = self.h.grad_x(
                    prec_intsq_xjsc_list[idx],
                    precomp=prec_intsq_prec_list[idx])[:,0,:]
                grad_a = self.h.grad_a(
                    prec_intsq_xjsc_list[idx],
                    precomp=prec_intsq_prec_list[idx])[:,0,:]
                grad_a_grad_x = self.h.grad_a_grad_x(
                    prec_intsq_xjsc_list[idx],
                    precomp=prec_intsq_prec_list[idx])[:,0,:,:]
                grad_a_hess_x = self.h.grad_a_hess_x(
                    prec_intsq_xjsc_list[idx],
                    precomp=prec_intsq_prec_list[idx])[:,0,:,:,:]
                integrand = 2. * (ev[:,nax,nax,nax] * grad_a_hess_x + hess_x[:,nax,:,:] * grad_a[:,:,nax,nax] + \
                                    grad_a_grad_x[:,:,:,nax]*grad_x[:,nax,nax,:] + grad_x[:,nax,:,nax]*grad_a_grad_x[:,:,nax,:])
                out[i,:,:,:] += np.einsum( 'i,ijkl->jkl', prec_intsq_wjsc_list[idx], integrand )
            out[:,:,-1,:] = self.grad_a_grad_x_partial_xd(x, precomp)[:,0,:,:]
            out[:,:,:,-1] = out[:,:,-1,:]
        else:
            try:
                precomp['hess_x_IntSqVmd_mat']
            except (TypeError, KeyError) as e:
                precomp = self.precomp_hess_x(x, precomp, precomp_type='multi')
                idxs_slice = slice(None)
            hess_x_IntSqVmd_mat = precomp['hess_x_IntSqVmd_mat']
            # Convert slice to range
            if idxs_slice.start is None: start = 0
            else: start = idxs_slice.start
            if idxs_slice.stop is None: stop = x.shape[0]
            else: stop = idxs_slice.stop
            idxs_list = range(start, stop)
            # Evaluate
            out = np.zeros((len(idxs_list), self.n_coeffs, self.dim_in, self.dim_in))
            # Upper triangular part and diagonal
            # Check with DB for coeff (2x) and happened to hess_x c?
            for d1 in range(self.dim_in-1):
                for d2 in range(d1, self.dim_in-1):
                    hess_x_V = hess_x_IntSqVmd_mat[d1,d2]
                    out[:,:,d1,d2] = 2. * np.tensordot( hess_x_V[idxs_slice,:,:], self.h.coeffs, axes=(2,0))
            # Symmetrize
            for d1 in range(1,self.dim_in-1):
                for d2 in range(d1):
                    out[:,:,d1,d2] = out[:,:,d2,d1]
            # Complete last col and row
            out[:,:,-1,:] = self.grad_a_grad_x_partial_xd(x, precomp)[:,0,:,:]
            out[:,:,:,-1] = out[:,:,-1,:]
        return out[:,nax,:,:,:]

    @cached()
    @counted
    def grad_a(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla_{\bf a} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict<dict>`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N`]) --
            :math:`\nabla_{\bf a} f_{\bf a}({\bf x})`
        """
        if self.sq_basis is None:
            try:
                prec_intsq_xjsc_list = precomp['xjsc_list']
                prec_intsq_wjsc_list = precomp['wjsc_list']
                prec_intsq_prec_list = precomp['prec_list']
                for p in prec_intsq_prec_list:
                    if 'V_list' not in p: raise KeyError()
            except (TypeError, KeyError) as e:
                idxs_slice = slice(None)
                precomp = self.precomp_evaluate(x, precomp)
            prec_intsq_xjsc_list = precomp['xjsc_list']
            prec_intsq_wjsc_list = precomp['wjsc_list']
            prec_intsq_prec_list = precomp['prec_list']
            # Convert slice to range
            if idxs_slice.start is None: start = 0
            else: start = idxs_slice.start
            if idxs_slice.stop is None: stop = x.shape[0]
            else: stop = idxs_slice.stop
            idxs_list = range(start, stop)
            # Evaluate
            out = np.zeros((len(idxs_list),self.n_coeffs))
            for i, idx in enumerate(idxs_list):# other_idxs:
                xjsc = prec_intsq_xjsc_list[idx]
                wjsc = prec_intsq_wjsc_list[idx]
                precomp_sq = prec_intsq_prec_list[idx]
                h_eval = self.h.evaluate(xjsc, precomp_sq)[:,0]
                integrand = 2. * self.h.grad_a(xjsc, precomp_sq)[:,0,:] * h_eval[:,nax]
                out[i,:] = np.dot( wjsc, integrand )
        else:
            try:
                precomp['IntSqVmd']
            except (TypeError, KeyError) as e:
                try:
                    precomp['V_list']
                    precomp['IntSqV1d']
                    self.precomp_evaluate(x, precomp, precomp_type='multi')
                except (TypeError, KeyError) as e:
                    precomp = self.precomp_evaluate(x, precomp, precomp_type='multi')
                    idxs_slice = slice(None)
            V = precomp['IntSqVmd']
            out = 2. * np.tensordot(V[idxs_slice,:,:], self.h.coeffs, axes=(2,0))
        return out[:,nax,:]

    @counted
    def hess_a(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Evaluate :math:`\nabla^2_{\bf a} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,N`]) --
            :math:`\nabla^2_{\bf a} f_{\bf a}({\bf x})`
        """
        if self.sq_basis is None:
            try:
                prec_intsq_xjsc_list = precomp['xjsc_list']
                prec_intsq_wjsc_list = precomp['wjsc_list']
                prec_intsq_prec_list = precomp['prec_list']
                for p in prec_intsq_prec_list:
                    if 'V_list' not in p: raise KeyError()
            except (TypeError, KeyError) as e:
                idxs_slice = slice(None)
                precomp = self.precomp_evaluate(x, precomp)
            prec_intsq_xjsc_list = precomp['xjsc_list']
            prec_intsq_wjsc_list = precomp['wjsc_list']
            prec_intsq_prec_list = precomp['prec_list']
            # Convert slice to range
            if idxs_slice.start is None: start = 0
            else: start = idxs_slice.start
            if idxs_slice.stop is None: stop = x.shape[0]
            else: stop = idxs_slice.stop
            idxs_list = range(start, stop)
            # Evaluate
            out = np.zeros((len(idxs_list),self.n_coeffs,self.n_coeffs))
            for i, idx in enumerate(idxs_list):
                xjsc = prec_intsq_xjsc_list[idx]
                wjsc = prec_intsq_wjsc_list[idx]
                precomp_sq = prec_intsq_prec_list[idx]
                if isinstance(self.h, LinearSpanTensorizedParametricFunctional):
                    grad_a_h_t = self.h.grad_a_t( xjsc, precomp_sq )[:,0,:]
                    sqrt_w_abs = np.sqrt(np.abs(wjsc))
                    w_sign = np.sign(wjsc)
                    grad_a_h_t_1 = grad_a_h_t * sqrt_w_abs[nax,:]
                    grad_a_h_t_2 = grad_a_h_t * (w_sign*sqrt_w_abs)[nax,:]
                    np.einsum('ik,jk->ij', grad_a_h_t_1, grad_a_h_t_2,
                              out=out[i,:,:], casting='unsafe')
                    out[i,:,:] *= 2.
                else:
                    ev = self.h.evaluate( xjsc, precomp_sq )[:,0,:]
                    hess_a = self.h.hess_a( xjsc, precomp_sq )[:,0,:,:] # zero if h LinSpanApprox
                    grad_a = self.h.grad_a( xjsc, precomp_sq )[:,0,:]
                    integrand = 2. * (hess_a * ev[:,nax,nax] + grad_a[:,:,nax] * grad_a[:,nax,:])
                    np.einsum('i...,i', integrand, wjsc, out=out[i,:,:])
        else:
            try:
                precomp['IntSqVmd']
            except (TypeError, KeyError) as e:
                try:
                    precomp['V_list']
                    precomp['IntSqV1d']
                    self.precomp_evaluate(x, precomp, precomp_type='multi')
                except (TypeError, KeyError) as e:
                    precomp = self.precomp_evaluate(x, precomp, precomp_type='multi')
                    idxs_slice = slice(None)
            V = precomp['IntSqVmd']
            out = 2. * V[idxs_slice,:,:]
        return out[:,nax,:,:]

    def precomp_partial_xd(self, x, precomp=None, precomp_type='uni'):
        if precomp is None: precomp = {}
        try:
            V_list = precomp['V_list']
        except KeyError as e:
            V_list = [ b.GradVandermonde(x[:,i], o)
                       for i,(b,o) in
                       enumerate(zip(self.h.basis_list[:-1],
                                     self.h.directional_orders[:-1])) ]
            precomp['V_list'] = V_list
        if len(V_list) < self.dim_in:
            # Append Vandermonde in last direction
            V_list.append( self.h.basis_list[-1].GradVandermonde(
                x[:,-1], self.h.directional_orders[-1] ) )
        if precomp_type == 'multi':
            self.h.precomp_Vandermonde_evaluate(x, precomp)
        return precomp

    @cached([('h',None)])
    @counted
    def partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict<dict>`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1`]) --
            :math:`\partial_{x_d} f_{\bf a}({\bf x})`
        """
        # Retreive h cache
        h_cache = get_sub_cache(cache, ('h',None))
        # Evaluate
        ev = self.h.evaluate(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        # Evaluate the square and return
        out = ev**2.
        return out

    def precomp_grad_x_partial_xd(self, x, precomp=None, precomp_type='uni'):
        if precomp is None: precomp = {}
        try:
            precomp['V_list'][self.dim_in-1]
        except (KeyError, IndexError) as e:
            self.precomp_partial_xd(x, precomp, precomp_type)
        try:
            partial_x_V_list = precomp['partial_x_V_list']
        except KeyError as e:
            partial_x_V_list = [ b.GradVandermonde(x[:,i], o, k=1)
                                 for i,(b,o) in enumerate(zip(
                                         self.h.basis_list[:-1],
                                         self.h.directional_orders[:-1])) ]
            precomp['partial_x_V_list'] = partial_x_V_list
        if len(partial_x_V_list) < self.dim_in:
            partial_x_V_list.append( self.h.basis_list[-1].GradVandermonde(
                x[:,-1], self.h.directional_orders[-1], k=1) )
        if precomp_type == 'multi':
            self.h.precomp_Vandermonde_grad_x(x, precomp)
        return precomp

    @cached([('h',None)])
    @counted
    def grad_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,d`]) --
            :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        # Retreive h cache
        try:
            h_cache = cache['h_cache']
        except TypeError:
            h_cache = None
        # Evaluate using super methods
        ev = self.h.evaluate(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        gx = self.h.grad_x(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        # Evaluate output
        out = 2. * ev[:,:,nax] * gx
        return out

    @cached([('h',None)])
    @counted
    def grad_a_grad_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None),
                                 cache=None):
        r""" Evaluate :math:`\nabla_{\bf a}\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,d`]) --
            :math:`\nabla_{\bf a}\nabla_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        # Retreive h cache
        try:
            h_cache = cache['h_cache']
        except TypeError:
            h_cache = None
        # Evaluate using super methods
        ev = self.h.evaluate(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        gx = self.h.grad_x(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        ga = self.h.grad_a(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        gagx = self.h.grad_a_grad_x(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        # Evaluate output
        out = 2. * gagx * ev[:,:,nax,nax] + 2.* ga[:,:,:,nax] * gx[:,:,nax,:]
        return out

    def precomp_hess_x_partial_xd(self, x, precomp=None, precomp_type='uni'):
        if precomp is None: precomp = {}
        try:
            precomp['V_list'][self.dim_in-1]
        except (KeyError, IndexError) as e:
            self.precomp_partial_xd(x, precomp, precomp_type)
        try:
            precomp['partial_x_V_list'][self.dim_in-1]
        except (KeyError, IndexError) as e:
            self.precomp_grad_x_partial_xd(x, precomp, precomp_type)
        try:
            partial2_x_V_list = precomp['partial2_x_V_list']
        except KeyError as e:
            partial2_x_V_list = [ b.GradVandermonde(x[:,i], o, k=2)
                                  for i,(b,o) in enumerate(zip(
                                          self.h.basis_list[:-1],
                                          self.h.directional_orders[:-1])) ]
            precomp['partial2_x_V_list'] = partial2_x_V_list
        if len(partial2_x_V_list) < self.dim_in:
            partial2_x_V_list.append( self.h.basis_list[-1].GradVandermonde(
                x[:,-1], self.h.directional_orders[-1], k=2) )
        if precomp_type == 'multi':
            self.h.precomp_Vandermonde_hess_x(x, precomp)
        return precomp

    @cached([('h',None)])
    @counted
    def hess_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,d,d`]) --
            :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        # Retreive h cache
        try:
            h_cache = cache['h_cache']
        except TypeError:
            h_cache = None
        # Evaluate using super methods
        ev = self.h.evaluate(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        gx = self.h.grad_x(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        hx = self.h.hess_x(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        # Evaluate output
        out = 2. * (hx * ev[:,:,nax,nax] + gx[:,:,:,nax] * gx[:,:,nax,:])
        return out

    @cached([('h',None)])
    @counted
    def grad_a_hess_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None),
                                 cache=None):
        r""" Evaluate :math:`\nabla_{\bf a}\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,d,d`]) --
            :math:`\nabla_{\bf a}\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        # Retreive h cache
        try:
            h_cache = cache['h_cache']
        except TypeError:
            h_cache = None
        # Evaluate using super methods
        ev = self.h.evaluate(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        gx = self.h.grad_x(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        hx = self.h.hess_x(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        ga = self.h.grad_a(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        gagx = self.h.grad_a_grad_x(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        gahx = self.h.grad_a_hess_x(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        # Evaluate output
        out = 2. * (
            gahx * ev[:,:,nax,nax,nax] + \
            hx[:,:,nax,:,:] * ga[:,:,:,nax,nax] + \
            gagx[:,:,:,nax,:]*gx[:,:,nax,:,nax] + \
            gx[:,:,nax,nax,:]*gagx[:,:,:,:,nax])
        return out

    def precomp_partial2_xd(self, x, precomp=None, precomp_type='uni'):
        if precomp is None: precomp = {}
        try:
            precomp['V_list'][self.dim_in-1]
        except (KeyError, IndexError) as e:
            self.precomp_partial_xd(x, precomp, precomp_type)
        try:
            precomp['partial_xd_V_last']
        except KeyError as e:
            if precomp_type == 'uni':
                self.h.precomp_partial_xd(x, precomp)
            elif precomp_type == 'multi':
                self.h.precomp_Vandermonde_partial_xd(x, precomp)
        return precomp

    @cached([('h',None)])
    @counted
    def partial2_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\partial^2_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1`]) --
            :math:`\partial^2_{x_d} f_{\bf a}({\bf x})`
        """
        # Retreive h cache
        try:
            h_cache = cache['h_cache']
        except TypeError:
            h_cache = None
        # Evaluate using super
        ev = self.h.evaluate(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        pxd = self.h.partial_xd(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        # Evaluate output
        out = 2. * ev * pxd
        return out[:,1]

    @cached([('h',None)])
    @counted
    def grad_a_partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla_{\bf a}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N`]) --
            :math:`\nabla_{\bf a}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        # Retreive h cache
        h_cache = get_sub_cache(cache, ('h',None))
        # Evaluate using super
        ev = self.h.evaluate(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        ga = self.h.grad_a(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        # Evaluate output
        out = 2. * ev[:,:,nax] * ga
        return out

    @cached([('h',None)],False)
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
        # Retreive h cache
        h_cache = get_sub_cache(cache, ('h',None))
        # Evaluate using super
        ga = self.h.grad_a(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
        out = 2. * ga[:,:,:,nax] * ga[:,:,nax,:]
        if not isinstance(self.h, LinearSpanTensorizedParametricFunctional):
            ev = self.h.evaluate(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
            ha = self.h.hess_a(x, precomp, idxs_slice=idxs_slice, cache=h_cache)
            out += 2. * ev[:,:,nax,nax] * ha
        return out


##############
# DEPRECATED #
##############

class IntegratedSquaredParametricFunctionApproximation(AnchoredIntegratedSquaredParametricFunctional):
    @deprecate(
        'IntegratedSquaredParametricFunctionApproximation',
        '3.0',
        'Use Functionals.AnchoredIntegratedSquaredParametricFunctional instead'
    )
    def __init__(self, *args, **kwargs):
        super(IntegratedSquaredParametricFunctionApproximation, self).__init__(*args, **kwargs)
