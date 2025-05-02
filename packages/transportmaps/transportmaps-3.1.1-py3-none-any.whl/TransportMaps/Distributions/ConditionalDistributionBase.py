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

from TransportMaps.Misc import counted, cached_tuple

from .DistributionBase import Distribution

__all__ = [
    'ConditionalDistribution'
]


class ConditionalDistribution(Distribution):
    r""" Abstract distribution :math:`\pi_{{\bf X}\vert{\bf Y}}`.

    Args:
      dim (int): input dimension of the distribution
      dim_y (int): dimension of the conditioning variables
    """
    def __init__(self, dim, dim_y):
        super(ConditionalDistribution, self).__init__(dim)
        self._dim_y = dim_y

    @property
    def dim_y(self):
        return self._dim_y

    @dim_y.setter
    def dim_y(self, dim_y):
        self._dim_y = dim_y
    
        
    def rvs(self, m, y, *args, **kwargs):
        r""" [Abstract] Generate :math:`m` samples from the distribution.

        Args:
          m (int): number of samples to generate
          y (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- :math:`m`
             :math:`d`-dimensional samples

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    def quadrature(self, qtype, qparams, y, mass, *args, **kwargs):
        r""" [Abstract] Generate quadrature points and weights.

        Args:
          qtype (int): quadrature type number. The different types are defined in
            the associated sub-classes.
          qparams (object): inputs necessary to the generation of the selected
            quadrature
          y (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          mass (float): total mass of the quadrature (1 for probability measures)

        Return:
          (:class:`tuple` (:class:`ndarray<numpy.ndarray>` [:math:`m,d`],
            :class:`ndarray<numpy.ndarray>` [:math:`m`])) -- list of quadrature
            points and weights

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    @counted
    def pdf(self, x, y, params=None, idxs_slice=slice(None,None,None), cache=None):
        r""" Evaluate :math:`\pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dist): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\pi`
            at the ``x`` points.

        Raises:
          NotImplementedError: the method calls :fun:`log_pdf`
        """
        return np.exp(
            self.log_pdf(x, y, params=params, idxs_slice=idxs_slice, cache=cache) )

    def log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None), **kwargs):
        r""" [Abstract] Evaluate :math:`\log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\log\pi`
            at the ``x`` points.

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    def grad_x_log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None),
                       **kwargs):
        r""" [Abstract] Evaluate :math:`\nabla_{\bf x,y} \log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\nabla_x\log\pi` at the ``x`` points.

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    @cached_tuple(['log_pdf','grad_x_log_pdf'])
    @counted
    def tuple_grad_x_log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None),
                             cache=None, **kwargs):
        r""" Evaluate :math:`\left(\log \pi({\bf x}\vert{\bf y}), \nabla_{\bf x,y} \log \pi({\bf x}\vert{\bf y})\right)`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dist): cache

        Returns:
          (:class:`tuple`) -- containing
            :math:`\left(\log \pi({\bf x}\vert{\bf y}), \nabla_{\bf x,y} \log \pi({\bf x}\vert{\bf y})\right)`

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        return (self.log_pdf(
            x, y, params=params, idxs_slice=idxs_slice, cache=cache),
                self.grad_x_log_pdf(
                    x, y, params=params, idxs_slice=idxs_slice, cache=cache))

    def hess_x_log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None),
                       **kwargs):
        r""" [Abstract] Evaluate :math:`\nabla^2_{\bf x,y} \log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) -- values of
            :math:`\nabla^2_x\log\pi` at the ``x`` points.

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    def action_hess_x_log_pdf(self, x, y, dx, dy, params=None,
                              idxs_slice=slice(None,None,None),
                              **kwargs):
        r""" [Abstract] Evaluate :math:`\langle\nabla^2_{\bf x,y} \log \pi({\bf x}\vert{\bf y}), [\delta{\bf x},\delta{\bf y}]\rangle`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): ``x`` direction
            on which to evaluate the Hessian
          dy (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): ``y`` direction
            on which to evaluate the Hessian
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) -- values of
            :math:`\nabla^2_x\log\pi` at the ``x`` points.

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    def mean_log_pdf(self, y):
        r""" [Abstract] Evaluate :math:`\mathbb{E}_{\pi}[\log \pi]`

        Args:
          y (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
        
        Returns:
          (float) -- :math:`\mathbb{E}_{\pi}[\log \pi]`

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")
