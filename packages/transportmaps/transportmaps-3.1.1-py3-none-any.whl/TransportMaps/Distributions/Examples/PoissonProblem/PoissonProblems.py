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

from ....Misc import required_kwargs, deprecate
from ....External import DOLFIN_SUPPORT
from .... import DOLFIN as TMDOL

if DOLFIN_SUPPORT:
    import dolfin as dol
    if dol.__version__ == '2017.2.0':
        import mpi4py.MPI as MPI
        from petsc4py import PETSc
    dol.set_log_level(30)

__all__ = [
    # Solvers
    'MixedPoissonSolver',
    'PoissonSolver',
    # Problems
    'get_Poisson_problem_solver',
    'PoissonSolverProblem1',
]

###########
# SOLVERS #
###########

class MixedPoissonSolver(TMDOL.Solver):
    r""" Defines the solver (and adjoints) for the Poisson problem.

    .. math::

       \begin{cases}
         - \nabla \cdot \kappa({\bf x}) \nabla u({\bf x}) = f({\bf x}) & {\bf x} \in \Omega \\
         u({\bf x}) = g({\bf x}) & {\bf x} \in \Gamma_D \\
         - \frac{\partial u}{\partial n}({\bf x}) = h({\bf x}) & {\bf x} \in \Gamma_N
       \end{cases}

    where :math:`\Omega`, :math:`\Gamma_D \subset \partial\Omega`
    and :math:`\Gamma_N \subset \partial\Omega`.
    """
    @required_kwargs('VEFS', 'f', 'h', 'bcs', 'bcs_adj')
    def set_up(self, **kwargs):
        self.f           = kwargs.pop('f')
        self.h           = kwargs.pop('h')
        self.bcs         = kwargs.pop('bcs')
        self.bcs_adj     = kwargs.pop('bcs_adj')
        super(MixedPoissonSolver, self).set_up(**kwargs)

    def _solve(self, f, kappa, bcs):
        # Trial an test functions
        u = dol.TrialFunction(self.VEFS)
        v = dol.TestFunction(self.VEFS)
        # Forms
        lhs = dol.inner(dol.nabla_grad(u), kappa * dol.nabla_grad(v)) * dol.dx
        if isinstance(f, dol.cpp.la.GenericVector):
            # An already assembled right handside has been provided
            LHS = dol.assemble(lhs)
            for bc in bcs:
                bc.apply(LHS, f)
            w = dol.Function(self.VEFS)
            W = w.vector()
            dol.solve(LHS, W, f)
        else:
            rhs = f * v * dol.dx - self.h * v * dol.ds
            # Solve
            w = dol.Function(self.VEFS)
            dol.solve(lhs == rhs, w, bcs)
        return w
    
    def solve(self, kappa):
        return self._solve(self.f, kappa, self.bcs)

    def solve_adjoint(self, f, kappa):
        return self._solve(f, kappa, self.bcs_adj)

    def solve_action_hess_adjoint(self, dx, usol, kappa):
        # Trial and test functions
        u = dol.TrialFunction(self.VEFS)
        v = dol.TestFunction(self.VEFS)
        # Forms
        lhs = dol.inner(dol.nabla_grad(u), kappa * dol.nabla_grad(v)) * dol.dx 
        rhs = dol.inner(dol.nabla_grad(usol), dx * dol.nabla_grad(v)) * dol.dx
        # Solve
        w = dol.Function(self.VEFS)
        dol.solve(lhs == rhs, w, self.bcs_adj)
        return w

