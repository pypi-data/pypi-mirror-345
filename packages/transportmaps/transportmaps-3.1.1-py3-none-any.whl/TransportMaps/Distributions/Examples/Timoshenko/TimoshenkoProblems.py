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
    "TimoshenkoSolver",
    "AdjointTimoshenkoSolver",
    "ClampedTimoshenkoProblem"
]

###########
# SOLVERS #
###########

class TimoshenkoSolver(TMDOL.Solver):
    @required_kwargs('VEFS', 'UEFS', 'AUXFS', 'bcs')
    def set_up(self, **kwargs):
        self.bcs = kwargs.pop('bcs')
        self.UEFS = kwargs.pop('UEFS')
        self.AUXFS = kwargs.pop('AUXFS')
        self.A = self.thickness * self.width
        self.I = self.width * self.thickness**3. / 12.
        super(TimoshenkoSolver, self).set_up(**kwargs)
        # Set up dirac dela
        self.nrm_dirac = dol.assemble(
            dol.Expression(
                "exp(-.5 * pow(x[0]-L,2) / pow(eps,2))",
                pi=np.pi, eps=1e-4, L=self.length,
                element=self.VEFS.sub(0).ufl_element()
            ) * dol.project(dol.Constant(1.), self.UEFS) * dol.dx
        )
        self.dirac = dol.Expression(
            "1./nrm * exp(-.5 * pow(x[0]-L,2) / pow(eps,2))",
            nrm=self.nrm_dirac, pi=np.pi, eps=1e-4, L=self.length,
            element=self.VEFS.sub(0).ufl_element()
        )
        
    def new_function(self, FS):
        return dol.Function(FS)

    def project(self, f, FS):
        return dol.project(f, FS)
        
    def dof_to_fun(self, x):
        ndofs = len(x)
        # Load dofs into function in auxiliary FS
        fun = self.new_function(self.AUXFS)
        if dol.__version__ == '2017.2.0':
            fun.vector().set_local(x, np.arange(ndofs, dtype=np.intc))
        else:
            fun.vector().set_local(x)
        fun.vector().apply('insert')
        return fun
        
    def solve(self, E):
        r"""
        Args:
          E (:class:`ndarray<numpy.ndarray>`): spatially varying Young's modulus (GPa)
        """
        E = self.dof_to_fun(E)
        # Other params
        A = dol.Constant(self.A)
        I = dol.Constant(self.I)
        kappa = dol.Constant(self.kappa)
        r = dol.Constant(2 * (1+self.poisson)) # G = E/(2*(1+nu))
        giga = dol.Constant(1e9)
        # Point load (at the end)
        q = dol.Constant(self.q)
        # Test and trial functions
        u_ = dol.TestFunction(self.VEFS)
        ub = dol.TrialFunction(self.VEFS)
        (w_, phi_) = dol.split(u_)
        (wb, phib) = dol.split(ub)
        # Define variational problem
        a = giga*E * I * dol.inner(dol.grad(phi_), dol.grad(phib)) * dol.dx + \
            kappa * A * (giga*E / r) * dol.dot(dol.grad(w_)[0]-phi_, dol.grad(wb)[0]-phib) * dol.dx
        L = q * self.dirac * w_ * dol.dx
        # Solve
        u = dol.Function(self.VEFS)
        dol.solve(a == L, u, self.bcs)
        w,_ = dol.split(u)
        return w

