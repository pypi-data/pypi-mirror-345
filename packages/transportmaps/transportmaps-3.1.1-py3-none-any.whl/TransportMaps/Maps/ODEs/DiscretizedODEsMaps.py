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

from TransportMaps.Maps import Map
from TransportMaps.Misc import counted

__all__ = [
    'DiscretizedAutonomousODEsMap',
    'AutonomousForwardEulerMap',
]

class DiscretizedAutonomousODEsMap( Map ):
    r""" Defines the map of discretized system of autonomous ODEs.

    Evaluates the map

    .. math::

       {\bf u}_n \mapsto {\bf u}_{n+1}

    that takes the state :math:`{\bf u}_n` at time :math:`t`
    into the state :math:`{\bf u}_{n+1}` at time :math:`t+\Delta t`,
    thorugh the discretization of the ODE

    .. math::

       \dot{\bf u} = f({\bf u}) \;.

    .. document private functions
    .. automethod:: __init__
    """
    def __init__(
            self,
            dt,
            rhs,
    ):
        r"""
        Args:
          dt (float): time step :math:`\Delta t`
          rhs (:class:`Map<TransportMaps.Maps.Map>`): the
            :math:`d` dimensional map :math:`f`.
        """
        self._dt = dt
        self._rhs = rhs
        super(DiscretizedAutonomousODEsMap, self).__init__(
            dim_in  = self._rhs.dim,
            dim_out = self._rhs.dim)

    @property
    def dt(self):
        return self._dt

    @property
    def rhs(self):
        return self._rhs

    @counted
    def evaluate(
            self,
            u,
            *args,
            **kwargs
    ):
        raise NotImplementedError("To be implemented in sub-classes.")

    @counted
    def grad_x(
            self,
            u,
            *args,
            **kwargs
    ):
        raise NotImplementedError("To be implemented in sub-classes.")

    @counted
    def tuple_grad_x(
            self,
            u,
            *args,
            **kwargs
    ):
        raise NotImplementedError("To be implemented in sub-classes.")

    @counted
    def hess_x(
            self,
            u,
            *args,
            **kwargs
    ):
        raise NotImplementedError("To be implemented in sub-classes.")

    @counted
    def action_hess_x(
            self,
            u,
            du,
            *args,
            **kwargs
    ):
        raise NotImplementedError("To be implemented in sub-classes.")


class AutonomousForwardEulerMap( DiscretizedAutonomousODEsMap ):
    r""" Defines the map of a forward Euler discretized system of autonomous ODEs.

    Evaluates the Euler step:

    .. math::

       {\bf u}_{n+1} = {\bf u}_n + \Delta t \cdot f({\bf u}_n)

    where :math:`f:\mathbb{R}^d \rightarrow \mathbb{R}^d`
    is the right hand side of the ODE system.

    .. document private functions
    .. automethod:: __init__
    """
    def __init__(
            self,
            dt,
            rhs,
    ):
        r"""
        Args:
          dt (float): time step :math:`\Delta t`
          rhs (:class:`Map<TransportMaps.Maps.Map>`): the
            :math:`d` dimensional map :math:`f`.
        """
        super(AutonomousForwardEulerMap, self).__init__(dt, rhs)

    @counted
    def evaluate(
            self,
            u,
            *args,
            **kwargs
    ):
        return u + self._dt * self._rhs.evaluate(u, *args, **kwargs)

    @counted
    def grad_x(
            self,
            u,
            *args,
            **kwargs
    ):
        m = u.shape[0]
        out = np.zeros( (m, self.dim, self.dim) )
        out_diag = np.einsum('...ii->...i', out)
        out_diag[:,:] = 1.
        return out + self._dt * self._rhs.grad_x(u, *args, **kwargs)

    @counted
    def tuple_grad_x(
            self,
            u,
            *args,
            **kwargs
    ):
        m = u.shape[0]
        
        (rhs, gx_rhs) = self._rhs.tuple_grad_x(u, *args, **kwargs)
        
        f = u + self._dt * rhs

        gx = np.zeros( (m, self.dim, self.dim) )
        gx_diag = np.einsum('...ii->...i', gx)
        gx_diag[:,:] = 1.
        gx += self._dt * gx_rhs

        return (f, gx)
        
    @counted
    def hess_x(
            self,
            u,
            *args,
            **kwargs
    ):
        return self._dt * self._rhs.hess_x( u, *args, **kwargs )

    @counted
    def action_hess_x(
            self,
            u,
            du,
            *args,
            **kwargs
    ):
        return self._dt * self._rhs.action_hess_x( u, du, *args, **kwargs )
