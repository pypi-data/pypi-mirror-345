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
from TransportMaps.Maps.ODEs import AutonomousForwardEulerMap

from TransportMaps.Misc import counted
from TransportMaps.Distributions.Decomposable.SequentialInferenceDistributions import \
    AR1TransitionDistribution, \
    SequentialHiddenMarkovChainDistribution
from TransportMaps.Maps import \
    Map, \
    ListCompositeMap

from TransportMaps.Likelihoods.LikelihoodBase import AdditiveLogLikelihood

__all__ = [
    'Lorenz63DynamicsMap',
    'Lorenz63ForwardEulerMap',
    'Lorenz63MultipleStepsForwardEulerMap',
    'Lorenz63ForwardEulerDistribution'
]

class Lorenz63DynamicsMap(Map):
    r""" Defines the evolution of the dynamics.

    Evaluates the right hand side of the Lorenz-63 system:

    .. math::
    
       \begin{cases}
          \dot{x} = \sigma ( y - x ) & \\
          \dot{y} = x (\rho - z) - y & \\
          \dot{z} = xy - \beta z & 
       \end{cases}

    .. document private functions
    .. automethod:: __init__
    """
    def __init__(
            self,
            sigma = 10.,
            beta  = 8./3.,
            rho   = 28.
    ):
        r"""
        Args:
          sigma (foat): :math:`\sigma`
          beta(foat): :math:`\beta`
          rho (foat): :math:`\rho`
        """
        self._sigma = sigma
        self._beta = beta
        self._rho = rho
        super(Lorenz63DynamicsMap,
              self).__init__(
                  dim_in  = 3,
                  dim_out = 3,
              )

    @property
    def sigma(self):
        return self._sigma

    @property
    def beta(self):
        return self._beta

    @property
    def rho(self):
        return self._rho

    @staticmethod
    def _extract_state(u):
        return (u[:,0], u[:,1], u[:,2])
        
    @counted
    def evaluate(
            self,
            u,
            *args,
            **kwargs
    ):
        x, y, z = Lorenz63DynamicsMap._extract_state( u )
        out = np.zeros( (u.shape[0], self.dim_out) )
        out[:,0] = self._sigma * (y - x)
        out[:,1] = x * (self._rho - z) - y
        out[:,2] = x * y - self._beta * z
        return out

    @counted
    def grad_x(
            self,
            u,
            *args,
            **kwargs
    ):
        x, y, z = Lorenz63DynamicsMap._extract_state( u )
        out = np.zeros( (u.shape[0], self.dim_out, self.dim_in) )
        # \dot{x} = \sigma ( y - x )
        out[:,0,0] = -self._sigma
        out[:,0,1] = self._sigma
        # \dot{y} = x (\rho - z) - y
        rmz = self._rho - z
        out[:,1,0] = rmz 
        out[:,1,1] = - 1.
        out[:,1,2] = - x 
        # \dot{z} = xy - \beta z
        out[:,2,0] = y
        out[:,2,1] = x
        out[:,2,2] = - self._beta
        return out

    @counted
    def hess_x(
            self,
            u,
            *args,
            **kwargs
    ):
        x, y, z = Lorenz63DynamicsMap._extract_state( u )
        out = np.zeros( (
            u.shape[0], self.dim_out, self.dim_in, self.dim_in) )
        # \dot{x} = \sigma ( y - x ) [all zeros]
        # \dot{y} = x (\rho - z) - y
        out[:,1,0,2] = - 1.
        out[:,1,2,0] = - 1.
        # \dot{z} = xy - \beta z
        out[:,2,0,1] = 1.
        out[:,2,1,0] = 1.
        return out

    @counted
    def action_hess_x(
            self,
            u,
            du,
            *args,
            **kwargs
    ):
        x, y, z = Lorenz63DynamicsMap._extract_state( u )
        dx, dy, dz = Lorenz63DynamicsMap._extract_state( du )
        out = np.zeros( (
            u.shape[0], self.dim_out, self.dim_in) )
        # \dot{x} = \sigma ( y - x ) [all zeros]
        # \dot{y} = x (\rho - z) - y
        out[:,1,0] = - dz
        out[:,1,2] = - dx
        # \dot{z} = xy - \beta z
        out[:,2,0] = dy
        out[:,2,1] = dx
        return out
        
class Lorenz63ForwardEulerMap( AutonomousForwardEulerMap ):
    r""" Defines the evolution of the Lorenz-63 dynamics for one forward Euler step.

    Evaluates the Euler step of the Lorenz-63 system:

    .. math::
    
       \begin{cases}
          x_{n+1} = x_n + \Delta t \cdot \sigma ( y_n - x_n ) & \\
          y_{n+1} = y_n + \Delta t \cdot x_n (\rho - z_n) - y_n & \\
          z_{n+1} = z_n + \Delta t \cdot x_n y_n - \beta z_n & 
       \end{cases}

    .. document private functions
    .. automethod:: __init__
    """
    def __init__(
            self,
            dt,
            sigma = 10.,
            beta  = 8./3.,
            rho   = 28.
    ):
        r"""
        Args:
          dt (float): step size :math:`\Delta t`
          sigma (foat): :math:`\sigma`
          beta(foat): :math:`\beta`
          rho (foat): :math:`\rho`
        """
        super(Lorenz63ForwardEulerMap, self).__init__(
            dt, Lorenz63DynamicsMap(sigma, beta, rho) )

    @property
    def sigma(self):
        return self._rhs.sigma

    @property
    def beta(self):
        return self._rhs.beta

    @property
    def rho(self):
        return self._rhs.rho

