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
from typing import List, Union

import numpy as np

from TransportMaps.Misc import counted, cached, cached_tuple, get_sub_cache, deprecate
from TransportMaps.Distributions import \
    Distribution, ConditionalDistribution, FactorizedDistribution
from TransportMaps.Distributions.Inference.InferenceBase import BayesPosteriorDistribution
from TransportMaps.Distributions.FrozenDistributions import StandardNormalDistribution
from TransportMaps.Likelihoods.LikelihoodBase import IndependentLogLikelihood, LogLikelihood

__all__ = [
    # Transition distributions
    'Lag1TransitionDistribution',
    # Markov chain distributions
    'MarkovChainDistribution',
    'TimeHomogeneousMarkovChainDistribution',
    'Lag1TransitionTimeHomogeneousMarkovChainDistribution',
    # Hidden Markov chain distributions
    'HiddenMarkovChainDistribution',
    'HiddenTimeHomogeneousMarkovChainDistribution',
    'HiddenLag1TransitionTimeHomogeneousMarkovChainDistribution',
    # Markov component distributions
    'MarkovComponentDistribution',
    # Deprecated
    'AR1TransitionDistribution',
    'SequentialHiddenMarkovChainDistribution',
]

nax = np.newaxis


class Lag1TransitionDistribution(ConditionalDistribution):
    r""" Transition probability for an auto-regressive (1) process (possibly with hyper-parameters)

    Defines the probability distribution
    :math:`\pi({\bf Z}_{k+1}\vert {\bf Z}_{k}, \Theta)=\pi({\bf Z}_{k+1} - T({\bf Z}_{k},\Theta) \vert \Theta)`
    for the lag-1 process

    .. math::

       {\bf Z}_{k+1} = T({\bf Z}_k, \Theta) + \varepsilon
       \;, \quad
       \varepsilon \sim \nu_\pi

    Args:
      pi (:class:`Distribution<TransportMaps.Distributions.ConditionalDistribution`):
        distribution :math:`\pi:\mathbb{R}^d\times\mathbb{R}^{d_\theta}\rightarrow\mathbb{R}`
      T (:class:`Map<TransportMaps.Maps.Map>`): map
        :math:`T:\mathbb{R}^{d+d_\theta}\rightarrow\mathbb{R}^d`
    """
    def __init__(self, pi, T):
        if pi.dim != T.dim_out:
            raise ValueError("The dimension of pi must match the output " + \
                             "dimension of T.")
        self._pi = pi
        if issubclass(type(pi), ConditionalDistribution):
            self._isPiCond = True
        else:
            self._isPiCond = False
        self._T = T
        self._state_dim = pi.dim
        self._hyper_dim = T.dim_in - T.dim_out
        super(Lag1TransitionDistribution, self).__init__(pi.dim, T.dim_in)

    def get_ncalls_tree(self, indent=""):
        out = super(Lag1TransitionDistribution, self).get_ncalls_tree(indent)
        out += self._T.get_ncalls_tree(indent + '  ')
        out += self._pi.get_ncalls_tree(indent + '  ')
        return out

    def get_nevals_tree(self, indent=""):
        out = super(Lag1TransitionDistribution, self).get_nevals_tree(indent)
        out += self._T.get_nevals_tree(indent + '  ')
        out += self._pi.get_nevals_tree(indent + '  ')
        return out

    def get_teval_tree(self, indent=""):
        out = super(Lag1TransitionDistribution, self).get_teval_tree(indent)
        out += self._T.get_teval_tree(indent + '  ')
        out += self._pi.get_teval_tree(indent + '  ')
        return out

    def update_ncalls_tree(self, obj):
        super(Lag1TransitionDistribution, self).update_ncalls_tree(obj)
        self._T.update_ncalls_tree(obj._T)
        self._pi.update_ncalls_tree(obj._pi)

    def update_nevals_tree(self, obj):
        super(Lag1TransitionDistribution, self).update_nevals_tree(obj)
        self._T.update_nevals_tree(obj._T)
        self._pi.update_nevals_tree(obj._pi)

    def update_teval_tree(self, obj):
        super(Lag1TransitionDistribution, self).update_teval_tree(obj)
        self._T.update_teval_tree(obj._T)
        self._pi.update_teval_tree(obj._pi)

    def reset_counters(self):
        super(Lag1TransitionDistribution, self).reset_counters()
        self._T.reset_counters()
        self._pi.reset_counters()
        
    @property
    def T(self):
        return self._T

    @property
    def pi(self):
        return self._pi

    @property
    def isPiCond(self):
        return self._isPiCond

    @property
    def state_dim(self):
        return self._state_dim

    @property
    def hyper_dim(self):
        return self._hyper_dim

    def rvs(self, m, y, *args, **kwargs):
        r""" [Abstract] Generate :math:`m` samples from the distribution.

        Args:
          m (int): number of samples to generate
          y (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- :math:`m`
             :math:`d`-dimensional samples
        """
        frw = self.T.evaluate(y)
        if self.isPiCond:
            return frw + self.pi.rvs(m, y[:,self.dim:])
        else:
            return frw + self.pi.rvs(m)

    @cached([("pi",None),("T",None)])
    @counted
    def log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None), cache=None):
        r""" Evaluate :math:`\log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\log\pi`
            at the ``x`` points.
        """
        pi_cache, T_cache = get_sub_cache(cache, ("pi",None), ("T",None))
        frw = self.T.evaluate(y, params, idxs_slice=idxs_slice, cache=T_cache)
        if self.isPiCond:
            return self.pi.log_pdf(
                x - frw, y[:,self.dim:], idxs_slice=idxs_slice, cache=pi_cache)
        else:
            return self.pi.log_pdf(x - frw, idxs_slice=idxs_slice, cache=pi_cache)

    @cached([("pi",None),("T",None)])
    @counted
    def grad_x_log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None),
                       cache=None):
        r""" Evaluate :math:`\nabla_{\bf x,y} \log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\nabla_x\log\pi` at the ``x`` points.
        """
        pi_cache, T_cache = get_sub_cache(cache, ("pi",None), ("T",None))
        frw = self.T.evaluate(y, params, idxs_slice=idxs_slice, cache=T_cache)
        gx_frw = self.T.grad_x(y, params, idxs_slice=idxs_slice, cache=T_cache)
        if self.isPiCond:
            gxlpdf = self.pi.grad_x_log_pdf(
                x - frw, y[:,self.dim:], idxs_slice=idxs_slice, cache=pi_cache)
        else:
            gxlpdf = self.pi.grad_x_log_pdf(
                x - frw, idxs_slice=idxs_slice, cache=pi_cache)
        out = np.zeros((x.shape[0], self.dim + self.dim_y))
        out[:,:self.dim] = gxlpdf
        out[:,self.dim:] = - np.einsum('...i,...ij->...j', gxlpdf, gx_frw)
        return out

    @cached([("pi",None),("T",None)],False)
    @counted
    def hess_x_log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None),
                       cache=None):
        r""" Evaluate :math:`\nabla^2_{\bf x,y} \log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) -- values of
            :math:`\nabla^2_x\log\pi` at the ``x`` points.
        """
        pi_cache, T_cache = get_sub_cache(cache, ("pi",None), ("T",None))
        m = x.shape[0]
        dx = self.dim
        dy = self.dim_y
        frw = self.T.evaluate(y, params, idxs_slice=idxs_slice,  cache=T_cache)
        gx_frw = self.T.grad_x(y, params, idxs_slice=idxs_slice, cache=T_cache)
        hx_frw = self.T.hess_x(y, params, idxs_slice=idxs_slice, cache=T_cache)
        if self.isPiCond:
            gx_lpdf = self.pi.grad_x_log_pdf(
                x - frw, y[:,dx:], idxs_slice=idxs_slice, cache=pi_cache)
            hx_lpdf = self.pi.hess_x_log_pdf(
                x - frw, y[:,dx:], idxs_slice=idxs_slice, cache=pi_cache)
        else:
            gx_lpdf = self.pi.grad_x_log_pdf(
                x - frw, idxs_slice=idxs_slice, cache=pi_cache)
            hx_lpdf = self.pi.hess_x_log_pdf(
                x - frw, idxs_slice=idxs_slice, cache=pi_cache)
        out = np.zeros((m, dx+dy, dx+dy))
        out[:,:dx,:dx] = hx_lpdf
        out[:,:dx,dx:] = - np.einsum('...ij,...ik->...jk', hx_lpdf, gx_frw)
        out[:,dx:,:dx] = out[:,:dx,dx:].transpose((0,2,1))
        tmp = - out[:,:dx,dx:] # m x dx x dy
        tmp = np.einsum('...ij,...ik->...jk', tmp, gx_frw)
        tmp -= np.einsum('...i,...ijk->...jk', gx_lpdf, hx_frw)
        out[:,dx:,dx:] = tmp
        return out

