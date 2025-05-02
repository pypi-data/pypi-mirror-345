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

from .MapBase import Map
from ..Misc import \
    cached, cached_tuple, counted, get_sub_cache

__all__ = [
    'TransportMap'
]

nax = np.newaxis


class TransportMap(Map):
    r"""Transport map :math:`T({\bf x},{\bf a}): \mathbb{R}^d \rightarrow \mathbb{R}^d`.

    Args:
        dim_in (int): input dimension
        dim_out (int): output dimension
    """
    def __init__(self, *args, **kwargs):
        if 'dim' in kwargs:
            kwargs['dim_in'] = kwargs['dim']
            kwargs['dim_out'] = kwargs['dim']
        if kwargs['dim_in'] != kwargs['dim_out']:
            raise ValueError("The map is not square")
        kwargs['dim'] = kwargs['dim_in']
        super(TransportMap, self).__init__(**kwargs)


    @counted
    def inverse(self, y, precomp=None, idxs_slice=slice(None)):
        r""" [Abstract] Compute: :math:`T^{-1}({\bf x})`

        Args:
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`T^{-1}({\bf x})` for every evaluation point
        """
        raise NotImplementedError("To be implemented in subclasses")

    def grad_x_inverse(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" [Abstract] Compute :math:`\nabla_{\bf x} T^{-1}({\bf x})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           gradient matrices for every evaluation point.

        Raises:
           NotImplementedError: to be implemented in subclasses
        """
        raise NotImplementedError("To be implemented in subclasses")

    def hess_x_inverse(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" [Abstract] Compute :math:`\nabla_{\bf x}^2 T^{-1}({\bf x})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           Hessian tensors for every evaluation point.

        Raises:
           NotImplementedError: to be implemented in subclasses
        """
        raise NotImplementedError("To be implemented in subclasses")

    @counted
    def det_grad_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" [Abstract] Compute: :math:`\det \nabla_{\bf x} T({\bf x}, {\bf a})`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\det \nabla_{\bf x} T({\bf x}, {\bf a})` at every
           evaluation point
        """
        return np.exp(self.log_det_grad_x(
            x, precomp, idxs_slice=idxs_slice, *args, **kwargs))

    @cached()
    @counted
    def log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" [Abstract] Compute: :math:`\log \det \nabla_{\bf x} T({\bf x}, {\bf a})`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \det \nabla_{\bf x} T({\bf x}, {\bf a})` at every
           evaluation point
        """
        raise NotImplementedError("To be implemented in subclasses")

    @counted
    def log_det_grad_x_inverse(self, x, precomp=None, idxs_slice=slice(None),
                               *args, **kwargs):
        r""" [Abstract] Compute: :math:`\log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})` at every
           evaluation point
        """
        raise NotImplementedError("To be implemented in subclasses")

    @cached()
    @counted
    def grad_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None),
                              *args, **kwargs):
        r""" [Abstract] Compute: :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        .. seealso:: :func:`log_det_grad_x`.
        """
        raise NotImplementedError("To be implemented in subclasses")

    @cached()
    @counted
    def hess_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None),
                              *args, **kwargs):
        r""" [Abstract] Compute: :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        raise NotImplementedError("To be implemented in subclasses")


    @cached()
    @counted
    def action_hess_x_log_det_grad_x(
            self,
            x: np.ndarray,
            dx: np.ndarray,
            precomp: dict = None,
            idxs_slice=slice(None),
            *args, **kwargs
    ):
        r""" [Abstract] Compute: :math:`\langle\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}), \delta{\bf x}\rangle`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): directions on which to evaluate the Hessian
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\langle\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}), \delta{\bf x}\rangle`
           at every evaluation point

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        raise NotImplementedError("To be implemented in subclasses")

    def grad_x_log_det_grad_x_inverse(self, x, precomp=None, idxs_slice=slice(None),
                                      *args, **kwargs):
        r""" [Abstract] Compute: :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`
           at every evaluation point

        .. seealso:: :func:`log_det_grad_x`.
        """
        raise NotImplementedError("To be implemented in subclasses")

    def hess_x_log_det_grad_x_inverse(self, x, precomp=None, idxs_slice=slice(None),
                                      *args, **kwargs):
        r""" [Abstract] Compute: :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`
           at every evaluation point

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        raise NotImplementedError("To be implemented in subclasses")

    @cached()
    @counted
    def action_hess_x_log_det_grad_x_inverse(
            self,
            x: np.ndarray,
            dx: np.ndarray,
            precomp: dict = None,
            idxs_slice=slice(None),
            *args, **kwargs
    ):
        r""" [Abstract] Compute: :math:`\langle\nabla^2_{\bf x} \log \det \nabla_{\bf x} T^-1({\bf x}), \delta{\bf x}\rangle`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): directions on which to evaluate the Hessian
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\langle\nabla^2_{\bf x} \log \det \nabla_{\bf x} T^-1({\bf x}), \delta{\bf x}\rangle`
           at every evaluation point

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        raise NotImplementedError("To be implemented in subclasses")

    @counted
    def log_pushforward(self, x, pi, params_t=None, params_pi=None, idxs_slice=slice(None),
                        cache=None):
        r""" Compute: :math:`\log \pi \circ T_{\bf a}^{-1}({\bf y}) + \log \vert\det \grad_{\bf x}T_{\bf a}^{-1}({\bf y})\vert`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           pi (:class:`Distributions.Distribution`): distribution to be pushed forward
           params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
           params_pi (dict): parameters for the evaluation of :math:`\pi`
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
           cache (dict): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \pi \circ T^{-1}({\bf y,a}) + \log \vert\det \grad_{\bf x}T^{-1}({\bf y,a})\vert`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        raise NotImplementedError("To be implemented in subclasses")

    @counted
    def pushforward(self, x, pi, params_t=None, params_pi=None, idxs_slice=slice(None),
                    cache=None):
        r""" Compute: :math:`\pi \circ T_{\bf a}^{-1}({\bf y}) \vert\det \grad_{\bf x}T_{\bf a}^{-1}({\bf y})\vert`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           pi (:class:`Distributions.Distribution`): distribution to be pushed forward
           params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
           params_pi (dict): parameters for the evaluation of :math:`\pi`
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
           cache (dict): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\pi \circ T^{-1}({\bf y,a}) \vert\det \grad_{\bf x}T^{-1}({\bf y,a})\vert`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        return np.exp(
            self.log_pushforward(
                x, pi, params_t=params_t, params_pi=params_pi,
                idxs_slice=idxs_slice, cache=cache
            )
        )

    @counted
    def log_pullback(
            self, x, pi, params_t=None, params_pi=None, idxs_slice=slice(None),
            cache=None):
        r""" Compute: :math:`\log\pi \circ T({\bf x}) + \log \vert\det \grad_{\bf x}T({\bf x})\vert`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          pi (:class:`Distributions.Distribution`): distribution to be pulled back
          params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
          params_pi (dict): parameters for the evaluation of :math:`\pi`
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \pi \circ T({\bf x}) + \log\vert\det \grad_{\bf x}T({\bf x})\vert`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        raise NotImplementedError("To be implemented in subclasses")

    @counted
    def pullback(self, x, pi, params_t=None, params_pi=None, idxs_slice=slice(None),
                 cache=None):
        r""" Compute: :math:`\pi \circ T({\bf x}) \vert\det \grad_{\bf x}T({\bf x})\vert`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          pi (:class:`Distributions.Distribution`): distribution to be pulled back
          params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
          params_pi (dict): parameters for the evaluation of :math:`\pi`
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache
          
        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\pi \circ T({\bf x}) \vert\det \grad_{\bf x}T({\bf x})\vert`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        return np.exp(self.log_pullback(x, pi, params_t, params_pi, idxs_slice, cache))
