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

from ...Builders import L2RegressionBuilder
from ...L2 import L2_misfit

__all__ = [
    'ToleranceSequentialL2RegressionBuilder'
]


class ToleranceSequentialL2RegressionBuilder(L2RegressionBuilder):
    def __init__(self, eps, regression_params_list, monitor_params):
        self.eps = eps
        self.regression_params_list = regression_params_list
        self.monitor_params = monitor_params
        super(ToleranceSequentialL2RegressionBuilder,
              self).__init__(self.regression_params_list[0])
    
    def solve(self, transport_map_list, target_map, **extra_reg_params):
        tm = None
        x0 = None
        for transport_map, self.regression_params in zip(
                transport_map_list, self.regression_params_list):
            if tm is not None:
                for c1, c2 in zip(tm.approx_list, transport_map.approx_list):
                    # Constant part
                    for i1, midx1 in enumerate(c1.c.multi_idxs):
                        for i2, midx2 in enumerate(c2.c.multi_idxs):
                            if midx1 == midx2:
                                break
                        c2.c.coeffs[i2] = c1.c.coeffs[i1]
                    # Integrated part
                    for i1, midx1 in enumerate(c1.h.multi_idxs):
                        for i2, midx2 in enumerate(c2.h.multi_idxs):
                            if midx1 == midx2:
                                break
                        c2.h.coeffs[i2] = c1.h.coeffs[i1]
                self.regression_params['x0'] = transport_map.coeffs
            tm_new, log_list = super(
                ToleranceSequentialL2RegressionBuilder,
                self).solve(transport_map, target_map, **extra_reg_params)
            if not log_list[-1]['success']:
                if tm is None: # If no map is available return the target map
                    return target_map, log_list
                else:
                    break
            else:
                tm = transport_map
            # Check error
            err = L2_misfit(target_map, tm, **self.monitor_params)
            if err < self.eps:
                break
        return transport_map, log_list
            