##############################
# MARKOV CHAIN DISTRIBUTIONS #
##############################


class MarkovChainDistribution(FactorizedDistribution):
    r""" Distribution of a Markov process (optionally with hyper-parameters)

    For the index set :math:`A=[t_0,\ldots,t_k]` with :math:`t_0<t_1<\ldots <t_k`,
    and the user defined distributions
    :math:`\pi({\bf Z}_{t_i} \vert {\bf Z}_{t_{i-1}}, \Theta)`,
    :math:`\pi({\bf Z}_{t_0} \vert \Theta)` and :math:`\pi(\Theta)`
    defines the distribution

    .. math::

       \pi(\Theta, {\bf Z}_A) = \left( \prod_{i=1}^k \pi(t_i; {\bf Z}_{t_i} \vert {\bf Z}_{t_{i-1}}, \Theta) \right) \pi({\bf Z}_{t_0} \vert \Theta) \pi(\Theta)

    associated to the process :math:`{\bf Z}_A`.

    Args:
      pi_list (:class:`list` of :class:`ConditionalDistribution`):
        list of transition distributions
        :math:`\{\pi({\bf Z}_{t_0} \vert \Theta), \pi({\bf Z}_{t_1}\vert {\bf Z}_{t_{0}},\Theta), \ldots \}`
      pi_hyper (:class:`Distribution`): prior on hyper-parameters :math:`h(\Theta)`
    """
    def __init__(
            self,
            pi_list: List[ConditionalDistribution],
            pi_hyper: Union[Distribution, None] = None
    ):
        factors = []
        # Figure out dimension hyper-parameters
        if pi_hyper is None:
            hdim = 0
        else:
            hdim = pi_hyper.dim
            factors.append( (pi_hyper, list(range(hdim)), []) )
        # Check consistency
        dim = hdim
        sdim = None
        for i, pi in enumerate(pi_list):
            if i == 0:
                if issubclass(type(pi), ConditionalDistribution):
                    if pi.dim_y != hdim:
                        raise ValueError("The dimension of the %d component " % i + \
                                         "is not consistent")
                elif hdim != 0:
                    raise ValueError("The dimension of the %d component " % i + \
                                     "is not consistent")
                sdim = pi.dim
                factors.append( (pi, list(range(dim,dim+sdim)), list(range(hdim))) )
            else:
                if pi.dim != sdim or pi.dim_y != sdim + hdim:
                    raise ValueError("The dimension of the %d component " % i + \
                                     "is not consistent")
                factors.append( (pi, list(range(dim,dim+sdim)),
                                 list(range(dim-sdim,dim)) + list(range(hdim))) )
            dim += sdim
        # Init
        super(MarkovChainDistribution, self).__init__(factors)
        self.pi_list = pi_list
        self.pi_hyper = pi_hyper
        self.state_dim = sdim
        self.hyper_dim = hdim

    @property
    def nsteps(self):
        r""" Returns the number of steps (time indices) :math:`\sharp A`.
        """
        return len(self.pi_list)

    def append(self, pi):
        r""" Append a new transition distribution :math:`\pi(t_{k+1};{\bf Z}_{t_{k+1}}\vert {\bf Z}_{t_{k}},\Theta)`

        Args:
          pi (:class:`Distribution` or :class:`ConditionaDistribution`):
            transition distribution
            :math:`\pi({\bf Z}_{t_{k+1}}\vert {\bf Z}_{t_{k}},\Theta)`
        """
        # Check consistency
        if len(self.pi_list) == 0:
            if issubclass(type(pi), ConditionalDistribution):
                if pi.dim_y != self.hyper_dim:
                    raise ValueError("The dimension of the new component is not consistent")
            elif self.hyper_dim != 0:
                raise ValueError("The initial conditon prior must be conditional on " + \
                                 "the hyper parameters.")
            self.state_dim = pi.dim
            # Prepare factor
            factor = (pi, list(range(self.dim,self.dim+self.state_dim)),
                      list(range(self.hyper_dim)))
        else:
            if pi.dim != self.state_dim or pi.dim_y != self.state_dim + self.hyper_dim:
                raise ValueError("The dimension of the new component is not consistent")
            # Prepare factor
            factor = (pi, list(range(self.dim,self.dim+self.state_dim)),
                      list(range(self.dim-self.state_dim,self.dim)) + list(range(self.hyper_dim)))
        super(MarkovChainDistribution, self).append(factor)
        self.pi_list.append( pi )

    def rvs(self, m, *args, **kwargs):
        r""" Generate :math:`m` samples from the distribution.

        Args:
          m (int): number of samples to generate

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- :math:`m`
             :math:`d`-dimensional samples
        """
        out = np.zeros((m, self.dim))
        for i, (is_cond, pi, xidxs, yidxs) in enumerate(self.factors):
            if is_cond:
                out[:,xidxs] = pi.rvs(m, out[:,yidxs])
            else:
                out[:,xidxs] = pi.rvs(m)
        return out

class TimeHomogeneousMarkovChainDistribution(MarkovChainDistribution):
    r""" A Markov chain distribution where transitions do not depend on time.

    The distribution is defined by

    .. math::

       \pi(\Theta, {\bf Z}_A) = \left( \prod_{i=1}^k \pi({\bf Z}_{t_i} \vert {\bf Z}_{t_{i-1}}, \Theta) \right) \pi({\bf Z}_{t_0} \vert \Theta) \pi(\Theta)

    Args:
      pi_init (:class:`Distribution`): distribution :math:`\pi({\bf Z}_{t_0}\vert\Theta)`
      pi_trans (:class:`ConditionalDistribution`): transition distribution
        :math:`\pi({\bf Z}_{t_i}\vert{\bf Z}_{t_{i-1}},\Theta)`
      pi_list (:class:`list` of :class:`ConditionalDistribution`):
        list of transition distributions
        :math:`\{\pi({\bf Z}_{t_0} \vert \Theta), \pi({\bf Z}_{t_1}\vert {\bf Z}_{t_{0}},\Theta), \ldots \}`
      pi_hyper (:class:`Distribution`): prior on hyper-parameters :math:`h(\Theta)`
    """
    def __init__(self, pi_init, pi_trans,
                 pi_list=[], pi_hyper=None):
        if pi_init.dim != pi_trans.dim_y != pi_trans.dim:
            raise ValueError("Inconsistent dimensions between " + \
                             "initial and transition distributions.")
        self._pi_init = pi_init
        self._pi_trans = pi_trans
        super(TimeHomogeneousMarkovChainDistribution, self).__init__(
            pi_list=pi_list, pi_hyper=pi_hyper)

    @property
    def pi_init(self):
        return self._pi_init

    @property
    def pi_trans(self):
        return self._pi_trans

    def next_transition(self):
        if self.nsteps == 0:
            return self.pi_init
        else:
            return self.pi_trans

    def append(self):
        r""" Append a transition distribution :math:`\pi({\bf Z}_{t_{k+1}}\vert {\bf Z}_{t_{k}},\Theta)`
        """
        super(TimeHomogeneousMarkovChainDistribution, self).append(
            self.next_transition() )

