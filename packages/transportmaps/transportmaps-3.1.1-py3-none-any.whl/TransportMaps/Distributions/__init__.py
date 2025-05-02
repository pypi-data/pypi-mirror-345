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

###########
# IMPORTS #
###########

from . import DistributionBase
from .DistributionBase import *
from . import ProductDistributionBase
from .ProductDistributionBase import *
from . import ConditionalDistributionBase
from .ConditionalDistributionBase import *
from . import DistributionFromSamplesBase
from .DistributionFromSamplesBase import *
from . import FactorizedDistributionBase
from .FactorizedDistributionBase import *

from . import ParametricDistributionBase
from .ParametricDistributionBase import *

from . import ConditionalDistributions
from .ConditionalDistributions import *

from . import TransportMapDistributionBase
from .TransportMapDistributionBase import *
from . import TransportMapDistributions
from .TransportMapDistributions import *

from . import ParametricTransportMapDistributionBase
from .ParametricTransportMapDistributionBase import *
from . import ParametricTransportMapDistributions
from .ParametricTransportMapDistributions import *

from . import FrozenDistributions
from .FrozenDistributions import *

from . import Deprecated
from .Deprecated import *

from . import Inference
from . import Decomposable
# from . import Examples

####################
# VISIBLE ELEMENTS #
####################

__all__ = []

__all__ += DistributionBase.__all__
__all__ += ProductDistributionBase.__all__
__all__ += ConditionalDistributionBase.__all__
__all__ += DistributionFromSamplesBase.__all__
__all__ += FactorizedDistributionBase.__all__

__all__ += ParametricDistributionBase.__all__

__all__ += ConditionalDistributions.__all__

__all__ += TransportMapDistributionBase.__all__
__all__ += TransportMapDistributions.__all__

__all__ += ParametricTransportMapDistributionBase.__all__
__all__ += ParametricTransportMapDistributions.__all__

__all__ += FrozenDistributions.__all__

__all__ += Deprecated.__all__

__all__ += ['Inference']
__all__ += ['Decomposable']
__all__ += ['Examples']

###################
# CLEAN NAMESPACE #
###################

del DistributionBase
del ProductDistributionBase
del ConditionalDistributionBase
del DistributionFromSamplesBase
del FactorizedDistributionBase

del ParametricDistributionBase

del ConditionalDistributions

del TransportMapDistributionBase
del TransportMapDistributions

del ParametricTransportMapDistributionBase
del ParametricTransportMapDistributions

del FrozenDistributions

del Deprecated
