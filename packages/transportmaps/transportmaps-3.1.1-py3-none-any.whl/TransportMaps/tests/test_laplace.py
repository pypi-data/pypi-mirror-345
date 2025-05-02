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

import unittest
import numpy as np
import numpy.random as npr
import numpy.linalg as npla

import TransportMaps.tests.TestFunctions as TF
import TransportMaps as TM
import TransportMaps.Diagnostics as DIAG
import TransportMaps.Likelihoods as LKL
import TransportMaps.Distributions as DIST
import TransportMaps.Distributions.Inference as INFDIST
from TransportMaps.KL import kl_divergence

# TM.setLogLevel(20)

try:
    import mpi_map
    MPI_SUPPORT = True
except:
    MPI_SUPPORT = False


class LaplaceApproximation(unittest.TestCase):

    def setUp(self):
        npr.seed(1)
        self.tol = 1e-8

    def compute_laplace(self, d):
        # Build Laplace approximation
        d_laplace = TM.laplace_approximation(d, None, tol=self.tol)

        # Compare mean
        self.assertTrue( npla.norm(d.mu - d_laplace.mu) <= self.tol )

        # Compute KL divergence between the two
        qtype = 3
        qparams = [10]*d.dim
        kldiv = kl_divergence(d, d_laplace, None, None,
                                 qtype=qtype, qparams=qparams)
        self.assertTrue( np.abs(kldiv) <= 1e-2 )

    def test_linear1d(self):
        title, setup, Tparams = TF.get(0)
        self.compute_laplace(Tparams['target_distribution'])

    def test_linear2d(self):
        title, setup, Tparams = TF.get(9)
        self.compute_laplace(Tparams['target_distribution'])

    def test_gauss_low_rank_nd_hessact(self):
        #################
        # Construct distribution
        dx = 40
        dy = 10
        # Prior
        mux = npr.randn(dx)
        sigmax = npr.randn(dx**2).reshape((dx,dx))
        sigmax = np.dot(sigmax, sigmax.T)
        prior = DIST.NormalDistribution(mux, sigmax)
        # Likelihood
        mu = npr.randn(dy)
        sigma = npr.randn(dy**2).reshape((dy,dy))
        sigma = np.dot(sigma, sigma.T)
        c = npr.randn(dy)
        T = npr.randn(dy*dx).reshape((dy,dx))
        T[-5:,:] = T[:5,:]
        y = c + np.dot(T, prior.rvs(1)[0,:])
        logL = LKL.AdditiveLinearNormalLogLikelihood(y, c, T, mu, sigma)
        # Posterior
        pi = INFDIST.BayesPosteriorDistribution(logL, prior)

        ##################
        # Build Laplace approximation using action of Hessian
        pi_laplace = TM.laplace_approximation(pi, None, tol=self.tol, ders=2,
                                              hessact=True)
        # Check variance diagnostic (should be at machine precision)
        var_diag = DIAG.variance_approx_kl(pi_laplace, pi, qtype=0, qparams=10000)
        self.assertTrue( var_diag < 1e-12 )

    def test_gauss_low_rank_nd_outer_grad(self):
        #################
        # Construct distribution
        dx = 40
        dy = 10
        # Prior
        mux = npr.randn(dx)
        sigmax = npr.randn(dx**2).reshape((dx,dx))
        sigmax = np.dot(sigmax, sigmax.T)
        prior = DIST.NormalDistribution(mux, sigmax)
        # Likelihood
        mu = npr.randn(dy)
        sigma = npr.randn(dy**2).reshape((dy,dy))
        sigma = np.dot(sigma, sigma.T)
        c = npr.randn(dy)
        T = npr.randn(dy*dx).reshape((dy,dx))
        T[-5:,:] = T[:5,:]
        y = c + np.dot(T, prior.rvs(1)[0,:])
        logL = LKL.AdditiveLinearNormalLogLikelihood(y, c, T, mu, sigma)
        # Posterior
        pi = INFDIST.BayesPosteriorDistribution(logL, prior)

        ##################
        # Build Laplace low-rank approximation using outer product of gradients
        pi_laplace = TM.laplace_approximation(pi, None, tol=self.tol, ders=1)
        # Check variance diagnostic (should be at machine precision)
        var_diag = DIAG.variance_approx_kl(pi_laplace, pi, qtype=0, qparams=10000)
        self.assertTrue( var_diag < 1e-12 )

def build_suite(ttype='all'):
    suite_laplace_approx = unittest.TestLoader().loadTestsFromTestCase( LaplaceApproximation )
    # GROUP SUITES
    suites_list = []
    if ttype in ['all','serial']:
        suites_list = [ suite_laplace_approx ]
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