class AdjointTimoshenkoSolver(TimoshenkoSolver):
    r"""

    .. math::
  
       J(u) = \sum_{i=1}^{n_\text{obs}} w_i \left( y_i - \int u s_i dx \right)^2

    """

    _serializable = [
        '_sens_pos_list',
        '_sens_geo_eps',
        '_obs_list',
        '_weights_list',
    ]

    def __init__(self, *args, **kwargs):
        super(AdjointTimoshenkoSolver, self).__init__(*args, **kwargs)
        self._sens_pos_list = None
        self._sens_geo_eps = None
        self._obs_list = None
        self._weights_list = None
        self._sensors_list = None
    
    def set_up(self, **kwargs):
        super(AdjointTimoshenkoSolver, self).set_up(**kwargs)
        # Set up diract delta
        self.dirac = doladj.Expression(
            "1./nrm * exp(-.5 * pow(x[0]-L,2) / pow(eps,2))",
            nrm=self.nrm_dirac, pi=np.pi, eps=1e-4, L=self.length,
            element=self.VEFS.sub(0).ufl_element()
        )

    def set_sensors_list(self, sens_pos_list, sens_geo_eps):
        self._sens_pos_list = sens_pos_list
        self._sens_geo_eps = sens_geo_eps
        if self._sens_pos_list is not None and self._sens_geo_eps is not None:
            nrm_list = [
                dol.assemble(
                    doladj.Expression(
                        'exp(-.5 * pow(p-x[0],2) / pow(eps,2))',
                        pi=np.pi, p=p, eps=self._sens_geo_eps,
                        element=self.AUXFS.ufl_element()
                    ) * dol.project(dol.Constant(1.), self.AUXFS) * dol.dx
                )
                for p in self._sens_pos_list
            ]
            sens_expr = '1./nrm * exp(-.5 * pow(p-x[0],2) / pow(eps,2))'
            self._sensors_list = [
                doladj.Expression(
                    sens_expr, nrm=nrm, pi=np.pi, p=p,
                    eps=self._sens_geo_eps,
                    element=self.AUXFS.ufl_element()
                )
                for p, nrm in zip(self._sens_pos_list, nrm_list)
            ]
        else:
            self._sensors_list = None

    def set_data(self, obs_list, sens_pos_list, sens_geo_eps, weights_list=None):
        if weights_list is None and obs_list is not None: weights_list = [1.] * len(obs_list)
        if obs_list is not None and sens_pos_list is not None and \
           not (len(obs_list) == len(sens_pos_list) == len(weights_list)):
            raise ValueError(
                "Number of sensors, observations and weights must be the same."
            )
        self.set_sensors_list(sens_pos_list, sens_geo_eps)
        self._obs_list = obs_list
        self._weights_list = weights_list
        if self._sensors_list is not None and self._obs_list is not None:
            self._set_up_reduced_functional()
        elif hasattr(self, 'Jhat'):
            delattr(self, 'Jhat')
            
    def __getstate__(self):
        d = super(AdjointTimoshenkoSolver, self).__getstate__()
        d.update( (arg, getattr(self, arg)) for arg in AdjointTimoshenkoSolver._serializable )
        return d

    def __setstate__(self, state):
        super(AdjointTimoshenkoSolver, self).__setstate__(state)
        self.set_up()
        self.set_data(
            self._obs_list,
            self._sens_pos_list,
            self._sens_geo_eps,
            self._weights_list
        )
        
    @property
    def sensors_list(self):
        return self._sensors_list

    @property
    def obs_list(self):
        return self._obs_list

    @property
    def weights_list(self):
        return self._weights_list

    def new_function(self, FS):
        return doladj.Function(FS)

    def project(self, f, FS):
        return doladj.project(f, FS)

    def _set_up_reduced_functional(self):
        r"""
        ``E`` is in GPa
        """
        # Warm up setting
        E = self.dof_to_fun(200 * np.ones(self.nels+1))
        # Set up controls
        contrE = doladj.Control(E)
        # Other parameters
        A = doladj.Constant(self.A)
        I = doladj.Constant(self.I)
        kappa = doladj.Constant(self.kappa)
        r = doladj.Constant(2 * (1+self.poisson)) # G = E/(2*(1+nu))
        giga = doladj.Constant(1e9)
        q = doladj.Constant(self.q)
        # Test and trial functions
        u_ = dol.TestFunction(self.VEFS)
        ub = dol.TrialFunction(self.VEFS)
        (w_, phi_) = dol.split(u_)
        (wb, phib) = dol.split(ub)
        # Define variational problem
        a = giga*E * I * dol.inner(dol.grad(phi_), dol.grad(phib)) * dol.dx + \
            kappa * A * (giga*E / r) * dol.dot(dol.grad(w_)[0]-phi_, dol.grad(wb)[0]-phib) * dol.dx
        L = q * self.dirac * w_ * dol.dx
        # Solve
        u = doladj.Function(self.VEFS)
        doladj.solve(a == L, u, self.bcs)
        w,_ = dol.split(u)
        # Create objective
        J = doladj.AdjFloat(0.)
        for obs, sensor, weight in zip(
                self.obs_list, self.sensors_list, self.weights_list):
            # Evaluate sensor functional
            J += doladj.AdjFloat(weight) * (
                doladj.AdjFloat(obs) - doladj.assemble(w * sensor * dol.dx)
            )**2
        # Create reduced functional
        self.Jhat = doladj.ReducedFunctional(J, contrE)

    def observe(self, E):
        r"""
        Args:
          E (:class:`ndarray<numpy.ndarray>`): spatially varying Young's modulus (GPa)

        Returns:
          observations though the sensors
        """
        u = self.solve(E)
        out = np.zeros(len(self.sensors_list))
        for i, sensor in enumerate(self.sensors_list):
            out[i] = dol.assemble(u * sensor * dol.dx)
        return out

    def evaluate(self, E):
        r"""
        Args:
          E (:class:`ndarray<numpy.ndarray>`): spatially varying Young's modulus (GPa)
        """
        E = self.dof_to_fun(E)
        return self.Jhat(E)

    def grad_x(self, E):
        r"""
        Args:
          E (:class:`ndarray<numpy.ndarray>`): spatially varying Young's modulus (GPa)
        """
        J, dJdE = self.tuple_grad_x(E)
        return dJdE

    def tuple_grad_x(self, E):
        r"""
        Args:
          E (:class:`ndarray<numpy.ndarray>`): spatially varying Young's modulus (GPa)
        """
        E = self.dof_to_fun(E)
        J = self.Jhat(E)
        dJdE = self.Jhat.derivative()
        return J, dJdE.vector().get_local()

