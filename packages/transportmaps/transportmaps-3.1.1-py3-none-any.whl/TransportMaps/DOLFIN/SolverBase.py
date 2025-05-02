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

from TransportMaps.ObjectBase import TMO
from TransportMaps.Misc import cmdinput, required_kwargs
from TransportMaps.External import DOLFIN_SUPPORT

if DOLFIN_SUPPORT:
    import dolfin as dol
    if dol.__version__ == '2017.2.0':
        import mpi4py.MPI as MPI
        from petsc4py import PETSc
    dol.set_log_level(30)

__all__ = [
    'Solver'
]
    
class Solver(TMO):
    r""" [Abstract] Generic class for a PDE solver

    It offers only stub functions and a function to convert degrees of freedom 
    to fenics functions defined on the prescribed approximation space.
    """
    def __init__(self, **kwargs):
        super(Solver, self).__init__()
        if not DOLFIN_SUPPORT:
            raise ImportError("Please install FENICS (dolfin) in order to use this class")
        self._dolfin_version = dol.__version__
        self.init_mpi()
        self.set_up(**kwargs)

    def init_mpi(self):
        # Taking care of MPI
        if dol.__version__ == '2017.2.0':
            self.wcomm = MPI.COMM_WORLD
            self.scomm = PETSc.Comm(MPI.COMM_SELF)
        else:
            self.wcomm = dol.MPI.comm_world
            self.scomm = dol.MPI.comm_self

    def __getstate__(self):
        if hasattr(self, '_dolfin_version'):
            return {'_dolfin_version': self._dolfin_version}
        else:
            return {}
            
    def __setstate__(self, state):
        super(Solver, self).__setstate__(state)
        if hasattr(self, '_dolfin_version'):
            if self._dolfin_version != dol.__version__:
                self.logger.warn(
                    "The dolfin version of the solver does not match " + \
                    "the dolfin version that was used to create it. " + \
                    "Dolfin version expected: " + self._dolfin_version + ". " + \
                    "Dolfin version installed: " + dol.__version__ + "."
                )
                instr = None
                while instr not in ['y', 'Y', 'n', 'N']:
                    instr = cmdinput("Do you want to continue? [y/N] ", 'N')
                if instr in ['n', 'N']:
                    exit(0)
        else:
             self.logger.warn(
                 "The solver has no defined dolfin version. " + \
                 "This may be incompatible with the installed version."
             )
        self.init_mpi()
        self.set_up()
            
    @required_kwargs('VEFS')
    def set_up(self, **kwargs):
        self.VEFS = kwargs.pop('VEFS')
    
    def solve(self, *args, **kwargs):
        raise NotImplementedError("To be implemented in sub-classes")

    def solve_adjoint(self, *args, **kwargs):
        raise NotImplementedError("To be implemented in sub-classes")

    def solve_action_hess_adjoint(self, *args, **kwargs):
        raise NotImplementedError("To be implemented in sub-classes")

    def new_function(self):
        return dol.Function(self.VEFS)

    def dof_to_fun(self, x):
        ndofs = len(x)
        fun = self.new_function()
        if dol.__version__ == '2017.2.0':
            fun.vector().set_local(x, np.arange(ndofs, dtype=np.intc))
        else:
            fun.vector().set_local(x)
        fun.vector().apply('insert')
        return fun
