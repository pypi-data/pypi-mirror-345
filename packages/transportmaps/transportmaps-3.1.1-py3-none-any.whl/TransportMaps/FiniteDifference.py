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
    'check_grad_a',
    'check_hess_a_from_grad_a',
    'check_action_hess_a_from_grad_a',
    'check_grad_x',
    'check_hess_x_from_grad_x',
]

import numpy as np
import time

from .Misc import deprecate
from .DerivativesChecks import fd


@deprecate('check_grad_a', '3.0',
           'Use TransportMaps.DerivativeChecks.fd_gradient_check instead')
def check_grad_a(f, grad_f, x, dx, params={}, newdim=None, title='', verbose=True):
    app_start = time.time()
    app = fd(f, x, dx, params=params, newdim=newdim)
    app_stop = time.time()
    app_time = app_stop-app_start
    exa_start = time.time()
    exa = grad_f(x, **params)
    exa_stop = time.time()
    exa_time = exa_stop - exa_start
    err = np.abs(app-exa).flatten()
    idxmer = np.argmax(err)
    maxerr = err[idxmer]
    if verbose:
        print("Check grad %s - Max err: %e - FD time: %.4f - Analytic time: %.4f" % (
            title,maxerr,app_time,exa_time))
    return np.allclose(exa, app, rtol=100*dx, atol=10*dx)

@deprecate('check_hess_a_from_grad_a', '3.0',
           'Use TransportMaps.DerivativeChecks.fd_gradient_check instead')
def check_hess_a_from_grad_a(grad_f, hess_f, x, dx, params={}, title='', verbose=True):
    exa_start = time.time()
    exa = hess_f(x, **params)
    exa_stop = time.time()
    exa_time = exa_stop - exa_start
    app_start = time.time()
    app = fd(grad_f, x, dx, params=params)
    app_stop = time.time()
    app_time = app_stop-app_start
    err = np.abs(app-exa).flatten()
    maxerr = np.max(err)
    if verbose:
        print("Check hess %s - Max err: %e - FD time: %.4f - Analytic time: %.4f" % (
            title,maxerr, app_time,exa_time))
    return np.allclose(exa, app, rtol=100*dx, atol=10*dx)

@deprecate('check_action_hess_a_from_grad_a', '3.0',
           'Use TransportMaps.DerivativeChecks.action_hess_check instead')
def check_action_hess_a_from_grad_a(grad_f, action_hess_f, x, dx, v, params={}, title='', verbose=True):
    exa_start = time.time()
    exa = action_hess_f(x, v, **params)
    exa_stop = time.time()
    exa_time = exa_stop - exa_start
    app_start = time.time()
    app = fd(grad_f, x, dx, params)
    app = np.dot(app, v)
    app_stop = time.time()
    app_time = app_stop-app_start
    err = np.abs(app-exa).flatten()
    maxerr = np.max(err)
    if verbose:
        print("Check hess %s - Max err: %e - FD time: %.4f - Analytic time: %.4f" % (
            title,maxerr,app_time,exa_time))
    return np.allclose(exa, app, rtol=100*dx, atol=10*dx)

@deprecate('check_grad_x', '3.0',
           'Use TransportMaps.DerivativeChecks.fd_gradient_check instead')
def check_grad_x(f, grad_f, x, dx, params={}, title='', verbose=True):
    if verbose:
        print("Checking %s ..." % title, end='')
    try:
        app_start = time.time()
        app = fd(f,x,dx,params)
        app_stop = time.time()
        app_time = app_stop-app_start
        exa_start = time.time()
        exa = grad_f(x, **params)
        exa_stop = time.time()
        exa_time = exa_stop - exa_start
    except NotImplementedError:
        print("NOT IMPLEMENTED")
        return True
    else:
        err = np.abs(app-exa).flatten()
        maxerr = np.max(err)
        success = np.allclose(exa, app, rtol=dx, atol=dx)
        if verbose:
            if success:
                print("ok (FD time: %.4f - Analytic time: %.4f)" % (
                    app_time, exa_time))
            else:
                print("FAIL (max err: %e)" % maxerr)
        return success

@deprecate('check_hess_x_from_grad_x', '3.0',
           'Use TransportMaps.DerivativeChecks.fd_gradient_check instead')
def check_hess_x_from_grad_x(grad_f, hess_f, x, dx, params={}, title='', verbose=True):
    exa_start = time.time()
    exa = hess_f(x, **params)
    exa_stop = time.time()
    exa_time = exa_stop - exa_start
    app_start = time.time()
    app = fd(grad_f, x, dx, params)
    app_stop = time.time()
    app_time = app_stop-app_start
    err = np.abs(app-exa).flatten()
    maxerr = np.max(err)
    if verbose:
        print("Check hess %s - Max err: %e - FD time: %.4f - Analytic time: %.4f" % (title,maxerr,
                                                                                     app_time,exa_time))
    # return np.allclose(exa, app, rtol=100*dx, atol=10*dx)
    return np.allclose(exa, app, rtol=dx, atol=dx)

@deprecate('grad_a_fd', '3.0',
           'Use TransportMaps.DerivativeChecks.fd instead')
def grad_a_fd(f, x, dx, params={}, end=True):
    tmp = f(x, **params)
    if isinstance(tmp, float): extradims = 0
    else: extradims = tmp.ndim
    if end:
        out = np.zeros(tmp.shape + (len(x),))
    else:
        out = np.zeros(tmp.shape[:1] + (len(x),) + tmp.shape[1:])
    idxbase = tuple( [slice(None)]* extradims )
    for i in range(len(x)):
        xc_minus = x.copy()
        xc_plus = x.copy()
        xc_minus[i] -= dx/2.
        xc_plus[i] += dx/2.
        fm = f(xc_minus, **params)
        fp = f(xc_plus, **params)
        if end:
            out[idxbase + (i,)] = (fp-fm)/dx
        else:
            idx = (idxbase[:1] + (i,) + idxbase[1:])
            out[idx] = (fp-fm)/dx
    return out

@deprecate('grad_x_fd', '3.0',
           'Use TransportMaps.DerivativeChecks.fd instead')
def grad_x_fd(f, x, dx, params={}):
    r""" Compute :math:`\nabla_{\bf x} f({\bf x})` of :math:`f:\mathbb{R}^d\rightarrow\mathbb{R}`
    """
    tmp = f(x, **params)
    if isinstance(tmp, float): extradims = 0
    else: extradims = tmp.ndim
    nsamp = x.shape[0]
    dim = x.shape[1]
    out = np.zeros(tmp.shape + (dim,))
    idxbase = tuple( [slice(None)]* extradims )
    for i in range(dim):
        xcm = x.copy()
        xcp = x.copy()
        xcm[:,i] -= dx/2.
        xcp[:,i] += dx/2.
        fm = f(xcm, **params)
        fp = f(xcp, **params)
        out[idxbase + (i,)] = (fp-fm)/dx
    return out
