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

__all__ = []

from ._version import __version__

# Transport map imports
from . import External
from .External import *

from . import ObjectBase
from .ObjectBase import *

from . import Misc
from .Misc import *

from . import MPI
from .MPI import *

from . import LinAlg

from . import DerivativesChecks

from . import RandomizedLinearAlgebra

from . import Maps
from . import Distributions
from . import Likelihoods

from . import Routines
from .Routines import *

from . import KL
from . import L2

from . import LaplaceApproximationRoutines
from .LaplaceApproximationRoutines import *

from . import Defaults
from .Defaults import *

from . import Builders
from . import Algorithms
from . import Diagnostics
from . import Samplers
from . import CLI
from . import tests

from . import DOLFIN

__all__ += External.__all__
__all__ += ObjectBase.__all__
__all__ += Misc.__all__
__all__ += MPI.__all__
__all__ += ['LinAlg']
__all__ += ['DerivativesChecks']
__all__ += ['RandomizedLinearAlgebra']
__all__ += ['Distributions']
__all__ += ['Maps']
__all__ += ['Likelihoods']
__all__ += Routines.__all__
__all__ += ['KL']
__all__ += ['L2']
__all__ += LaplaceApproximationRoutines.__all__
__all__ += Defaults.__all__
__all__ += ['Builders']
__all__ += ['Algorithms']
__all__ += ['Diagnostics']
__all__ += ['Samplers']
__all__ += ['CLI']
__all__ += ['tests']

__all__ += ['DOLFIN']

############
# DEPRECATED
from . import Defaults
from .Defaults import *

from . import Densities
from . import FiniteDifference
# from . import Functionals
__all__ += ['Densities']
__all__ += ['FiniteDifference']
__all__ += ['Functionals']
############

###################
# CLEAR NAMESPACE #
###################
del External
del ObjectBase
del Misc
del Routines
del LaplaceApproximationRoutines
del Defaults

################
# PACKAGE INFO #
################

__author__ = "Transport Map Team"
__copyright__ = """LGPLv3, Copyright (C) 2015-2017, Massachusetts Institute of Technology"""
__credits__ = ["Transport Map Team"]
__maintainer__ = "Transport Map Team"
__website__ = "transportmaps.mit.edu"
__status__ = "Development"

