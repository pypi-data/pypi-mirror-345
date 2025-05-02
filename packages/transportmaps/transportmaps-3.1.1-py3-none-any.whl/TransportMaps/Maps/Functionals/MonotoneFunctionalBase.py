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
import scipy.optimize as sciopt

from TransportMaps.Misc import \
    counted

from .FunctionalBase import Functional

__all__ = [
    'MonotoneFunctional'
]

nax = np.newaxis

class MonotoneFunctional(Functional):
    r""" Abstract class for the functional :math:`f \approx f_{\bf a} = \sum_{{\bf i} \in \mathcal{I}} {\bf a}_{\bf i} \Phi_{\bf i}` assumed to be monotonic in :math:`x_d`

    The class defines a series of methods (like the inverse) specific to monotone functions.
    """

    def xd_misfit(self, x, args):
        r""" Compute :math:`f_{\bf a}({\bf x}) - y`

        Given the fixed coordinates :math:`{\bf x}_{1:d-1}`, the value
        :math:`y`, and the last coordinate :math:`{\bf x}_d`, compute:

        .. math::

           f_{\bf a}({\bf x}_{1:d-1},{\bf x}_d) - y

        Args:
          x (float): evaluation point :math:`{\bf x}_d`
          args (tuple): containing :math:`({\bc x}_{1:d-1},y)`

        Returns:
          (:class:`float<float>`) -- misfit.
        """
        (xkm1,y) = args
        x = np.hstack( (xkm1,x) )[nax,:]
        return self.evaluate(x) - y

    def partial_xd_misfit(self, x, args):
        r""" Compute :math:`\partial_{x_d} f_{\bf a}({\bf x}) - y = \partial_{x_d} f_{\bf a}({\bf x})`

        Given the fixed coordinates :math:`{\bf x}_{1:d-1}`, the value
        :math:`y`, and the last coordinate :math:`{\bf x}_d`, compute:

        .. math::

           \partial f_{\bf a}({\bf x}_{1:d-1},{\bf x}_d)

        Args:
          x (float): evaluation point :math:`{\bf x}_d`
          args (tuple): containing :math:`({\bc x}_{1:d-1},y)`

        Returns:
          (:class:`float<float>`) -- misfit derivative.
        """
        (xkm1,y) = args
        x = np.hstack( (xkm1,x) )[nax,:]
        return self.partial_xd(x)

    @counted
    def inverse(self, xmd, y, xtol=1e-12, rtol=1e-15):
        r""" Compute :math:`{\bf x}_d` s.t. :math:`f_{\bf a}({\bf x}_{1:d-1},{\bf x}_d) - y = 0`.

        Given the fixed coordinates :math:`{\bf x}_{1:d-1}`, the value
        :math:`y`, find the last coordinate :math:`{\bf x}_d` such that:

        .. math::

           f_{\bf a}({\bf x}_{1:d-1},{\bf x}_d) - y = 0

        We will define this value the inverse of :math:`f_{\bf a}({\bf x})` and
        denote it by :math:`f_{\bf a}^{-1}({\bf x}_{1:d-1})(y)`.

        Args:
          xmd (:class:`ndarray<numpy.ndarray>` [:math:`d-1`]): fixed coordinates
            :math:`{\bf x}_{1:d-1}`
          y (float): value :math:`y`
          xtol (float): absolute tolerance
          rtol (float): relative tolerance

        Returns:
          (:class:`float<float>`) -- inverse value :math:`x`.
        """
        if y == -np.inf:
            return -np.inf
        elif y == np.inf:
            return np.inf
        args = (xmd,y)
        fail = True
        ntry = 0
        maxtry = 10
        mul = 1.
        while fail and ntry < maxtry:
            ntry += 1
            try:
                # out = sciopt.bisect( self.xd_misfit, a=-10.*mul, b=10.*mul,
                #                      args=(args,), xtol=xtol, rtol=rtol, maxiter=100 )
                out = sciopt.brentq( self.xd_misfit, a=-10.*mul, b=10.*mul,
                                     args=(args,), xtol=xtol, rtol=rtol, maxiter=100 )
                fail = False
            except ValueError:
                mul *= 10.
        if ntry == maxtry:
            raise RuntimeError(
                "Failed to converge: the interval does not contain the root.")
        else:
            return out

    @counted
    def partial_xd_inverse(self, xmd, y):
        r""" Compute :math:`\partial_y f_{\bf a}^{-1}({\bf x}_{1:d-1})(y)`.

        Args:
          xmd (:class:`ndarray<numpy.ndarray>` [:math:`d-1`]): fixed coordinates
            :math:`{\bf x}_{1:d-1}`
          y (float): value :math:`y`

        Returns:
          (:class:`float<float>`) -- derivative of the inverse value :math:`x`.
        """
        x = self.inverse(xmd, y)
        xeval = np.hstack((xmd, x))
        return 1. / self.partial_xd(xeval)


