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

import logging
import numpy as np
import numpy.linalg as npla
import scipy.optimize as sciopt

from ...Misc import deprecate
from ...MPI import mpi_map, mpi_map_alloc_dmem, mpi_bcast_dmem

from .LinearSpanTensorizedParametricFunctionalBase import LinearSpanTensorizedParametricFunctional
from .ParametricMonotoneFunctionalBase import ParametricMonotoneFunctional

__all__ = [
    'PointwiseMonotoneLinearSpanTensorizedParametricFunctional',
    # Deprecated
    'MonotonicLinearSpanApproximation'
]

nax = np.newaxis

class PointwiseMonotoneLinearSpanTensorizedParametricFunctional(
        LinearSpanTensorizedParametricFunctional,
        ParametricMonotoneFunctional
):
    r""" Approximation of the type :math:`f \approx f_{\bf a} = \sum_{{\bf i} \in \mathcal{I}} {\bf a}_{\bf i} \Phi_{\bf i}`, monotonic in :math:`x_d`

    Args:
      basis_list (list): list of :math:`d`
        :class:`OrthogonalBasis<SpectralToolbox.OrthogonalBasis>`
      spantype (str): Span type. 'total' total order, 'full' full order,
        'midx' multi-indeces specified
      order_list (:class:`list<list>` of :class:`int<int>`): list of 
        orders :math:`\{N_i\}_{i=0}^d`
      multi_idxs (list): list of tuples containing the active multi-indices
    """
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
        precomp.update( self.precomp_partial_xd(x) )
        return precomp

    def get_identity_coeffs(self):
        coeffs = np.zeros(self.n_coeffs)
        idx = next( i for i, idx in enumerate(self.multi_idxs)
                    if idx == tuple([0]*(self.dim_in-1) + [1]) )
        coeffs[idx] = 1.
        return coeffs

    def regression(self, f, fparams=None, d=None, qtype=None, qparams=None,
                   x=None, w=None, x0=None,
                   regularization=None, tol=1e-4, maxit=100,
                   batch_size=(None,None), mpi_pool=None, import_set=set()):
        r""" Compute :math:`{\bf a}^* = \arg\min_{\bf a} \Vert f - f_{\bf a} \Vert_{\pi}`.

        Args:
          f (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
            :math:`f` or its functions values
          d (Distribution): distribution :math:`\pi`
          fparams (dict): parameters for function :math:`f`
          qtype (int): quadrature type to be used for the approximation of
            :math:`\mathbb{E}_{\pi}`
          qparams (object): parameters necessary for the construction of the
            quadrature
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
            used for the approximation of :math:`\mathbb{E}_{\pi}`
          w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
            used for the approximation of :math:`\mathbb{E}_{\pi}`
          x0 (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients to be used
            as initial values for the optimization
          regularization (dict): defines the regularization to be used.
            If ``None``, no regularization is applied.
            If key ``type=='L2'`` then applies Tikonhov regularization with
            coefficient in key ``alpha``.
          tol (float): tolerance to be used to solve the regression problem.
          maxit (int): maximum number of iterations
          batch_size (:class:`list<list>` [2] of :class:`int<int>`): the list contains the
            size of the batch to be used for each iteration. A size ``1`` correspond
            to a completely non-vectorized evaluation. A size ``None`` correspond to a
            completely vectorized one.
          mpi_pool (:class:`mpi_map.MPI_Pool`): pool of processes to be used
          import_set (set): list of couples ``(module_name,as_field)`` to be imported
            as ``import module_name as as_field`` (for MPI purposes)

        Returns:
          (:class:`tuple<tuple>`(:class:`ndarray<numpy.ndarray>` [:math:`N`],
          :class:`list<list>`)) -- containing the :math:`N` coefficients and
          log information from the optimizer.

        .. seealso:: :func:`TransportMaps.TriangularTransportMap.regression`

        .. note:: the resulting coefficients :math:`{\bf a}` are automatically
           set at the end of the optimization. Use :func:`coeffs` in order
           to retrieve them.
        .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
          exclusive, but one pair of them is necessary.
        """
        if (x is None) and (w is None):
            (x,w) = d.quadrature(qtype, qparams)
        params = {}
        params['x'] = x
        params['w'] = w
        params['regularization'] = regularization
        params['batch_size'] = batch_size
        params['mpi_pool'] = mpi_pool
        cons = ({'type': 'ineq',
                 'fun': self.regression_constraints,
                 'jac': self.regression_grad_a_constraints,
                 'args': (params,)})
        options = {'maxiter': maxit,
                   'disp': False}
        if x0 is None:
            x0 = self.get_default_init_values_regression()
        params['nobj'] = 0
        params['nda_obj'] = 0
        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            self.logger.debug("regression(): Precomputation started")
        # Prepare parameters
        if isinstance(f, np.ndarray):
            params['fvals'] = f
        else:
            scatter_tuple = (['x'], [x])
            bcast_tuple = (['precomp'], [fparams])
            params['fvals'] = mpi_map("evaluate", scatter_tuple=scatter_tuple,
                                      bcast_tuple=bcast_tuple,
                                      obj=f, mpi_pool=mpi_pool)
        # Init precomputation memory
        params['params1'] = {}
        mpi_bcast_dmem(params1=params['params1'], f1=self, mpi_pool=mpi_pool)
        
        # Precompute
        scatter_tuple = (['x'], [x])
        mpi_map("precomp_regression", scatter_tuple=scatter_tuple,
                dmem_key_in_list=['params1'],
                dmem_arg_in_list=['precomp'],
                dmem_val_in_list=[params['params1']],
                obj='f1', obj_val=self,
                mpi_pool=mpi_pool,
                 concatenate=False)
        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            self.logger.debug("regression(): Precomputation ended")
        # Minimize
        res = sciopt.minimize(self.regression_objective, x0, args=params, \
                              jac=self.regression_grad_a_objective,
                              constraints=cons, \
                              method='SLSQP', options=options, tol=tol)
        if not res['success']:
            self.logger.warn("Regression failure: " + res['message'])
        coeffs = res['x']
        self.coeffs = coeffs
        return (coeffs, res)
        
    def regression_constraints(self, a, params):
        # Update coefficients
        bcast_tuple = (['coeffs'], [a])
        mpi_pool = params['mpi_pool']
        mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
                obj='f1', obj_val=self,
                mpi_pool=mpi_pool, concatenate=False)
        # Evaluate
        x = params['x']
        scatter_tuple = (['x'], [x])
        dmem_key_in_list = ['params1']
        dmem_arg_in_list=['precomp']
        dmem_val_in_list = [params['params1']]
        out = mpi_map("partial_xd", scatter_tuple=scatter_tuple,
                      dmem_key_in_list=dmem_key_in_list,
                      dmem_arg_in_list=dmem_arg_in_list,
                      dmem_val_in_list=dmem_val_in_list,
                      obj='f1', obj_val=self, mpi_pool=mpi_pool)
        return out[:,0]

    def regression_grad_a_constraints(self, a, params):
        mpi_pool = params['mpi_pool']
        # Update coefficients
        bcast_tuple = (['coeffs'], [a])
        mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
                obj='f1', obj_val=self,
                mpi_pool=mpi_pool, concatenate=False)
        # Evaluate
        x = params['x']
        scatter_tuple = (['x'], [x])
        dmem_key_in_list = ['params1']
        dmem_arg_in_list=['precomp']
        dmem_val_in_list = [params['params1']]
        out = mpi_map("grad_a_partial_xd", scatter_tuple=scatter_tuple,
                      dmem_key_in_list=dmem_key_in_list,
                      dmem_arg_in_list=dmem_arg_in_list,
                      dmem_val_in_list=dmem_val_in_list,
                      obj='f1', obj_val=self, mpi_pool=mpi_pool)
        return out[:,0,:]


##############
# DEPRECATED #
##############


class MonotonicLinearSpanApproximation(
        PointwiseMonotoneLinearSpanTensorizedParametricFunctional
):
    @deprecate(
        'MonotonicLinearSpanApproximation',
        '3.0',
        'Use Functionals.PointwiseMonotoneLinearSpanTensorizedParametricFunctional instead.'
    )
    def __init__(self, *args, **kwargs):
        super(MonotonicLinearSpanApproximation, self).__init__(*args, **kwargs)
