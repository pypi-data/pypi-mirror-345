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

from TransportMaps.Misc import deprecate
from .ParametricFunctionalBase import ParametricFunctional

__all__ = [
    'TensorizedParametricFunctional',
    'TensorizedFunctionApproximation'
]

class TensorizedParametricFunctional(ParametricFunctional):
    r""" [Abstract] Class for approximations using tensorization of unidimensional basis

    Args:
      basis_list (list): list of :math:`d` :class:`Basis<SpectralToolbox.Basis>`
      full_basis_list (list): full list of :class:`Basis<SpectralToolbox.Basis>`.
        ``basis_list`` is a subset of ``full_basis_list``. This may be used to
        automatically increase the input dimension of the approximation.
    """
    def __init__(self, basis_list, full_basis_list=None):
        self.basis_list = basis_list
        self.full_basis_list = full_basis_list
        super(TensorizedParametricFunctional,self).__init__(len(self.basis_list))

    def precomp_evaluate(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute the uni-variate Vandermonde matrices for the evaluation of :math:`f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`list<list>`
            [:math:`d`] of :class:`ndarray<numpy.ndarray>` [:math:`m,n_i`]) --
            dictionary containing the list of Vandermonde matrices
        """
        if precomp is None: precomp = {}
        # Vandermonde matrices
        try: V_list = precomp['V_list']
        except KeyError as e:
            precomp['V_list'] = [ b.GradVandermonde(x[:,i], o)
                                  for i,(b,o) in
                                  enumerate(zip(self.basis_list,
                                                self.directional_orders)) ]
        if precomp_type == 'multi':
            self.precomp_Vandermonde_evaluate(x, precomp)
        return precomp

    def precomp_grad_x(self, x, precomp=None):
        r""" Precompute the uni-variate Vandermonde matrices for the evaluation of :math:`\nabla_{\bf x} f_{\bf a}` at ``x``

        Letting :math:`\Phi^{(i)}(x_i)` being the uni-variate Vandermonde in
        :math:`x_i`, the ``i``-th element of the returned list is
        :math:`\partial_{x_i}\Phi^{(i)}(x_i)`.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Return:
          (:class:`dict<dict>` with :class:`list<list>`
            [:math:`d`] of :class:`ndarray<numpy.ndarray>` [:math:`m,n_i`]) --
            dictionary containing the list of Vandermonde matrices
        """
        if precomp is None: precomp = {}
        try: V_list = precomp['V_list']
        except KeyError as e:
            self.precomp_evaluate(x, precomp)
        try: partial_x_V_list = precomp['partial_x_V_list']
        except KeyError as e:
            partial_x_V_list = [ b.GradVandermonde(x[:,i], o, k=1)
                                 for i,(b,o)
                                 in enumerate(zip(self.basis_list,
                                                  self.directional_orders)) ]
            precomp['partial_x_V_list'] = partial_x_V_list
        return precomp

    def precomp_hess_x(self, x, precomp=None):
        r""" Precompute the uni-variate Vandermonde matrices for the evaluation of :math:`\nabla^2_{\bf x} f_{\bf a}` at ``x``

        Letting :math:`\Phi^{(i)}(x_i)` being the uni-variate Vandermonde in
        :math:`x_i`, the ``i``-th element of the returned list is
        :math:`\partial^2_{x_i}\Phi^{(i)}(x_i)`.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Return:
          (:class:`dict<dict>` with :class:`list<list>`
            [:math:`d`] of :class:`ndarray<numpy.ndarray>` [:math:`m,n_i`]) --
            dictionary containing the list of Vandermonde matrices
        """
        if precomp is None: precomp = {}
        try: V_list = precomp['V_list']
        except KeyError as e:
            self.precomp_evaluate(x, precomp)
        try: partial_x_V_list = precomp['partial_x_V_list']
        except KeyError as e:
            self.precomp_grad_x(x, precomp)
        try: partial2_x_V_list = precomp['partial2_x_V_list']
        except KeyError as e:
            partial2_x_V_list = [ b.GradVandermonde(x[:,i], o, k=2)
                                  for i,(b,o) in enumerate(zip(
                                          self.basis_list, self.directional_orders)) ]
            precomp['partial2_x_V_list'] = partial2_x_V_list
        return precomp

    def precomp_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute uni-variate Vandermonde matrix for the evaluation of :math:`\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`ndarray<numpy.ndarray>` [:math:`m,n_d`]) --
            dictionary with Vandermonde matrix
        """
        if precomp is None: precomp = {}
        try: V_list = precomp['V_list']
        except KeyError as e:
            self.precomp_evaluate(x, precomp)
        try: partial_xd_V_last = precomp['partial_xd_V_last']
        except KeyError as e:
            o = self.directional_orders[-1]
            precomp['partial_xd_V_last'] = self.basis_list[-1].GradVandermonde(
                x[:,-1], o, k=1)
        if precomp_type == 'multi':
            self.precomp_Vandermonde_partial_xd(x, precomp)
        return precomp

    def precomp_partial2_xd(self, x, precomp=None):
        r""" Precompute uni-variate Vandermonde matrix for the evaluation of :math:`\partial^2_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`ndarray<numpy.ndarray>` [:math:`m,n_d`]) --
            dictionary with Vandermonde matrix
        """
        if precomp is None: precomp = {}
        try: V_list = precomp['V_list']
        except KeyError as e:
            self.precomp_evaluate(x, precomp)
        try: partial2_xd_V_last = precomp['partial2_xd_V_last']
        except KeyError as e:
            o = self.directional_orders[-1]
            precomp['partial2_xd_V_last'] = self.basis_list[-1].GradVandermonde(x[:,-1], o, k=2)
        return precomp

    def precomp_grad_x_partial_xd(self, x, precomp=None):
        r""" Precompute uni-variate Vandermonde matrices for the evaluation of :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`list<list>` [d]
            :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary containing the list of uni-variate Vandermonde matrices.
        """
        if precomp is None: precomp = {}
        try: V_list = precomp['V_list']
        except KeyError as e:
            self.precomp_evaluate(x, precomp)
        try: partial_x_V_list = precomp['partial_x_V_list']
        except KeyError as e:
            self.precomp_grad_x(x, precomp)
        try: partial2_xd_V_last = precomp['partial2_xd_V_last']
        except KeyError as e:
            self.precomp_partial2_xd(x, precomp)
        return precomp

    def precomp_partial3_xd(self, x, precomp=None):
        r""" Precompute uni-variate Vandermonde matrix for the evaluation of :math:`\partial^3_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`ndarray<numpy.ndarray>` [:math:`m,n_d`]) --
            dictionary with Vandermonde matrix
        """
        if precomp is None: precomp = {}
        try: V_list = precomp['V_list']
        except KeyError as e:
            self.precomp_evaluate(x, precomp)
        try: partial3_xd_V_last = precomp['partial3_xd_V_last']
        except KeyError as e:
            o = self.directional_orders[-1]
            precomp['partial3_xd_V_last'] = self.basis_list[-1].GradVandermonde(x[:,-1], o, k=3)
        return precomp

    def precomp_hess_x_partial_xd(self, x, precomp=None):
        r""" Precompute uni-variate Vandermonde matrices for the evaluation of :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`list<list>` [d]
            :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary containing the list of uni-variate Vandermonde matrices.
        """
        if precomp is None: precomp = {}
        try: V_list = precomp['V_list']
        except KeyError as e:
            self.precomp_evaluate(x, precomp)
        try: partial_x_V_list = precomp['partial_x_V_list']
        except KeyError as e:
            self.precomp_grad_x(x, precomp)
        try: partial2_x_V_list = precomp['partial2_x_V_list']
        except KeyError as e:
            self.precomp_hess_x(x, precomp)
        try: partial3_xd_V_last = precomp['partial3_xd_V_last']
        except KeyError as e:
            self.precomp_partial3_xd(x, precomp)
        return precomp

##############
# DEPRECATED #
##############

class TensorizedFunctionApproximation(TensorizedParametricFunctional):
    @deprecate(
        'TensorizedFunctionApproximation',
        '3.0',
        'Use Functionals.TensorizedParametricFunctional instead'
    )
    def __init__(self, dim):
        super(TensorizedFunctionApproximation, self).__init__(dim)