class PureNeumannPoissonSolver(TMDOL.Solver):
    r""" Defines the solver (and adjoints) for the Poisson problem.

    .. math::

       \begin{cases}
         - \nabla \cdot \kappa({\bf x}) \nabla u({\bf x}) = f({\bf x}) & {\bf x} \in \Omega \\
         \nabla u({\bf x}) \cdot n({\bf x}) = h({\bf x}) & {\bf x} \in \Gamma_N
       \end{cases}

    with the constraint

    .. math::

       \int_\Omega u dx = 0

    where :math:`\Omega`, :math:`\Gamma_N \subset \partial\Omega`
    """
    @required_kwargs('VEFS', 'f', 'h')
    def set_up(self, **kwargs):
        self.f = kwargs.pop('f')
        self.h = kwargs.pop('h')
        super(PureNeumannPoissonSolver, self).set_up(**kwargs)
    def _solve(self, f, h, kappa):
        # Trial an test functions
        (u, c) = dol.TrialFunction(self.VEFS)
        (v, d) = dol.TestFunction(self.VEFS)
        # Forms
        LagMult = (c*v + u*d) * dol.ds
        lhs = dol.inner(dol.nabla_grad(u), kappa * dol.nabla_grad(v)) * dol.dx + LagMult
        rhs = f * v * dol.dx + h * v * dol.ds
        # Solve
        w = dol.Function(self.VEFS)
        dol.solve(lhs == rhs, w)
        (u, c) = w.split(deepcopy=True)
        return u

class PoissonSolver(MixedPoissonSolver):
    @deprecate(
        'PoissonSolver',
        '3.0',
        'MixedPoissonSolver'
    )
    def __init__(self, *args, **kwargs):
        super(PoissonSolver, self).__init__(*args, **kwargs)


#####################
# SPECIFIC PROBLEMS #
#####################

def get_Poisson_problem_solver(n, ndiscr):
    if n == 1:
        return PoissonSolverProblem1(ndiscr)
    else:
        raise NotImplementedError("Option %d not available." % n)
        
class PoissonSolverProblem1(MixedPoissonSolver):
    r""" Defines the solver (and adjoints) for the following setting of the Poisson problem.

    .. math::

       \begin{cases}
         - \nabla \cdot \kappa({\bf x}) \nabla u({\bf x}) = 0 & {\bf x} \in [0,1]^2\Omega \\
         u({\bf x}) = 0 & {\bf x}_1 = 0  \\
         u({\bf x}) = 1 & {\bf x}_1 = 1  \\
         - \frac{\partial u}{\partial n}({\bf x}) = 0 & {\bf x}_2 \in {0,1}
       \end{cases}

    Args:
      ndiscr (int): number of discretization points per dimension
    """
    def __init__(self, ndiscr):
        self.ndiscr = ndiscr
        super(PoissonSolverProblem1, self).__init__()
    def __getstate__(self):
        dd = super(PoissonSolverProblem1, self).__getstate__()
        dd['ndiscr'] = self.ndiscr
        return dd
    def set_up(self, **kwargs):
        # Building mesh and function space
        try:
            self.mesh = kwargs['mesh']
        except KeyError:
            if not hasattr(self, 'mesh'):
                self.mesh = dol.UnitSquareMesh(self.scomm,self.ndiscr, self.ndiscr)
            else: # Mesh already set
                return 
        self.VE = dol.FiniteElement("Lagrange", dol.triangle, 1)
        VEFS = dol.FunctionSpace(self.mesh, self.VE)
        self.coord = VEFS.tabulate_dof_coordinates().reshape((-1,2))
        self.ndofs = self.coord.shape[0]
        # Setting up functions and boundary conditions
        def b0(x, on_boundary):
            tol = 1e-14
            return on_boundary and dol.near(x[0], 0, tol)
        def b1(x, on_boundary):
            tol = 1e-14
            return on_boundary and dol.near(x[0], 1, tol)
        self.bc_loc_list = [b0, b1]
        bcs = [
            dol.DirichletBC(VEFS, dol.Constant(0.), self.bc_loc_list[0]),
            dol.DirichletBC(VEFS, dol.Constant(1.), self.bc_loc_list[1])
        ]
        bcs_adj = [
            dol.DirichletBC(VEFS, dol.Constant(0.), bc)
            for bc in self.bc_loc_list
        ]
        f = dol.Constant(0.)
        h = dol.Constant(0.)
        super(PoissonSolverProblem1, self).set_up(
            VEFS=VEFS, f=f, h=h, bcs=bcs, bcs_adj=bcs_adj
        )