class Lag1TransitionTimeHomogeneousMarkovChainDistribution(
        TimeHomogeneousMarkovChainDistribution):
    r""" A Markov chain distribution defined by lag-1 transitions that do not depend on time.

    The distribution is defined by

    .. math::

       \pi(\Theta, {\bf Z}_A) = \left( \prod_{i=1}^k \pi({\bf Z}_{t_i} \vert {\bf Z}_{t_{i-1}}, \Theta) \right) \pi({\bf Z}_{t_0} \vert \Theta) \pi(\Theta)

    where each conditional :math:`\pi({\bf Z}_{t_i} \vert {\bf Z}_{t_{i-1}}, \Theta)` describe
    the lag-1 process

    .. math::

       {\bf Z}_{k+1} = T({\bf Z}_k, \Theta) + \varepsilon
       \;, \quad
       \varepsilon \sim \pi_{\text{dyn}}

    Args:
      pi_init (:class:`Distribution`): distribution :math:`\pi({\bf Z}_{t_0}\vert\Theta)`
      dyn_map (:class:`Map`): map :math:`T`
      pi_dyn (:class:`Distribution<TransportMaps.Distributions.ConditionalDistribution`):
        distributin of the noise of the dynamics
      pi_list (:class:`list` of :class:`ConditionalDistribution`):
        list of transition distributions
        :math:`\{\pi({\bf Z}_{t_0} \vert \Theta), \pi({\bf Z}_{t_1}\vert {\bf Z}_{t_{0}},\Theta), \ldots \}`
      pi_hyper (:class:`Distribution`): prior on hyper-parameters :math:`h(\Theta)`
    """
    def __init__(self, pi_init, dyn_map, pi_dyn,
                 pi_list=[], pi_hyper=None):
        if pi_init.dim != dyn_map.dim != pi_dyn.dim:
            raise ValueError("Inconsistent dimensions between " + \
                             "initial and transition distributions.")
        pi_trans = Lag1TransitionDistribution( pi_dyn, dyn_map )
        super(Lag1TransitionTimeHomogeneousMarkovChainDistribution, self).__init__(
            pi_init=pi_init, pi_trans=pi_trans,
            pi_list=pi_list, pi_hyper=pi_hyper)

    @property
    def pi_dyn(self):
        return self._pi_trans.pi

    @property
    def dyn_map(self):
        return self._pi_trans.T

#####################################
# HIDDEN MARKOV CHAIN DISTRIBUTIONS #
#####################################
        
class HiddenMarkovChainDistribution(BayesPosteriorDistribution):
    r""" Distribution of a Hidden Markov chain model (optionally with hyper-parameters)

    For the index sets :math:`A=[t_0,\ldots,t_k]` with :math:`t_0<t_1<\ldots <t_k`, 
    :math:`B \subseteq A`, 
    the user defined transition densities (:class:`Distribution`)
    :math:`\{\pi({\bf Z}_{t_0}\vert\Theta), \pi({\bf Z}_{1}\vert{\bf Z}_{t_{0}},\Theta), \ldots \}`,
    the prior :math:`\pi(\Theta)` and 
    the log-likelihoods (:class:`LogLikelihood<TransportMaps.Likelihoods.LogLikelihood>`)
    :math:`\{\log\mathcal{L}({\bf y}_t \vert{\bf Z}_t,\Theta)\}_{t\in B}`, defines the distribution

    .. math::

       \pi(\Theta, {\bf Z}_A \vert {\bf y}_B) =
         \left( \prod_{t\in B} \mathcal{L}(t; {\bf y}_t \vert {\bf Z}_t, \Theta) \right)
         \pi({\bf Z}_{t_0},\ldots,{\bf Z}_{t_k},\Theta)

    associated to the process :math:`{\bf Z}_A`, where
    :math:`\pi({\bf Z}_{t_0},\ldots,{\bf Z}_{t_k},\Theta)` is Markov chain distribution.
    
    .. note:: Each of the log-likelihoods already embed its own data :math:`{\bf y}_t`.
       The list of log-likelihoods must be of the same length of the list of
       transitions. Missing data are simulated by setting the corresponding
       entry in the list of log-likelihood to ``None``.

    Args:
      pi_markov (:class:`MarkovChainDistribution`): Markov chain distribution describing
        :math:`\pi({\bf Z}_{t_0},\ldots,{\bf Z}_{t_k},\Theta)`
      ll_list (:class:`list` of :class:`LogLikelihood<TransportMaps.Likelihoods.LogLikelihood>`):
        list of log-likelihoods
        :math:`\{\log\mathcal{L}({\bf y}_t \vert {\bf Z}_t,\Theta)\}_{t\in B}`

    """
    def __init__(
            self,
            pi_markov: MarkovChainDistribution,
            ll_list: List[LogLikelihood] = []
    ):
        if pi_markov.nsteps != len(ll_list):
            raise ValueError("Length of list of transition must be the same of " + \
                             "the list of log-likelihoods")
        # Prepare likelihood factors and check consistency
        ll_factors = []
        sdim = pi_markov.state_dim
        hdim = pi_markov.hyper_dim
        dim = hdim
        for i, ll in enumerate(ll_list):
            if ll is not None and ll.dim_in != sdim + hdim:
                raise ValueError("Dimension of log-likelihood %d is not consistent" % i)
            ll_factors.append( (ll, list(range(dim,dim+sdim)) + list(range(hdim))) )
            dim += sdim
        logL = IndependentLogLikelihood( ll_factors )
        super(HiddenMarkovChainDistribution, self).__init__(logL, pi_markov)

    @property
    def state_dim(self):
        return self.prior.state_dim

    @property
    def hyper_dim(self):
        return self.prior.hyper_dim

    @property
    def pi_hyper(self):
        return self.prior.pi_hyper

    @property
    def pi_list(self):
        return self.prior.pi_list

    @property
    def ll_list(self):
        return [ll for ll,_ in self.logL.factors]

    @property
    def nsteps(self):
        return self.prior.nsteps

    @property
    def ys(self):
        return [ ll.y for ll in self.ll_list if ll is not None ]

    @property
    def dim(self):
        return self.prior.dim

    @dim.setter
    def dim(self, dim):
        if dim != self.prior.dim:
            raise RuntimeError(
                "Trying to change the dimension of the hidden Markov chain distribution to %d" % dim +  \
                "while the Markov chain (prior) has dimension %d " % self.prior.dim 
            )
        
    def _append_ll(self, ll=None):
        # Prepare likelihood factor and check consistency
        sdim = self.state_dim
        hdim = self.hyper_dim
        if ll is not None and ll.dim_in != sdim + hdim:
            raise ValueError("Dimension of log-likelihood is not consistent")
        self.logL.append( (ll, list(range(self.dim-sdim,self.dim)) + list(range(hdim))) )
        
    def append(self, pi, ll=None):
        r""" Append a new transition distribution :math:`\pi({\bf Z}_{t_{k+1}}\vert\Theta, {\bf Z}_{t_{k}})` and the corresponding log-likelihood :math:`\log\mathcal{L}({\bf y}_{t_k} \vert \Theta, {\bf Z}_{t_k})` if any.

        Args:
          pi (:class:`ConditionalDistribution`): transition distribution
            :math:`\pi({\bf Z}_{t_{k+1}}\vert\Theta, {\bf Z}_{t_{k}})`
          ll (:class:`LogLikelihood<TransportMaps.Likelihoods.LogLikelihood>`):
            log-likelihood
            :math:`\log\mathcal{L}({\bf y}_{t_k} \vert \Theta, {\bf Z}_{t_k})`.
            Missing data are represented by ``None``.
        """
        self.prior.append( pi )
        self._append_ll( ll )

    def get_MarkovComponent(self, i, n=1, state_map=None, hyper_map=None):
        r""" Extract the (:math:`n\geq 1` steps) :math:`i`-th Markov component from the distribution

        If :math:`i=-1` the Markov component is given by

        .. math::

           \pi^{0:n}(\Theta, {\bf Z}_{t_0}, \ldots, {\bf Z}_{t_n}) :=
             \left( \prod_{t \in \{t_0,\ldots,t_n\} \cap B}
                \mathcal{L}({\bf y}_t \vert \Theta, {\bf Z}_t) \right)
             \left( \prod_{i=1}^n \pi({\bf Z}_{t_i}\vert \Theta, {\bf Z}_{t_{i-1}}) \right)
             \pi({\bf Z}_{t_0}\vert\Theta) \pi(\Theta) \;.

        If :math:`i\geq 0` then the Markov component is

        .. math::

           \pi^{i:i+n}\left(\Theta, {\bf Z}_{t_i}, \ldots, {\bf Z}_{t_{i+n}}\right) :=
             \eta(\Theta, {\bf Z}_{t_i}) 
             \left( \prod_{t \in \left\{t_{i+1},\ldots,t_{i+n}\right\} \cap B}
                \mathcal{L}\left({\bf y}_t \vert
                  \mathfrak{T}_{i-1}^{\Theta}(\Theta), {\bf Z}_t\right) \right)
             \left( \prod_{k=i+1}^{i+n-1}
                \pi\left({\bf Z}_{t_k+1}\vert {\bf Z}_{t_{k}},
                   \mathfrak{T}_{i-1}^{\Theta}(\Theta) \right) \right)
             \pi\left({\bf Z}_{t_{i+1}} \vert
                \mathfrak{M}_{i-1}^{1}(\Theta, {\bf Z}_{t_i}),
                \mathfrak{T}_{i-1}^{\Theta}(\Theta)
             \right) \;,

        where :math:`\mathfrak{T}_{i-1}^{\Theta}` and
        :math:`\mathfrak{M}_{i-1}^{1}` are the hyper-parameter and forecast
        components of the map computed at step :math:`i-1`, using the
        sequential algorithm described in :cite:`Spantini2017`.

        Args:
          i (int): index :math:`i` of the Markov component
          n (int): number of steps :math:`n`
          state_map (:class:`TransportMap<TransportMaps.Maps.TransportMap>`):
            forecast map :math:`\mathfrak{M}_{i-1}^{1}` from step :math:`i-1`.
          hyper_map (:class:`TransportMap<TransportMaps.Maps.TransportMap>`):
            hyper-parameter map :math:`\mathfrak{T}_{i-1}^{\Theta}`
            from step :math:`i-1`.

        Returns:
          (:class:`Distribution<TransportMaps.Distributions.Distribution>`) --
            Markov component :math:`\pi^{i:i+n}`.
        """        
        if i == -1:
            out = MarkovComponentDistribution(
                i, self.pi_list[:n+1], self.ll_list[:n+1],
                self.state_dim, self.hyper_dim,
                self.pi_hyper)
        elif i >= 0:
            out = MarkovComponentDistribution(
                i, self.pi_list[i+1:i+n+1], self.ll_list[i+1:i+n+1],
                self.state_dim, self.hyper_dim,
                self.pi_hyper,
                state_map, hyper_map)
        else:
            raise AttributeError("Index must be i >= -1")
        return out

    def trim(self, nsteps):
        r""" Trim the Markov chain to the first ``nsteps``

        Args:
          (int) nsteps: number of steps in the Markov chain of the returned
             distribution
        Returns:
          (:class:`HiddenMarkovChainDistribution`) -- trimmed distribution
        """
        return HiddenMarkovChainDistribution(
            self.pi_list[:nsteps],
            self.ll_list[:nsteps],
            self.pi_hyper)        

