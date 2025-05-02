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
# Author: Transport Map Team
# Website: transportmaps.mit.edu
# Support: transportmaps.mit.edu/qa/
#

__all__ = [
    'fd',
    'fd_gradient_check',
    'action_hess_check',
]

import numpy as np
import time


def fd(
        f,
        x,
        dx,
        params=None,
        fshape=None,
        newdim=None,
):
    r""" Compute finite difference of ``f``

    The function ``f`` may be any scalar, vector, matrix, tensor etc. valued function
    :math:`f:\mathbb{R}^d\rightarrow \mathbb{R}^{n_1 \times \cdot \times n_k}`.
    If the function :math:`f` has :math:`k` output dimensions, the
    result of :func:`fd` will be of :math:`k+1` dimensions, where the extra dimension
    will be appended at the position prescribed by ``newdim``.

    Args:
      f (:class:`function`): the function :math:`f`
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.
        If the function is not vectorized then ``x`` should be 
        of dimension :math:`d`.
      dx (float): finite difference perturbation
      params (dict): dictionary of parameters
      fshape (tuple): expected shape of the output of :math:`f`. 
        It should correspond to :math:`n_1, \ldots, n_k`.
        If not provided, then it will be inferred by calling ``f``.
      newdim (int): dimension along which to add the gradient.

    Return:
      :class:`ndarray<numpy.ndarray>` [:math:`m,n_1,\ldots,n_{k+1}`] -- gradient of 
        :math:`f`, where one of the :math:`n_i` is :math:`d`.
    """
    if not params:
        params = {}

    # Figure out the dimension of the output
    if not fshape:
        tmp = f(x, **params)
        fshape = tmp.shape

    # Check whether function is vectorized by inspection of x
    vectorized = (x.ndim == 2)

    # Figure out the dimension d
    d = x.shape[1] if vectorized else x.shape[0]
    
    # Checking that newdim is at most contiguous
    if not newdim:
        newdim = len(fshape)
    elif newdim < 0 or newdim > len(fshape):
        raise ValueError(
            "The condition 0 <= newdim <= k must hold.")

    # Prepare output array
    out = np.zeros(
        fshape[:newdim] + (d,) + fshape[newdim:])

    # Prepare output index
    idxbase = tuple( [slice(None)]* len(fshape) )

    # Compute finite difference
    for i in range(d):
        xc_minus = x.copy()
        xc_plus = x.copy()
        if vectorized:
            xc_minus[:,i] -= dx/2.
            xc_plus[:,i] += dx/2.
        else:
            xc_minus[i] -= dx/2.
            xc_plus[i] += dx/2.
        fm = f(xc_minus, **params)
        fp = f(xc_plus, **params)
        idx = (idxbase[:newdim] + (i,) + idxbase[newdim:])
        out[idx] = (fp-fm)/dx
    return out

def fd_gradient_check(
        f,
        gf,
        x,
        dx,
        rtol=None,
        atol=None,
        params=None,
        fshape=None,
        newdim=None,
        verbose=True,
        title='',
):
    r""" Check the gradient ``grad_f`` using finite difference approximation of ``f``.

    Args:
      f (:class:`function`): the function :math:`f` or :math:`(f, \nabla f)`
      gf (:class:`function`): the funtion :math:`\nabla f`. If ``None``, then
        it is assumed that ``f`` returns the tuple :math:`(f,\nabla f)`.
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.
        If the function is not vectorized then ``x`` should be 
        of dimension :math:`d`.
      dx (float): finite difference perturbation
      rtol (float): relative tolerance (default is ``dx``)
      atol (float): absolute tolerance (default is ``dx``)
      params (dict): dictionary of parameters
      fshape (tuple): expected shape of the output of :math:`f`. 
        It should correspond to :math:`n_1, \ldots, n_k`.
        If not provided, then it will be inferred by calling ``f``.
      newdim (int): dimension along which to add the gradient.
      verbose (bool): whether to output the result of the test
      title (str): if ``verbose==True`` it is used to identify the gradient in the outputs

    Returns:
      :class:`bool` -- whether the gradient and its finite difference approximation
        are within the specified error tolerances.
    """
    if not rtol:
        rtol = dx
    if not atol:
        atol = dx
    if not params:
        params = {}
    
    if verbose:
        print("Checking %s ... " % title, end='')

    # Figuring out whether the function f returns the tuple (f,\nabla f)
    tmp = f(x, **params)
    if isinstance(tmp, tuple):
        if gf is None: # Testing for the gradient
            ftuple = f
            def f(x, **params):
                return ftuple(x, **params)[0]
            def gf(x, **params):
                return ftuple(x, **params)[1]
        else: # Testing for the Hessian
            ftuple = f
            def f(x, **params):
                return ftuple(x, **params)[1]
        
    # Compute analytic gradient
    exa_start = time.time()
    exa = gf(x, **params)
    exa_stop = time.time()
    exa_time = exa_stop - exa_start
    # Compute the finite difference approximation
    app_start = time.time()
    app = fd(f, x, dx, params=params, fshape=fshape, newdim=newdim)
    app_stop = time.time()
    app_time = app_stop-app_start

    # Compute and evaluate error
    err = np.abs(app-exa).flatten()
    maxerr = np.max(err)
    success = np.allclose(exa, app, rtol=rtol, atol=atol)
    if verbose:
        if success:
            print("ok (Approximation time: %.4f - Analytic time: %.4f)" % (
                app_time, exa_time))
        else:
            print("FAIL (max err: %e)" % maxerr)
    return success

