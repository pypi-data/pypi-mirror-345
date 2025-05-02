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

__all__ = [
    'MPI_SUPPORT', 'PLOT_SUPPORT',
    'H5PY_SUPPORT', 'PYHMC_SUPPORT',
    'DARKSPARK_SUPPORT',
    'DOLFIN_SUPPORT',
    'SUITESPARSE_SUPPORT'
]

import warnings

try:
    import mpi_map
    from mpi4py import MPI
except ImportError:
    # warnings.warn("MPI support disabled: install mpi4py and mpi_map if needed.")
    MPI_SUPPORT = False
else:
    MPI_SUPPORT = True
    # __all__ += ['mpi_map']

try:
    import matplotlib as mpl
    import matplotlib.pyplot as plt
except ImportError:
    PLOT_SUPPORT = False
else:
    PLOT_SUPPORT = True
    # __all__ += ['mpl', 'plt']

try:
    import h5py
except ImportError:
    warnings.warn("H5 file support disabled: install h5py if needed.")
    H5PY_SUPPORT = False
else:
    H5PY_SUPPORT = True
    # __all__ += ['h5py']

try:
    import pyhmc
except ImportError:
    PYHMC_SUPPORT = False
else:
    PYHMC_SUPPORT = True

try:
    import DARKSparK
except ImportError:
    DARKSPARK_SUPPORT = False
else:
    DARKSPARK_SUPPORT = True

try:
    import dolfin
except ImportError:
    DOLFIN_SUPPORT = False
else:
    DOLFIN_SUPPORT = True

try:
    import sksparse
except ImportError:
    SUITESPARSE_SUPPORT = False
else:
    SUITESPARSE_SUPPORT = True
