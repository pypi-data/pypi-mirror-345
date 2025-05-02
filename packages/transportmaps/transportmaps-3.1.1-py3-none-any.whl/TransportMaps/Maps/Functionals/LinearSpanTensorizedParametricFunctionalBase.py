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

import sys
import logging
import numpy as np
import scipy.optimize as sciopt
import itertools

from sortedcontainers import SortedSet

import semilattices as SL

from ...Misc import generate_total_order_midxs, \
    cached, counted, deprecate
from ...MPI import mpi_map, mpi_alloc_dmem
from .TensorizedParametricFunctionalBase import TensorizedParametricFunctional

__all__ = [
    'LinearSpanSemilattice',
    'LinearSpanVertex',
    'LinearSpanTensorizedParametricFunctional',
    # Deprecated
    'LinearSpanApproximation'
]

nax = np.newaxis


class LinearSpanSemilattice(SL.DecreasingCoordinateSemilattice):
    def __init__(self, *args, **kwargs):
        kwargs['VertexConstructor'] = kwargs.get('VertexConstructor', LinearSpanVertex)
        if not issubclass(kwargs['VertexConstructor'], LinearSpanVertex):
            raise AttributeError(
                "The vertex constructor must be a subclass of LinearSpanVertex")
        super(LinearSpanSemilattice, self).__init__(
            *args,
            **kwargs
        )
        self._active_set = SortedSet()

    def _new_vertex_sans_check(self, **kwargs):
        v = super()._new_vertex_sans_check(**kwargs)
        self.set_active( v )
        return v

    def _getstate_inner(self, dd):
        super()._getstate_inner(dd)
        dd['active_set'] = [ v.position for v in self._active_set ]
        return dd

    def _setstate_inner(self, dd, tmp_vertices):
        super()._setstate_inner(dd, tmp_vertices)
        self._active_set = SortedSet(
            [ tmp_vertices[idx] for idx in dd['active_set'] ]
        )
                
    @property
    def dof(self):
        return self._active_set

    @property
    def coeffs(self):
        coeffs = np.empty( self.n_coeffs )
        for i, v in enumerate(self.dof):
            coeffs[i] = v.coeff 
        return coeffs 

    @coeffs.setter
    def coeffs(self, coeffs):
        i = 0
        for v in self.dof:
            v.coeff = coeffs[i]
            i += 1

    @property
    def n_coeffs(self):
        return len(self.dof)

    @property
    def multi_idxs(self):
        midxs = []
        for v in self.dof:
            midxs.append( tuple( v.coordinates[i] for i in range(self.dims) ) )
        return midxs

    def set_active(self, v):
        self._active_set.add( v )

    def set_inactive(self, v):
        self._active_set.discard( v )

    def is_active(self, v):
        return v in self._active_set

class LinearSpanVertex(SL.SparseCoordinateVertex):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._coeff  = 0.
        self._data   = {}

    def __getstate__(self):
        dd = super().__getstate__()
        dd['coeff'] = self._coeff
        dd['data'] = self._data
        return dd

    def __setstate__(self, dd):
        super().__setstate__(dd)
        self._coeff = dd['coeff']
        self._data = dd['data']

    @property
    def data(self):
        return self._data
    
    @property
    def coeff(self):
        return self._coeff

    @coeff.setter
    def coeff(self, c):
        self._coeff = c
        
