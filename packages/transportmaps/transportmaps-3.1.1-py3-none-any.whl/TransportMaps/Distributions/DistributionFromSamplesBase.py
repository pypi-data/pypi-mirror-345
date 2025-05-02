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

import numpy as np
import scipy.stats as stats

from .DistributionBase import Distribution

__all__ = [
    'DistributionFromSamples'
]


class DistributionFromSamples(Distribution):
    r""" Arbitrary density built from samples

    Args:
      samples (type, dimension?): independent samples
    """
    def __init__(self, samples, weights=None, qtype=0):
        super(DistributionFromSamples,self).__init__(samples.shape[1])
        self._quadratures = {qtype: {'x':samples, 'w':weights}}

    def rvs(self, m, *args, **kwargs):
        if m > self._quadratures[0]['x'].shape[0]:
            raise ValueError("Number of rvs must be less than or equal to length of samples provided")
        
        msamples = self._quadratures[0]['x'][0:m,:]
        return msamples
    
    def quadrature(self, qtype, qparams, *args, **kwargs):
        if qtype == 0:
            x = self.rvs(qparams)
            w = np.ones(qparams)/qparams
        else:
            raise NotImplementedError("qtype not available, still to do")
        return (x,w)

    #if no analytical form of pdf
    def kde(self, x, params=None):
        r""" Evaluate :math:`\pi(x)`
        """
        # kde takes data in form (#dim, #data)
        density = stats.gaussian_kde(self._quadratures[0]['x'].T)
        pdf_kde = density.evaluate(x.T)
        return pdf_kde 

    def log_kde(self, x, params=None):
        return np.log(self.kde(x,params))
