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

__all__ = [
    'ParametricFunctional',
    # Deprecated
    'ParametricFunctionApproximation'
]


from ...Misc import deprecate
from .FunctionalBase import Functional


class ParametricFunctional(Functional):
    r""" Abstract class for parametric approximation :math:`f_{\bf a}:\mathbb{R}^d\rightarrow\mathbb{R}` of :math:`f:\mathbb{R}^d\rightarrow\mathbb{R}`.

    Args:
      dim (int): number of dimensions
    """

    def __init__(self, dim):
        super(ParametricFunctional,self).__init__(dim)

    def get_identity_coeffs(self):
        raise NotImplementedError("To be implemented in subclasses")

    def get_default_init_values_regression(self):
        raise NotImplementedError("To be implemented in subclasses")

    def regression_callback(self, xk):
        self.params_callback['hess_assembled'] = False

    def regression_nominal_coeffs(self):
        return self.get_default_init_values_regression()

    def init_coeffs(self):
        r""" [Abstract] Initialize the coefficients :math:`{\bf a}`
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @property
    def n_coeffs(self):
        r""" [Abstract] Get the number :math:`N` of coefficients :math:`{\bf a}`

        Returns:
          (:class:`int<int>`) -- number of coefficients
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @deprecate("ParametricFunctionApproximation.get_n_coeffs()", "1.0b3",
               "Use property ParametricFunctionApproximation.n_coeffs instead")
    def get_n_coeffs(self):
        return self.n_coeffs

    @property
    def coeffs(self):
        r""" [Abstract] Get the coefficients :math:`{\bf a}`

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @deprecate("ParametricFunctionApproximation.get_coeffs()", "1.0b3",
               "Use property ParametricFunctionApproximation.coeffs instead")
    def get_coeffs(self):
        return self.coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" [Abstract] Set the coefficients :math:`{\bf a}`.

        Args:
          coeffs (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def _set_coeffs(self, coeffs):
        self.coeffs = coeffs

    @deprecate("ParametricFunctionApproximation.set_coeffs(value)", "1.0b3",
               "Use setter ParametricFunctionApproximation.coeffs = value instead.")
    def set_coeffs(self, coeffs):
        self.coeffs = coeffs

    def grad_a(self, x, precomp=None, idxs_slice=slice(None)):
        r""" [Abstract] Evaluate :math:`\nabla_{\bf a} f_{\bf a}` at ``x``.

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
        raise NotImplementedError("To be implemented in sub-classes")

    def hess_a(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" [Abstract] Evaluate :math:`\nabla^2_{\bf a} f_{\bf a}` at ``x``.

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
        raise NotImplementedError("To be implemented in sub-classes")

    def grad_a_partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" [Abstract] Evaluate :math:`\nabla_{\bf a}\partial_{x_d} f_{\bf a}` at ``x``.

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
        raise NotImplementedError("To be implemented in sub-classes")

    def hess_a_partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" [Abstract] Evaluate :math:`\nabla^2_{\bf a}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,N,N`]) --
            :math:`\nabla^2_{\bf a}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        raise NotImplementedError("To be implemented in sub-classes")


##############
# DEPRECATED #
##############


class ParametricFunctionApproximation(ParametricFunctional):
    @deprecate(
        'ParametricFunctionApproximation',
        '3.0',
        'Use Functionals.ParametricFunctional instead'
    )
    def __init__(self, dim):
        super(ParametricFunctionApproximation, self).__init__(dim)
