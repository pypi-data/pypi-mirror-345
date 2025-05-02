#!/usr/bin/env python

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

import numpy as np

from ....Misc import required_kwargs
from ....External import DOLFIN_SUPPORT
from .... import DOLFIN as TMDOL

if DOLFIN_SUPPORT:
    import dolfin as dol
    import dolfin_adjoint as doladj
    if dol.__version__ == '2017.2.0':
        import mpi4py.MPI as MPI
        from petsc4py import PETSc

__all__ = [
    # Solvers
    "BurgersSolver",
    "AdjointFinalL2MismatchBurgersSolver",
    # Problems
    "FinalL2MismatchBurgersProblem"
]

###########
# SOLVERS #
###########

class BurgersSolver(TMDOL.Solver):
    r""" Defines the solver for the Burger's problem with respect to prescribed initial and boundary conditions and viscosity

    It discretizes the time dependent problem using the backward Euler method.

    .. math::

       \begin{cases}
       \partial_t u({\bf x},t) = \nabla \cdot (\mu \nabla u({\bf x},t)) - u({\bf x},t) \sum_{i=1}^d \partial_{x_i}u({\bf x},t) & {\bf x} \in \Omega \\
       u({\bf x},0) = u_0({\bf x}) & t = 0\\
       u({\bf x},t) = g({\bf x}) & {\bf x} \in \partial\Omega
       \end{cases}
    """
    @required_kwargs('VEFS', 'dt', 'nsteps', 'bcs')
    def set_up(self, **kwargs):
        r"""
        Kwargs:
          VEFS (:class:`FunctionSpace<dolfin.FunctionSpace>`): function space where the problem is defined on
          dt (float): time step
          bcs (list): list of boundary conditions
          nsteps (int): number of integration steps
        """
        self.dt      = kwargs.pop('dt')
        self.nsteps  = kwargs.pop('nsteps')
        self.bcs     = kwargs.pop('bcs')
        super(BurgersSolver, self).set_up(**kwargs)
    
    def solve(self, nu, u0):
        r"""
        Args:
          nu (float): viscosity
          u0 (:class:`ndarray<numpy.ndarray>`): initial conditions

        Returns:
          (:class:`ndarray<numpy.ndarray>`) -- solution :math:`u({\bf x}, T)`
        """
        nu = dol.Constant(nu)
        u0 = self.dof_to_fun(u0)        
        # Test function
        v = dol.TestFunction(self.VEFS)
        # Function
        u_next = dol.Function(self.VEFS)
        u = dol.Function(self.VEFS)
        # Define variational problem
        k = dol.Constant(self.dt)
        F = (u_next - u) / k * v * dol.dx + \
            dol.dot(nu * dol.grad(u_next), dol.grad(v)) * dol.dx + \
            u_next * u_next.dx(0) * v * dol.dx
        # Time stepping
        u.assign(u0)
        for i in range(self.nsteps):
            dol.solve(F==0, u_next, self.bcs)
            u.assign(u_next)
        return np.array( u.vector()[:] )
        
