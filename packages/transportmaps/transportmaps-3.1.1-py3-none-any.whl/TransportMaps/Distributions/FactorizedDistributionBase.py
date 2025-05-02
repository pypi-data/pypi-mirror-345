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

from ..Misc import counted, cached, cached_tuple

from .DistributionBase import Distribution
from .ConditionalDistributionBase import ConditionalDistribution

__all__ = [
    'FactorizedDistribution'
]

class FactorizedDistribution(Distribution):
    r""" Distribution :math:`\nu_\pi` defiened by its conditional factors.

    The density of the distribution :math:`\nu_\pi` is defined by

    .. math::

       \pi({\bf x}) = \prod_{({\bf i},{\bf k}) \in \mathcal{I}} \pi({\bf x}_{\bf i},{\bf x}_{\bf k})`

    Args:
      factors (:class:`list` of :class:`tuple`): each tuple contains a factor
        (:class:`ConditionalDistribution` and/or :class:`Distribution`), and two lists
        containing the list of marginal variables and conditioning variables

    Example
    -------
    Let :math:`\pi(x_0,x_1,x_2) = \pi_1(x_2|x_1,x_0) \pi_2(x_0|x_1) \pi_3(x_1)`.

    >>> factors = [(p1, [2], [1,0] ),
    >>>            (p2, [0], [1]  ),
    >>>            (p3, [1], []    )]
    >>> pi = FactorizedDistribution(factors)
    
    """
    def __init__(self, factors):
        input_dim = []
        self.factors = []
        for i, (pi, xidxs, yidxs) in enumerate(factors):
            if issubclass(type(pi), ConditionalDistribution):
                is_cond = True
            elif issubclass(type(pi), Distribution):
                is_cond = False
            else:
                raise TypeError("The %d-th factor is nor " % i + \
                                "Distribution or ConditionalDistribution")
            # pi has right number of inputs
            if len(set(xidxs)) != pi.dim:
                raise TypeError("The dimension of the %d-th " % i + \
                                "distribution does not match the input variables.")
            if is_cond and len(set(yidxs)) != pi.dim_y:
                raise TypeError("The conditioning dimension of the %d-th " % i + \
                                "distribution does not match the input variables.")
            if not is_cond and len(yidxs) != 0:
                raise TypeError("The conditioning dimension of the %d-th " % i + \
                                "distribution (Distribution) must be zero.")
            self.factors.append( (is_cond, pi, xidxs, yidxs) )
            input_dim.extend( xidxs )
        # Check total dimension and that all the marginals are available
        if len(input_dim) != len(set(input_dim)) or \
           (len(input_dim) != 0 and len(input_dim) != max(input_dim)+1):
            raise TypeError("Some marginals are not defined or multiply defined")
        super(FactorizedDistribution, self).__init__(len(input_dim))
        self.update_var_to_factor_map()    

    @property
    def var_to_factor_map(self):
        return self._var_to_factor_map

    def get_ncalls_tree(self, indent=""):
        out = super(FactorizedDistribution, self).get_ncalls_tree(indent)
        for _,pi,_,_ in self.factors:
            out += pi.get_ncalls_tree(indent + '  ')
        return out

    def get_nevals_tree(self, indent=""):
        out = super(FactorizedDistribution, self).get_nevals_tree(indent)
        for _,pi,_,_ in self.factors:
            out += pi.get_nevals_tree(indent + '  ')
        return out

    def get_teval_tree(self, indent=""):
        out = super(FactorizedDistribution, self).get_teval_tree(indent)
        for _,pi,_,_ in self.factors:
            out += pi.get_teval_tree(indent + '  ')
        return out

    def update_ncalls_tree(self, obj):
        super(FactorizedDistribution, self).update_ncalls_tree(obj)
        for (_,pi,_,_),(_,obj_pi,_,_) in zip(self.factors,obj.factors):
            pi.update_ncalls_tree(obj_pi)

    def update_nevals_tree(self, obj):
        super(FactorizedDistribution, self).update_nevals_tree(obj)
        for (_,pi,_,_),(_,obj_pi,_,_) in zip(self.factors,obj.factors):
            pi.update_nevals_tree(obj_pi)

    def update_teval_tree(self, obj):
        super(FactorizedDistribution, self).update_teval_tree(obj)
        for (_,pi,_,_),(_,obj_pi,_,_) in zip(self.factors,obj.factors):
            pi.update_teval_tree(obj_pi)

    def reset_counters(self):
        super(FactorizedDistribution, self).reset_counters()
        for (_,pi,_,_) in self.factors:
            pi.reset_counters()
        
    def append(self, factor):
        r""" Add a new factor to the distribution

        Args:
          factor (:class:`tuple`): tuple containing a factor
            (:class:`ConditionalDistribution` and/or :class:`Distribution`), and two
            tuples with the list of marginal variables and conditioning variables

        Example
        -------
        Let :math:`\pi(x_0,x_1,x_2) = \pi_1(x_2|x_1,x_0) \pi_2(x_0|x_1) \pi_3(x_1)` and let's
        add the factor :math:`\pi_4(x_3|x_0,x_1,x_2)`, obtaining:

        .. math::

           \pi(x_0,x_1,x_2,x_3) = \pi_4(x_3|x_0,x_1,x_2)\pi_1(x_2|x_1,x_0) \pi_2(x_0|x_1) \pi_3(x_1)

        >>> factor = (pi4, [3], [0,1,2])
        >>> pi.append(factor)
        
        """
        pi, xidxs, yidxs = factor
        if issubclass(type(pi), ConditionalDistribution):
            is_cond = True
        elif issubclass(type(pi), Distribution):
            is_cond = False
        else:
            raise TypeError("The factor is nor " + \
                            "Distribution or ConditionalDistribution")
        # pi has right number of inputs
        if len(xidxs) != pi.dim:
            raise TypeError("The dimension of the " + \
                            "distribution does not match the input variables.")
        if is_cond and len(yidxs) != pi.dim_y:
            raise TypeError("The conditioning dimension of the " + \
                            "distribution does not match the input variables.")
        if not is_cond and len(yidxs) != 0:
            raise TypeError("The conditioning dimension of the " + \
                            "distribution (Distribution) must be zero.")
        # Check xidxs contains new coordinates and that all the marginals are available
        if min(xidxs) < self.dim or len(xidxs) != len(set(xidxs)) or \
           self.dim + len(xidxs) != max(xidxs)+1:
            raise TypeError("Some marginals are not defined or multiply defined")
        self.factors.append( (is_cond, pi, xidxs, yidxs) )
        self.dim += len(xidxs)
        self.update_var_to_factor_map()

    def update_var_to_factor_map(self):
        self._var_to_factor_map = np.zeros(self.dim, dtype=int)
        for i, factor in enumerate(self.factors):
            for var in factor[2]:
                self._var_to_factor_map[var] = i

    @property
    def n_factors(self):
        return len(self.factors)

    def rvs(self, m, *args, **kwargs):
        out = np.zeros((m, self.dim))
        touched = np.zeros(self.dim, dtype=bool)
        factor_list = self.factors[:]
        while len(factor_list) > 0:
            factor = factor_list.pop()
            filo_queue = factor[3][:]
            while len(filo_queue) > 0: # Search all the sub-tree
                idx = filo_queue.pop()
                if not touched[idx]:
                    child_factor = self.factors[self.var_to_factor_map[idx]]
                    child_factor_is_cond = child_factor[0]
                    child_factor_pi = child_factor[1]
                    child_factor_vars = child_factor[2]
                    if child_factor_is_cond: # the factor is a conditional distribution
                        child_factor_cond_var = child_factor[3]
                        if all(touched[child_factor_cond_var]):
                            # all the conditioning variables have been touched
                            out[:,child_factor_vars] = child_factor_pi.rvs(
                                m, out[:,child_factor_cond_var], *args, **kwargs)
                            touched[child_factor_vars] = True
                            factor_list.remove(child_factor)
                        else:
                            filo_queue.append(idx) # Re-append the factor
                            filo_queue.extend(
                                [cv for cv in child_factor_cond_var if not touched[cv]])
                    else: # the factor is a distribution
                        out[:,child_factor_vars] = child_factor_pi.rvs(m, *args, **kwargs)
                        touched[child_factor_vars] = True
                        factor_list.remove(child_factor)
            if factor[0]:
                out[:,factor[2]] = factor[1].rvs(m, out[:,factor[3]], *args, **kwargs)
            else:
                out[:,factor[2]] = factor[1].rvs(m, *args, **kwargs)
            touched[factor[2]] = True
        return out

    @cached([('factor_list','n_factors')])
    @counted
    def log_pdf(self, x, params=None, idxs_slice=slice(None,None,None), cache=None):
        r""" Evaluate :math:`\log \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\log\pi`
            at the ``x`` points.
        """
        if x.shape[1] != self.dim:
            raise ValueError("The dimension of the input does not match the dimension " + \
                             "of the distribution")
        try:
            factor_list_cache = cache['factor_list_cache']
        except TypeError:
            factor_list_cache = [None] * self.n_factors
        out = np.zeros(x.shape[0])
        for (is_cond, pi, xidxs, yidxs), fcache in zip(self.factors, factor_list_cache):
            if is_cond:
                out += pi.log_pdf(x[:,xidxs], x[:,yidxs],
                                  params=params, idxs_slice=idxs_slice, cache=fcache)
            else:
                out += pi.log_pdf(x[:,xidxs], params=params, idxs_slice=idxs_slice,
                                  cache=fcache)
        return out

    @cached([('factor_list','n_factors')])
    @counted
    def grad_x_log_pdf(self, x, params=None, idxs_slice=slice(None,None,None), cache=None):
        r""" Evaluate :math:`\nabla_{\bf x} \log \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\nabla_x\log\pi` at the ``x`` points.
        """
        if x.shape[1] != self.dim:
            raise ValueError("The dimension of the input does not match the dimension " + \
                             "of the distribution")
        try:
            factor_list_cache = cache['factor_list_cache']
        except TypeError:
            factor_list_cache = [None] * self.n_factors
        out = np.zeros(x.shape)
        for (is_cond, pi, xidxs, yidxs), fcache in zip(self.factors, factor_list_cache):
            if is_cond:
                gx = pi.grad_x_log_pdf(x[:,xidxs], x[:,yidxs],
                                       params=params, idxs_slice=idxs_slice, cache=fcache)
                out[:,yidxs] += gx[:,pi.dim:]
            else:
                gx = pi.grad_x_log_pdf(x[:,xidxs], params=params, idxs_slice=idxs_slice,
                                       cache=fcache)
            out[:,xidxs] += gx[:,:pi.dim]
        return out

    @cached_tuple(['log_pdf','grad_x_log_pdf'],[('factor_list','n_factors')])
    @counted
    def tuple_grad_x_log_pdf(
            self, x, params=None, idxs_slice=slice(None,None,None), cache=None):
        r""" Evaluate :math:`\log \pi({\bf x}), \nabla_{\bf x} \log \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`tuple`) -- function and gradient evaluation
        """
        if x.shape[1] != self.dim:
            raise ValueError("The dimension of the input does not match the dimension " + \
                             "of the distribution")
        try:
            factor_list_cache = cache['factor_list_cache']
        except TypeError:
            factor_list_cache = [None] * self.n_factors
        lpdf = np.zeros(x.shape[0])
        gxlpdf = np.zeros(x.shape)
        for (is_cond, pi, xidxs, yidxs), fcache in zip(self.factors, factor_list_cache):
            if is_cond:
                fx, gx = pi.tuple_grad_x_log_pdf(
                    x[:,xidxs], x[:,yidxs],
                    params=params, idxs_slice=idxs_slice, cache=fcache)
                lpdf += fx
                gxlpdf[:,yidxs] += gx[:,pi.dim:]
            else:
                fx, gx = pi.tuple_grad_x_log_pdf(
                    x[:,xidxs], params=params, idxs_slice=idxs_slice, cache=fcache)
                lpdf += fx
            gxlpdf[:,xidxs] += gx[:,:pi.dim]
        return lpdf, gxlpdf

    @cached([('factor_list','n_factors')],False)
    @counted
    def hess_x_log_pdf(self, x, params=None,
                       idxs_slice=slice(None,None,None), cache=None):
        r""" Evaluate :math:`\nabla^2_{\bf x} \log \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) -- values of
            :math:`\nabla^2_x\log\pi` at the ``x`` points.
        """
        if x.shape[1] != self.dim:
            raise ValueError("The dimension of the input does not match the dimension " + \
                             "of the distribution")
        try:
            factor_list_cache = cache['factor_list_cache']
        except TypeError:
            factor_list_cache = [None] * self.n_factors
        m = x.shape[0]
        out = np.zeros( (m, self.dim, self.dim) )
        for (is_cond, pi, xidxs, yidxs), fcache in zip(self.factors, factor_list_cache):
            if is_cond:
                hx = pi.hess_x_log_pdf(x[:,xidxs], x[:,yidxs],
                                       params=params, idxs_slice=idxs_slice, cache=fcache)
                out[np.ix_(range(m),xidxs,yidxs)] += hx[:,:pi.dim,pi.dim:]
                out[np.ix_(range(m),yidxs,xidxs)] += hx[:,pi.dim:,:pi.dim]
                out[np.ix_(range(m),yidxs,yidxs)] += hx[:,pi.dim:,pi.dim:]
            else:
                hx = pi.hess_x_log_pdf(x[:,xidxs], params=params, idxs_slice=idxs_slice,
                                       cache=fcache)
            out[np.ix_(range(m),xidxs,xidxs)] += hx[:,:pi.dim,:pi.dim]
        return out

    @cached([('factor_list','n_factors')],False)
    @counted
    def action_hess_x_log_pdf(self, x, dx, params=None,
                              idxs_slice=slice(None,None,None), cache=None):
        r""" Evaluate :math:`\nabla^2_{\bf x} \log \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): direction
            on which to evaluate the Hessian
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) -- values of
            :math:`\nabla^2_x\log\pi` at the ``x`` points.
        """
        if x.shape[1] != self.dim:
            raise ValueError("The dimension of the input does not match the dimension " + \
                             "of the distribution")
        try:
            factor_list_cache = cache['factor_list_cache']
        except TypeError:
            factor_list_cache = [None] * self.n_factors
        m = x.shape[0]
        out = np.zeros( (m, self.dim) )
        for (is_cond, pi, xidxs, yidxs), fcache in zip(self.factors, factor_list_cache):
            if is_cond:
                ahx = pi.action_hess_x_log_pdf(
                    x[:,xidxs], x[:,yidxs], dx[:,xidxs], dx[:,yidxs],
                    params=params, idxs_slice=idxs_slice, cache=fcache)
                out[np.ix_(range(m),xidxs)] += ahx[:,:pi.dim]
                out[np.ix_(range(m),yidxs)] += ahx[:,pi.dim:]
            else:
                ahx = pi.action_hess_x_log_pdf(
                    x[:,xidxs],
                    dx[:,xidxs],
                    params=params,
                    idxs_slice=idxs_slice,
                    cache=fcache)
            out[np.ix_(range(m),xidxs)] += ahx[:,:pi.dim]
        return out
