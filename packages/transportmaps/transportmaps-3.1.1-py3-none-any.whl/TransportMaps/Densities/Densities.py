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

from TransportMaps import deprecate
from TransportMaps.Distributions import *

__all__ = ["Density", "ParametricDensity",
           "TransportMapDensity",
           "PushForwardTransportMapDensity",
           "PullBackTransportMapDensity",
           'FrozenDensity_1d',
           'GaussianDensity', 'StandardNormalDensity',
           'LogNormalDensity', 'LogisticDensity',
           'GammaDensity', 'BetaDensity',
           'WeibullDensity',
           'GumbelDensity', 'BananaDensity']

class Density(Distribution):
    @deprecate("TransportMaps.Densities.Density", "1.0",
               "Use TransportMaps.Distributions.Distribution instead")
    def __init__(self, *args, **kwargs):
        super(Density, self).__init__(*args, **kwargs)

class ParametricDensity(ParametricDistribution):
    @deprecate("TransportMaps.Densities.ParametricDensity", "1.0",
               "Use TransportMaps.Distributions.ParametricDistribution instead")
    def __init__(self, *args, **kwargs):
        super(ParametricDensity, self).__init__(*args, **kwargs)

class TransportMapDensity(TransportMapDistribution):
    @deprecate("TransportMaps.Densities.TransportMapDensity", "1.0",
               "Use TransportMaps.Distributions.TransportMapDistribution instead")
    def __init__(self, *args, **kwargs):
        super(TransportMapDensity, self).__init__(*args, **kwargs)

    @property
    def base_density(self):
        return self.base_distribution

    @base_density.setter
    def base_density(self, value):
        self.base_distribution = value

class PushForwardTransportMapDensity(PushForwardTransportMapDistribution):
    @deprecate(
        "TransportMaps.Densities.PushForwardTransportMapDensity", "1.0",
        "Use TransportMaps.Distributions.PushForwardTransportMapDistribution instead")
    def __init__(self, *args, **kwargs):
        super(PushForwardTransportMapDensity, self).__init__(*args, **kwargs)

    @property
    def base_density(self):
        return self.base_distribution

    @base_density.setter
    def base_density(self, value):
        self.base_distribution = value

class PullBackTransportMapDensity(PullBackTransportMapDistribution):
    @deprecate(
        "TransportMaps.Densities.PullBackTransportMapDensity", "1.0",
        "Use TransportMaps.Distributions.PullBackTransportMapDistribution instead")
    def __init__(self, *args, **kwargs):
        super(PullBackTransportMapDensity, self).__init__(*args, **kwargs)

    @property
    def base_density(self):
        return self.base_distribution

    @base_density.setter
    def base_density(self, value):
        self.base_distribution = value

# FROZEN DISTRIBUTIONS
class FrozenDensity_1d(FrozenDistribution_1d):
    @deprecate("TransportMaps.Densities.FrozenDensity_1d", "1.0",
               "Use TransportMaps.Distributions.FrozenDistribution_1d instead")
    def __init__(self, *args, **kwargs):
        super(FrozenDensity_1d, self).__init__(*args, **kwargs)

class GaussianDensity(GaussianDistribution):
    @deprecate("TransportMaps.Densities.GaussianDensity", "1.0",
               "Use TransportMaps.Distributions.GaussianDistribution instead")
    def __init__(self, *args, **kwargs):
        super(GaussianDensity, self).__init__(*args, **kwargs)

class StandardNormalDensity(StandardNormalDistribution):
    @deprecate("TransportMaps.Densities.StandardNormalDensity", "1.0",
               "Use TransportMaps.Distributions.StandardNormalDistribution instead")
    def __init__(self, *args, **kwargs):
        super(StandardNormalDensity, self).__init__(*args, **kwargs)

class LogNormalDensity(LogNormalDistribution):
    @deprecate("TransportMaps.Densities.LogNormalDensity", "1.0",
               "Use TransportMaps.Distributions.LogNormalDistribution instead")
    def __init__(self, *args, **kwargs):
        super(LogNormalDensity, self).__init__(*args, **kwargs)

class LogisticDensity(LogisticDistribution):
    @deprecate("TransportMaps.Densities.LogisticDensity", "1.0",
               "Use TransportMaps.Distributions.LogisticDistribution instead")
    def __init__(self, *args, **kwargs):
        super(LogisticDensity, self).__init__(*args, **kwargs)

class GammaDensity(GammaDistribution):
    @deprecate("TransportMaps.Densities.GammaDensity", "1.0",
               "Use TransportMaps.Distributions.GammaDistribution instead")
    def __init__(self, *args, **kwargs):
        super(GammaDensity, self).__init__(*args, **kwargs)

class BetaDensity(BetaDistribution):
    @deprecate("TransportMaps.Densities.BetaDensity", "1.0",
               "Use TransportMaps.Distributions.BetaDistribution instead")
    def __init__(self, *args, **kwargs):
        super(BetaDensity, self).__init__(*args, **kwargs)

class WeibullDensity(WeibullDistribution):
    @deprecate("TransportMaps.Densities.WeibullDensity", "1.0",
               "Use TransportMaps.Distributions.WeibullDistribution instead")
    def __init__(self, *args, **kwargs):
        super(WeibullDensity, self).__init__(*args, **kwargs)

class GumbelDensity(GumbelDistribution):
    @deprecate("TransportMaps.Densities.GumbelDensity", "1.0",
               "Use TransportMaps.Distributions.GumbelDistribution instead")
    def __init__(self, *args, **kwargs):
        super(GumbelDensity, self).__init__(*args, **kwargs)

class BananaDensity(BananaDistribution):
    @deprecate("TransportMaps.Densities.BananaDensity", "1.0",
               "Use TransportMaps.Distributions.BananaDistribution instead")
    def __init__(self, *args, **kwargs):
        super(BananaDensity, self).__init__(*args, **kwargs)