class AdjointFinalL2MismatchBurgersSolver(BurgersSolver):
    r""" Defines the adjoint for the Burger's problem with respect to initial conditions and viscosity

    It discretizes the time dependent problem using the backward Euler method.

    .. math::

       \begin{cases}
       \partial_t u({\bf x},t) = \nabla \cdot (\mu \nabla u({\bf x},t)) - u({\bf x},t) \sum_{i=1}^d \partial_{x_i}u({\bf x},t) & {\bf x} \in \Omega \\
       u({\bf x},0) = u_0({\bf x}) & t = 0\\
       u({\bf x},t) = g({\bf x}) & {\bf x} \in \partial\Omega
       \end{cases}

    and compute the functional :math:`J(u) = \int (u(T) - u_d)^2 dx`, along with the 
    gradients :math:`\partial_{u_0} J` and :math:`\partial_\nu J`.
    """
    def set_up(self, ud=None, **kwargs):
        r""" 
        If the optional keyword arguments are provided, then        
        builds the reduced functional to the be used in function evaluations.
        To do so, an forward solve must be run, so that doflin_adjoint can
        gather all the list of operations.

        Optional Kwargs:
          ud (:class:`ndarray<numpy.ndarray>`): data forthe final tie :math:`u_d`
        """
        super(AdjointFinalL2MismatchBurgersSolver, self).set_up(**kwargs)
        self.ud = ud
        
    @property
    def ud(self):
        return self._ud

    @ud.setter
    def ud(self, ud):
        self._ud = ud
        if self.ud is not None:
            self._set_up_reduced_functional()
        elif hasattr(self, 'Jhat'):
            delattr(self, 'Jhat')

    def new_function(self):
        r"""
        Overrides the function generator to created :class:`dolfin_adjoint.Function` 
        instead of ordinary :class:`dolfin.Function`.
        """
        return doladj.Function(self.VEFS)
            
    def __getstate__(self):
        r"""
        Avoids storing the :class:`dolfin_adjoint.ReducedFunctional` ``Jhat``
        """
        state = super(AdjointFinalL2MismatchBurgersSolver, self).__getstate__()
        state['ud'] = self.ud
        return state

    def __setstate__(self, state):
        r"""
        Reloads the :class:`dolfin_adjoint.ReducedFunctional` ``Jhat``
        """
        super(AdjointFinalL2MismatchBurgersSolver, self).__setstate__(state)
        self.ud = state['ud']
            
    def _set_up_reduced_functional(self):
        ud = self.dof_to_fun( self.ud )
        # Warm up run
        u0  = ud
        nu  = doladj.Constant(1.)
        # Test function
        v = dol.TestFunction(self.VEFS)
        # Function
        u_next = doladj.Function(self.VEFS)
        u = doladj.Function(self.VEFS)
        # Define variational problem
        k = doladj.Constant(self.dt)
        F = (u_next - u) / k * v * dol.dx + \
            nu * dol.inner(dol.grad(u_next), dol.grad(v)) * dol.dx + \
            u_next * u_next.dx(0) * v * dol.dx
        # Time stepping
        u.assign(u0)
        control_u = doladj.Control(u)
        for i in range(self.nsteps):
            doladj.solve(F==0, u_next, self.bcs)
            u.assign(u_next)
        # Assemble functional
        J = doladj.assemble(dol.inner(u-ud,u-ud) * dol.dx)
        # Create the reduced functional
        self.Jhat = doladj.ReducedFunctional(J, [doladj.Control(nu), control_u])
    
    def evaluate(self, nu, u0):
        r"""
        Args:
          nu (float): viscosity :math:`\nu`
          u0 (:class:`ndarray<numpy.ndarray>`): initial conditions :math:`u_0`

        Returns
          (float): :math:`J`
        """
        nu = doladj.Constant(nu)
        u0 = self.dof_to_fun(u0)
        return self.Jhat([nu, u0])

    def grad_x(self, nu, u0):
        r"""
        Args:
          nu (float): viscosity :math:`\nu`
          u0 (:class:`ndarray<numpy.ndarray>`): initial conditions :math:`u_0`

        Returns:
          (:class:`tuple`) -- :math:`( \partial_{u_0} J, \partial_{\nu} J )`

        .. note:: since the adjoint is used, the forward model evaluation must
           also be called. Therefore this function behaves exactly as
           :fun:`tuple_grad_x`, but returns only the gradient.
        """
        J, dJdnu, dJdu = self.tuple_grad_x(nu, u0)
        return dJdnu, dJdu
        
    def tuple_grad_x(self, nu, u0):
        r"""
        Args:
          nu (float): viscosity :math:`\nu`
          u0 (:class:`ndarray<numpy.ndarray>`): initial conditions :math:`u_0`

        Returns:
          (:class:`tuple`) -- :math:`( J, \partial_{\nu} J, \partial_{u_0} J )`
        """
        nu = doladj.Constant(nu)
        u0 = self.dof_to_fun(u0)
        J = self.Jhat([nu, u0])
        dJdnu, dJdu = self.Jhat.derivative()
        return J, dJdnu.values()[0], np.array( dJdu.vector()[:] )

#####################
# Specific problems #
#####################

class FinalL2MismatchBurgersProblem(AdjointFinalL2MismatchBurgersSolver):
    _init_args = [
        # Problem definition parameters
        'T', 'xl', 'xr', 'ul', 'ur', 
        # Discretization parameters
        'nels', 'order', 'nsteps'
    ]
    
    @required_kwargs(*_init_args)
    def __init__(self, **kwargs):
        r"""
        Kwargs:
          T (float): final time
          xl (float): left end of domain
          xr (float): right end of domain
          ul (float): left Dirichlet condition
          ur (float): right Dirichlet condition
          nels (int): number of discretization elements
          order (int): order of the finite elements
          nsteps (int): number of time steps
        """
        vars(self).update(kwargs)
        super(FinalL2MismatchBurgersProblem, self).__init__(**kwargs)

    def __getstate__(self):
        state = super(FinalL2MismatchBurgersProblem, self).__getstate__()
        state.update( (arg, getattr(self, arg)) for arg in FinalL2MismatchBurgersProblem._init_args )
        return state

    def set_up(self):
        # Set up mesh and function space
        self.mesh = dol.IntervalMesh(self.scomm, self.nels, self.xl, self.xr)
        self.VE = dol.FiniteElement("Lagrange", dol.interval, self.order)
        VEFS = dol.FunctionSpace(self.mesh, self.VE)
        self.coord = VEFS.tabulate_dof_coordinates().flatten()
        self.ndofs = self.coord.shape[0]
        # Set up boundary conditions
        bcs = [
            doladj.DirichletBC(
                VEFS, doladj.Constant(self.ul), lambda x: x[0] < self.xl + 10 * dol.DOLFIN_EPS),
            doladj.DirichletBC(
                VEFS, doladj.Constant(self.ur), lambda x: x[0] > self.xr - 10 * dol.DOLFIN_EPS),
        ]
        # Set up time discretization
        dt = self.T / self.nsteps
        super(FinalL2MismatchBurgersProblem, self).set_up(
            VEFS=VEFS, dt=dt, nsteps=self.nsteps, bcs=bcs
        )
