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
from TransportMaps.Maps import assemble_IsotropicIntegratedExponentialDiagonalTransportMap, \
    assemble_IsotropicIntegratedSquaredTriangularTransportMap, assemble_IsotropicIntegratedSquaredDiagonalTransportMap, \
    assemble_IsotropicLinearSpanTriangularMap, assemble_IsotropicLinearSpanTriangularTransportMap, \
    assemble_LinearSpanTriangularMap

from .Misc import deprecate
from .Maps import assemble_IsotropicIntegratedExponentialTriangularTransportMap

__all__ = [
    # Deprecated
    'Default_IsotropicIntegratedExponentialTriangularTransportMap',
    'Default_IsotropicIntegratedExponentialDiagonalTransportMap',
    'Default_IsotropicIntegratedSquaredTriangularTransportMap',
    'Default_IsotropicIntegratedSquaredDiagonalTransportMap',
    'Default_IsotropicMonotonicLinearSpanTriangularTransportMap',
    'Default_IsotropicLinearSpanTriangularTransportMap',
    'Default_LinearSpanTriangularTransportMap'
]


@deprecate(
    'Default_IsotropicIntegratedExponentialTriangularTransportMap',
    '3.0',
    'Use Maps.assemble_IsotropicIntegratedExponentialTriangularTransportMap instead.'
)
def Default_IsotropicIntegratedExponentialTriangularTransportMap(
        *args, **kwargs
):
    return assemble_IsotropicIntegratedExponentialTriangularTransportMap(*args, **kwargs)

    
@deprecate(
    'Default_IsotropicIntegratedExponentialDiagonalTransportMap',
    '3.0',
    'Use Maps.assemble_IsotropicIntegratedExponentialDiagonalTransportMap instead.'
)
def Default_IsotropicIntegratedExponentialDiagonalTransportMap(
        *args, **kwargs
):
    return assemble_IsotropicIntegratedExponentialDiagonalTransportMap(*args, **kwargs)

    
@deprecate(
    'Default_IsotropicIntegratedSquaredTriangularTransportMap',
    '3.0',
    'Use Maps.assemble_IsotropicIntegratedSquaredTriangularTransportMap instead.'
)
def Default_IsotropicIntegratedSquaredTriangularTransportMap(
        *args, **kwargs
):
    return assemble_IsotropicIntegratedSquaredTriangularTransportMap(*args, **kwargs)

    
@deprecate(
    'Default_IsotropicIntegratedSquaredDiagonalTransportMap',
    '3.0',
    'Use Maps.assemble_IsotropicIntegratedSquaredDiagonalTransportMap instead.'
)
def Default_IsotropicIntegratedSquaredDiagonalTransportMap(
        *args, **kwargs
):
    return assemble_IsotropicIntegratedSquaredDiagonalTransportMap(*args, **kwargs)


@deprecate(
    'Default_IsotropicMonotonicLinearSpanTriangularTransportMap',
    '3.0',
    'Use Maps.assemble_IsotropicLinearSpanTriangularTransportMap instead'
)
def Default_IsotropicMonotonicLinearSpanTriangularTransportMap(
        *args, **kwargs
):
    return assemble_IsotropicLinearSpanTriangularTransportMap(*args, **kwargs)


@deprecate(
    'Default_IsotropicLinearSpanTriangularTransportMap',
    '3.0',
    'Use Maps.assemble_IsotropicLinearSpanTriangularMap instead'
)
def Default_IsotropicLinearSpanTriangularTransportMap(
        *args, **kwargs
):
    return assemble_IsotropicLinearSpanTriangularMap(*args, **kwargs)


@deprecate(
    'Default_LinearSpanTriangularTransportMap',
    '3.0',
    'Use Maps.assemble_LinearSpanTriangularMap instead'
)
def Default_LinearSpanTriangularTransportMap(
        *args, **kwargs
):
    return assemble_LinearSpanTriangularMap(*args, **kwargs)