class ClampedTimoshenkoProblem(AdjointTimoshenkoSolver):
    _init_args = [
        # Physical parameters
        'q', 'thickness', 'width', 'length', 'kappa', 'poisson',
        # Discretization parameters
        'nels'
    ]

    @required_kwargs(*_init_args)
    def __init__(self, **kwargs):
        r"""
        Kwargs:
          q (:class:`ndarray<numpy.ndarray>`): spatially distributed load
          thickness (float): thickness of the beam
          width (float): width of the beam
          length (float): length of the beam
          kappa (float): Timoshenko shear adjustment coefficient
          nels (int): number of elements
        """
        vars(self).update(kwargs)
        super(ClampedTimoshenkoProblem, self).__init__()

    def __getstate__(self):
        state = super(ClampedTimoshenkoProblem, self).__getstate__()
        state.update( (arg, getattr(self, arg)) for arg in ClampedTimoshenkoProblem._init_args )
        return state

    def set_up(self):
        # Set up mesh and function spaces
        self.mesh = dol.IntervalMesh(self.scomm, self.nels, 0, self.length)
        self.UE = dol.FiniteElement("CG", self.mesh.ufl_cell(), 2)
        UEFS = dol.FunctionSpace(self.mesh, self.UE)
        self.PE = dol.FiniteElement("CG", self.mesh.ufl_cell(), 1)
        VEFS = dol.FunctionSpace(self.mesh, self.UE * self.PE)
        self.coord = VEFS.tabulate_dof_coordinates().flatten()
        self.ndofs = self.coord.shape[0]
        # Create function space where to define input functionals
        AUXFS = dol.FunctionSpace( 
            self.mesh, dol.FiniteElement("CG", self.mesh.ufl_cell(), 1)
        )
        self.aux_coord = AUXFS.tabulate_dof_coordinates().flatten()
        self.aux_ndofs = self.aux_coord.shape[0]
        # Set boundary conditions
        bcs = [
            doladj.DirichletBC(
                VEFS.sub(0), dol.Constant(0.), lambda x: dol.near(x[0], 0)),
            doladj.DirichletBC(
                VEFS.sub(1), dol.Constant(0.), lambda x: dol.near(x[0], 0))
        ]
        # Set up super classes
        super(ClampedTimoshenkoProblem, self).set_up(
            VEFS=VEFS, UEFS=UEFS, AUXFS=AUXFS, bcs=bcs)
