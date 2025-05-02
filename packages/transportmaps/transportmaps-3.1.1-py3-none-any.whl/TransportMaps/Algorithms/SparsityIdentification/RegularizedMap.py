#
# This file is part of TransportMaps.
#
# TransportMaps is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TransportMaps is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with TransportMaps.  If not, see <http://www.gnu.org/licenses/>.
#
# Transport Maps Library
# Copyright (C) 2015-2016 Massachusetts Institute of Technology
# Uncertainty Quantification group
# Department of Aeronautics and Astronautics
#
# Author: Transport Map Team
# E-mail: tmteam@mit.edu
# Website: transport-maps.mit.edu
# Support: transport-maps.mit.edu/qa/
#

import numpy as np
import scipy.stats as stats

from ...KL import minimize_kl_divergence
#from TransportMaps.Defaults import Default_IsotropicIntegratedSquaredTriangularTransportMap, Default_IsotropicIntegratedExponentialTriangularTransportMap
from ...Maps import assemble_IsotropicIntegratedSquaredTriangularTransportMap
from ...Distributions import \
    StandardNormalDistribution, \
    PushForwardParametricTransportMapDistribution, PullBackTransportMapDistribution, \
    PullBackParametricTransportMapDistribution
import pdb

# Tolerance for l1 optimization
tol_l1 = 1e-6

# Threshold for coefficient values after opt
l1_threshold = 1e-6

# params for l1 optimization
max_iter = 10
tol_soln = 1e-6
eps = 1e-3
lambda_list = np.logspace(-6,0,20)

def reweighted_l1(eta, pi, qtype, qparams, REG, tol, ders, max_iter, tol_soln, eps, dim, order, active_vars):

    # initialize flags for reweighted l1
    err_soln = 1
    iter_count = 0

    # Build the transport map (isotropic for each entry)
    # *********************************TESTING*****************************
    #tm_approx = Default_IsotropicIntegratedSquaredTriangularTransportMap(
    #      dim, order, active_vars=active_vars)
    tm_approx = assemble_IsotropicIntegratedSquaredTriangularTransportMap(
        dim, order, active_vars=active_vars)
    #tm_approx = Default_IsotropicIntegratedExponentialTriangularTransportMap(
    #      dim, order, active_vars=active_vars)
    # ******************************END TESTING*****************************

    # Construct density T_\sharp \pi
    tm_density = PushForwardParametricTransportMapDistribution(tm_approx, pi)

    # set initial l1_weights
    REG['l1_weights'] = np.ones(tm_approx.n_coeffs)

    # Compute initial estimate for map and get weights
    solve = minimize_kl_divergence(
        tm_density.base_distribution,
        PullBackParametricTransportMapDistribution(
            tm_density.transport_map,
            eta
        ),
        qtype=qtype, qparams=qparams, \
        regularization=REG, tol=tol, ders=ders)
    coeffs = tm_density.coeffs

    while(err_soln > tol_soln and iter_count < max_iter):

        # Update weights based on coeffs
        weights = 1./(np.abs(coeffs) + eps)
        REG['l1_weights'] = weights

        # Compute new map and update weights
        solve = minimize_kl_divergence(
            tm_density.base_distribution,
            PullBackParametricTransportMapDistribution(
                tm_density.transport_map,
                eta
            ),
            qtype=qtype,
            qparams=qparams, regularization=REG, tol=tol, ders=ders)
        new_coeffs = tm_density.coeffs

        # Compute err_soln
        err_soln = np.linalg.norm(new_coeffs - coeffs)
        coeffs = new_coeffs

        # Update counter
        iter_count = iter_count + 1

    return tm_approx

def coeff_to_activevars(approx_list, threshold, prev_active_vars):

    dim = len(approx_list)
    # add diagonal map variables to active variables
    active_vars = [[i] for i in range(dim)]

    # loop over dimension and extract active vars for each
    for i in range(dim):

        # Extract and threshold coeffs
        c_coeffs = approx_list[i].c.coeffs
        h_coeffs = approx_list[i].h.coeffs
        c_coeffs[np.abs(c_coeffs) < threshold] = 0
        h_coeffs[np.abs(h_coeffs) < threshold] = 0

        # Extract c and h multi_idxs
        c_idx = approx_list[i].c.get_multi_idxs()
        h_idx = approx_list[i].h.get_multi_idxs()

        for j_idx,j in enumerate(prev_active_vars[i]):

            # Check if each coefficient in c is nonzero and variable involved in term
            for k in range(len(c_idx)):
                try:
                    if c_idx[k][j_idx] != 0 and c_coeffs[k] != 0:
                        active_vars[i].append(j)
                        break
                except:
                    pdb.set_trace()

            # Check if each coefficient in c is nonzero and variable involved in term
            for k in range(len(h_idx)):
                if h_idx[k][j_idx] != 0 and h_coeffs[k] != 0:
                    active_vars[i].append(j)
                    break

        # sort and take unique elements in list of active_vars
        active_vars[i] = sorted(set(active_vars[i]))

    return active_vars

