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

from . import MapBase
from .MapBase import *

from . import Functionals

from . import InverseMapBase
from .InverseMapBase import *
from . import ListCompositeMapBase
from .ListCompositeMapBase import *
from . import ListStackedMapBase
from .ListStackedMapBase import *
from . import SlicedMapBase
from .SlicedMapBase import *

from . import ParametricMapBase
from .ParametricMapBase import *
from . import ConstantMapBase
from .ConstantMapBase import *

from . import ComponentwiseMapBase
from .ComponentwiseMapBase import *
from . import TriangularComponentwiseMapBase
from .TriangularComponentwiseMapBase import *

from . import TransportMapBase
from .TransportMapBase import *

from . import SlicedTransportMapBase
from .SlicedTransportMapBase import *
from . import ConditionalTriangularTransportMapBase
from .ConditionalTriangularTransportMapBase import *
from . import ListStackedTransportMapBase
from .ListStackedTransportMapBase import *
from . import TriangularListStackedTransportMapBase
from .TriangularListStackedTransportMapBase import *
from . import ListCompositeTransportMapBase
from .ListCompositeTransportMapBase import *

from . import InverseTransportMapBase
from .InverseTransportMapBase import *
from . import InverseParametricMapBase
from .InverseParametricMapBase import *
from . import InverseParametricTransportMapBase
from .InverseParametricTransportMapBase import *

from . import IdentityTransportMapBase
from .IdentityTransportMapBase import *
from . import PermutationTransportMapBase
from .PermutationTransportMapBase import *
from . import IdentityEmbeddedTransportMapBase
from .IdentityEmbeddedTransportMapBase import *

from . import AffineMapBase
from .AffineMapBase import *
from . import AffineTriangularMapBase
from .AffineTriangularMapBase import *
from . import AffineTransportMapBase
from .AffineTransportMapBase import *

from . import ParametricComponentwiseMapBase
from .ParametricComponentwiseMapBase import *

from . import ComponentwiseTransportMapBase
from .ComponentwiseTransportMapBase import *

from . import ParametricTransportMapBase
from .ParametricTransportMapBase import *

from . import ListStackedParametricTransportMapBase
from .ListStackedParametricTransportMapBase import *
from . import TriangularListStackedParametricTransportMapBase
from .TriangularListStackedParametricTransportMapBase import *

from . import ParametricTriangularComponentwiseMapBase
from .ParametricTriangularComponentwiseMapBase import *

from . import IdentityEmbeddedParametricTransportMapBase
from .IdentityEmbeddedParametricTransportMapBase import *
from . import IdentityParametricTriangularComponentwiseTransportMapBase
from .IdentityParametricTriangularComponentwiseTransportMapBase import *

from . import TriangularComponentwiseTransportMapBase
from .TriangularComponentwiseTransportMapBase import *
from . import DiagonalComponentwiseTransportMapBase
from .DiagonalComponentwiseTransportMapBase import *
from . import DiagonalIsotropicTransportMapBase
from .DiagonalIsotropicTransportMapBase import *

from . import ParametricTriangularComponentwiseTransportMapBase
from .ParametricTriangularComponentwiseTransportMapBase import *

from . import LinearSpanParametricTriangularComponentwiseMapBase
from .LinearSpanParametricTriangularComponentwiseMapBase import *
from . import NonMonotoneLinearSpanParametricTriangularComponentwiseTransportMapBase
from .NonMonotoneLinearSpanParametricTriangularComponentwiseTransportMapBase import *

from . import IntegratedSquaredParametricTriangularComponentwiseTransportMapBase
from .IntegratedSquaredParametricTriangularComponentwiseTransportMapBase import *
from . import IntegratedExponentialParametricTriangularComponentwiseTransportMapBase
from .IntegratedExponentialParametricTriangularComponentwiseTransportMapBase import *

from . import MapFactoryBase
from .MapFactoryBase import *

from . import FrozenTriangularTransportMaps
from .FrozenTriangularTransportMaps import *

from . import Defaults
from .Defaults import *

from . import MiscMaps
from .MiscMaps import *

# Deprecated
from . import DeprecatedConditionallyLinearMapBase
from .DeprecatedConditionallyLinearMapBase import *

####################
# VISIBLE ELEMENTS #
####################

__all__ = []

__all__ += MapBase.__all__

__all__ += ['Functionals']

__all__ += InverseMapBase.__all__
__all__ += ListCompositeMapBase.__all__
__all__ += ListStackedMapBase.__all__
__all__ += SlicedMapBase.__all__