def action_hess_check(
        ghf,
        ahf,
        x,
        v,
        fd_dx=None,
        rtol=None,
        atol=None,
        params=None,
        fshape=None,
        newdim=None,
        verbose=True,
        title='',
):
    r""" Check the correctness of the action :math:`\langle \nabla^2 f, v \rangle`.

    If the perturbation ``fd_dx`` is provided, then ``ghf`` is assumed to be 
    the gradient :math:`\nabla f` and the Hessian :math:`\nabla^2 f` is 
    approximated using finite difference. Otherwise ``ghf`` is considered to 
    be the Hessian :math:`\nabla^2 f` itself.

    Args:
      ghf (:class:`function`): the function :math:`\nabla^2 f` or
        :math:`\nabla f` of :math:`(f, \nabla f)`. In the latter two cases the
        Hessian is approximated with finite difference and ``fd_dx`` must be provided
      ahf (:class:`function`): the funtion :math:`\langle \nabla^ f, v \rangle`
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.
        If the function is not vectorized then ``x`` should be 
        of dimension :math:`d`.
      v (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): vector :math:`v`.
        If the action of the Hessian is not vectorized with respect to
        the perturbation, then ``v`` should be of dimension :maht:`d`
      fd_dx (float): finite difference perturbation
      rtol (float): relative tolerance (default is ``dx``)
      atol (float): absolute tolerance (default is ``dx``)
      params (dict): dictionary of parameters
      fshape (tuple): expected shape of the output of :math:`f`. 
        It should correspond to :math:`n_1, \ldots, n_k`.
        If not provided, then it will be inferred by calling ``f``.
      newdim (int): dimension along which to add the gradient.
      verbose (bool): whether to output the result of the test
      title (str): if ``verbose==True`` it is used to identify the gradient in the outputs

    Returns:
      :class:`bool` -- whether the action of the Hessian
        is within the specified error tolerances.
    """
    if not rtol:
        rtol = fd_dx if fd_dx else 1e-13
    if not atol:
        atol = fd_dx if fd_dx else 1e-13
    if not params:
        params = {}
    
    if verbose:
        print("Checking %s ... " % title, end='')
        
    # Compute analytic action of the Hessian
    exa_start = time.time()
    exa = ahf(x, v, **params)
    exa_stop = time.time()
    exa_time = exa_stop - exa_start

    # Compute the action of the Hessian
    app_start = time.time()
    if not fd_dx:
        # Compute the Hessian using ghf
        h = ghf(x, **params)
    else:
        # Figure out whether ghf returns \nabla f or the tuple (f, \nabla f)
        tmp = ghf(x, **params)
        if isinstance(tmp, tuple):
            ghftuple = ghf
            def ghf(x, **params):
                return ghftuple(x, **params)[1]
        # Compute the Hessian using finite difference
        h = fd(ghf, x, fd_dx, params=params, fshape=fshape, newdim=newdim)
    # Compute inner product
    if v.ndim == 2:
        app = np.einsum('...i,...i->...', h, v)
    else:
        app = np.einsum('...i,i->...', h, v)
    app_stop = time.time()
    app_time = app_stop - app_start
    
    # Compute and evaluate error
    err = np.abs(app-exa).flatten()
    maxerr = np.max(err)
    success = np.allclose(exa, app, rtol=rtol, atol=atol)
    if verbose:
        if success:
            print("ok (Approximation time: %.4f - Analytic time: %.4f)" % (
                app_time, exa_time))
        else:
            print("FAIL (max err: %e)" % maxerr)
    return success
