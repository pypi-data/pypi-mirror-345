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
import scipy.optimize as sciopt

from .Misc import logger


__all__ = [
    # Maximum likelihood
    'maximum_likelihood'
]

nax = np.newaxis


def maximum_likelihood(logL, params=None, x0=None, tol=1e-5, ders=2, fungrad=False):
    r""" Compute the maximum likelihood of the log-likelihood :math:`\log\pi({\bf y}\vert{\bf x})`.

    Args:
      logL (:class:`LogLikelihood`): log-likelihood :math:`\log\pi({\bf y}\vert{\bf x})`
      params (dict): parameters for the log-likelihood :math:`\log\pi({\bf y}\vert{\bf x})`
      tol (float): tolerance to be used to solve the maximization problem
      ders (int): order of derivatives available for the solution of the
        optimization problem. 0 -> derivative free, 1 -> gradient, 2 -> hessian
      fungrad (bool): whether the distributions :math:`\pi_1,\pi_2` provide the method
        :func:`Distribution.tuple_grad_x_log_pdf` computing the evaluation and the
        gradient in one step. This is used only for ``ders==1``
    

    Returns:
      (:class:`ndarray<numpy.ndarray>`) -- Maximum likelihood estimator
    """
    # Minimize - logL
    if params is None:
        params = {}
    params['nobj'] = 0
    params['gx_nobj'] = 0
    params['hx_nobj'] = 0
    def objective(x, params):
        params['nobj'] += 1
        out = - logL.evaluate(x[nax,:], params)[0]
        logger.debug("Max-lkl Obj. Eval. %d - f val. = %.10e" % (params['nobj'], out))
        return out
    def dx_objective(x, params):
        params['gx_nobj'] += 1
        out = - logL.grad_x(x[nax,:], params)[0,:]
        logger.debug(
            "Max-lkl Grad. Obj. Eval. %d " % params['nobj'] + \
            "- ||grad f|| = %.10e" % npla.norm(out))
        return out
    def tuple_dx_objective(x, params):
        params['nobj'] += 1
        params['gx_nobj'] += 1
        ev, gx = logL.tuple_grad_x(x[nax,:], params)
        ev = -ev[0]
        gx = -gx[0,:]
        logger.debug("Max-lkl Obj. Eval. %d - f val. = %.10e" % (params['nobj'], ev))
        logger.debug(
            "Max-lkl Grad. Obj. Eval. %d " % params['nobj'] + \
            "- ||grad f|| = %.10e" % npla.norm(gx))
        return ev, gx
    def dx2_objective(x, params):
        params['hx_nobj'] += 1
        out = - logL.hess_x(x[nax,:], params)[0,:,:]
        logger.debug(
            "Max-lkl Hess. Obj. Eval. %d " % params['hx_nobj'])
        return out
    # Solve
    if x0 is None:
        x0 = np.zeros(logL.dim)
    options = {'maxiter': 10000,
               'disp': False}
    if ders == 0:
        res = sciopt.minimize(objective, args=params,
                              x0=x0,
                              method='BFGS',
                              tol=tol,
                              options=options)
    elif ders == 1:
        if not fungrad:
            res = sciopt.minimize(objective, args=params,
                                  x0=x0,
                                  jac=dx_objective,
                                  method='BFGS',
                                  tol=tol,
                                  options=options)
        else:
            res = sciopt.minimize(tuple_dx_objective, args=params,
                                  x0=x0,
                                  jac=True,
                                  method='BFGS',
                                  tol=tol,
                                  options=options)
    elif ders == 2:
        res = sciopt.minimize(objective, args=params,
                              x0=x0,
                              jac=dx_objective,
                              hess=dx2_objective,
                              method='newton-cg',
                              tol=tol,
                              options=options)
    else:
        raise ValueError("ders parameter not valid. Chose between 0,1,2.")
    # Log
    if res['success']:
        logger.info("Optimization terminated successfully")
    else:
        logger.info("Optimization failed.")
        logger.info("Message: %s" % res['message'])
    logger.info("  Function value:          %6f" % res['fun'])
    if ders >= 1:
        logger.info("  Norm of the Jacobian:    %6f" % npla.norm(res['jac']))
    logger.info("  Number of iterations:    %6d" % res['nit'])
    logger.info("  N. function evaluations: %6d" % res['nfev'])
    if ders >= 1:
        logger.info("  N. Jacobian evaluations: %6d" % res['njev'])
    if ders >= 2:
        logger.info("  N. Hessian evaluations:  %6d" % res['nhev'])
    # Set MAP point
    return res['x']