__all__ += ParametricMapBase.__all__
__all__ += ConstantMapBase.__all__

__all__ += ComponentwiseMapBase.__all__
__all__ += TriangularComponentwiseMapBase.__all__

__all__ += TransportMapBase.__all__

__all__ += SlicedTransportMapBase.__all__
__all__ += ConditionalTriangularTransportMapBase.__all__
__all__ += ListStackedTransportMapBase.__all__
__all__ += TriangularListStackedTransportMapBase.__all__
__all__ += ListCompositeTransportMapBase.__all__

__all__ += InverseTransportMapBase.__all__
__all__ += InverseParametricMapBase.__all__
__all__ += InverseParametricTransportMapBase.__all__

__all__ += IdentityTransportMapBase.__all__
__all__ += PermutationTransportMapBase.__all__
__all__ += IdentityEmbeddedTransportMapBase.__all__

__all__ += AffineMapBase.__all__
__all__ += AffineTriangularMapBase.__all__
__all__ += AffineTransportMapBase.__all__

__all__ += ParametricComponentwiseMapBase.__all__

__all__ += ComponentwiseTransportMapBase.__all__

__all__ += ParametricTransportMapBase.__all__

__all__ += ListStackedParametricTransportMapBase.__all__
__all__ += TriangularListStackedParametricTransportMapBase.__all__

__all__ += ParametricTriangularComponentwiseMapBase.__all__

__all__ += IdentityEmbeddedParametricTransportMapBase.__all__
__all__ += IdentityParametricTriangularComponentwiseTransportMapBase.__all__

__all__ += TriangularComponentwiseTransportMapBase.__all__
__all__ += DiagonalComponentwiseTransportMapBase.__all__
__all__ += DiagonalIsotropicTransportMapBase.__all__

__all__ += ParametricTriangularComponentwiseTransportMapBase.__all__

__all__ += LinearSpanParametricTriangularComponentwiseMapBase.__all__
__all__ += NonMonotoneLinearSpanParametricTriangularComponentwiseTransportMapBase.__all__

__all__ += IntegratedSquaredParametricTriangularComponentwiseTransportMapBase.__all__
__all__ += IntegratedExponentialParametricTriangularComponentwiseTransportMapBase.__all__

__all__ += MapFactoryBase.__all__

__all__ += FrozenTriangularTransportMaps.__all__

__all__ += Defaults.__all__

__all__ += MiscMaps.__all__

__all__ += ['Decomposable']
__all__ += ['ODEs']

# Deprecated
__all__ += DeprecatedConditionallyLinearMapBase.__all__

###################
# CLEAN NAMESPACE #
###################

del MapBase

del InverseMapBase
del ListCompositeMapBase
del ListStackedMapBase
del SlicedMapBase

del ParametricMapBase
del ConstantMapBase

del ComponentwiseMapBase
del TriangularComponentwiseMap

del TransportMapBase

del SlicedTransportMapBase
del ConditionalTriangularTransportMapBase
del ListStackedTransportMapBase
del TriangularListStackedTransportMapBase
del ListCompositeTransportMapBase

del InverseTransportMapBase
del InverseParametricMapBase
del InverseParametricTransportMapBase

del IdentityTransportMapBase
del PermutationTransportMapBase
del IdentityEmbeddedTransportMapBase

del AffineMapBase
del AffineTriangularMapBase
del AffineTransportMapBase

del ParametricComponentwiseMapBase

del ComponentwiseTransportMapBase

del ParametricTransportMapBase

del ListStackedParametricTransportMapBase
del TriangularListStackedParametricTransportMapBase

del ParametricTriangularComponentwiseMapBase

del IdentityEmbeddedParametricTransportMapBase
del IdentityParametricTriangularComponentwiseTransportMapBase

del TriangularComponentwiseTransportMapBase
del DiagonalComponentwiseTransportMapBase
del DiagonalIsotropicTransportMapBase

del ParametricTriangularComponentwiseTransportMapBase

del LinearSpanParametricTriangularComponentwiseMapBase
del NonMonotoneLinearSpanParametricTriangularComponentwiseTransportMapBase

del IntegratedSquaredParametricTriangularComponentwiseTransportMapBase
del IntegratedExponentialParametricTriangularComponentwiseTransportMapBase

del MapFactoryBase

del FrozenTriangularTransportMaps

del Defaults

del MiscMaps

# Deprecated
del DeprecatedConditionallyLinearMapBase
