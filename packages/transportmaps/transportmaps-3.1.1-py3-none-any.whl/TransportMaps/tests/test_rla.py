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

import unittest
import numpy as np
import numpy.random as npr
import numpy.linalg as npla

from TransportMaps.RandomizedLinearAlgebra import \
    adaptive_randomized_range_finder, \
    randomized_direct_eig, randomized_direct_svd

class RLATest(unittest.TestCase):

    def test_adaptive_randomized_range_finder(self):
        M = 50
        N = 70
        k = 5
        r = 10
        eps = 1e-6
        A1 = npr.randn(M, k)
        A2 = npr.randn(N, k)
        A = np.dot(A1, A2.T)
        def action(X, A):
            return np.dot(A, X)
        def action_transpose(X, A):
            return np.dot(A.T, X)
        power_n = 1
        kwargs = {'A': A}
        Q = adaptive_randomized_range_finder(
            action, N, M, eps, r, kwargs=kwargs,
            power_n=power_n, action_transpose=action_transpose)
        self.assertTrue(Q.shape[1] == r+k-1)
        B = action_transpose(Q, A)
        C = Q
        A1 = np.dot(C, B.T)
        self.assertTrue(np.allclose(A, A1))

    def test_randomized_direct_eigenvalue_decomposition(self):
        N = 70
        k = 5
        r = 10
        eps = 1e-6
        A = npr.randn(N, k)
        A = np.dot(A, A.T)
        def action(X, A):
            return np.dot(A, X)
        def action_transpose(X, A):
            return np.dot(A.T, X)
        power_n = 1
        kwargs = {'A': A}
        D, U = randomized_direct_eig(
            action, N, eps, r, kwargs=kwargs,
            power_n=power_n)
        A1 = np.dot(U, (D[np.newaxis,:] * U).T)
        self.assertTrue(np.allclose(A, A1))

    def test_randomized_direct_svd(self):
        N = 70
        M = 50
        k = 10
        r = 10
        eps = 1e-6
        U = npr.randn(N, k)
        Vt = npr.randn(k, M) 
        A = np.dot(U, Vt)
        def action(X, A):
            return np.dot(A, X)
        def action_transpose(X, A):
            return np.dot(A.T, X)
        power_n = 1
        kwargs = {'A': A}
        U, S, Vt = randomized_direct_svd(
            action, action_transpose,
            M, N, eps, r, kwargs=kwargs,
            power_n=power_n)
        A1 = np.dot(U, S[:,np.newaxis] * Vt)
        self.assertTrue(np.allclose(A, A1))

    def test_randomized_direct_svd_vs_eig(self):
        N = 70
        M = 50
        k = 10
        r = 10
        eps = 1e-6
        U = npr.randn(N, k)
        Vt = npr.randn(k, M) 
        A = np.dot(U, Vt)
        def action(X, A):
            return np.dot(A, X)
        def action_transpose(X, A):
            return np.dot(A.T, X)
        power_n = 1
        kwargs = {'A': A}
        U, S, Vt = randomized_direct_svd(
            action, action_transpose,
            M, N, eps, r, kwargs=kwargs,
            power_n=power_n, )
        AAT = np.dot(A,A.T)
        D, V = npla.eigh(AAT)
        idxs = D > 1e-10
        D = D[idxs]
        V = V[:,idxs]
        idxs_sort = np.argsort(D)[::-1]
        D = D[idxs_sort]
        V = V[:,idxs_sort]
        self.assertTrue(np.allclose(S**2, D))
        for i in range(D.shape[0]):
            self.assertTrue(
                np.allclose(V[:,i], U[:,i]) or
                np.allclose(V[:,i], -U[:,i]) )
        
def build_suite(*args, **kwargs):
    suite_rla = unittest.TestLoader().loadTestsFromTestCase( RLATest )
    # Group suites
    suites_list = [suite_rla]
    all_suites = unittest.TestSuite( suites_list )
    return all_suites


def run_tests(
        ttype='serial',
        failfast=False
):
    all_suites = build_suite(ttype)
    # RUN
    unittest.TextTestRunner(
        verbosity=2,
        failfast=failfast
    ).run(all_suites)


if __name__ == '__main__':
    run_tests()