def regularized_map(eta, pi, data, qtype, qparams, dim, order, active_vars, tol, ders, REG):
    nsamps = data.shape[0]

    if REG == None:

        # Build the transport map (isotropic for each entry)
        #tm_approx = Default_IsotropicIntegratedSquaredTriangularTransportMap(
        #          dim, order, active_vars=active_vars)
        tm_approx = assemble_IsotropicIntegratedSquaredTriangularTransportMap(
            dim, order, active_vars=active_vars)

        # Construct density T_\sharp \pi
        tm_density = PushForwardParametricTransportMapDistribution(tm_approx, pi)

        # Set regularization in REG
        REG = {'type': None }
        solve = minimize_kl_divergence(
            tm_density.base_distribution,
            PullBackParametricTransportMapDistribution(
                tm_density.transport_map,
                eta
            ), qtype=qtype,
            qparams=qparams,
            regularization=REG,
            tol=tol, ders=ders)

        coeff_iter = tm_density.coeffs

    elif REG['type'] == 'L1':
        # Set l1 tolerance
        REG['tol_l1'] = tol_l1
        # Set ders to be maximum of 1 with L1
        ders = np.min((ders, 1))
        # Create list to store approx_list and BIC values
        coeffs_list = []
        bic = []
        for lambda_t in lambda_list:
            # set regularization in REG
            REG['alpha'] = lambda_t
            if REG['reweight'] == None or REG['reweight'] == False:
                # Build the transport map (isotropic for each entry)
                #tm_approx = Default_IsotropicIntegratedSquaredTriangularTransportMap(
                #      dim, order, active_vars=active_vars)
                tm_approx = assemble_IsotropicIntegratedSquaredTriangularTransportMap(
                    dim, order, active_vars=active_vars)

                # Construct density T_\sharp \pi
                tm_density = PushForwardParametricTransportMapDistribution(tm_approx, pi)

                # set regularization in REG
                REG['l1_weights'] = np.ones(tm_approx.n_coeffs)
                minimize_kl_divergence(
                    tm_density.base_distribution,
                    PullBackParametricTransportMapDistribution(
                        tm_density.transport_map,
                        eta
                    ), qtype=qtype,
                    qparams=qparams,
                    regularization=REG,
                    tol=tol, ders=ders)
            elif REG['reweight'] == True:
                tm_approx = reweighted_l1(eta, pi, qtype, qparams, REG, tol, ders, max_iter, tol_soln, eps, dim, order, active_vars)

            coeffs_list.append(tm_approx.approx_list)
            coeff_iter = tm_approx.coeffs
            coeff_iter[abs(coeff_iter) < l1_threshold] = 0.0
            # Evaluate log-likelihood for data used to create map
            pull_S = PullBackTransportMapDistribution(tm_approx, eta)
            log_lik_trial = np.sum(pull_S.log_pdf(data))
            bic.append(np.log(nsamps)*np.count_nonzero(coeff_iter) - 2*log_lik_trial)

        idx = np.argmin(bic)
        coeffs_opt = coeffs_list[idx]
        new_active_vars = coeff_to_activevars(coeffs_opt, l1_threshold, tm_approx.active_vars)
        # Rerun transport map optimization (isotropic for each entry)
        print(new_active_vars)
        #tm_approx = Default_IsotropicIntegratedSquaredTriangularTransportMap(
        #      dim, order, active_vars=new_active_vars)
        tm_approx = assemble_IsotropicIntegratedSquaredTriangularTransportMap(
            dim, order, active_vars=active_vars)
        # Construct density T_\sharp \pi
        tm_density = PushForwardParametricTransportMapDistribution(tm_approx, pi)
        REG = {'type': None }
        minimize_kl_divergence(
            tm_density.base_distribution,
            PullBackParametricTransportMapDistribution(
                tm_density.transport_map,
                eta
            ), qtype=qtype,
            qparams=qparams,
            regularization=REG,
            tol=tol, ders=ders)
    
    return tm_approx

if __name__ == "__main__":
    import GaussianGraphs as gg
    import ExtraDensities 
    dim = 12
    nsamps = 1000
    tol = 1e-6
    graph_obj = gg.ChainGraph(dim)
    data = graph_obj.rvs(nsamps)
    eta = StandardNormalDistribution(dim)
    # Gradient information
    ders = 1
    # Approximation orders
    order = 2
    qtype = 0
    qparams = nsamps
    active_vars=None
    # define base_density from samples
    pi = ExtraDensities.SamplesDensity(data)

    REG = {'type': 'L1', 'reweight': True}
    tm_approx = regularized_map(eta, pi, data, qtype, qparams, dim, order, active_vars, tol, ders, REG)
    print(tm_approx.coeffs)
