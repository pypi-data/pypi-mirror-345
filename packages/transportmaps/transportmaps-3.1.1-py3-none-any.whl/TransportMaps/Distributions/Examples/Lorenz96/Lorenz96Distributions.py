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

from TransportMaps.Misc import counted, cached, get_sub_cache
from TransportMaps.Distributions.Decomposable.SequentialInferenceDistributions import \
    Lag1TransitionDistribution, \
    HiddenLag1TransitionTimeHomogeneousMarkovChainDistribution
from TransportMaps.Maps import \
    Map, \
    ListCompositeMap, \
    InverseMap

from TransportMaps.Likelihoods.LikelihoodBase import AdditiveLogLikelihood

try:
    from TransportMaps.Distributions.Examples.Lorenz96.fast_eval import \
        l96mII_evaluate, l96mII_grad_x, l96mII_tuple_grad_x, \
        l96mII_hess_x, l96mII_action_hess_x
    L96MII_FAST_EVAL_FLAG = True
except ImportError:
    L96MII_FAST_EVAL_FLAG = False

__all__ = [
    'Lorenz96DynamicsMap',
    'Lorenz96ForwardEulerMap',
    'Lorenz96MultipleStepsForwardEulerMap',
    'Lorenz96ForwardEulerDistribution',
    'Lorenz96ModalForwardEulerDistribution'
]


class Lorenz96DynamicsMap(Map):
    r""" Defines the evolution of the dynamics of the Lorenz-96 (model II) system.

    Evaluates the right hand side the Lorenz-96 system:

    .. math::

       \dot{x}_n = \sum_{j=-J}^J \sum_{i=-J}^J (-x_{n-2K-i} x_{n-K-j} + x_{n-K+j-i} x_{n+K+j})/K^2 - x_{n} + F

    where :math:`J=(K-1)/2` and :math:`K` is odd.
    
    The model is presented in

    Lorenz, E. N. (2005). Designing Chaotic Models. Journal of the Atmospheric Sciences, 62(5), 1574–1587.
    https://doi.org/10.1175/JAS3430.1

    For the parameter :math:`K=1`, this reverts to the original Lorenz-96 model

    Lorenz, E. (1963). Deterministic nonperiodic flow. Journal of the Atmospheric Sciences.
    https://doi.org/10.1175/1520-0469(1963)020<0130%3ADNF>2.0.CO%3B2
    
    .. document private functions
    .. automethod:: __init__
    """
    def __init__(
            self,
            d = 40,
            K = 1,
            F = 8.
    ):
        r"""
        Args:
          d (int): dimension of the state :math:`{\bf x}`
          K (int): smoothing term :math:`K` (must be odd)
          F (float): forcing term :math:`F`
        """
        if not L96MII_FAST_EVAL_FLAG:
            raise ImportError(
                "TransportMaps was installed without cython support. " + \
                "This class requires it."
            )
        
        if not isinstance(K, int) or K % 2 == 0:
            raise ValueError(
                "The smoothing factor K must be an odd integer.")
        self._K = K
        self._F = F
        super(Lorenz96DynamicsMap,
              self).__init__(
                  dim_in = d,
                  dim_out = d
              )

    @property
    def F(self):
        return self._F

    @counted
    def evaluate(
            self,
            x,
            *args,
            **kwargs
    ):
        return l96mII_evaluate(x, self._K, self._F)

    @counted
    def grad_x(
            self,
            x,
            *args,
            **kwargs
    ):
        return l96mII_grad_x(x, self._K, self._F)

    @counted
    def tuple_grad_x(
            self,
            x,
            *args,
            **kwargs
    ):
        return l96mII_tuple_grad_x(x, self._K, self._F)

    @counted
    def hess_x(
            self,
            x,
            *args,
            **kwargs
    ):
        return l96mII_hess_x(x, self._K, self._F)

    @counted
    def action_hess_x(
            self,
            x,
            dx,
            *args,
            **kwargs
    ):
        return l96mII_action_hess_x(x, dx, self._K, self._F)
        # out = np.zeros( (x.shape[0], self.dim_out, self.dim_in) )
        # d = self.dim
        # for i in range(d):
        #     out[:,i,(i-2)%d] += - dx[:,(i-1)%d] / self._K**2
        #     out[:,i,(i-1)%d] += - dx[:,(i-2)%d] / self._K**2
        #     out[:,i,(i-1)%d] +=   dx[:,(i+1)%d] / self._K**2
        #     out[:,i,(i+1)%d] +=   dx[:,(i-1)%d] / self._K**2
        # return out


