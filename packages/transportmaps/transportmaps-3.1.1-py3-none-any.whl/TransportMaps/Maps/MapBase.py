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

from ..Misc import required_kwargs, counted, cached, cached_tuple
from ..ObjectBase import TMO
from ..DerivativesChecks import \
    fd_gradient_check, \
    action_hess_check

__all__ = ['Map']


class Map(TMO):
    r""" Abstract map :math:`T:\mathbb{R}^{d_x}\rightarrow\mathbb{R}^{d_y}`

    Args:
        dim_in (int): input dimension
        dim_out (int): output dimension
    """
    @required_kwargs('dim_in', 'dim_out')
    def __init__(self, **kwargs):
        r"""
        Kwargs:
          dim_in (int): input dimension :math:`d_x`
          dim_out (int): output dimension :math:`d_y`
        """
        super(Map, self).__init__()
        self._dim_in = kwargs['dim_in']
        self._dim_out = kwargs['dim_out']

    @property
    def dim_in(self):
        try:
            self._dim_in
        except AttributeError:
            # backward compatibility
            self._dim_in = vars(self)['dim_in']
            del vars(self)['dim_in']
        finally:
            return self._dim_in

    @dim_in.setter
    def dim_in(self, dim_in):
        self._dim_in = dim_in
        vars(self).pop('dim_in', None)

    @property
    def dim_out(self):
        try:
            self._dim_out
        except AttributeError:
            # backward compatibility
            self._dim_out = vars(self)['dim_out']
            del vars(self)['dim_out']
        finally:
            return self._dim_out

    @dim_out.setter
    def dim_out(self, dim_out):
        self._dim_out = dim_out
        vars(self).pop('dim_out', None)

    @property
    def dim(self):
        vars(self).pop('dim', None)
        if self.dim_in == self.dim_out:
            return self.dim_in
        else:
            return None
            
    def __call__(self, x):
        r"""
        Calls :func:`evaluate`.
        """
        return self.evaluate( x )

    def get_ncalls_tree(self, indent=""):
        out = super(Map, self).get_ncalls_tree(indent)
        return out

    def get_nevals_tree(self, indent=""):
        out = super(Map, self).get_nevals_tree(indent)
        return out

    def get_teval_tree(self, indent=""):
        out = super(Map, self).get_teval_tree(indent)
        return out

    def update_ncalls_tree(self, obj):
        super(Map, self).update_ncalls_tree( obj )

    def update_nevals_tree(self, obj):
        super(Map, self).update_nevals_tree( obj )

    def update_teval_tree(self, obj):
        super(Map, self).update_teval_tree( obj )

    def reset_counters(self):
        super(Map, self).reset_counters()
        
    @cached()
    @counted
    def evaluate(self, x, precomp=None, idxs_slice=slice(None), **kwargs):
        r""" [Abstract] Evaluate the map :math:`T` at the points :math:`{\bf x} \in \mathbb{R}^{m \times d_x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]) -- transformed points

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @cached()
    @counted
    def grad_x(self, x, precomp=None, idxs_slice=slice(None), **kwargs):
        r""" [Abstract] Evaluate the gradient :math:`\nabla_{\bf x}T` at the points :math:`{\bf x} \in \mathbb{R}^{m \times d_x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y,d_x`]) -- transformed points

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @cached()
    @counted
    def action_grad_x(self, x, dx, precomp=None, idxs_slice=slice(None), **kwargs):
        r""" [Abstract] Evaluate the action of the gradient :math:`\langle\nabla_{\bf x}T({\bf x}),\delta{\bf x}\rangle` at the points :math:`{\bf x} \in \mathbb{R}^{m \times d_x}` on the vector :math:`\delta{\bf x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x,...`]): vector :math:`\delta{\bf x}`
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y,...`]) -- transformed points

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @cached()
    @counted
    def action_adjoint_grad_x(self, x, dx, precomp=None, idxs_slice=slice(None), **kwargs):
        r""" [Abstract] Evaluate the action of the gradient :math:`\langle\delta{\bf x},\nabla_{\bf x}T({\bf x})\rangle` at the points :math:`{\bf x} \in \mathbb{R}^{m \times d_x}` on the vector :math:`\delta{\bf x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x,...`]): vector :math:`\delta{\bf x}`
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y,...`]) -- transformed points

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @cached_tuple(['evaluate','grad_x'])
    @counted
    def tuple_grad_x(self, x, precomp=None, idxs_slice=slice(None), **kwargs):
        r""" [Abstract] Evaluate the function and gradient.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`tuple`) -- function and gradient evaluation

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @cached_tuple(['evaluate','grad_x'])
    @counted
    def action_tuple_grad_x(self, x, dx, precomp=None, idxs_slice=slice(None), **kwargs):
        r""" [Abstract] Evaluate the function and action of the gradient.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x,...`]): vector :math:`\delta{\bf x}`
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`tuple`) -- function and action of the gradient evaluation

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @cached(caching=False)
    @counted
    def hess_x(self, x, precomp=None, idxs_slice=slice(None), **kwargs):
        r""" [Abstract] Evaluate the Hessian :math:`\nabla^2_{\bf x}T` at the points :math:`{\bf x} \in \mathbb{R}^{m \times d_x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y,d_x,d_x`]) -- transformed points

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @cached(caching=False)
    @counted
    def action_hess_x(self, x, dx, precomp=None, idxs_slice=slice(None), **kwargs):
        r""" [Abstract] Evaluate the action of the Hessian :math:`\langle\nabla^2_{\bf x}T,\delta{\bf x}\rangle` at the points :math:`{\bf x} \in \mathbb{R}^{m \times d_x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): direction
            on which to evaluate the Hessian
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y,d_x`]) -- transformed points

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @counted
    def inverse(self, x, precomp=None, idxs_slice=slice(None), **kwargs):
        r""" [Abstract] Evaluate the Moore-Penrose inverse map :math:`T^\dagger` at the points :math:`{\bf x} \in \mathbb{R}^{m \times d_x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]) -- transformed points

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @counted
    def grad_x_inverse(self, x, precomp=None, idxs_slice=slice(None), **kwargs):
        r""" [Abstract] Evaluate the gradient of the Moore-Penrose inverse :math:`\nabla_{\bf x}T^\dagger` at the points :math:`{\bf x} \in \mathbb{R}^{m \times d_x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y,d_x`]) -- transformed points

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @counted
    def tuple_grad_x_inverse(self, x, precomp=None, idxs_slice=slice(None), **kwargs):
        r""" [Abstract] Evaluate the Moore-Penrose inverse function and gradient.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`tuple`) -- function and gradient evaluation

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @counted
    def hess_x_inverse(self, x, precomp=None, idxs_slice=slice(None), **kwargs):
        r""" [Abstract] Evaluate the Hessian of the Moore-Penrose inverse :math:`\nabla^2_{\bf x}T^\dagger` at the points :math:`{\bf x} \in \mathbb{R}^{m \times d_x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y,d_x,d_x`]) -- transformed points

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @cached(caching=False)
    @counted
    def action_hess_x_inverse(self, x, dx, precomp=None, idxs_slice=slice(None), **kwargs):
        r""" [Abstract] Evaluate the action of the Hessian of the Moore-Penrose inverse :math:`\langle\nabla^2_{\bf x}T^\dagger,\delta{\bf x}\rangle` at the points :math:`{\bf x} \in \mathbb{R}^{m \times d_x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): direction
            on which to evaluate the Hessian
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y,d_x`]) -- transformed points

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")
    
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
                    self.evaluate, self.grad_x, x, fd_dx,
                    title='grad_x from evaluate', verbose=verbose)
            except NotImplementedError:
                has_grad = False

            try:
                success &= fd_gradient_check(
                    self.tuple_grad_x, None, x, fd_dx,
                    title='tuple_grad_x from evaluate', verbose=verbose)
            except NotImplementedError:
                print("not implemented")
                has_tuple_grad = False

            if has_grad or has_tuple_grad:
                gx = self.grad_x if has_grad else self.tuple_grad_x
                try:
                    success &= fd_gradient_check(
                        gx, self.hess_x, x, fd_dx,
                        title='hess_x from grad_x', verbose=verbose)
                except NotImplementedError:
                    has_hess = False

            if has_hess and v is not None:
                try:
                    success &= action_hess_check(
                        self.hess_x, self.action_hess_x, x, v,
                        title='action_hess_x from hess_x', verbose=verbose)
                except NotImplementedError:
                    pass

            elif (has_grad or has_tuple_grad) and v is not None:
                gx = self.grad_x if has_grad else self.tuple_grad_x
                try:
                    success &= action_hess_check(
                        gx, self.action_hess_x, x, v,
                        fd_dx=fd_dx,
                        title='action_hess_x from grad_x', verbose=verbose)
                except NotImplementedError:
                    pass
            
        else:
            raise NotImplementedError("Testing method not implemented")
        return success
