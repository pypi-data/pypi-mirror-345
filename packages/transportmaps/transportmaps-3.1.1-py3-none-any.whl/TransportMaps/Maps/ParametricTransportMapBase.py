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
import numpy.linalg as npla

from ..Misc import required_kwargs, \
    cached, counted
from .ParametricMapBase import ParametricMap
from .TransportMapBase import TransportMap

__all__ = [
    'ParametricTransportMap',
]

nax = np.newaxis

class ParametricTransportMap(ParametricMap, TransportMap):
    r"""Transport map :math:`T[{\bf a}]({\bf x}): \mathbb{R}^n \times \mathbb{R}^{d_x}\rightarrow\mathbb{R}^{d_x}`.
    """
    @required_kwargs('dim')
    def __init__(self, **kwargs):
        kwargs['dim_in'] = kwargs['dim']
        kwargs['dim_out'] = kwargs['dim']

        super(ParametricTransportMap, self).__init__(**kwargs)

    @property
    def n_coeffs(self):
        r""" Returns the total number of coefficients.

        Returns:
           total number :math:`N` of coefficients characterizing the transport map.
        """
        return np.sum([a.n_coeffs for a in self.approx_list])

    @property
    def coeffs(self):
        r""" Returns the actual value of the coefficients.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients.
        """
        out = np.zeros(self.n_coeffs)
        start = 0
        for a in self.approx_list:
            n_coeffs = np.sum(a.n_coeffs)
            out[start:start + n_coeffs] = a.coeffs
            start += n_coeffs
        return out

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients.

        Args:
           coeffs (:class:`ndarray<numpy.ndarray>` [:math:`N`]):
              coefficients for the various maps

        Raises:
           ValueError: if the number of input coefficients does not match the
              number of required coefficients :func:`n_coeffs`.
        """
        start = 0
        for a in self.approx_list:
            n_coeffs = a.n_coeffs
            a.coeffs = coeffs[start:start + n_coeffs]
            start += n_coeffs

    def get_identity_coeffs(self):
        r""" [Abstract] Returns the coefficients corresponding to the identity map

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients

        Raises:
          NotImplementedError: must be implemented in subclasses.
        """
        raise NotImplementedError("Must be implemented in subclasses.")

    @counted
    def grad_a_inverse(self, x, precomp=None, idxs_slice=slice(None)):
        r""" [Abstract] Compute :math:`\nabla_{\bf a} T^{-1}[{\bf a}]({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,N`]) --
              :math:`\nabla_{\bf a} T^{-1}[{\bf a}]({\bf x})`

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        raise NotImplementedError("Abstract method")

    @cached()
    @counted
    def grad_a_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None),
                              *args, **kwargs):
        r""" [Abstract] Compute: :math:`\nabla_{\bf a} \log \det \nabla_{\bf x} T[{\bf a}]({\bf x})`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
             :math:`\nabla_{\bf a} \log \det \nabla_{\bf x} T[{\bf a}]({\bf x})`
             at every evaluation point

        .. seealso:: :func:`log_det_grad_x`
        """
        raise NotImplementedError("Abstract method")

    @cached()
    @counted
    def hess_a_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None),
                              *args, **kwargs):
        r""" [Abstract] Compute: :math:`\nabla^2_{\bf a} \log \det \nabla_{\bf x} T[{\bf a}]({\bf x})`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,N,N`]) --
           :math:`\nabla^2_{\bf a} \log \det \nabla_{\bf x} T[{\bf a}]({\bf x})`
           at every evaluation point

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_a_log_det_grad_x`
        """
        raise NotImplementedError("Abstract method")

    def minimize_kl_divergence_callback(self, xk):
        self.it_callback += 1
        msg = "Iteration %d - " % self.it_callback + \
            "obj = %.5e - " % self.params_callback['fval']
        if hasattr(self.params_callback, 'jac'):
            msg += "jac 2-norm = %.2e - " % npla.norm(self.params_callback['jac']) + \
                "jac inf-norm = %.2e" % npla.norm(self.params_callback['jac'], ord=np.inf)
        self.logger.info(msg)
        if self.ders_callback == 2:
            self.params_callback['hess_assembled'] = False