class HiddenTimeHomogeneousMarkovChainDistribution(
        HiddenMarkovChainDistribution):
    r""" Distribution of an hidden time homogenoeus Markov chain model
    
    This is a sequential hidden Markov chain where transitions
    do not depend on time. The distribution is then defined as

    .. math::

       \pi(\Theta, {\bf Z}_A \vert {\bf y}_B) =
         \left( \prod_{t\in B} \mathcal{L}(t; {\bf y}_t \vert {\bf Z}_t, \Theta) \right)
         \left( \prod_{i=1}^k \pi({\bf Z}_{t_i}\vert{\bf Z}_{t_{i-1}},\Theta) \right)
         \pi({\bf Z}_{t_0}\vert\Theta) \pi(\Theta)

    Args:
      pi_init (:class:`Distribution`): distribution :math:`\pi({\bf Z}_{t_0}\vert\Theta)`
      pi_trans (:class:`ConditionalDistribution`): transition distribution
        :math:`\pi({\bf Z}_{t_i}\vert{\bf Z}_{t_{i-1}},\Theta)`
      pi_list (:class:`list` of :class:`ConditionalDistribution`): list of transition densities
        :math:`[\pi({\bf Z}_{t_0}\vert\Theta), \pi({\bf Z}_{t_1}\vert{\bf Z}_{t_{0}},\Theta), \ldots ]`
      ll_list (:class:`list` of :class:`LogLikelihood<TransportMaps.Likelihoods.LogLikelihood>`):
        list of log-likelihoods
        :math:`\{\log\mathcal{L}({\bf y}_t \vert {\bf Z}_t,\Theta)\}_{t\in B}`
      pi_hyper (:class:`Distribution`): prior on hyper-parameters :math:`h(\Theta)`
    """
    def __init__(self,
                 pi_init, pi_trans, pi_list=[], pi_hyper=None,
                 ll_list=[]):
        pi_markov = TimeHomogeneousMarkovChainDistribution(
            pi_init=pi_init, pi_trans=pi_trans,
            pi_list=pi_list, pi_hyper=pi_hyper)
        super(HiddenTimeHomogeneousMarkovChainDistribution, self).__init__(
            pi_markov, ll_list=ll_list)

    @property
    def pi_init(self):
        return self.prior.pi_init

    @property
    def pi_trans(self):
        return self.prior.pi_trans

    def append(self, ll=None):
        self.prior.append()
        self._append_ll( ll )

class HiddenLag1TransitionTimeHomogeneousMarkovChainDistribution(
        HiddenTimeHomogeneousMarkovChainDistribution):
    r""" Distribution of an hidden time homogenoeus Markov chain model with lag-1 transitions
    
    This is a sequential hidden Markov chain where transitions
    do not depend on time and describe a lag-1 process.
    The distribution is then defined as

    .. math::

       \pi(\Theta, {\bf Z}_A \vert {\bf y}_B) =
         \left( \prod_{t\in B} \mathcal{L}(t; {\bf y}_t \vert {\bf Z}_t, \Theta) \right)
         \left( \prod_{i=1}^k \pi({\bf Z}_{t_i}\vert{\bf Z}_{t_{i-1}},\Theta) \right)
         \pi({\bf Z}_{t_0}\vert\Theta) \pi(\Theta)

    Args:
      pi_init (:class:`Distribution`): distribution :math:`\pi({\bf Z}_{t_0}\vert\Theta)`
      dyn_map (:class:`Map`): map :math:`T`
      pi_dyn (:class:`Distribution<TransportMaps.Distributions.ConditionalDistribution`):
        distributin of the noise of the dynamics
      pi_list (:class:`list` of :class:`ConditionalDistribution`): list of transition densities
        :math:`[\pi({\bf Z}_{t_0}\vert\Theta), \pi({\bf Z}_{t_1}\vert{\bf Z}_{t_{0}},\Theta), \ldots ]`
      ll_list (:class:`list` of :class:`LogLikelihood<TransportMaps.Likelihoods.LogLikelihood>`):
        list of log-likelihoods
        :math:`\{\log\mathcal{L}({\bf y}_t \vert {\bf Z}_t,\Theta)\}_{t\in B}`
      pi_hyper (:class:`Distribution`): prior on hyper-parameters :math:`h(\Theta)`

    .. seealso::

       :class:`Lag1TransitionTimeHomogeneousMarkovChainDistribution`
    """
    def __init__(self,
                 pi_init, dyn_map, pi_dyn, pi_list=[], pi_hyper=None,
                 ll_list=[]):
        pi_markov = Lag1TransitionTimeHomogeneousMarkovChainDistribution(
            pi_init=pi_init, dyn_map=dyn_map, pi_dyn=pi_dyn,
            pi_list=pi_list, pi_hyper=pi_hyper)
        HiddenMarkovChainDistribution.__init__(
            self, pi_markov, ll_list=ll_list)

    @property
    def pi_dyn(self):
        return self.prior.pi_dyn

    @property
    def dyn_map(self):
        return self.prior.dyn_map
        
