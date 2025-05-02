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

###########
# IMPORTS #
###########

from . import FunctionalBase
from .FunctionalBase import *

from . import ParametricFunctionalBase
from .ParametricFunctionalBase import *
from . import TensorizedParametricFunctionalBase
from .TensorizedParametricFunctionalBase import *

from . import LinearSpanTensorizedParametricFunctionalBase
from .LinearSpanTensorizedParametricFunctionalBase import *

from . import AnchoredIntegratedSquaredParametricFunctionalBase
from .AnchoredIntegratedSquaredParametricFunctionalBase import *

from . import MonotoneFunctionalBase
from .MonotoneFunctionalBase import *

from . import ParametricMonotoneFunctionalBase
from .ParametricMonotoneFunctionalBase import *

from . import IdentityParametricMonotoneFunctionalBase
from .IdentityParametricMonotoneFunctionalBase import *

from . import PointwiseMonotoneLinearSpanTensorizedParametricFunctionalBase
from .PointwiseMonotoneLinearSpanTensorizedParametricFunctionalBase import *

from . import IntegratedExponentialParametricMonotoneFunctionalBase
from .IntegratedExponentialParametricMonotoneFunctionalBase import *
from . import IntegratedSquaredParametricMonotoneFunctionalBase
from .IntegratedSquaredParametricMonotoneFunctionalBase import *

from . import ProductDistributionParametricPullbackComponentFunctionBase
from .ProductDistributionParametricPullbackComponentFunctionBase import *
from . import FrozenMonotonicFunctions
from .FrozenMonotonicFunctions import *

####################
# VISIBLE ELEMENTS #
####################

__all__ = []

__all__ += FunctionalBase.__all__

__all__ += ParametricFunctionalBase.__all__
__all__ += TensorizedParametricFunctionalBase.__all__

__all__ += LinearSpanTensorizedParametricFunctionalBase.__all__

__all__ += AnchoredIntegratedSquaredParametricFunctionalBase.__all__

__all__ += MonotoneFunctionalBase.__all__

__all__ += ParametricMonotoneFunctionalBase.__all__

__all__ += IdentityParametricMonotoneFunctionalBase.__all__

__all__ += PointwiseMonotoneLinearSpanTensorizedParametricFunctionalBase.__all__

__all__ += IntegratedExponentialParametricMonotoneFunctionalBase.__all__
__all__ += IntegratedSquaredParametricMonotoneFunctionalBase.__all__

__all__ += ProductDistributionParametricPullbackComponentFunctionBase.__all__
__all__ += FrozenMonotonicFunctions.__all__

###################
# CLEAR NAMESPACE #
###################

del FunctionalBase

del ParametricFunctionalBase
del TensorizedParametricFunctionalBase

del LinearSpanTensorizedParametricFunctionalBase

del AnchoredIntegratedSquaredParametricFunctionalBase

del MonotoneFunctionalBase

del ParametricMonotoneFunctionalBase

del IdentityParametricMonotoneFunctionalBase

del PointwiseMonotoneLinearSpanTensorizedParametricFunctionalBase

del IntegratedExponentialParametricMonotoneFunctionalBase
del IntegratedSquaredParametricMonotoneFunctionalBase
