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

from TransportMaps.Misc import counted, cached, cached_tuple, get_sub_cache
from TransportMaps.Distributions import Distribution

__all__ = ['BayesPosteriorDistribution']

class BayesPosteriorDistribution(Distribution):
    r""" Given a log-likelihood and a prior, assemble the posterior density

    Given the log-likelihood :math:`\log\pi({\bf y}\vert{\bf x})` and the
    prior density :math:`\pi({\bf x})`, assemble the Bayes' posterior density

    .. math::

      \pi({\bf x}\vert {\bf y}) \propto \pi({\bf y}\vert{\bf x}) \pi({\bf x})

    Args:
      logL (:class:`LogLikelihood<TransportMaps.Likelihoods.LogLikelihood>`):
        log-likelihood :math:`\log\pi({\bf y}\vert{\bf x})`
      prior (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        prior density :math:`\pi({\bf x})`
    """
    def __init__(self, logL, prior):
        self.prior = prior
        self.logL = logL
        super(BayesPosteriorDistribution, self).__init__(prior.dim)
    
    def get_ncalls_tree(self, indent=""):
        out = super(BayesPosteriorDistribution, self).get_ncalls_tree(indent)
        out += self.prior.get_ncalls_tree(indent + '  ')
        out += self.logL.get_ncalls_tree(indent + '  ')
        return out

    def get_nevals_tree(self, indent=""):
        out = super(BayesPosteriorDistribution, self).get_nevals_tree(indent)
        out += self.prior.get_nevals_tree(indent + '  ')
        out += self.logL.get_nevals_tree(indent + '  ')
        return out

    def get_teval_tree(self, indent=""):
        out = super(BayesPosteriorDistribution, self).get_teval_tree(indent)
        out += self.prior.get_teval_tree(indent + '  ')
        out += self.logL.get_teval_tree(indent + '  ')
        return out

    def update_ncalls_tree(self, obj):
        super(BayesPosteriorDistribution, self).update_ncalls_tree(obj)
        self.prior.update_ncalls_tree(obj.prior)
        self.logL.update_ncalls_tree(obj.logL)

    def update_nevals_tree(self, obj):
        super(BayesPosteriorDistribution, self).update_nevals_tree(obj)
        self.prior.update_nevals_tree(obj.prior)
        self.logL.update_nevals_tree(obj.logL)

    def update_teval_tree(self, obj):
        super(BayesPosteriorDistribution, self).update_teval_tree(obj)
        self.prior.update_teval_tree(obj.prior)
        self.logL.update_teval_tree(obj.logL)

    def reset_counters(self):
        super(BayesPosteriorDistribution, self).reset_counters()
        self.prior.reset_counters()
        self.logL.reset_counters()
        
    @property
    def observations(self):
        return self.logL.y

    @cached([("logL",None),("prior",None)])
    @counted
    def log_pdf(self, x, idxs_slice=slice(None,None,None), cache=None, **kwargs):
        r""" Evaluate :math:`\log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\log\pi`
            at the ``x`` points.
        """
        logL_cache, prior_cache = get_sub_cache(cache, ("logL",None), ("prior",None))
        return self.logL.evaluate(x, idxs_slice=idxs_slice, cache=logL_cache)[:,0] \
            + self.prior.log_pdf(x, idxs_slice=idxs_slice, cache=prior_cache)

    @cached([("logL",None),("prior",None)])
    @counted
    def grad_x_log_pdf(self, x, idxs_slice=slice(None,None,None),
                       cache=None, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf x} \log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\nabla_{\bf x}\log\pi` at the ``x`` points.
        """
        logL_cache, prior_cache = get_sub_cache(cache, ("logL",None), ("prior",None))
        return self.logL.grad_x(x, idxs_slice=idxs_slice, cache=logL_cache)[:,0,:] \
            + self.prior.grad_x_log_pdf(x, idxs_slice=idxs_slice, cache=prior_cache)

    @cached_tuple(['log_pdf','grad_x_log_pdf'],[("logL",None),("prior",None)])
    @counted
    def tuple_grad_x_log_pdf(self, x, idxs_slice=slice(None,None,None),
                             cache=None, **kwargs):
        r""" Evaluate :math:`\left(\log \pi({\bf x}\vert{\bf y}), \nabla_{\bf x} \log \pi({\bf x}\vert{\bf y})\right)`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`tuple`) --
            :math:`\left(\log \pi({\bf x}\vert{\bf y}), \nabla_{\bf x} \log \pi({\bf x}\vert{\bf y})\right)`
        """
        logL_cache, prior_cache = get_sub_cache(cache, ("logL",None), ("prior",None))
        ll, gxll = self.logL.tuple_grad_x(x, idxs_slice=idxs_slice, cache=logL_cache)
        lpr, gxlpr = self.prior.tuple_grad_x_log_pdf(
            x, idxs_slice=idxs_slice, cache=prior_cache)
        ev = ll[:,0] + lpr
        gx = gxll[:,0,:] + gxlpr
        return (ev, gx)

    @cached([("logL",None),("prior",None)],False)
    @counted
    def hess_x_log_pdf(self, x, idxs_slice=slice(None,None,None), cache=None, **kwargs):
        r""" Evaluate :math:`\nabla^2_{\bf x} \log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) -- values of
            :math:`\nabla^2_{\bf x}\log\pi` at the ``x`` points.
        """
        logL_cache, prior_cache = get_sub_cache(cache, ("logL",None), ("prior",None))
        return self.logL.hess_x(x, idxs_slice=idxs_slice, cache=logL_cache)[:,0,:,:] \
            + self.prior.hess_x_log_pdf(x, idxs_slice=idxs_slice, cache=prior_cache)

    @cached([("logL",None),("prior",None)],False)
    @counted
    def action_hess_x_log_pdf(self, x, dx,
                              idxs_slice=slice(None,None,None), cache=None, **kwargs):
        r""" Evaluate :math:`\langle\nabla^2_{\bf x} \log \pi({\bf x}\vert{\bf y}), \delta{\bf x}\rangle`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): direction
            on which to evaluate the Hessian
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\langle\nabla^2_{\bf x} \log \pi({\bf x}\vert{\bf y}), \delta{\bf x}\rangle` at the ``x`` points.
        """
        logL_cache, prior_cache = get_sub_cache(cache, ("logL",None), ("prior",None))
        return self.logL.action_hess_x(
            x, dx, idxs_slice=idxs_slice, cache=logL_cache)[:,0,:] \
            + self.prior.action_hess_x_log_pdf(
                x, dx, idxs_slice=idxs_slice, cache=prior_cache)