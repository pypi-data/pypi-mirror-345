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

from TransportMaps.DerivativesChecks import \
    fd_gradient_check, \
    action_hess_check
from TransportMaps.Misc import \
    counted, cached, cached_tuple
from TransportMaps.ObjectBase import TMO

__all__ = [
    'Distribution'
]


class Distribution(TMO):
    r""" Abstract distribution :math:`\nu_\pi`.
    """
    def __init__(self, dim):
        r"""
        Args:
          dim (int): input dimension of the distribution
        """
        super(Distribution, self).__init__()
        self.dim = dim

    @property
    def dim(self):
        return self._dim

    @dim.setter
    def dim(self, dim):
        self._dim = dim

    def rvs(self, m, *args, **kwargs):
        r""" [Abstract] Generate :math:`m` samples from the distribution.

        Args:
          m (int): number of samples to generate

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- :math:`m`
             :math:`d`-dimensional samples

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    def quadrature(self, qtype, qparams, mass, *args, **kwargs):
        r""" [Abstract] Generate quadrature points and weights.

        Args:
          qtype (int): quadrature type number. The different types are defined in
            the associated sub-classes.
          qparams (object): inputs necessary to the generation of the selected
            quadrature
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
    def pdf(self, x, params=None, idxs_slice=slice(None,None,None), **kwargs):
        r""" Evaluate :math:`\pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\pi`
            at the ``x`` points.

        Raises:
          NotImplementedError: the method calls :fun:`log_pdf`
        """
        return np.exp( self.log_pdf(x, params=params, idxs_slice=idxs_slice) )

    @cached()
    @counted
    def log_pdf(self, x, params=None, idxs_slice=slice(None,None,None), **kwargs):
        r""" [Abstract] Evaluate :math:`\log \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
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

    @cached()
    @counted
    def grad_x_log_pdf(self, x, params=None, idxs_slice=slice(None,None,None),
                       **kwargs):
        r""" [Abstract] Evaluate :math:`\nabla_{\bf x} \log \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
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
    def tuple_grad_x_log_pdf(self, x, params=None, idxs_slice=slice(None,None,None),
                             cache=None, **kwargs):
        r""" [Abstract] Compute the tuple :math:`\left(\log \pi({\bf x}), \nabla_{\bf x} \log \pi({\bf x})\right)`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`tuple`) -- containing
            :math:`\left(\log \pi({\bf x}), \nabla_{\bf x} \log \pi({\bf x})\right)`

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    @cached(caching=False)
    @counted
    def hess_x_log_pdf(self, x, params=None, idxs_slice=slice(None,None,None),
                       *args, **kwargs):
        r""" [Abstract] Evaluate :math:`\nabla^2_{\bf x} \log \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
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

    @cached(caching=False)
    @counted
    def action_hess_x_log_pdf(self, x, dx, params=None, idxs_slice=slice(None,None,None),
                              **kwargs):
        r""" [Abstract] Evaluate :math:`\langle \nabla^2_{\bf x} \log \pi({\bf x}), \delta{\bf x}\rangle`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): direction
            on which to evaluate the Hessian
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\langle \nabla^2_{\bf x} \log \pi({\bf x}), \delta{\bf x}\rangle`.

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    def mean_log_pdf(self):
        r""" [Abstract] Evaluate :math:`\mathbb{E}_{\pi}[\log \pi]`

        Returns:
          (float) -- :math:`\mathbb{E}_{\pi}[\log \pi]`

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    def test_gradients(
            self,
            x,
            v=None,
            method='fd',
            fd_dx=1e-4,
            verbose=True,
    ):
        r""" Automatically tests all the gradients implemented.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          v (:class:`ndarray<numpy.ndarray>` [:math:`d`]): direction
            on which to evaluate the action of the Hessian
          method (str): method to use for testing. Default ``fd`` is finite difference
          fd_dx (float): finite difference perturbation

        Returns:
          :class:`bool` -- whether all the implemented gradients pass the test.
        """
        success = True

        has_grad = True
        has_tuple_grad = True
        has_hess = True

        if method == 'fd':
            try:
                success &= fd_gradient_check(
                    self.log_pdf, self.grad_x_log_pdf, x, fd_dx,
                    title='grad_x_log_pdf from evaluate', verbose=verbose)
            except NotImplementedError:
                print("not implemented")
                has_grad = False

            try:
                success &= fd_gradient_check(
                    self.tuple_grad_x_log_pdf, None, x, fd_dx,
                    title='tuple_grad_x_log_pdf from evaluate', verbose=verbose)
            except NotImplementedError:
                print("not implemented")
                has_tuple_grad = False
                
            if has_grad or has_tuple_grad:
                gx = self.grad_x_log_pdf if has_grad else self.tuple_grad_x_log_pdf
                try:
                    success &= fd_gradient_check(
                        gx, self.hess_x_log_pdf, x, fd_dx,
                        title='hess_x_log_pdf from grad_x_log_pdf', verbose=verbose)
                except NotImplementedError:
                    print("not implemented")
                    has_hess = False

            if has_hess and v is not None:
                try:
                    success &= action_hess_check(
                        self.hess_x_log_pdf, self.action_hess_x_log_pdf, x, v,
                        title='action_hess_x_log_pdf from hess_x_log_pdf', verbose=verbose)
                except NotImplementedError:
                    print("not implemented")
                    pass

            elif (has_grad or has_tuple_grad) and v is not None:
                gx = self.grad_x_log_pdf if has_grad else self.tuple_grad_x_log_pdf
                try:
                    success &= action_hess_check(
                        gx, self.action_hess_x_log_pdf, x, v,
                        fd_dx=fd_dx,
                        title='action_hess_x_log_pdf from grad_x_log_pdf', verbose=verbose)
                except NotImplementedError:
                    print("not implemented")
                    pass
            
        else:
            raise NotImplementedError("Testing method not implemented")
        return success
                        