class MarkovComponentDistribution(Distribution):
    r""" :math:`i`-th Markov component of a :class:`HiddenMarkovChainDistribution`

    If :math:`i=-1` the Markov component is given by

    .. math::

       \pi^{0:n}(\Theta, {\bf Z}_{t_0}, \ldots, {\bf Z}_{t_n}) :=
         \left( \prod_{t \in \{t_0,\ldots,t_n\} \cap B}
            \mathcal{L}({\bf y}_t \vert \Theta, {\bf Z}_t) \right)
         \left( \prod_{i=1}^n \pi({\bf Z}_{t_i}\vert \Theta, {\bf Z}_{t_{i-1}}) \right)
         \pi({\bf Z}_{t_0}\vert\Theta) \pi(\Theta) \;.

    If :math:`i>=0` then the Markov component is

    .. math::

       \pi^{i:i+n}\left(\Theta, {\bf Z}_{t_i}, \ldots, {\bf Z}_{t_{i+n}}\right) :=
         \eta(\Theta, {\bf Z}_{t_i}) 
         \left( \prod_{t \in \left\{t_{i+1},\ldots,t_{i+n}\right\} \cap B}
            \mathcal{L}\left({\bf y}_t \vert
              \mathfrak{T}_{i-1}^{\Theta}(\Theta), {\bf Z}_t\right) \right)
         \left( \prod_{k=i+1}^{i+n-1}
            \pi\left({\bf Z}_{t_k+1}\vert {\bf Z}_{t_{k}},
               \mathfrak{T}_{i-1}^{\Theta}(\Theta) \right) \right)
         \pi\left({\bf Z}_{t_{i+1}} \vert
            \mathfrak{M}_{i-1}^{1}(\Theta, {\bf Z}_{t_i}),
            \mathfrak{T}_{i-1}^{\Theta}(\Theta)
         \right) \;,

    where :math:`\mathfrak{T}_{i-1}^{\Theta}` and
    :math:`\mathfrak{M}_{i-1}^{1}` are the hyper-parameter and forecast
    components of the map computed at step :math:`i-1`, using the
    sequential algorithm described in :cite:`Spantini2017`.

    Args:
      idx0 (int): index :math:`i` of the Markov component
      pi_list (:class:`list` of :class:`Distribution`): list of :math:`n`
        transition densities
      ll_list (:class:`list` of :class:`LogLikelihood<TransportMaps.Likelihoods.LogLikelihood>`):
        list of :math:`n` log-likelihoods (``None`` for missing data)
        :math:`\{\log\mathcal{L}({\bf y}_t \vert \Theta, {\bf Z}_t)\}_{t\in B}`
      state_dim (int): dimension of the state-space
      hyper_dim (int): dimension of the parameter-space
      pi_hyper (:class:`Distribution`): prior on hyper-parameters :math:`h(\Theta)`
      state_map (:class:`TransportMap<TransportMaps.Maps.TransportMap>`):
        forecast map :math:`\mathfrak{M}_{i-1}^{1}` from step :math:`i-1`.
      hyper_map (:class:`TransportMap<TransportMaps.Maps.TransportMap>`):
        hyper-parameter map :math:`\mathfrak{T}_{i-1}^{\Theta}`
        from step :math:`i-1`.
    """
    def __init__(self, idx0, pi_list, ll_list,
                 state_dim, hyper_dim,
                 pi_hyper=None,
                 state_map=None, hyper_map=None):
        # Figure out dimension and check correct arguments are provided
        self.idx0 = idx0
        self.state_dim = state_dim
        self.hyper_dim = hyper_dim
        if idx0 == -1:
            if pi_hyper is not None and pi_hyper.dim != hyper_dim:
                raise AttributeError(
                    "Dimension of prior of hyper-paramenter not consistent")
            self.pi_hyper = pi_hyper
        elif idx0 >= 0:
            if state_map is None:
                raise AttributeError(
                    "The state_map parameter must be provided for idx0>=0")
            if state_map.dim_in != hyper_dim + state_dim:
                raise AttributeError(
                    "Dimension of state_map not consistent")
            if self.hyper_dim > 0 and hyper_map is None:
                raise AttributeError(
                    "The hyper_map parameter must be provided for hyper_dim>0")
            if self.hyper_dim > 0 and hyper_map.dim != hyper_dim:
                raise AttributeError(
                    "Dimension of hyper_map not consistent")
            self.state_map = state_map
            self.hyper_map = hyper_map
            self.pi_hyper = StandardNormalDistribution(hyper_dim + state_dim)
        else:
            raise AttributeError("Only idx0>=-1 admitted")
        if len(pi_list) != len(ll_list):
            raise AttributeError("Length of list of transition must be the same of " + \
                                 "the list of log-likelihoods")
        if idx0 == -1 and len(pi_list) < 2:
            raise AttributeError("The (-1)-th Markov component must be composed " + \
                                 "by at least two transition densities")
        if idx0 >= 0 and len(pi_list) < 1:
            raise AttributeError("The (i>=0)-th Markov component must be composed " + \
                                 "by at least one transition distribution")
        if idx0 == -1: # We can get away with a SequentialInferenceDistribution
            self.seqinfdens = HiddenMarkovChainDistribution(
                MarkovChainDistribution(pi_list, pi_hyper), ll_list)
            dim = self.seqinfdens.dim
        else:
            dim = hyper_dim + state_dim
            for i, (pi, ll) in enumerate(zip(pi_list,ll_list)):
                if pi.dim != state_dim or pi.dim_y != hyper_dim + state_dim:
                    raise AttributeError(
                        "The dimension of the %d transition is not consistent" % i)
                if ll is not None and ll.dim_in != hyper_dim + state_dim:
                    raise AttributeError(
                        "The dimension of the %d log-likelihood is not consistent" % i)
                dim += state_dim
        self.pi_list = pi_list
        self.ll_list = ll_list
        super(MarkovComponentDistribution, self).__init__(dim)

    def get_ncalls_tree(self, indent=""):
        out = super(MarkovComponentDistribution, self).get_ncalls_tree(indent)
        if self.idx0 == -1:
            out += self.seqinfdens.get_ncalls_tree(indent + '  ')
        else:
            out += self.state_map.get_ncalls_tree(indent + '  ')
            if self.hyper_map is not None:
                out += self.hyper_map.get_ncalls_tree(indent + '  ')
            if self.pi_hyper is not None:
                out += self.pi_hyper.get_ncalls_tree(indent + '  ')
            for pi, ll in zip(self.pi_list, self.ll_list):
                out += pi.get_ncalls_tree(indent + '  ')
                if ll is not None:
                    out += ll.get_ncalls_tree(indent + '  ')
        return out

    def get_nevals_tree(self, indent=""):
        out = super(MarkovComponentDistribution, self).get_nevals_tree(indent)
        if self.idx0 == -1:
            out += self.seqinfdens.get_nevals_tree(indent + '  ')
        else:
            out += self.state_map.get_nevals_tree(indent + '  ')
            if self.hyper_map is not None:
                out += self.hyper_map.get_nevals_tree(indent + '  ')
            if self.pi_hyper is not None:
                out += self.pi_hyper.get_nevals_tree(indent + '  ')
            for pi, ll in zip(self.pi_list, self.ll_list):
                out += pi.get_nevals_tree(indent + '  ')
                if ll is not None:
                    out += ll.get_nevals_tree(indent + '  ')
        return out

    def get_teval_tree(self, indent=""):
        out = super(MarkovComponentDistribution, self).get_teval_tree(indent)
        if self.idx0 == -1:
            out += self.seqinfdens.get_teval_tree(indent + '  ')
        else:
            out += self.state_map.get_teval_tree(indent + '  ')
            if self.hyper_map is not None:
                out += self.hyper_map.get_teval_tree(indent + '  ')
            if self.pi_hyper is not None:
                out += self.pi_hyper.get_teval_tree(indent + '  ')
            for pi, ll in zip(self.pi_list, self.ll_list):
                out += pi.get_teval_tree(indent + '  ')
                if ll is not None:
                    out += ll.get_teval_tree(indent + '  ')
        return out

    def update_ncalls_tree(self, obj):
        super(MarkovComponentDistribution, self).update_ncalls_tree(obj)
        if self.idx0 == -1:
            self.seqinfdens.update_ncalls_tree(obj.seqinfdens)
        else:
            self.state_map.update_ncalls_tree(obj.state_map)
            if self.hyper_map is not None:
                self.hyper_map.update_ncalls_tree(obj.hyper_map)
            if self.pi_hyper is not None:
                self.pi_hyper.update_ncalls_tree(obj.pi_hyper)
            for pi, ll, obj_pi, obj_ll in zip(
                    self.pi_list, self.ll_list,
                    obj.pi_list, obj.ll_list):
                pi.update_ncalls_tree(obj_pi)
                if ll is not None:
                    ll.update_ncalls_tree(obj_ll)

    def update_nevals_tree(self, obj):
        super(MarkovComponentDistribution, self).update_nevals_tree(obj)
        if self.idx0 == -1:
            self.seqinfdens.update_nevals_tree(obj.seqinfdens)
        else:
            self.state_map.update_nevals_tree(obj.state_map)
            if self.hyper_map is not None:
                self.hyper_map.update_nevals_tree(obj.hyper_map)
            if self.pi_hyper is not None:
                self.pi_hyper.update_nevals_tree(obj.pi_hyper)
            for pi, ll, obj_pi, obj_ll in zip(
                    self.pi_list, self.ll_list,
                    obj.pi_list, obj.ll_list):
                pi.update_nevals_tree(obj_pi)
                if ll is not None:
                    ll.update_nevals_tree(obj_ll)

    def update_teval_tree(self, obj):
        super(MarkovComponentDistribution, self).update_teval_tree(obj)
        if self.idx0 == -1:
            self.seqinfdens.update_teval_tree(obj.seqinfdens)
        else:
            self.state_map.update_teval_tree(obj.state_map)
            if self.hyper_map is not None:
                self.hyper_map.update_teval_tree(obj.hyper_map)
            if self.pi_hyper is not None:
                self.pi_hyper.update_teval_tree(obj.pi_hyper)
            for pi, ll, obj_pi, obj_ll in zip(
                    self.pi_list, self.ll_list,
                    obj.pi_list, obj.ll_list):
                pi.update_teval_tree(obj_pi)
                if ll is not None:
                    ll.update_teval_tree(obj_ll)

    def reset_counters(self):
        super(MarkovComponentDistribution, self).reset_counters()
        if self.idx0 == -1:
            self.seqinfdens.reset_counters()
        else:
            self.state_map.reset_counters()
            if self.hyper_map is not None:
                self.hyper_map.reset_counters()
            if self.pi_hyper is not None:
                self.pi_hyper.reset_counters()
            for pi, ll in zip(
                    self.pi_list, self.ll_list):
                pi.reset_counters()
                if ll is not None:
                    ll.reset_counters()

    @property
    def n_steps(self):
        return len(self.pi_list)

    def _transform_input(
            self, x, hdim, sdim, hyper_map_cache, state_map_cache, **kwargs):
        xtr = x.copy() # Transformed input
        # Apply hyper and component maps to obtain transformed inputs
        if hdim > 0:
            xtr[:,:hdim] = self.hyper_map.evaluate(
                x[:,:hdim], cache=hyper_map_cache, **kwargs)
        xtr[:,hdim:hdim+sdim] = self.state_map.evaluate(
            x[:,:hdim+sdim], cache=state_map_cache, **kwargs)
        return xtr
        
    def _transition_log_pdf(self, lpdf, out):
        out += lpdf

    def _ll_log_pdf(self, llev, out):
        out += llev
        
    @cached([
        ("seqinfdens", None),
        ("state_map",None),("hyper_map",None),("pi_hyper",None),
        ("pi_list","n_steps"),("ll_list","n_steps")])
    @counted
    def log_pdf(self, x, cache=None, **kwargs):
        params = kwargs.pop('params',None) # Remove params if in kwargs
        (seqinfdens_cache, state_map_cache,
         hyper_map_cache, pi_hyper_cache,
         pi_list_cache, ll_list_cache) = get_sub_cache(
             cache, ("seqinfdens",None), ("state_map",None),
             ("hyper_map",None), ("pi_hyper",None),
             ("pi_list",self.n_steps), ("ll_list",self.n_steps))
        if self.idx0 == -1:
            out = self.seqinfdens.log_pdf(x, cache=seqinfdens_cache, **kwargs)
        else:
            hdim = self.hyper_dim
            sdim = self.state_dim
            xtr = self._transform_input(
                x, hdim, sdim, hyper_map_cache, state_map_cache, **kwargs)
            # Evaluate pi_hyper
            out = self.pi_hyper.log_pdf(
                x[:,:hdim+sdim], cache=pi_hyper_cache, **kwargs)
            # Evaluate transitions and likelihoods
            for i, (pi, ll, pi_cache, ll_cache) in enumerate(zip(
                    self.pi_list, self.ll_list, pi_list_cache, ll_list_cache)):
                s1 = hdim + i*sdim
                s2 = s1 + sdim
                s3 = s2 + sdim
                xin = xtr[:,s2:s3]
                yin = np.hstack( (xtr[:,s1:s2], xtr[:,:hdim]) )
                lpdf = pi.log_pdf(xin, yin, cache=pi_cache, **kwargs)
                self._transition_log_pdf(lpdf, out)
                if ll is not None:
                    xin = np.hstack( (xtr[:,s2:s3], xtr[:,:hdim]) )
                    llev = ll.evaluate(xin, cache=ll_cache, **kwargs)[:,0]
                    self._ll_log_pdf(llev, out)
        return out

    def _transition_grad_x_log_pdf(
            self, gxlpdf, out, i, hdim, sdim, gx_hyper, gx_comp, s1, s3):
        gxlpdfinner = np.zeros(gxlpdf.shape)
        gxlpdfinner[:,hdim+sdim:] = gxlpdf[:,hdim+sdim:]
        if hdim > 0: # Apply gradient hyper map
            gxlpdfinner[:,:hdim] += np.einsum(
                '...i,...ij->...j', gxlpdf[:,:hdim], gx_hyper)
        if i == 0: # Apply gradient component map
            gxlpdfinner[:,:hdim+sdim] += np.einsum(
                '...i,...ij->...j', gxlpdf[:,hdim:hdim+sdim], gx_comp)
        else:
            gxlpdfinner[:,hdim:hdim+sdim] = gxlpdf[:,hdim:hdim+sdim]
        out[:,:hdim] += gxlpdfinner[:,:hdim]
        out[:,s1:s3] += gxlpdfinner[:,hdim:]

    def _ll_grad_x_log_pdf(
            self, gxllev, out, hdim, gx_hyper, s2, s3):
        if hdim > 0:
            gxllev[:,:hdim] = np.einsum(
                '...i,...ij->...j', gxllev[:,:hdim], gx_hyper)
        out[:,:hdim] += gxllev[:,:hdim]
        out[:,s2:s3] += gxllev[:,hdim:]
        
    @cached([
        ("seqinfdens", None),
        ("state_map",None),("hyper_map",None),("pi_hyper",None),
        ("pi_list","n_steps"),("ll_list","n_steps")])
    @counted
    def grad_x_log_pdf(self, x, cache=None, **kwargs):
        params = kwargs.pop('params',None) # Remove params if in kwargs
        (seqinfdens_cache, state_map_cache,
         hyper_map_cache, pi_hyper_cache,
         pi_list_cache, ll_list_cache) = get_sub_cache(
             cache, ("seqinfdens",None), ("state_map",None),
             ("hyper_map",None), ("pi_hyper",None),
             ("pi_list",self.n_steps), ("ll_list",self.n_steps))
        if self.idx0 == -1:
            out = self.seqinfdens.grad_x_log_pdf(
                x, cache=seqinfdens_cache, **kwargs)
        else:
            hdim = self.hyper_dim
            sdim = self.state_dim
            xtr = self._transform_input(
                x, hdim, sdim, hyper_map_cache, state_map_cache, **kwargs)
            if hdim > 0:
                gx_hyper = self.hyper_map.grad_x(
                    x[:,:hdim], cache=hyper_map_cache, **kwargs)
            else:
                gx_hyper = None
            gx_comp = self.state_map.grad_x(
                x[:,:hdim+sdim], cache=state_map_cache, **kwargs)
            # Evaluate
            out = np.zeros((x.shape[0], self.dim))
            # Evaluate pi_hyper
            out[:,:hdim+sdim] += self.pi_hyper.grad_x_log_pdf(
                x[:,:hdim+sdim], cache=pi_hyper_cache, **kwargs)
            # Evaluate transitions and likelihoods
            perm_pi = list(range(2*sdim,2*sdim+hdim)) + \
                      list(range(sdim,2*sdim)) + \
                      list(range(0, sdim))
            perm_ll = list(range(sdim, sdim+hdim)) + \
                      list(range(0, sdim))
            for i, (pi, ll, pi_cache, ll_cache) in enumerate(zip(
                    self.pi_list, self.ll_list, pi_list_cache, ll_list_cache)):
                s1 = hdim + i*sdim
                s2 = s1 + sdim
                s3 = s2 + sdim
                xin = xtr[:,s2:s3]
                yin = np.hstack( (xtr[:,s1:s2], xtr[:,:hdim]) )
                # Transition
                gxlpdf = pi.grad_x_log_pdf(
                    xin, yin, cache=pi_cache, **kwargs)[:,perm_pi]
                self._transition_grad_x_log_pdf(
                    gxlpdf, out, i, hdim, sdim, gx_hyper, gx_comp, s1, s3)
                # Likelihood
                if ll is not None:
                    xin = np.hstack( (xtr[:,s2:s3], xtr[:,:hdim]) )
                    gxllev = ll.grad_x(
                        xin, cache=ll_cache, **kwargs)[:,0,perm_ll]
                    self._ll_grad_x_log_pdf(
                        gxllev, out, hdim, gx_hyper, s2, s3)
        return out

    @cached_tuple(
        ['log_pdf', 'grad_x_log_pdf'],
        [ ("seqinfdens", None),
          ("state_map",None),("hyper_map",None),("pi_hyper",None),
          ("pi_list","n_steps"),("ll_list","n_steps") ] )
    @counted
    def tuple_grad_x_log_pdf(self, x, cache=None, **kwargs):
        params = kwargs.pop('params',None) # Remove params if in kwargs
        (seqinfdens_cache, state_map_cache,
         hyper_map_cache, pi_hyper_cache,
         pi_list_cache, ll_list_cache) = get_sub_cache(
             cache, ("seqinfdens",None), ("state_map",None),
             ("hyper_map",None), ("pi_hyper",None),
             ("pi_list",self.n_steps), ("ll_list",self.n_steps))
        if self.idx0 == -1:
            lpdf_out, gxlpdf_out = self.seqinfdens.tuple_grad_x_log_pdf(
                x, cache=seqinfdens_cache, **kwargs)
        else:
            hdim = self.hyper_dim
            sdim = self.state_dim
            xtr = self._transform_input(
                x, hdim, sdim, hyper_map_cache, state_map_cache, **kwargs)
            if hdim > 0:
                gx_hyper = self.hyper_map.grad_x(
                    x[:,:hdim], cache=hyper_map_cache, **kwargs)
            else:
                gx_hyper = None
            gx_comp = self.state_map.grad_x(
                x[:,:hdim+sdim], cache=state_map_cache, **kwargs)
            # Evaluate
            gxlpdf_out = np.zeros((x.shape[0], self.dim))
            # Evaluate pi_hyper
            lpdf_out = self.pi_hyper.log_pdf(
                x[:,:hdim+sdim], cache=pi_hyper_cache, **kwargs)
            gxlpdf_out[:,:hdim+sdim] += self.pi_hyper.grad_x_log_pdf(
                x[:,:hdim+sdim], cache=pi_hyper_cache, **kwargs)
            # Evaluate transitions and likelihoods
            perm_pi = list(range(2*sdim,2*sdim+hdim)) + \
                      list(range(sdim,2*sdim)) + \
                      list(range(0, sdim))
            perm_ll = list(range(sdim, sdim+hdim)) + \
                      list(range(0, sdim))
            # Evaluate transitions and likelihoods
            for i, (pi, ll, pi_cache, ll_cache) in enumerate(zip(
                    self.pi_list, self.ll_list, pi_list_cache, ll_list_cache)):
                s1 = hdim + i*sdim
                s2 = s1 + sdim
                s3 = s2 + sdim
                xin = xtr[:,s2:s3]
                yin = np.hstack( (xtr[:,s1:s2], xtr[:,:hdim]) )
                # Transition
                lpdf, gxlpdf = pi.tuple_grad_x_log_pdf(
                    xin, yin, cache=pi_cache, **kwargs)
                gxlpdf = gxlpdf[:,perm_pi]
                self._transition_log_pdf(lpdf, lpdf_out)
                self._transition_grad_x_log_pdf(
                    gxlpdf, gxlpdf_out, i, hdim, sdim, gx_hyper, gx_comp, s1, s3)
                # Likelihood
                if ll is not None:
                    xin = np.hstack( (xtr[:,s2:s3], xtr[:,:hdim]) )
                    llev, gxllev = ll.tuple_grad_x(
                        xin, cache=ll_cache, **kwargs)
                    llev = llev[:,0]
                    gxllev = gxllev[:,0,perm_ll]
                    self._ll_log_pdf(llev, lpdf_out)
                    self._ll_grad_x_log_pdf(
                        gxllev, gxlpdf_out, hdim, gx_hyper, s2, s3)
        return lpdf_out, gxlpdf_out
        
    @cached([
        ("seqinfdens", None),
        ("state_map",None),("hyper_map",None),("pi_hyper",None),
        ("pi_list","n_steps"),("ll_list","n_steps")],
                    False)
    @counted
    def hess_x_log_pdf(self, x, cache=None, **kwargs):
        params = kwargs.pop('params',None) # Remove params if in kwargs
        (seqinfdens_cache, state_map_cache,
         hyper_map_cache, pi_hyper_cache,
         pi_list_cache, ll_list_cache) = get_sub_cache(
             cache, ("seqinfdens",None), ("state_map",None),
             ("hyper_map",None), ("pi_hyper",None),
             ("pi_list",self.n_steps), ("ll_list",self.n_steps))
        if self.idx0 == -1:
            out = self.seqinfdens.hess_x_log_pdf(
                x, cache=seqinfdens_cache, **kwargs)
        else:
            xtr = x.copy() # Transformed input
            hdim = self.hyper_dim
            sdim = self.state_dim
            # Apply hyper and component maps to obtain transformed inputs and
            # compute gradients and Hessians of the maps
            xtr[:,hdim:hdim+sdim] = self.state_map.evaluate(
                x[:,:hdim+sdim], cache=state_map_cache, **kwargs)
            gx_comp = self.state_map.grad_x(
                x[:,:hdim+sdim], cache=state_map_cache, **kwargs)
            hx_comp = self.state_map.hess_x(
                x[:,:hdim+sdim], cache=state_map_cache, **kwargs)
            if hdim > 0:
                xtr[:,:hdim] = self.hyper_map.evaluate(
                    x[:,:hdim], cache=hyper_map_cache, **kwargs)
                gx_hyper = self.hyper_map.grad_x(
                    x[:,:hdim], cache=hyper_map_cache, **kwargs)
                hx_hyper = self.hyper_map.hess_x(
                    x[:,:hdim], cache=hyper_map_cache, **kwargs)
            # Evaluate
            m = x.shape[0]
            out = np.zeros((x.shape[0], self.dim, self.dim))
            # Evaluate pi_hyper
            out[:,:hdim+sdim,:hdim+sdim] += self.pi_hyper.hess_x_log_pdf(
                x[:,:hdim+sdim], cache=pi_hyper_cache, **kwargs)
            # Evaluate transitions and likelihoods
            perm_pi = list(range(2*sdim,2*sdim+hdim)) + \
                      list(range(sdim,2*sdim)) + \
                      list(range(0, sdim))
            perm_ll = list(range(sdim, sdim+hdim)) + \
                      list(range(0, sdim))
            for i, (pi, ll, pi_cache, ll_cache) in enumerate(zip(
                    self.pi_list, self.ll_list, pi_list_cache, ll_list_cache)):
                s1 = hdim + i*sdim
                s2 = s1 + sdim
                s3 = s2 + sdim
                xin = xtr[:,s2:s3]
                yin = np.hstack( (xtr[:,s1:s2], xtr[:,:hdim]) )
                #############
                # Transition
                c1 = hdim
                c2 = c1 + sdim
                hxlpdf = pi.hess_x_log_pdf(
                    xin, yin,
                    cache=pi_cache, **kwargs)[np.ix_(range(m),perm_pi,perm_pi)]
                gxlpdf = pi.grad_x_log_pdf(
                    xin, yin, cache=pi_cache, **kwargs)[:,perm_pi]
                hx = np.zeros(hxlpdf.shape)

                # H_th (logpi(T(th), M(th,y), x))
                if hdim > 0: # Apply hyper map
                    # <H_th logpi, (d_th T)(d_th T)^T>
                    tmp = np.einsum('...ij,...ik->...jk', hxlpdf[:,:c1,:c1], gx_hyper)
                    tmp = np.einsum('...ij,...ik->...jk', tmp, gx_hyper)
                    hx[:,:c1,:c1] += tmp
                    if i == 0:
                        # <H_{th,y} logpi, (d_th T)(d_th M)^T>
                        tmp = np.einsum('...ij,...ik->...jk', hxlpdf[:,:c1,c1:c2], gx_hyper)
                        tmp = np.einsum('...ij,...ik->...jk', tmp, gx_comp[:,:,:c1])
                        hx[:,:c1,:c1] += tmp + tmp.transpose((0,2,1)) # Symmetry
                        # <H_{y} logpi, (d_th M)(d_th M)^T>
                        tmp = np.einsum('...ij,...ik->...jk',
                                        hxlpdf[:,c1:c2,c1:c2], gx_comp[:,:,:c1])
                        tmp = np.einsum('...ij,...ik->...jk', tmp, gx_comp[:,:,:c1])
                        hx[:,:c1,:c1] += tmp
                    # <d_th logpi, H_th T>
                    tmp = np.einsum('...i,...ijk->...jk', gxlpdf[:,:c1], hx_hyper)
                    hx[:,:c1,:c1] += tmp
                    if i == 0:
                        # <d_y logpi, H_th M>
                        tmp = np.einsum('...i,...ijk->...jk',
                                        gxlpdf[:,c1:c2], hx_comp[:,:,:c1,:c1])
                        hx[:,:c1,:c1] += tmp

                # H_y (logpi(T(th), M(th,y), x))
                if i == 0:
                    # <H_y logpi, (d_y M)(d_y M)^T>
                    tmp = np.einsum('...ij,...ik->...jk',
                                    hxlpdf[:,c1:c2,c1:c2], gx_comp[:,:,c1:])
                    tmp = np.einsum('...ij,...ik->...jk', tmp, gx_comp[:,:,c1:])
                    hx[:,c1:c2,c1:c2] += tmp
                    # <d_y logpi, H_y M>
                    tmp = np.einsum('...i,...ijk->...jk',
                                    gxlpdf[:,c1:c2], hx_comp[:,:,c1:,c1:])
                    hx[:,c1:c2,c1:c2] += tmp
                else:
                    hx[:,c1:c2,c1:c2] += hxlpdf[:,c1:c2,c1:c2]

                # H_x (logpi(T(th), M(th,y), x))
                hx[:,c2:,c2:] += hxlpdf[:,c2:,c2:] # Identity

                # H_{th,y} (logpi(T(th), M(th,y), x))
                if hdim > 0:
                    if i == 0:
                        # <H_{th,y} logpi, (d_th T)(d_y M)^T>
                        tmp = np.einsum('...ij,...ik->...jk', hxlpdf[:,:c1,c1:c2], gx_hyper)
                        tmp = np.einsum('...ij,...ik->...jk', tmp, gx_comp[:,:,c1:])
                        hx[:,:c1,c1:c2] += tmp
                        # <H_y logpi, (d_th M)(d_y M)^T>
                        tmp = np.einsum('...ij,...ik->...jk',
                                        hxlpdf[:,c1:c2,c1:c2], gx_comp[:,:,:c1])
                        tmp = np.einsum('...ij,...ik->...jk', tmp, gx_comp[:,:,c1:])
                        hx[:,:c1,c1:c2] += tmp
                        # <d_y logpi, H_{th,y} M>
                        tmp = np.einsum('...i,...ijk->...jk',
                                        gxlpdf[:,c1:c2], hx_comp[:,:,:c1,c1:])
                        hx[:,:c1,c1:c2] += tmp
                    else:
                        # <H_{th,y} logpi, (d_th T) I^T>
                        tmp = np.einsum('...ij,...ik->...kj', hxlpdf[:,:c1,c1:c2], gx_hyper)
                        hx[:,:c1,c1:c2] += tmp

                # H_{y,th} (logpi(T(th), M(th,y), x)) -- symmetry
                hx[:,c1:c2,:c1] += hx[:,:c1,c1:c2].transpose((0,2,1))

                # H_{th,x} (logpi(T(th), M(th,y), x))
                if hdim > 0:
                    # <H_{th,x} logpi, (d_th T) I^T>
                    tmp = np.einsum('...ij,...ik->...kj', hxlpdf[:,:c1,c2:], gx_hyper)
                    hx[:,:c1,c2:] += tmp
                    if i == 0:
                        tmp = np.einsum('...ij,...ik->...kj',
                                        hxlpdf[:,c1:c2,c2:], gx_comp[:,:,:c1])
                        hx[:,:c1,c2:] += tmp

                # H_{x,th} (logpi(T(th), M(th,y), x)) -- symmetry
                hx[:,c2:,:c1] += hx[:,:c1,c2:].transpose((0,2,1))

                # H_{y,x} (logpi(T(th), M(th,y), x))
                if i == 0:
                    # <H_{y,x} logpi, (d_y M) I^T>
                    tmp = np.einsum('...ij,...ik->...kj',
                                    hxlpdf[:,c1:c2,c2:], gx_comp[:,:,c1:])
                    hx[:,c1:c2,c2:] += tmp
                else:
                    hx[:,c1:c2,c2:] += hxlpdf[:,c1:c2,c2:]

                # H_{x,y} (logpi(T(th), M(th,y), x)) -- symmetry
                hx[:,c2:,c1:c2] = hx[:,c1:c2,c2:].transpose((0,2,1))

                # Update out
                out[:,:hdim,:hdim] += hx[:,:hdim,:hdim]
                out[:,:hdim,s1:s3] += hx[:,:hdim,hdim:]
                out[:,s1:s3,:hdim] += hx[:,hdim:,:hdim]
                out[:,s1:s3,s1:s3] += hx[:,hdim:,hdim:]
                
                #############
                # Likelihood
                if ll is not None:
                    xin = np.hstack( (xtr[:,s2:s3], xtr[:,:hdim]) )
                    hxll = ll.hess_x(
                        xin,
                        cache=ll_cache, **kwargs)[np.ix_(range(m),[0],perm_ll,perm_ll)][:,0,:,:]
                    gxll = ll.grad_x(
                        xin, cache=ll_cache, **kwargs)[:,0,perm_ll]
                    hx = np.zeros(hxll.shape)

                    # H_th (logL(T(th),x))
                    if hdim > 0:
                        # <H_th logL, (d_th T)(d_th T)^T>
                        tmp = np.einsum('...ij,...ik->...jk', hxll[:,:hdim,:hdim], gx_hyper)
                        tmp = np.einsum('...ij,...ik->...jk', tmp, gx_hyper)
                        hx[:,:hdim,:hdim] += tmp
                        # <d_th logL, H_th T>
                        tmp = np.einsum('...i,...ijk->...jk', gxll[:,:hdim], hx_hyper)
                        hx[:,:hdim,:hdim] += tmp

                    # H_x (logL(T(th),x))
                    hx[:,hdim:,hdim:] += hxll[:,hdim:,hdim:]

                    # H_{th,x} (logL(T(th),x))
                    if hdim > 0:
                        # <H_{th,x} logL, (d_th T) I^T>
                        tmp = np.einsum('...ij,...ik->...kj', hxll[:,:hdim,hdim:], gx_hyper)
                        hx[:,:hdim,hdim:] += tmp

                    # H_{th,x} (logL(T(th),x)) -- symmetry
                    hx[:,hdim:,:hdim] += hx[:,:hdim,hdim:].transpose((0,2,1))

                    # Update out
                    out[:,:hdim,:hdim] += hx[:,:hdim,:hdim]
                    out[:,:hdim,s2:s3] += hx[:,:hdim,hdim:]
                    out[:,s2:s3,:hdim] += hx[:,hdim:,:hdim]
                    out[:,s2:s3,s2:s3] += hx[:,hdim:,hdim:]
        return out