class Lorenz96ForwardEulerMap( AutonomousForwardEulerMap ):
    r""" Defines the evolution of the Lorenz-96 dynamics for one forward Euler step.

    Evaluates the Euler step of the Lorenz-96 system:

    .. math::

       \dot{x}_i^{(n+1)} = x_i^{(n)} +
       \Delta t \cdot (x_{i+1}^{(n)} - x_{i-2}^{(n)}) x_{i-1}^{(n)} / K^2 - x_{i}^{(n)} + F
    
    .. document private functions
    .. automethod:: __init__
    """
    def __init__(
            self,
            dt,
            d = 40,
            K = 1,
            F = 8.
    ):
        r"""
        Args:
          dt (float): step site :math:`\Delta t`
          d (int): dimension of the state :math:`{\bf x}`
          K (int): smoothing term :math:`K` (must be odd)
          F (float): forcing term :math:`F`
        """
        super(Lorenz96ForwardEulerMap, self).__init__(
            dt, Lorenz96DynamicsMap(d, K, F) )

    @property
    def K(self):
        return self._rhs.K
        
    @property
    def F(self):
        return self._rhs.F


class Lorenz96MultipleStepsForwardEulerMap( ListCompositeMap ):
    r""" Defines the evolution of the Lorenz-96 dynamics for :math:`n` forward Euler steps.

    Evaluates :math:`n` times the Euler step of the Lorenz-96 system:

    .. math::

       \dot{x}_i^{(k)} \mapsto x_i^{(k)} +
       \Delta t \cdot (x_{i+1}^{(k)} - x_{i-2}^{(k)}) x_{i-1}^{(k)} / K^2 - x_{i}^{(k)} + F

    .. document private functions
    .. automethod:: __init__
    """
    def __init__(
            self,
            n,
            dt,
            d = 40,
            K = 1,
            F = 8.
    ):
        r"""
        Args:
          n (int): number :math:`n` of Euler steps.
          dt (float): step size :math:`\Delta t`
          d (int): dimension of the state :math:`{\bf x}`
          K (int): smoothing term :math:`K` (must be odd)
          F (float): forcing term :math:`F`
        """
        self._l96femap = Lorenz96ForwardEulerMap(
            dt, d=d, K=K, F=F)
        super(Lorenz96MultipleStepsForwardEulerMap, self).__init__(
            [self._l96femap] * n)

    @property
    def n(self):
        return self.n_maps
    
    @property
    def dt(self):
        return self._l96femap.dt

    @property
    def K(self):
        return self._l96femap.K
        
    @property
    def F(self):
        return self._l96femap.F

    @property
    def l96femap(self):
        return self._l96femap


