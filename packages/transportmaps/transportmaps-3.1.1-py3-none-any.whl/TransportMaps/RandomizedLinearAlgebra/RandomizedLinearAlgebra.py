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

from collections import deque
import numpy as np
import numpy.linalg as npla
import numpy.random as npr

import TransportMaps as TM

__all__ = ['adaptive_randomized_range_finder',
           'randomized_direct_svd',
           'randomized_direct_eig',
           'randomized_nystrom_eigenvalue_decomposition']

nax = np.newaxis

def adaptive_randomized_range_finder(
        action, dim_in, dim_out, eps, r, rng=npr.randn, kwargs={},
        power_n=0, action_transpose=None):
    r""" Adaptive randomized range finder with subspace iterations

    .. see:: Algorithms 4.2 and 4.4 in Halko, N., Martinsson, P., & Tropp, J. (2011). Finding structure with randomness: Probabilistic algorithms for constructing approximate matrix decompositions. SIAM Review, 53(2), 217–288. Retrieved from http://epubs.siam.org/doi/abs/10.1137/090771806
    """
    Omega = rng(dim_in*r).reshape((dim_in, r))
    Y = action(Omega, **kwargs)
    for k in range(power_n):
        Y, R = npla.qr(Y)
        Y = action_transpose(Y, **kwargs)
        Y, R = npla.qr(Y)
        Y = action(Y, **kwargs)
    Y = [Y[:,[i]] for i in range(r)]
    j = 0
    Q = np.zeros((dim_out,0))
    nrm_list = deque([npla.norm(y) for y in Y])
    tar_eps = eps / (10. * np.sqrt(2/np.pi))
    TM.logger.info(
        "Randomized adaptive range finder: it=%d - " % j + \
        "eps=%e (target %e)" % (max(nrm_list), tar_eps))
    while max(nrm_list) > tar_eps or j == 0:
        Y[j] -= np.dot(Q, np.dot(Q.T, Y[j]))
        q = Y[j] / npla.norm(Y[j])
        Q = np.hstack((Q, q))
        # New direction
        w = rng(dim_in).reshape((dim_in,1))
        Aw = action(w, **kwargs)
        for k in range(power_n):
            Aw, R = npla.qr(Aw)
            Aw = action_transpose(Aw, **kwargs)
            Aw, R = npla.qr(Aw)
            Aw = action(Aw, **kwargs)
        Y.append( Aw - np.dot(Q, np.dot(Q.T, Aw)) )
        for i in range(j+1, j+r+1):
            Y[i] -= Q[:,[j]] * np.dot(Q[:,j], Y[i])
        # Update norms
        nrm_list.popleft()
        nrm_list.append( npla.norm(Y[-1]) )
        j += 1
        TM.logger.info(
            "Randomized adaptive range finder: it=%d - " % j + \
            "eps=%e (target %e)" % (max(nrm_list), tar_eps))
    return Q

def randomized_direct_svd(
        action, action_transpose, dim_in, dim_out, eps, r, rng=npr.randn, kwargs={},
        power_n=0, range_finder=adaptive_randomized_range_finder,
        min_singval=1e-12):
    Q = range_finder(
        action, dim_in, dim_out, eps, r, rng=rng, kwargs=kwargs,
        power_n=power_n, action_transpose=action_transpose)
    B = action_transpose(Q, **kwargs).T
    Utilde, S, V = npla.svd(B, full_matrices=False)
    U = Q.dot(Utilde)
    idx = next( ( i for i in range(S.shape[0]) if S[i] <= min_singval ), S.shape[0] )
    TM.logger.info("Randomized direct svd - Truncation dimension: %d" % idx)
    S = S[:idx]
    U = U[:,:idx]
    V = V[:idx,:]
    return U, S, V
    
def randomized_direct_eig(
        action, dim, eps, r, rng=npr.randn, kwargs={},
        power_n=0, range_finder=adaptive_randomized_range_finder,
        min_eigval=1e-12):
    Q = range_finder(
        action, dim, dim, eps, r, rng=rng, kwargs=kwargs,
        power_n=power_n, action_transpose=action)
    AQ = action(Q, **kwargs)
    B = np.dot(Q.T, AQ)
    D, V = npla.eigh(B)
    # Remove eigenvalues smaller than min_eigval
    idxs = np.abs(D) > min_eigval
    TM.logger.info(
        "Randomized direct eigenvalue decomposition " + \
        "- Truncation dimension: %d" % sum(idxs))
    D = D[idxs]
    V = V[:,idxs]
    U = np.dot(Q, V)
    return D, U

def randomized_nystrom_eigenvalue_decomposition(
        action, dim, eps, r, rng=npr.randn, kwargs={},
        power_n=0, range_finder=adaptive_randomized_range_finder,
        min_eigval=1e-12):
    Q = range_finder(
        action, dim, dim, eps, r, rng=rng, kwargs=kwargs,
        power_n=power_n, action_transpose=action)
    B1 = action(Q, **kwargs)
    B2 = np.dot(Q.T, B1)
    L = npla.cholesky(B2)
    F = npla.solve_triangular(L, B1.T).T
    U,S,V = npla.svd(F)
    D = S**2.
    # Remove eigenvalues smaller than min_eigval
    idxs = np.abs(D) > min_eigval
    TM.logger.info("Randomized direct eigenvalue decomposition - Truncation dimension: %d" % len(idxs))
    D = D[idxs]
    U = U[:,idxs]
    return D, U