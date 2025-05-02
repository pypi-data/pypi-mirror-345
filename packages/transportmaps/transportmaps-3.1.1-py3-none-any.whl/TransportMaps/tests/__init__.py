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

from .TestFunctions import *
from .test_all import *
from .test_distributions import *
from .test_functions import *
from .test_kl_divergence import *
from .test_kl_minimization import *
from .test_L2_minimization import *
from .test_L2_misfit import *
from .test_laplace import *
from .test_rla import *
from .test_scripts import *
from .test_sequential_inference import *
from .test_transportmap_distributions import *
from .test_transportmap_distributions_sampling import *
from .test_transportmaps import *

__author__ = "Daniele Bigoni"
__copyright__ = """LGPLv3, Copyright 2015-2016, Massachusetts Institute of Technology"""
__credits__ = ["Daniele Bigoni"]
__maintainer__ = "Daniele Bigoni"
__email__ = "dabi@limitcycle.it"
__status__ = "Development"