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

from TransportMaps.Maps import Map

__all__ = [
    'Functional',
    # Deprecated
    'Function'
]


class Functional(Map):
    r""" Abstract class for functions :math:`f:\mathbb{R}^d\rightarrow\mathbb{R}`.
    """
    def __init__(self, dim):
        r"""
        Args:
          dim (int): dimension :math:`d`
        """
        super(Functional, self).__init__(
            dim_in=dim,
            dim_out=1
        )

    @property
    def dim(self):
        return self.dim_in

    def evaluate(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" [Abstract] Evaluate :math:`f_{\bf a}` at ``x``.

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
        raise NotImplementedError("To be implemented in sub-classes")

    def grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" [Abstract] Evaluate :math:`\nabla_{\bf x} f_{\bf a}` at ``x``.

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
        raise NotImplementedError("To be implemented in sub-classes")

    def partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" [Abstract] Evaluate :math:`\partial_{x_d} f_{\bf a}` at ``x``.

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
        raise NotImplementedError("To be implemented in sub-classes")

    def grad_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" [Abstract] Evaluate :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

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
        raise NotImplementedError("To be implemented in sub-classes")

    def hess_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" [Abstract] Evaluate :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1,d,d`]) --
            :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def partial2_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" [Abstract] Evaluate :math:`\partial^2_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict`): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,1`]) --
            :math:`\partial^2_{x_d} f_{\bf a}({\bf x})`
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def precomp_evaluate(self, x, precomp=None):
        r""" [Abstract] Precompute necessary structures for the evaluation of :math:`f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
          (:class:`dict<dict>`) -- data structures
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def precomp_grad_x(self, x, precomp=None):
        r""" [Abstract] Precompute necessary structures for the evaluation of :math:`\nabla_{\bf x} f_{\bf a}` at ``x``

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Return:
          (:class:`dict<dict>`) -- data structures
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def precomp_partial_xd(self, x, precomp=None):
        r""" [Abstract] Precompute necessary structures for the evaluation of :math:`\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
          (:class:`dict<dict>`) -- data structures
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def precomp_grad_x_partial_xd(self, x, precomp=None):
        r""" [Abstract] Precompute  necessary structures for the evaluation of :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
          (:class:`dict<dict>`) -- data structures
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def precomp_partial2_xd(self, x, precomp=None):
        r""" [Abstract] Precompute necessary structures for the evaluation of :math:`\partial^2_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
          (:class:`dict<dict>`) -- data structures
        """
        raise NotImplementedError("To be implemented in sub-classes")

        
##############
# DEPRECATED #
##############

class Function(Functional):
    @deprecate(
        'Function',
        '3.0',
        'Use Functionals.Functional instead.'
    )
    def __init__(self, dim):
        super(Function, self).__init__(dim)
