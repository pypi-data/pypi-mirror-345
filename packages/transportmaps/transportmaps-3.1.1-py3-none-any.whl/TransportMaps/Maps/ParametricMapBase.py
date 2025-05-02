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

from ..Misc import deprecate, required_kwargs
from .MapBase import Map

__all__ = [
    'ParametricMap'
]


class ParametricMap(Map):
    r""" Abstract map :math:`T:\mathbb{R}^{d_a}\times\mathbb{R}^{d_x}\rightarrow\mathbb{R}^{d_y}`
    """
    @required_kwargs('dim_in', 'dim_out')
    def __init__(self, **kwargs):
        r"""
        Kwargs:
          dim_in (int): input dimension :math:`d_x`
          dim_out (int): output dimension :math:`d_y`
        """
        super(ParametricMap, self).__init__(**kwargs)
    
    @property
    def n_coeffs(self):
        r""" Returns the total number of coefficients.

        Returns:
          (:class:`int`) -- total number :math:`N` of
              coefficients characterizing the map.

        Raises:
          NotImplementedError: needs to be implemented in subclasses
        """
        raise NotImplementedError("Must be implemented in subclasses")

    @deprecate("ParametricMap.get_n_coeffs()", "1.0b3",
               "Use property ParametricMap.n_coeffs instead")
    def get_n_coeffs(self):
        return self.n_coeffs
        
    @property
    def coeffs(self):
        r""" Returns the actual value of the coefficients.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients.

        Raises:
          NotImplementedError: needs to be implemented in subclasses
        """
        raise NotImplementedError("Must be implemented in subclasses")

    @deprecate("ParametricMap.get_coeffs()", "1.0b3",
               "Use property ParametricMap.coeffs instead")
    def get_coeffs(self):
        return self.coeffs
    
    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients.

        Args:
           coeffs (:class:`ndarray<numpy.ndarray>` [:math:`N`]):
              coefficients for the various maps

        Raises:
          NotImplementedError: needs to be implemented in subclasses
        """
        raise NotImplementedError("Must be implemented in subclasses")

    def _set_coeffs(self, coeffs):
        self.coeffs = coeffs

    @deprecate("ParametricMap.set_coeffs(value)", "1.0b3",
               "Use setter ParametricMap.coeffs = value instead.")
    def set_coeffs(self, coeffs):
        self.coeffs = coeffs

    def get_identity_coeffs(self):
        r""" [Abstract] Returns the coefficients corresponding to the identity map

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients

        Raises:
          NotImplementedError: must be implemented in subclasses.
        """
        raise NotImplementedError("Must be implemented in subclasses.")

    def grad_a(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute :math:`\nabla_{\bf a} T[{\bf a}]({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          
        Returns:
           (:class:`ndarray<numpy.ndarray>`) -- gradient

        Raises:
          NotImplementedError: needs to be implemented in subclasses
        """
        raise NotImplementedError("Must be implemented in subclasses")

    def tuple_grad_a(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute :math:`(T[{\bf a}]({\bf x}), \nabla_{\bf a} T[{\bf a}]({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          
        Returns:
           (:class:`ndarray<numpy.ndarray>`) -- gradient

        Raises:
          NotImplementedError: needs to be implemented in subclasses
        """
        raise NotImplementedError("Must be implemented in subclasses")

    def hess_a(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute :math:`\nabla^2_{\bf a} T[{\bf a}]({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          
        Returns:
           (:class:`ndarray<numpy.ndarray>`) -- Hessian

        Raises:
          NotImplementedError: needs to be implemented in subclasses
        """
        raise NotImplementedError("Must be implemented in subclasses")

    def action_hess_a(self, x, da, precomp=None, idxs_slice=slice(None)):
        r""" Compute :math:`\langle\nabla^2_{\bf a} T[{\bf a}]({\bf x}), \delta{\bf a}\rangle`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          da (:class:`ndarray<numpy.ndarray>` [:math:`N`]): direction
            on which to evaluate the Hessian
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          
        Returns:
           (:class:`ndarray<numpy.ndarray>`) -- action of the Hessian

        Raises:
          NotImplementedError: needs to be implemented in subclasses
        """
        raise NotImplementedError("Must be implemented in subclasses")

    def grad_a_grad_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf a} \nabla_{\bf x} T[{\bf a}]({\bf x})`
        """
        raise NotImplementedError("Must be implemented in subclasses")
        
    def grad_a_hess_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf a} \nabla^2_{\bf x} T[{\bf a}]({\bf x})`.
        """
        raise NotImplementedError("Must be implemented in subclasses")
