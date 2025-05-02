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

from TransportMaps.KL import minimize_kl_divergence
from TransportMaps.L2 import map_regression
from TransportMaps.ObjectBase import TMO
from TransportMaps.Misc import state_loader
from TransportMaps.Distributions import PullBackParametricTransportMapDistribution

__all__ = [
    'Builder',
    'L2RegressionBuilder',
    'KullbackLeiblerBuilder'
]


class Builder(TMO):
    r""" [Abstract] Basis builder class.

    Provides a :fun:`solve` for constructing a transport map
    """
    def solve(self, *args, **kwargs):
        raise NotImplementedError("To be implemented in sub-classes")


class L2RegressionBuilder(Builder):
    r""" Basis builder through :math:`\mathcal{L}^2` regression

    Given a map :math:`M`, fit a supplied parametric transport map :math:`T`
    through the solution of the :math:`\mathcal{L}^2` regression problem

    .. math::

       \arg\min_{\bf a}\left\Vert M - T \right\Vert_{\mathcal{L}^2} + \alpha \Vert {\bf a} \Vert_x

    where :math:`\alpha\Vert{\bf a}\Vert_x` is a regularization term, with
    respect to one of the available norms.

    Args:
      regression_params (dict): dictionary of regression parameters
    """
    def __init__(self, regression_params={}):
        self.regression_params = regression_params
        super(L2RegressionBuilder, self).__init__()
        
    def solve(self, transport_map, target_map, **extra_reg_params):
        params = {}
        for key in self.regression_params:
            params[key] = self.regression_params[key]
        for key in extra_reg_params:
            params[key] = extra_reg_params[key]
        log_list = map_regression(transport_map, target_map, **params)
        return transport_map, log_list


class KullbackLeiblerBuilder(Builder):
    r""" Basis builder through minimization of kl divergence

    Given distribution :math:`\nu_\rho` and :math:`\nu_\pi`,
    and the parametric transport map :math:`T[{\bf a}]`,
    provides the functionalities to solve the problem

    .. math::

       \arg\min_{\bf a}\mathcal{D}_{\rm KL}\left(
       T[{\bf a}]_\sharp\rho \Vert \pi\right)

    up to a chosen tolerance.
    """
    def __init__(
            self,
            validator=None,
            callback=None,
            callback_kwargs={},
            verbosity=0,
            interactive=False
    ):
        r"""
        Args:
          validator (:class:`Validator<TransportMaps.Diagnostic.Validator>`):
            validator to be used to check stability of the solution
          callback (function): function taking a map and optional additional arguments
            which is called whenever it is deemed necessary by the chosen algorithm
            (e.g. for storing purposes)
          callback_kwargs (dict): additional arguments to be provided to the function
            ``callback``.
          verbosity (int): level of verbosity of the builder
        """
        self.validator = validator
        self.callback = callback
        self.callback_kwargs = callback_kwargs
        self.verbosity = verbosity
        self.interactive = interactive
        super(KullbackLeiblerBuilder, self).__init__()

    def __getstate__(self):
        out = super(KullbackLeiblerBuilder, self).__getstate__()
        out.pop('callback', None)
        out.pop('callback_kwargs', None)
        return out

    def __setstate__(self, state):
        super(KullbackLeiblerBuilder, self).__setstate__(state)

    @state_loader(
        keys = [
            'transport_map',
            'base_distribution',
            'target_distribution',
            'solve_params']
    )
    def solve(
            self,
            transport_map=None,
            base_distribution=None,
            target_distribution=None,
            solve_params=None,
            state=None,
            mpi_pool=None
    ):
        r"""
        Args
          transport_map (:class:`TransportMap<TransportMaps.Maps.TransportMap>`):
            transport map :math:`T`
          base_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            distribution :math:`\nu_\rho`
          target_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            distribution :math:`\nu_\pi`
          solve_params (dict): dictionary of parameters for solution
          state (:class:`TransportMaps.DataStorageObject`): 
            if provided, it must contain all the information needed for reloading,
            or a handle to an empty storage object which can be externally stored.
            If ``state`` contains the keys corresponding to arguments to this function, 
            they will be used instead of the input themselves.
      
        Returns:
          (:class:`TransportMaps.Maps.TransportMap`) -- the transport map fitted.
        """
        
        if self.validator is None:
            if 'x' not in state.solve_params:
                x, w = state.base_distribution.quadrature(
                    qtype=state.solve_params['qtype'],
                    qparams=state.solve_params['qparams']
                )
                state.solve_params['x'] = x
                state.solve_params['w'] = w
            pull_tar = PullBackParametricTransportMapDistribution(
                state.transport_map,
                state.target_distribution)
            log = minimize_kl_divergence(
                state.base_distribution,
                pull_tar,
                mpi_pool=mpi_pool,
                **state.solve_params)
        else:
            log = self.validator.solve_to_tolerance(
                state.transport_map,
                state.base_distribution,
                state.target_distribution,
                state.solve_params,
                mpi_pool=mpi_pool
            )
        return state.transport_map, log