#
# DEPRECATED
#
        
class AR1TransitionDistribution(Lag1TransitionDistribution):
    @deprecate(
        'AR1TransitionDistribution', '3.0',
        'Use Lag1TransitionDistribution instead.'
    )
    def __init__(self, *args, **kwargs):
        super(AR1TransitionDistribution, self).__init__(*args, **kwargs)

class SequentialHiddenMarkovChainDistribution(HiddenMarkovChainDistribution):
    r"""
    Args:
      pi_list (:class:`list` of :class:`ConditionalDistribution`): list of transition densities
        :math:`[\pi({\bf Z}_{t_0}\vert\Theta), \pi({\bf Z}_{t_1}\vert{\bf Z}_{t_{0}},\Theta), \ldots ]`
      ll_list (:class:`list` of :class:`LogLikelihood<TransportMaps.Likelihoods.LogLikelihood>`):
        list of log-likelihoods
        :math:`\{\log\mathcal{L}({\bf y}_t \vert {\bf Z}_t,\Theta)\}_{t\in B}`
      pi_hyper (:class:`Distribution`): prior on hyper-parameters :math:`h(\Theta)`

    """
    @deprecate(
        'SequentialHiddenMarkovChainDistribution', '3.0',
        'Use HiddenMarkovChainDistribution instead.'
    )
    def __init__(self, pi_list=[], ll_list=[], pi_hyper=None):
        if len(pi_list) != len(ll_list):
            raise ValueError("Length of list of transition must be the same of " + \
                             "the list of log-likelihoods")
        pi_markov = MarkovChainDistribution(pi_list, pi_hyper)
        super(SequentialHiddenMarkovChainDistribution, self).__init__(
            pi_markov,
            ll_list=ll_list
        )