class Lorenz63MultipleStepsForwardEulerMap( ListCompositeMap ):
    r""" Defines the evolution of the dynamics for :math:`n` forward Euler steps.

    Evaluates :math:`n` times the Euler step of the Lorenz-63 system:

    .. math::
    
       \begin{array}{c}
          x_{k} \\
          y_{k} \\
          z_{k}
       \end{array}
       \mapsto
       \begin{array}{c}
          x_k + \Delta t \cdot \sigma ( y_k - x_k ) \\
          y_k + \Delta t \cdot x_k (\rho - z_k) - y_k \\
          z_k + \Delta t \cdot x_k y_k - \beta z_k
       \end{array}

    .. document private functions
    .. automethod:: __init__
    """
    def __init__(
            self,
            n,
            dt,
            sigma = 10.,
            beta  = 8./3.,
            rho   = 28.
    ):
        r"""
        Args:
          n (int): number :math:`n` of Euler steps.
          dt (float): step size :math:`\Delta t`
          sigma (foat): :math:`\sigma`
          beta(foat): :math:`\beta`
          rho (foat): :math:`\rho`
        """
        self._l63femap = Lorenz63ForwardEulerMap(
            dt, sigma=sigma, beta=beta, rho=rho)
        super(Lorenz63MultipleStepsForwardEulerMap, self).__init__(
            [self._l63femap] * n)

    @property
    def n(self):
        return self.n_maps
    
    @property
    def dt(self):
        return self._l63femap.dt
        
    @property
    def sigma(self):
        return self._l63femap.sigma

    @property
    def beta(self):
        return self._l63femap.beta

    @property
    def rho(self):
        return self._l63femap.rho
        
class Lorenz63ForwardEulerDistribution( SequentialHiddenMarkovChainDistribution ):
    r""" Defines the Hidden Markov Chain distribution defined by the Lorenz-63 dynamics.

    For :math:`{\bf u} = [x, y, z]^\top` and the index sets
    :math:`\Lambda={in : i=0,\ldots}` and :math:`\Xi \subset \Lambda`
    the model is defined by

    .. math::

       \begin{cases}
         {\bf u}_{k+n} = g({\bf u}_k) + \varepsilon_{\text{dyn}} & \text{for } k \in \Lambda \\
         {\bf y}_{k+n} &= h({\bf u}_{k+n}) + \varepsilon_{\text{noise}} & \text{for } k+n \in \Xi \;,
       \end{cases}

    where :math:`g:{\bf u}_k \mapsto {\bf u}_{k+n}` is the map corresponding
    to :math:`n` Euler steps of the discretized dynamics with time step :math:`\Delta t`,
    :math:`h` is the observation operator,
    :math:`\varepsilon_{\text{dyn}} \sim \pi_{\text{dyn}}` is the dynamics noise,
    :math:`\varepsilon_{\text{noise}} \sim \pi_{\text{noise}}` is the observational noise
    and the initial conditions :math:`{\bf u}_0` are distributed
    according to :math:`\pi_{\text{init}}`.
    """
    def __init__(
            self,
            # Lorenz parameters
            n, dt, sigma, beta, rho,
            # Initial conditions
            pi_init,
            # Transitions
            pi_dyn,
            # Observations
            obs_map, pi_noise,
    ):
        r"""
        Args:
          n (int): number :math:`n` of Euler steps defining the map :math:`g`
          dt (float): step size :math:`\Delta t`
          sigma (foat): :math:`\sigma`
          beta(foat): :math:`\beta`
          rho (foat): :math:`\rho`
          pi_init (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            distribution :math:`\pi_{\text{init}}` of the initial conditions
          pi_dyn (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            distribution :math:`\pi_{\text{dyn}}` of the dynamics noise
          obs_map (:class:`Map<TransportMaps.Maps.Map>`): observation operator :math:`h`
          pi_noise (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            distribution :math:`\pi_{\text{noise}}` of the observations noise
        """
        # Set up the transition distribution
        self._l63map = Lorenz63MultipleStepsForwardEulerMap(
            n=n, dt=dt, sigma=sigma, beta=beta, rho=rho)
        self._pi_dyn = pi_dyn
        self._pi_trans = AR1TransitionDistribution(
            self._pi_dyn, self._l63map)

        # Set up the distribution of the initial conditions
        self._pi_init = pi_init

        # Set up the components of the likelihoods
        self._obs_map = obs_map
        self._pi_noise = pi_noise

        # Tracking time and states (optional)
        self._t = []
        self._xs = []

        # Call constructor
        super(Lorenz63ForwardEulerDistribution, self).__init__([], [])

    @property
    def n(self):
        return self._l63map.n
        
    @property
    def dt(self):
        return self._l63map.dt

    @property
    def sigma(self):
        return self._l63map.sigma

    @property
    def beta(self):
        return self._l63map.beta

    @property
    def rho(self):
        return self._l63map.rho

    @property
    def t(self):
        return self._t

    @property
    def t_obs(self):
        return [ t for t, ll in zip(self.t, self.ll_list) if ll is not None ]

    @property
    def xs(self):
        return self._xs

    @property
    def ys(self):
        return [ ll.y for ll in self.ll_list if ll is not None ]

    def step(self, y, x=None):
        r""" Add a step to the hidden Markov Chain.

        Args:
          y: observation. ``None`` if missing.
          x: state if known (for diagnostic)
        """
        if self.nsteps == 0:
            pin = self._pi_init
        else:
            pin = self._pi_trans
        if y is not None:
            ll = AdditiveLogLikelihood(
                y, self._pi_noise, self._obs_map)
        else:
            ll = None
        # Update time and (optional) state
        self._t.append( self._t[-1] + self.n * self.dt if self.nsteps > 0 else 0. )
        self._xs.append( x )
        # Append
        self.append( pin, ll )