class LinearSpanTensorizedParametricFunctional(TensorizedParametricFunctional):
    r""" Parametric function :math:`f_{\bf a} = \sum_{{\bf i} \in \mathcal{I}} {\bf a}_{\bf i} \Phi_{\bf i}`

    The set of multi-indices :math:`\mathcal{I}` is generated using the 
    module :mod:`semilattices`. Given a dimension :math:`d`, 
    a ``norm`` :math:`q`, an order :math:`p\geq 0` and 
    weights :math:`\{w_i \geq 1\}_{i=1}^d`, 

    .. math::
       
       \mathcal{I} := \left\{ {\bf i} \middle\vert 
         \left\Vert{\bf i}\right\Vert_{\ell^p_W} =
         \left( 
           \sum_{j=1}^d w_j \left\vert {\bf i}_j \right\vert^p 
         \right)^{1/p} <= q
       \right\}

    For example, :math:`p=1` and :math:`w_i=1` for all :math:`i` results
    in isotropic total order sets (``spantype==total`` in version ``<3.0``).
    For :math:`p=\inf` and :math:`w_i=1` for all :math:`i` one gets 
    isotropic full order sets (``spantype==full`` in version ``<3.0``).

    Args:
      basis_list (list): list of :math:`d`
        :class:`OrthogonalBasis<SpectralToolbox.OrthogonalBasis>`
      q (float): norm of the :math:`\ell^p` spherical sector enclosing 
        all multi-indices.
      p (float): the order :math:`p` of the :math:`\ell^p` norm.
      w (:class:`semilattices.SpaceWeightDict`): Weightings for the 
        :math:`\ell^p` norm. Each dictionary key corresponds to a dimension
        :math:`i` and each corresponding value is the weight :math:`w_i`.
        Weights must be ``>1``. Missing values are considered ``1``.
      SemilatticeConstructor (:class:`class`): constructor for the semilattice.
        It must be a sub-class of :class:`LinearSpanSemilattice`.
      extra_label_keys (iterable of strings): extra labels to be used to 
        sort vertices in the semilattice.
      extra_data_keys (iterable of strings): extra keys referring to 
        data contained in each vertex of the semilattice
      semilattice (:class:`semilattice<semilattices.semilattice>`):
        user provided semilattice to be used for handling of the degrees
        of freedom.
      spantype (str): Span type. 'total' total order, 'full' full order,
        'midx' multi-indeces specified. Deprecated since version ``3.0``.
      order_list (:class:`list<list>` of :class:`int<int>`): list of 
        orders :math:`\{N_i\}_{i=0}^d`. Deprecated since version ``3.0``.
      multi_idxs (list): list of tuples containing the active multi-indices
      full_basis_list (list): full list of :class:`Basis<SpectralToolbox.Basis>`.
        ``basis_list`` is a subset of ``full_basis_list``. This may be used to
        automatically increase the input dimension of the approximation.
    """

    def __init__(self,
                 basis_list,
                 # Parameters for the creation of the decreasing semilattice
                 q=None,
                 p=1.,    # Norm power (total order)
                 w=None,  # weights (isotropic)
                 SemilatticeConstructor=LinearSpanSemilattice,
                 # Parameter for user provided semilattice (should match len(basis_list))
                 semilattice=None,
                 # Deprecated arguments since v3.0
                 spantype=None,
                 order_list=None,
                 multi_idxs=None,
                 # Optional argument
                 full_basis_list=None):
        if spantype == 'midx' and multi_idxs is not None:
            self.logger.warning(
                "Initialization using parameter spantype==midx is deprecated since v3.0." + \
                "Use parameters q, p and w relating to the semilattices module instead."
            )
            self.multi_idxs = multi_idxs
            self.max_order_list = list( np.max(np.asarray(self.multi_idxs), axis=0) )
        else: # Initialize using semilattices
            if sum( p is not None for p in [q, semilattice, spantype] ) != 1:
                raise AttributeError(
                    "semilattice, spantype and q are mutually exclusive."
                )
            if semilattice is not None:
                if not issubclass(type(semilattice), LinearSpanSemilattice):
                    raise TypeError(
                        "The provided semilattice must be an instance of a " + \
                        "sub-class of LinearSpanSemilattice."
                    )
                if semilattice.dims != len(basis_list):
                    raise AttributeError(
                        "The provided semilattice has a dimension that is " + \
                        "inconsistent with the number of basis provided: " + \
                        "semilattice.dims=%d, " % semilattice.dims + \
                        "len(basis_list)=%d" % len(basis_list)
                    )
                self._semilattice = semilattice
            else:
                if spantype in ['total','full'] and order_list is not None:
                    q = max(order_list)
                    p = 1. if spantype == 'total' else float('inf')
                    w = SL.SpaceWeightDict()
                    if q > 0:
                        for d, o in enumerate(order_list):
                            if o != q:
                                w[d] = q / o if o > 0 else sys.float_info.max
                self._semilattice = SL.create_lp_semilattice(
                    dims=len(basis_list),
                    norm=q,
                    p=p,
                    weights=w,
                    SemilatticeConstructor=SemilatticeConstructor,
                )
        super(LinearSpanTensorizedParametricFunctional,self).__init__(basis_list, full_basis_list)

    @deprecate("LinearSpanApproximation.generate_multi_idxs()",
               "3.0",
               "Multi indices are managed through the semilattice.")
    def generate_multi_idxs(self, spantype):
        r""" Generate the list of multi-indices
        """
        if spantype == 'full':
            return list(itertools.product(*[range(o+1) for o in self.max_order_list]))
        elif spantype == 'total':
            midxs = generate_total_order_midxs(self.max_order_list)
            return midxs
        raise NotImplementedError("Not implemented for the selected spantype (%s)" % spantype)

    def init_coeffs(self):
        r""" Initialize the coefficients :math:`{\bf a}`
        """
        if hasattr(self, '_semilattice'):
            self.coeffs = np.zeros(self.n_coeffs)
        else: # version <3.0
            self._coeffs = np.zeros(self.n_coeffs)

    def get_default_init_values_regression(self):
        return np.zeros(self.n_coeffs)

    @property
    def semilattice(self):
        r""" The semilattice representing the degrees of freedom of the parametrization.
        """
        return self._semilattice

    @semilattice.setter
    def semilattice(self, semilattice):
        r""" Sets the semilattice representing the degrees of freedom of the parametrization
        """
        if not issubclass(type(semilattice), LinearSpanSemilattice):
            raise TypeError(
                "The provided semilattice must be an instance of a " + \
                "sub-class of LinearSpanSemilattice."
            )
        if semilattice.dims != self.dim_in:
            raise AttributeError(
                "The provided semilattice has a dimension that is " + \
                "inconsistent with the dimension of the parametrization: " + \
                "semilattice.dims=%d, " % semilattice.dims + \
                "self.dim=%d" % self.dim_in
            )
        self._semilattice = semilattice

    @property
    def n_coeffs(self):
        r""" Get the number :math:`N` of coefficients :math:`{\bf a}`

        Returns:
          (:class:`int<int>`) -- number of coefficients
        """
        if hasattr(self, '_semilattice'):
            return self.semilattice.n_coeffs
        else: # version <3.0
            return len(self.multi_idxs)
        
    @property
    def coeffs(self):
        r""" Get the coefficients :math:`{\bf a}`

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients
        """
        if hasattr(self, '_semilattice'):
            return self.semilattice.coeffs
        else:
            return self._coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients :math:`{\bf a}`.

        Args:
          coeffs (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
        """
        if len(coeffs) != self.n_coeffs:
            raise ValueError("The number of input coefficients does not agree " +
                             "with the number of expected coefficients.")
        if hasattr(self, '_semilattice'):
            self.semilattice.coeffs = coeffs
        else: # version <3.0
            self._coeffs = coeffs

    @deprecate("LinearSpanApproximation.get_multi_idxs()",
               "2.0",
               "Use property LinearSpanApproximation.multi_idxs")
    def get_multi_idxs(self):
        r""" Get the list of multi indices

        Return:
          (:class:`list` of :class:`tuple`) -- multi indices
        """
        return self.multi_idxs

    @deprecate("LinearSpanApproximation.set_multi_idxs()",
               "2.0",
               "Use property LinearSpanApproximation.multi_idxs")
    def set_multi_idxs(self, multi_idxs):
        r""" Set the list of multi indices

        Args:
          multi_idxs (:class:`list` of :class:`tuple`): multi indices
        """
        if hasattr(self, '_semilattice'):
            raise Exception(
                "Multi indices cannot be set using this method since v3.0." + \
                "Modify the underlying semilattice instead."
            )
        self.multi_idxs = multi_idxs

    @property
    def multi_idxs(self):
        if hasattr(self, '_semilattice'):
            return self.semilattice.multi_idxs
        else: # version <3.0
            return self._multi_idxs[:]

    @multi_idxs.setter
    def multi_idxs(self, midxs):
        if hasattr(self, '_semilattice'):
            raise Exception(
                "Multi indices cannot be set using this method since v3.0." + \
                "Modify the underlying semilattice instead."
            )
        self._multi_idxs = midxs
        self.max_order_list = list( np.max(np.asarray(midxs), axis=0) )

    @deprecate("LinearSpanApproximation.get_directional_orders()",
               "2.0",
               "Use property LinearSpanApproximation.directional_orders")
    def get_directional_orders(self):
        r""" Get the maximum orders of the univariate part of the representation.

        Returns:
          (:class:`list<list>` [d] :class:`int<int>`) -- orders

        .. deprecated:: use property :func:`directional_orders`
        """
        return self.directional_orders

    @property
    def directional_orders(self):
        r""" Get the maximum orders of the univariate part of the representation.

        Returns:
          (:class:`list<list>` [d] :class:`int<int>`) -- orders
        """
        if hasattr(self, '_semilattice'):
            return self._semilattice.max_coordinates
        else: # version <3.0
            if not hasattr(self, "max_order_list"): # Backcompatibility
                self.max_order_list = list( np.max(np.asarray(self.multi_idxs), axis=0) )
            return self.max_order_list[:]

    def __setstate__(self, state):
        r"""
        Defined to preserve compatibility with stored files where multi_idx is
        an attribute and not a property.
        """
        if not hasattr(self, '_semilattice'): # version <3.0
            try:
                self.multi_idxs = state.pop('multi_idxs')
            except KeyError:
                pass
        super(LinearSpanTensorizedParametricFunctional, self).__setstate__(state)
        
    def precomp_Vandermonde_evaluate(self, x, precomp=None):
        r""" Precompute the multi-variate Vandermonde matrices for the evaluation of :math:`f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary containing the Vandermonde matrix
        """
        if precomp is None: precomp = {}
        try: V = precomp['V']
        except KeyError as e:
            try:
                V_list = precomp['V_list']
            except (TypeError, KeyError) as e:
                self.precomp_evaluate(x, precomp)
                V_list = precomp['V_list']
            precomp['V'] = np.ones((V_list[0].shape[0], self.n_coeffs))
            for i,midx in enumerate(self.multi_idxs):
                for idx, V1d in zip(midx, V_list):
                    precomp['V'][:,i] *= V1d[:,idx]
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
          cache (:class:`dict`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1`]) -- function evaluations
        """
        try:
            V = precomp['V']
        except (TypeError, KeyError) as e:
            try:
                V_list = precomp['V_list']
            except (TypeError, KeyError) as e:
                precomp = self.precomp_evaluate(x, precomp)
                idxs_slice = slice(None)
                V_list = precomp['V_list']
            tot_size = V_list[0].shape[0]
            out = np.zeros((x.shape[0],1))
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate this loop?
            for c, midx in zip(self.coeffs, self.multi_idxs):
                tmp[:] = 1.
                for idx,V in zip(midx,V_list):
                    tmp *= V[idxs_slice,idx]
                out[:,0] += c * tmp
        else:
            tot_size = V.shape[0]
            out = np.dot(V[idxs_slice,:], self.coeffs)
            out = out.reshape((out.shape[0],1))
        return out

    def precomp_Vandermonde_grad_x(self, x, precomp=None):
        r""" Precompute the multi-variate Vandermonde matrices for the evaluation of :math:`\nabla_{\bf x} f_{\bf a}` at ``x``

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Return:
          (:class:`dict<dict>` with :class:`list<list>`
            [:math:`d`] of :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary containing the list of multi-variate Vandermonde matrices.
        """
        if precomp is None: precomp = {}
        try: grad_x_V_list = precomp['grad_x_V_list']
        except KeyError as e:
            try: V_list = precomp['V_list']
            except KeyError as e:
                self.precomp_evaluate(x, precomp)
                V_list = precomp['V_list']
            try: partial_x_V_list = precomp['partial_x_V_list']
            except KeyError as e:
                self.precomp_grad_x(x, precomp)
                partial_x_V_list = precomp['partial_x_V_list']
            grad_x_V_list = []
            # TODO: Accelerate this loops?
            for d in range(self.dim_in):
                grad_x_V = np.ones((x.shape[0], self.n_coeffs))
                for i,midx in enumerate(self.multi_idxs):
                    for j, (idx, V1d, pxV1d) in enumerate(zip(midx, V_list, partial_x_V_list)):
                        if j != d:
                            grad_x_V[:,i] *= V1d[:,idx]
                        else:
                            grad_x_V[:,i] *= pxV1d[:,idx]
                grad_x_V_list.append( grad_x_V )
            precomp['grad_x_V_list'] = grad_x_V_list
        return precomp

    @cached()
    @counted
    def grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
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
        try:
            grad_x_V_list = precomp['grad_x_V_list']
        except (TypeError, KeyError) as e:
            try:
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
            except (TypeError,KeyError) as e:
                # Clean pre-existing
                precomp.pop('V_list', None)
                precomp.pop('partial_x_V_list', None)
                # Ignoring slice
                idxs_slice = slice(None)
                # Compute
                precomp = self.precomp_evaluate(x, precomp)
                precomp = self.precomp_grad_x(x, precomp)
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
            out = np.zeros((x.shape[0],1,x.shape[1]))
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate this loops?
            for d in range(self.dim_in):
                for c, midx in zip(self.coeffs, self.multi_idxs):
                    tmp[:] = 1.
                    for j, (idx, V1d, pxV1d) in enumerate(zip(midx, V_list,
                                                              partial_x_V_list)):
                        if j != d:
                            tmp *= V1d[idxs_slice,idx]
                        else:
                            tmp *= pxV1d[idxs_slice,idx]
                    out[:,0,d] += c * tmp
        else:
            out = np.zeros( x.shape )
            for i, grad_x_V in enumerate(grad_x_V_list):
                out[idxs_slice,i] = np.dot( grad_x_V[idxs_slice,:], self.coeffs )
            out = np.reshape(out, (out.shape[0],1,out.shape[1]))
        return out

    @cached()
    @counted
    def grad_a_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla_{\bf a} \nabla_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,d`]) --
            :math:`\nabla_{\bf a} \nabla_{\bf x} f_{\bf a}({\bf x})`
        """
        try:
            grad_x_V_list = precomp['grad_x_V_list']
        except (TypeError, KeyError) as e:
            try: V_list = precomp['V_list']
            except KeyError as e:
                precomp = self.precomp_evaluate(x)
            except TypeError as e:
                x = x[idxs_slice,:]
                precomp = self.precomp_evaluate(x)
                idxs_slice = slice(None)
            finally:
                V_list = precomp['V_list']
            try: partial_x_V_list = precomp['partial_x_V_list']
            except KeyError as e:
                self.precomp_grad_x(x, precomp)
                partial_x_V_list = precomp['partial_x_V_list']
            out = np.zeros( (x.shape[0], 1, self.n_coeffs, x.shape[1]) )
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate this loops?
            for d in range(self.dim_in):
                cidx = 0
                for c, midx in zip(self.coeffs, self.multi_idxs):
                    tmp[:] = 1.
                    for j, (idx, V1d, pxV1d) in enumerate(zip(midx, V_list,
                                                              partial_x_V_list)):
                        if j != d:
                            tmp *= V1d[idxs_slice,idx]
                        else:
                            tmp *= pxV1d[idxs_slice,idx]
                    out[:,0,cidx,d] += tmp#*(c != 0)
                    cidx = cidx + 1
        else:
            out = np.zeros( (x.shape[0], self.n_coeffs, x.shape[1]) )
            # coeff_ind = indicator function applied to coefficients in map component
            #coeff_ind = [int(x != 0) for x in self.coeffs]
            for i, grad_x_V in enumerate(grad_x_V_list):
                out[idxs_slice,:,i] = grad_x_V[idxs_slice,:]#np.dot(grad_x_V[idxs_slice,:], coeff_ind)
            out = out[:,nax,:,:]
        return out

    def precomp_Vandermonde_hess_x(self, x, precomp=None):
        r""" Precompute the multi-variate Vandermonde matrices for the evaluation of :math:`\nabla^2_{\bf x} f_{\bf a}` at ``x``

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Return:
          (:class:`dict<dict>` with :class:`ndarray<numpy.ndarray>`
            [:math:`d,d`] of :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary containing the matrix of multi-variate Vandermonde matrices
        """
        if precomp is None: precomp = {}
        try: hess_x_V_mat = precomp['hess_x_V_mat']
        except KeyError as e:
            try: V_list = precomp['V_list']
            except KeyError as e:
                self.precomp_evaluate(x, precomp)
                V_list = precomp['V_list']
            try: partial_x_V_list = precomp['partial_x_V_list']
            except KeyError as e:
                self.precomp_grad_x(x, precomp)
                partial_x_V_list = precomp['partial_x_V_list']
            try: partial2_x_V_list = precomp['partial2_x_V_list']
            except KeyError as e:
                self.precomp_hess_x(x, precomp)
                partial2_x_V_list = precomp['partial2_x_V_list']
            hess_x_V_mat = np.empty((self.dim_in,self.dim_in), dtype=object)
            # TODO: Accelerate these loops?
            for d1 in range(self.dim_in):
                for d2 in range(self.dim_in):
                    hess_x_V = np.ones((x.shape[0],self.n_coeffs))
                    for i, midx in enumerate(self.multi_idxs):
                        for j, (idx, V1d, pxV1d, p2xV1d) in enumerate(zip(
                                midx, V_list, partial_x_V_list, partial2_x_V_list)):
                            if d1 == d2 and j == d1:
                                hess_x_V[:,i] *= p2xV1d[:,idx]
                            elif j == d1 or j == d2:
                                hess_x_V[:,i] *= pxV1d[:,idx]
                            else:
                                hess_x_V[:,i] *= V1d[:,idx]
                    hess_x_V_mat[d1,d2] = hess_x_V
            precomp['hess_x_V_mat'] = hess_x_V_mat
        return precomp

    @cached()
    @counted
    def hess_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla^2_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,d,d`]) --
            :math:`\nabla^2_{\bf x} f_{\bf a}({\bf x})`
        """
        try:
            hess_x_V_mat = precomp['hess_x_V_mat']
        except (TypeError, KeyError) as e:
            try:
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
                partial2_x_V_list = precomp['partial2_x_V_list']
            except (TypeError,KeyError) as e:
                # Clean pre-existing
                precomp.pop('V_list', None)
                precomp.pop('partial_x_V_list', None)
                precomp.pop('partial2_x_V_list', None)
                # Ignoring slice
                idxs_slice = slice(None)
                # Compute
                precomp = self.precomp_evaluate(x, precomp)
                precomp = self.precomp_grad_x(x, precomp)
                precomp = self.precomp_hess_x(x, precomp)
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
                partial2_x_V_list = precomp['partial2_x_V_list']
            out = np.zeros((x.shape[0],1,self.dim_in,self.dim_in))
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate these loops?
            for d1 in range(self.dim_in):
                for d2 in range(self.dim_in):
                    for i, (c, midx) in enumerate(zip(self.coeffs,self.multi_idxs)):
                        tmp[:] = 1.
                        for j, (idx, V1d,
                                pxV1d, p2xV1d) in enumerate(zip(midx, V_list,
                                                                partial_x_V_list,
                                                                partial2_x_V_list)):
                            if d1 == d2 and j == d1:
                                tmp *= p2xV1d[idxs_slice,idx]
                            elif j == d1 or j == d2:
                                tmp *= pxV1d[idxs_slice,idx]
                            else:
                                tmp *= V1d[idxs_slice,idx]
                        out[:,0,d1,d2] += c * tmp
        else:
            out = np.zeros((x.shape[0],self.dim_in,self.dim_in))
            for i in range(self.dim_in):
                for j in range(self.dim_in):
                    out[idxs_slice,i,j] = np.dot( hess_x_V_mat[i,j][idxs_slice,:],
                                                  self.coeffs )
            out = np.reshape(out, (out.shape[0],1,self.dim_in,self.dim_in))
        return out

    @cached()
    @counted
    def grad_a_hess_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla_{\bf a} \nabla^2_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,d,d`]) --
            :math:`\nabla_{\bf a} \nabla^2_{\bf x} f_{\bf a}({\bf x})`
        """
        try:
            hess_x_V_mat = precomp['hess_x_V_mat']
        except (TypeError, KeyError) as e:
            try: V_list = precomp['V_list']
            except KeyError as e:
                precomp = self.precomp_evaluate(x)
            except TypeError as e:
                x = x[idxs_slice,:]
                precomp = self.precomp_evaluate(x)
                idxs_slice = slice(None)
            finally:
                V_list = precomp['V_list']
            try: partial_x_V_list = precomp['partial_x_V_list']
            except KeyError as e:
                self.precomp_grad_x(x, precomp)
                partial_x_V_list = precomp['partial_x_V_list']
            try: partial2_x_V_list = precomp['partial2_x_V_list']
            except KeyError as e:
                self.precomp_hess_x(x, precomp)
                partial2_x_V_list = precomp['partial2_x_V_list']
            out = np.zeros((x.shape[0], 1, self.n_coeffs, self.dim_in,self.dim_in))
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate these loops?
            for d1 in range(self.dim_in):
                for d2 in range(self.dim_in):
                    cidx = 0
                    for i, (c, midx) in enumerate(zip(self.coeffs,self.multi_idxs)):
                        tmp[:] = 1.
                        for j, (idx, V1d,
                                pxV1d, p2xV1d) in enumerate(zip(midx, V_list,
                                                                partial_x_V_list,
                                                                partial2_x_V_list)):
                            if d1 == d2 and j == d1:
                                tmp *= p2xV1d[idxs_slice,idx]
                            elif j == d1 or j == d2:
                                tmp *= pxV1d[idxs_slice,idx]
                            else:
                                tmp *= V1d[idxs_slice,idx]
                        out[:,0,cidx,d1,d2] += tmp#*(c != 0)
                        cidx = cidx + 1
        else:
            out = np.zeros((x.shape[0], self.n_coeffs, self.dim_in,self.dim_in))
            #coeff_ind = [int(x != 0) for x in self.coeffs]
            for i in range(self.dim_in):
                for j in range(self.dim_in):
                    out[idxs_slice,:,i,j] = hess_x_V_mat[i,j][idxs_slice,:]#np.dot(hess_x_V_mat[i,j][idxs_slice,:], coeff_ind)
            out = out[:,nax,:,:,:]
        return out

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
          cache (:class:`dict`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N`]) --
            :math:`\nabla_{\bf a} f_{\bf a}({\bf x})`
        """
        try:
            V = precomp['V']
        except KeyError as e:
            if 'V_list' not in precomp:
                idxs_slice = slice(None)
            precomp = self.precomp_Vandermonde_evaluate(x, precomp)
        except TypeError as e:
            idxs_slice = slice(None)
            precomp = self.precomp_Vandermonde_evaluate(x, precomp)
        finally:
            V = precomp['V']
        return V[idxs_slice,:][:,nax,:]

    @cached()
    @counted
    def grad_a_t(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\left(\nabla_{\bf a} f_{\bf a}\right)^T` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N`]) --
            :math:`\left(\nabla_{\bf a} f_{\bf a}({\bf x}\right)^T)`
        """
        try:
            VT = precomp['VT']
        except (TypeError, KeyError) as e:
            try:
                V = precomp['V']
            except KeyError:
                if 'V_list' not in precomp:
                    idxs_slice = slice(None)
                precomp = self.precomp_Vandermonde_evaluate(x, precomp)
            except TypeError:
                idxs_slice = slice(None)
                precomp = self.precomp_Vandermonde_evaluate(x, precomp)
            finally:
                V = precomp['V']
            VT = np.transpose(V).copy()
            precomp['VT'] = VT
        return VT[:,idxs_slice][:,nax,:]

    def precomp_VVT_evaluate(self, x, precomp=None):
        r""" Precompute the product :math:`VV^T` of the multi-variate Vandermonde matrices for the evaluation of :math:`f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary containing the desired product
        """
        try:
            V = precomp['V']
        except (TypeError, KeyError) as e:
            precomp = self.precomp_Vandermonde_evaluate(x, precomp)
            V = precomp['V']
        precomp['VVT'] = V[:,:,nax] * V[:,nax,:]
        return precomp

    @cached()
    @counted
    def grad_a_squared(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\left(\nabla_{\bf a} f_{\bf a}\right)\left(\nabla_{\bf a} f_{\bf a}\right)^T` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,N`]) --
            :math:`\left(\nabla_{\bf a} f_{\bf a}\right)\left(\nabla_{\bf a} f_{\bf a}\right)^T`
        """
        try:
            VVT = precomp['VVT']
        except KeyError:
            if 'V_list' not in precomp:
                idxs_slice = slice(None)
            precomp = self.precomp_VVT_evaluate(x, precomp)
        except TypeError:
            idxs_slice = slice(None)
            precomp = self.precomp_VVT_evaluate(x, precomp)
        finally:
            VVT = precomp['VVT']
        return VVT[idxs_slice,:,:][:,nax,:,:]

    @counted
    def hess_a(self, x, precomp=None, idxs_slice=slice(None), *arg, **kwargs):
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
        return np.zeros((1,1,self.n_coeffs,self.n_coeffs))

    def precomp_Vandermonde_partial_xd(self, x, precomp=None):
        r""" Precompute multi-variate Vandermonde matrix for the evaluation of :math:`\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary with Vandermonde matrix
        """
        if precomp is None: precomp = {}
        try: partial_xd_V = precomp['partial_xd_V']
        except KeyError as e:
            try: V_list = precomp['V_list']
            except KeyError as e:
                self.precomp_evaluate(x, precomp)
                V_list = precomp['V_list']
            try: partial_xd_V_last = precomp['partial_xd_V_last']
            except KeyError as e:
                self.precomp_partial_xd(x, precomp)
                partial_xd_V_last = precomp['partial_xd_V_last']
            partial_xd_V = np.ones((V_list[0].shape[0], self.n_coeffs))
            for i, midx in enumerate(self.multi_idxs):
                for idx, V1d in zip(midx[:-1], V_list[:-1]):
                    partial_xd_V[:,i] *= V1d[:,idx]
                partial_xd_V[:,i] *= partial_xd_V_last[:,midx[-1]]
            precomp['partial_xd_V'] = partial_xd_V
        return precomp

    @cached()
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
        try:
            partial_xd_V = precomp['partial_xd_V']
        except (TypeError, KeyError) as e:
            try:
                V_list = precomp['V_list']
                partial_xd_V_last = precomp['partial_xd_V_last']
            except (TypeError, KeyError) as e:
                # Clean pre-existing
                precomp.pop('V_list', None)
                precomp.pop('partial_x_V_last', None)
                # Ignoring slice
                idxs_slice = slice(None)
                # Compute
                precomp = self.precomp_evaluate(x, precomp)
                precomp = self.precomp_partial_xd(x, precomp)
                V_list = precomp['V_list']
                partial_xd_V_last = precomp['partial_xd_V_last']
            tot_size = V_list[0].shape[0]
            out = np.zeros((x.shape[0],1))
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate these loops?
            for i, (c, midx) in enumerate(zip(self.coeffs,self.multi_idxs)):
                tmp[:] = 1.
                for idx, V1d in zip(midx[:-1], V_list[:-1]):
                    tmp *= V1d[idxs_slice,idx]
                tmp *= partial_xd_V_last[idxs_slice,midx[-1]]
                out[:,0] += c * tmp
        else:
            tot_size = partial_xd_V.shape[0]
            out = np.dot(partial_xd_V[idxs_slice,:], self.coeffs)
            out = out[:,nax]
        return out
    
    def precomp_Vandermonde_grad_x_partial_xd(self, x, precomp=None):
        r""" Precompute multi-variate Vandermonde matrices for the evaluation of :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`list<list>` [d]
            :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary containing the list of multi-variate Vandermonde matrices.
        """
        if precomp is None: precomp = {}
        try: grad_x_partial_xd_V_list = precomp['grad_x_partial_xd_V_list']
        except KeyError as e:
            try: V_list = precomp['V_list']
            except KeyError as e:
                self.precomp_evaluate(x, precomp)
                V_list = precomp['V_list']
            try: partial_x_V_list = precomp['partial_x_V_list']
            except KeyError as e:
                self.precomp_grad_x(x, precomp)
                partial_x_V_list = precomp['partial_x_V_list']
            try: partial2_xd_V_last = precomp['partial2_xd_V_last']
            except KeyError as e:
                self.precomp_partial2_xd(x, precomp)
                partial2_xd_V_last = precomp['partial2_xd_V_last']
            grad_x_partial_xd_V_list = []
            # TODO: Accelerate these loops?
            for d in range(self.dim_in):
                grad_x_partial_xd_V = np.ones((x.shape[0], self.n_coeffs))
                for i, midx in enumerate(self.multi_idxs):
                    for j, (idx, V1d, pxV1d) in enumerate(zip(midx, V_list,
                                                              partial_x_V_list)):
                        if j == d and d == (self.dim_in-1):
                            grad_x_partial_xd_V[:,i] *= partial2_xd_V_last[:,idx]
                        elif j == d or j == (self.dim_in-1):
                            grad_x_partial_xd_V[:,i] *= pxV1d[:,idx]
                        else:
                            grad_x_partial_xd_V[:,i] *= V1d[:,idx]
                grad_x_partial_xd_V_list.append( grad_x_partial_xd_V )
            precomp['grad_x_partial_xd_V_list'] = grad_x_partial_xd_V_list
        return precomp

    @cached()
    @counted
    def grad_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,d`]) --
            :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try:
            grad_x_partial_xd_V_list = precomp['grad_x_partial_xd_V_list']
        except (TypeError, KeyError) as e:
            try:
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
                partial2_xd_V_last = precomp['partial2_xd_V_last']
            except (TypeError, KeyError) as e:
                # Clean pre-existing
                precomp.pop('V_list', None)
                precomp.pop('partial_x_V_list', None)
                precomp.pop('partial2_xd_V_last', None)
                # Ignoring slice
                idxs_slice = slice(None)
                # Compute
                precomp = self.precomp_evaluate(x, precomp)
                precomp = self.precomp_grad_x(x, precomp)
                precomp = self.precomp_partial2_xd(x, precomp)
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
                partial2_xd_V_last = precomp['partial2_xd_V_last']
            out = np.zeros((x.shape[0], 1, self.dim_in))
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate these loops?
            for d in range(self.dim_in):
                for i, (c, midx) in enumerate(zip(self.coeffs,self.multi_idxs)):
                    tmp[:] = 1.
                    for j, (idx, V1d, pxV1d) in enumerate(zip(midx, V_list,
                                                              partial_x_V_list)):
                        if j == d and d == (self.dim_in-1):
                            tmp *= partial2_xd_V_last[:,idx]
                        elif j == d or j == (self.dim_in-1):
                            tmp *= pxV1d[:,idx]
                        else:
                            tmp *= V1d[:,idx]
                    out[:,0,d] += c * tmp
        else:
            out = np.zeros( x.shape )
            for i in range( self.dim_in ):
                out[:,i] = np.dot(
                    grad_x_partial_xd_V_list[i][idxs_slice,:], self.coeffs )
            out = out[:,nax,:]
        return out

    @cached()
    @counted
    def grad_a_grad_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate :math:`\nabla_{\bf a}\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,d`]) --
            :math:`\nabla_{\bf a}\nabla_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try:
            grad_x_partial_xd_V_list = precomp['grad_x_partial_xd_V_list']
        except (TypeError, KeyError) as e:
            try: V_list = precomp['V_list']
            except (TypeError, KeyError) as e:
                precomp = self.precomp_evaluate(x, precomp)
                V_list = precomp['V_list']
            try: partial_x_V_list = precomp['partial_x_V_list']
            except (TypeError, KeyError) as e:
                precomp = self.precomp_grad_x(x, precomp)
                partial_x_V_list = precomp['partial_x_V_list']
            try: partial2_xd_V_last = precomp['partial2_xd_V_last']
            except (TypeError, KeyError) as e:
                precomp = self.precomp_partial2_xd(x, precomp)
                partial2_xd_V_last = precomp['partial2_xd_V_last']
            out = np.zeros((x.shape[0], 1, self.n_coeffs, self.dim_in))
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate these loops?
            for d in range(self.dim_in):
                cidx = 0
                for i, (c, midx) in enumerate(zip(self.coeffs,self.multi_idxs)):
                    tmp[:] = 1.
                    for j, (idx, V1d, pxV1d) in enumerate(zip(midx, V_list,
                                                              partial_x_V_list)):
                        if j == d and d == (self.dim_in-1):
                            tmp *= partial2_xd_V_last[:,idx]
                        elif j == d or j == (self.dim_in-1):
                            tmp *= pxV1d[:,idx]
                        else:
                            tmp *= V1d[:,idx]
                    out[:,0,cidx,d] += tmp#*(c != 0)
                    cidx = cidx + 1
        else:
            out = np.zeros((x.shape[0], 1, self.n_coeffs, self.dim_in))
            #coeff_ind = [int(x != 0) for x in self.coeffs]
            for i in range( self.dim_in ):
                out[:,0,:,i] = grad_x_partial_xd_V_list[i]#np.dot(grad_x_partial_xd_V_list[i], coeff_ind)
        return out

    def precomp_Vandermonde_hess_x_partial_xd(self, x, precomp=None):
        r""" Precompute Vandermonde matrices for the evaluation of :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`ndarray<ndarray>` [d,d]
            :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary with list of Vandermonde matrices for the computation
            of the gradient.
        """
        if precomp is None: precomp = {}
        try: hess_x_partial_xd_V_mat = precomp['hess_x_partial_xd_V_mat']
        except KeyError as e:
            try: V_list = precomp['V_list']
            except KeyError as e:
                self.precomp_evaluate(x, precomp)
                V_list = precomp['V_list']
            try: partial_x_V_list = precomp['partial_x_V_list']
            except KeyError as e:
                self.precomp_grad_x(x, precomp)
                partial_x_V_list = precomp['partial_x_V_list']
            try: partial2_x_V_list = precomp['partial2_x_V_list']
            except KeyError as e:
                self.precomp_hess_x(x, precomp)
                partial2_x_V_list = precomp['partial2_x_V_list']
            try: partial3_xd_V_last = precomp['partial3_xd_V_last']
            except KeyError as e:
                self.precomp_partial3_xd(x, precomp)
                partial3_xd_V_last = precomp['partial3_xd_V_last']
            hess_x_partial_xd_V_mat = np.empty((self.dim_in,self.dim_in),dtype=object)
            # TODO: Accelerate these loops?
            for d1 in range(self.dim_in):
                for d2 in range(self.dim_in):
                    hess_x_partial_xd_V = np.ones((x.shape[0], self.n_coeffs))
                    for i, midx in enumerate(self.multi_idxs):
                        for j, (idx, V1d,
                                pxV1d, p2xV1d) in enumerate(zip(midx, V_list,
                                                                partial_x_V_list,
                                                                partial2_x_V_list)):
                            if j == d1 == d2 == (self.dim_in-1):
                                hess_x_partial_xd_V[:,i] *= partial3_xd_V_last[:,idx]
                            elif j == d1 == d2 or j == d1 == (self.dim_in-1) \
                                 or j == d2 == (self.dim_in-1):
                                hess_x_partial_xd_V[:,i] *= p2xV1d[:,idx]
                            elif j == d1 or j == d2 or j == (self.dim_in-1):
                                hess_x_partial_xd_V[:,i] *= pxV1d[:,idx]
                            else:
                                hess_x_partial_xd_V[:,i] *= V1d[:,idx]
                    hess_x_partial_xd_V_mat[d1,d2] = hess_x_partial_xd_V
            precomp['hess_x_partial_xd_V_mat'] = hess_x_partial_xd_V_mat
        return precomp

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
        try:
            hess_x_partial_xd_V_mat = precomp['hess_x_partial_xd_V_mat']
        except (TypeError, KeyError) as e:
            try:
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
                partial2_x_V_list = precomp['partial2_x_V_list']
                partial3_xd_V_last = precomp['partial3_xd_V_last']
            except (TypeError, KeyError) as e:
                # Clean pre-existing
                precomp.pop('V_list', None)
                precomp.pop('partial_x_V_list', None)
                precomp.pop('partial2_x_V_list', None)
                precomp.pop('partial3_xd_V_last', None)
                # Ignoring slice
                idxs_slice = slice(None)
                # Compute
                precomp = self.precomp_evaluate(x, precomp)
                precomp = self.precomp_grad_x(x, precomp)
                precomp = self.precomp_hess_x(x, precomp)
                precomp = self.precomp_partial2_xd(x, precomp)
                precomp = self.precomp_partial3_xd(x, precomp)
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
                partial2_x_V_list = precomp['partial2_x_V_list']
                partial3_xd_V_last = precomp['partial3_xd_V_last']
            out = np.zeros( (x.shape[0], 1, self.dim_in, self.dim_in) )
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate these loops?
            for d1 in range(self.dim_in):
                for d2 in range(self.dim_in):
                    for i, (c, midx) in enumerate(zip(self.coeffs,self.multi_idxs)):
                        tmp[:] = 1.
                        for j, (idx, V1d,
                                pxV1d, p2xV1d) in enumerate(zip(midx, V_list,
                                                                partial_x_V_list,
                                                                partial2_x_V_list)):
                            if j == d1 == d2 == (self.dim_in-1):
                                tmp *= partial3_xd_V_last[:,idx]
                            elif j == d1 == d2 or j == d1 == (self.dim_in-1) \
                                 or j == d2 == (self.dim_in-1):
                                tmp *= p2xV1d[:,idx]
                            elif j == d1 or j == d2 or j == (self.dim_in-1):
                                tmp *= pxV1d[:,idx]
                            else:
                                tmp *= V1d[:,idx]
                        out[:,0,d1,d2] += c * tmp
        else:
            out = np.zeros( (x.shape[0], 1, self.dim_in, self.dim_in) )
            for i in range( self.dim_in ):
                for j in range(self.dim_in):
                    out[:,0,i,j] = np.dot( hess_x_partial_xd_V_mat[i,j], self.coeffs )
        return out

    @counted
    def grad_a_hess_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None),
                                 *args, **kwars):
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
        try:
            hess_x_partial_xd_V_mat = precomp['hess_x_partial_xd_V_mat']
        except (TypeError, KeyError) as e:
            try:
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
                partial2_x_V_list = precomp['partial2_x_V_list']
                partial3_xd_V_last = precomp['partial3_xd_V_last']
            except (TypeError, KeyError) as e:
                # Clean pre-existing
                precomp.pop('V_list', None)
                precomp.pop('partial_x_V_list', None)
                precomp.pop('partial2_x_V_list', None)
                precomp.pop('partial3_xd_V_last', None)
                # Ignoring slice
                idxs_slice = slice(None)
                # Compute
                precomp = self.precomp_evaluate(x, precomp)
                precomp = self.precomp_grad_x(x, precomp)
                precomp = self.precomp_hess_x(x, precomp)
                precomp = self.precomp_partial2_xd(x, precomp)
                precomp = self.precomp_partial3_xd(x, precomp)
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
                partial2_x_V_list = precomp['partial2_x_V_list']
                partial3_xd_V_last = precomp['partial3_xd_V_last']
            out = np.zeros( (x.shape[0], 1, self.n_coeffs, self.dim_in, self.dim_in) )
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate these loops?
            for d1 in range(self.dim_in):
                for d2 in range(self.dim_in):
                    for i, (c, midx) in enumerate(zip(self.coeffs,self.multi_idxs)):
                        tmp[:] = 1.
                        for j, (idx, V1d,
                                pxV1d, p2xV1d) in enumerate(zip(midx, V_list,
                                                                partial_x_V_list,
                                                                partial2_x_V_list)):
                            if j == d1 == d2 == (self.dim_in-1):
                                tmp *= partial3_xd_V_last[:,idx]
                            elif j == d1 == d2 or j == d1 == (self.dim_in-1) \
                                 or j == d2 == (self.dim_in-1):
                                tmp *= p2xV1d[:,idx]
                            elif j == d1 or j == d2 or j == (self.dim_in-1):
                                tmp *= pxV1d[:,idx]
                            else:
                                tmp *= V1d[:,idx]
                        out[:,0,i,d1,d2] = tmp
        else:
            out = np.zeros( (x.shape[0], 1, self.n_coeffs, self.dim_in, self.dim_in) )
            for i in range( self.dim_in ):
                for j in range(self.dim_in):
                    out[:,0,:,i,j] = hess_x_partial_xd_V_mat[i,j]
        return out

    def precomp_Vandermonde_partial2_xd(self, x, precomp=None):
        r""" Precompute multi-variate Vandermonde matrix for the evaluation of :math:`\partial^2_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary with Vandermonde matrix
        """
        if precomp is None: precomp = {}
        try: partial2_xd_V = precomp['partial2_xd_V']
        except KeyError as e:
            try: V_list = precomp['V_list']
            except (TypeError, KeyError) as e:
                self.precomp_evaluate(x, precomp)
                V_list = precomp['V_list']
            try: partial2_xd_V_last = precomp['partial2_xd_V_last']
            except (TypeError, KeyError) as e:
                self.precomp_partial2_xd(x, precomp)
                partial2_xd_V_last = precomp['partial2_xd_V_last']
            partial2_xd_V = np.ones((x.shape[0], self.n_coeffs))
            # TODO: Accelerate these loops?
            for i, midx in enumerate(self.multi_idxs):
                for idx, V1d in zip(midx[:-1], V_list[:-1]):
                    partial2_xd_V[:,i] *= V1d[:,idx]
                partial2_xd_V[:,i] *= partial2_xd_V_last[:,midx[-1]]
            precomp['partial2_xd_V'] = partial2_xd_V
        return precomp

    @counted
    def partial2_xd(self, x, precomp=None, idxs_slice=slice(None)):
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
        try:
            partial2_xd_V = precomp['partial2_xd_V']
        except (TypeError, KeyError) as e:
            try:
                V_list = precomp['V_list']
                partial2_xd_V_last = precomp['partial2_xd_V_last']
            except (TypeError, KeyError) as e:
                # Clean pre-existing
                precomp.pop('V_list', None)
                precomp.pop('partial2_xd_V_last', None)
                # Ignoring slice
                idxs_slice = slice(None)
                # Compute
                precomp = self.precomp_evaluate(x, precomp)
                precomp = self.precomp_partial2_xd(x, precomp)
                V_list = precomp['V_list']
                partial2_xd_V_last = precomp['partial2_xd_V_last']
            out = np.zeros((x.shape[0],1))
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate these loops?
            for i, (c, midx) in enumerate(zip(self.coeffs,self.multi_idxs)):
                tmp[:] = 1.
                for idx, V1d in zip(midx[:-1], V_list[:-1]):
                    tmp *= V1d[:,idx]
                tmp *= partial2_xd_V_last[:,midx[-1]]
                out[:,0] += c * tmp
        else:
            out = np.dot(partial2_xd_V, self.coeffs)
            out = out[:,nax]
        return out

    @cached()
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
        try:
            partial_xd_V = precomp['partial_xd_V']
        except KeyError as e:
            if 'V_list' not in precomp or 'partial_xd_V_last' not in precomp:
                idxs_slice = slice(None)
                precomp.pop('V_list', None)
                precomp.pop('partial_xd_V_last', None)
            precomp = self.precomp_Vandermonde_partial_xd(x, precomp)
        except TypeError as e:
            idxs_slice = slice(None)
            precomp = self.precomp_Vandermonde_partial_xd(x, precomp)
        finally:
            partial_xd_V = precomp['partial_xd_V']
        return partial_xd_V[idxs_slice,:][:,nax,:]

    @counted
    def hess_a_partial_xd(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Evaluate :math:`\nabla^2_{\bf a}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,N`]) --
            :math:`\nabla^2_{\bf a}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        nc = self.n_coeffs
        return np.zeros( (x.shape[0], 1, nc, nc) )
        
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


class LinearSpanApproximation(LinearSpanTensorizedParametricFunctional):
    @deprecate(
        'LinearSpanApproximation',
        '3.0',
        'Use Functionals.LinearSpanTensorizedParametricFunctional instead'
    )
    def __init__(self, *args, **kwargs):
        super(LinearSpanApproximation, self).__init__(*args, **kwargs)