class Lorenz96ForwardEulerDistribution( HiddenLag1TransitionTimeHomogeneousMarkovChainDistribution ):
    r""" Defines the Hidden Markov Chain distribution defined by the Lorenz-96 dynamics.

    For the index sets :math:`\Lambda={in : i=0,\ldots}`
    and :math:`\Xi \subset \Lambda` the model is defined by

    .. math::

       \begin{cases}
         {\bf x}_{k+n} = g({\bf x}_k) + \varepsilon_{\text{dyn}} & \text{for } k \in \Lambda \\
         {\bf y}_{k+n} &= h({\bf x}_{k+n}) + \varepsilon_{\text{noise}} & \text{for } k+n \in \Xi \;,
       \end{cases}

    where :math:`g:{\bf x}_k \mapsto {\bf x}_{k+n}` is the map corresponding
    to :math:`n` Euler steps of the discretized dynamics with time step :math:`\Delta t`,
    :math:`h` is the observation operator,
    :math:`\varepsilon_{\text{dyn}} \sim \pi_{\text{dyn}}` is the dynamics noise,
    :math:`\varepsilon_{\text{noise}} \sim \pi_{\text{noise}}` is the observational noise
    and the initial conditions :math:`{\bf x}_0` are distributed
    according to :math:`\pi_{\text{init}}`.
    """
    def __init__(
            self,
            # Lorenz parameters
            n, dt, d, K, F,
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
          d (int): dimension of the state :math:`{\bf x}`
          K (int): smoothing term :math:`K` (must be odd)
          F (float): forcing term :math:`F`
          pi_init (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            distribution :math:`\pi_{\text{init}}` of the initial conditions
          pi_dyn (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            distribution :math:`\pi_{\text{dyn}}` of the dynamics noise
          obs_map (:class:`Map<TransportMaps.Maps.Map>`): observation operator :math:`h`
          pi_noise (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            distribution :math:`\pi_{\text{noise}}` of the observations noise
        """
        # Set up the transition distribution
        self._l96map = Lorenz96MultipleStepsForwardEulerMap(
            n=n, dt=dt, d=d, K=K, F=F)

        # Set up the components of the likelihoods
        self._obs_map = obs_map
        self._pi_noise = pi_noise

        # Tracking time and states (optional)
        self._t = []
        self._xs = []

        # Call constructor
        super(Lorenz96ForwardEulerDistribution, self).__init__(
            pi_init, self._l96map, pi_dyn, pi_list=[], pi_hyper=None, ll_list=[])

    @property
    def n(self):
        return self._l96map.n
        
    @property
    def dt(self):
        return self._l96map.dt

    @property
    def K(self):
        return self._l96map.K

    @property
    def F(self):
        return self._l96map.F

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
    def l96map(self):
        return self._l96map

    @property
    def obs_map(self):
        return self._obs_map

    def step(self, y, x=None):
        r""" Add a step to the hidden Markov Chain.

        Args:
          y: observation. ``None`` if missing.
          x: state if known (for diagnostic)
        """
        if y is not None:
            ll = AdditiveLogLikelihood(
                y, self._pi_noise, self._obs_map)
        else:
            ll = None
        # Update time and (optional) state
        self._t.append( self._t[-1] + self.n * self.dt if self.nsteps > 0 else 0. )
        self._xs.append( x )
        # Append
        self.append( ll )

class Lorenz96ModalForwardEulerDistribution( Lorenz96ForwardEulerDistribution ):
    r""" Defines the Hidden Markov Chain distribution defined by the Lorenz-96 dynamics in modal form.

    For the index sets :math:`\Lambda={in : i=0,\ldots}`
    and :math:`\Xi \subset \Lambda` the model is defined by

    .. math::

       \begin{cases}
         {\bf b}_{k+n} = P_r^{-1} \circ g \circ P_r({\bf b}_k) + \varepsilon^r_{\text{dyn}} & \text{for } k \in \Lambda \\
         {\bf y}_{k+n} &= h\circ P_r({\bf b}_{k+n}) + \varepsilon_{\text{noise}} & \text{for } k+n \in \Xi \;,
       \end{cases}

    where :math:`g:{\bf x}_k \mapsto {\bf x}_{k+n}` is the map corresponding
    to :math:`n` Euler steps of the discretized dynamics with time step :math:`\Delta t`,
    :math:`P_r:\mathbb{R}^d\rightarrow\mathbb{R}^r` is a projection operator onto
    the modal subspace (:math:`r\leq d`),
    :math:`h` is the observation operator,
    :math:`\varepsilon^r_{\text{dyn}} \sim \pi^r_{\text{dyn}}` is the noise of the modal dynamics,
    :math:`\varepsilon_{\text{noise}} \sim \pi_{\text{noise}}` is the observational noise
    and the initial conditions :math:`{\bf b}_0` are distributed
    according to :math:`\pi^r_{\text{init}}`.
    """
    def __init__(
            self,
            # Lorenz parameters
            n, dt, d, K, F,
            # Modal parameters
            modal_map,
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
          d (int): dimension of the state :math:`{\bf x}`
          K (int): smoothing term :math:`K` (must be odd)
          F (float): forcing term :math:`F`
          modal_map (:class:`Map<TransportMaps.Maps.Map>`): projection operator :math:`P_r`
          pi_init (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            distribution :math:`\pi_{\text{init}}` of the initial conditions
          pi_dyn (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            distribution :math:`\pi_{\text{dyn}}` of the dynamics noise
          obs_map (:class:`Map<TransportMaps.Maps.Map>`): observation operator :math:`h`
          pi_noise (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            distribution :math:`\pi_{\text{noise}}` of the observations noise
        """
        # Set up the transition distribution
        self._l96map = Lorenz96MultipleStepsForwardEulerMap(
            n=n, dt=dt, d=d, K=K, F=F)
        self._modal_map = modal_map
        F = ListCompositeMap( [
            InverseMap( modal_map ),
            self._l96map,
            modal_map ] )

        # Set up the distribution of the initial conditions
        pi_init = pi_init

        # Set up the components of the likelihoods
        self._obs_map = ListCompositeMap( [obs_map, modal_map] )
        self._pi_noise = pi_noise

        # Tracking time and states (optional)
        self._t = []
        self._xs = []
        self._bs = []

        # Call constructor
        HiddenLag1TransitionTimeHomogeneousMarkovChainDistribution.__init__(
            self,
            pi_init, F, pi_dyn, pi_list=[],
            pi_hyper=None, ll_list=[])

    @property
    def modal_map(self):
        return self._modal_map

    @property
    def obs_map(self):
        return self._obs_map.tm_list[0]

    @property
    def bs(self):
        return self._bs
    
    def step(self, y, x=None):
        r""" Add a step to the hidden Markov Chain.

        Args:
          y: observation. ``None`` if missing.
          x: state if known (for diagnostic)
        """
        super(Lorenz96ModalForwardEulerDistribution, self).step(y, x=x)
        # Update modal truth if any
        b = self._modal_map.inverse(x[np.newaxis,:])[0,:] if x is not None else None
        self._bs.append( b ) 
