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

from TransportMaps.Misc import deprecate, counted
from .DistributionBase import *

__all__ = [
    'ParametricDistribution'
]

class ParametricDistribution(Distribution):
    r""" Parametric distribution :math:`\pi_{\bf a}`.
    """

    @property
    def coeffs(self):
        r""" [Abstract] Get the coefficients :math:`{\bf a}` of the distribution

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    @deprecate("ParametricDistribution.get_coeffs()", "1.0b3",
               "Use property ParametricDistribution.coeffs instead")
    def get_coeffs(self):
        return self.coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" [Abstract] Set the coefficients :math:`{\bf a}` of the distribution

        Args:
          a (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    def _set_coeffs(self, coeffs):
        self.coeffs = coeffs

    @deprecate("ParametricDistribution.set_coeffs(value)", "1.0b3",
               "Use setter ParametricDistribution.coeffs = value instead")
    def set_coeffs(self, coeffs):
        self.coeffs = coeffs

    @property
    def n_coeffs(self):
        r""" [Abstract] Get the number :math:`N` of coefficients

        Returns:
          (int) -- number of coefficients.

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    @deprecate("ParametricDistribution.get_n_coeffs()", "1.0b3",
               "Use property ParametricDistribution.n_coeffs instead")
    def get_n_coeffs(self):
        return self.n_coeffs

        
    def grad_a_log_pdf(self, x, *args, **kwargs):
        r""" [Abstract] Evaluate :math:`\nabla_{\bf a} \log \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N`]) -- :math:`\nabla_{\bf a} \log \pi({\bf x})`

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    @counted
    def tuple_grad_a_log_pdf(self, x, params=None, idxs_slice=slice(None,None,None),
                             cache=None):
        r""" [Abstract] Evaluate :math:`\left(\log \pi({\bf x}), \nabla_{\bf a} \log \pi({\bf x})\right)`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`tuple`) -- :math:`\left(\log \pi({\bf x}), \nabla_{\bf a} \log \pi({\bf x})\right)`

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        return (self.log_pdf(x, params, idxs_slice, cache=cache),
                self.grad_a_log_pdf(x, params, idxs_slice, cache=cache))

    def hess_a_log_pdf(self, x, *args, **kwargs):
        r""" [Abstract] Evaluate :math:`\nabla^2_{\bf a} \log \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N`]) -- :math:`\nabla^2_{\bf a} \log \pi({\bf x})`

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    def action_hess_a_log_pdf(self, x, da, *args, **kwargs):
        r""" [Abstract] Evaluate :math:`\langle \nabla^2_{\bf a} \log \pi({\bf x}), \delta{\bf a}\rangle`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          da (:class:`ndarray<numpy.ndarray>` [:math:`N`]): direction
            on which to evaluate the Hessian
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N`]) -- :math:`\nabla^2_{\bf a} \log \pi({\bf x})`

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")
