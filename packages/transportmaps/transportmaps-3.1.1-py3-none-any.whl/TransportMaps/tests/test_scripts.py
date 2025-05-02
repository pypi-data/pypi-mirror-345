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

try:
    import mpi_map
    MPI_SUPPORT = True
except:
    MPI_SUPPORT = False

class Scripts_unittest(unittest.TestCase):
    def setUp(self):
        import pickle
        import numpy as np
        import numpy.random as npr
        import TransportMaps.Distributions as DIST
        # Parameters
        self.dim = 5
        self.dist_fname = 'Distribution.pkl'
        self.fname_list = [self.dist_fname, self.dist_fname + '.lock']
        # Build and store target distribution
        tar_mu = npr.randn(self.dim)
        tar_sig = npr.randn(self.dim**2).reshape((self.dim, self.dim))
        tar_sig2 = np.dot(tar_sig, tar_sig.T)
        target = DIST.NormalDistribution(tar_mu, covariance=tar_sig2)
        with open(self.dist_fname, 'wb') as out_stream:
            pickle.dump(target, out_stream)

    def tearDown(self):
        import os
        for fname in self.fname_list:
            if os.path.exists(fname):
                os.remove(fname)

    def postprocess(self):
        from distutils.spawn import find_executable
        from subprocess import call
        # Parameters
        self.post_fname = 'Postprocess'
        self.fname_list.append( self.post_fname + '.pkl' )
        self.fname_list.append( self.post_fname + '.bak' )
        self.fname_list.append( self.post_fname + '.hdf5' )
        self.fname_list.append( self.post_fname + '.hdf5.lock' )
        # Find path to script (to avoid long paths with sh..)
        script_path = find_executable("tmap-postprocess")
        # Run post-process script with different options
        # Target aligned conditionals
        outsig = call([
            "python", script_path, "aligned-conditionals",
            "--input=" + self.tm_fname,
            "--dist=exact-target",
            "--no-plotting",
            "--output-pkl=" + self.post_fname + '.pkl',
            "--overwrite"
        ])
        self.assertFalse( outsig )
        # Random aligned conditionals
        outsig = call([
            "python", script_path, "random-conditionals",
            "--input=" + self.tm_fname,
            "--dist=approx-base", "--no-plotting",
            "--n-points-x-ax=20", "--n-plots-x-ax=3",
            "--output-pkl=" + self.post_fname + '.pkl',
            "--overwrite"])
        self.assertFalse( outsig )
        # Pullback aligned conditionals
        outsig = call([
            "python", script_path, "aligned-conditionals",
            "--input=" + self.tm_fname,
            "--dist=approx-base", "--no-plotting",
            "--n-points-x-ax=20",
            "--output-pkl=" + self.post_fname + '.pkl',
            "--overwrite"
        ])
        self.assertFalse( outsig )
        # Target aligned conditionals
        outsig = call([
            "python", script_path, "aligned-marginals",
            "--input=" + self.tm_fname,
            "--dist=approx-target",
            "--no-plotting",
            "--output-h5=" + self.post_fname + '.hdf5',
            "--overwrite"
        ])
        self.assertFalse(outsig)
        # Variance diagnostic (MC)
        outsig = call([
            "python", script_path, "variance-diagnostic",
            "--input=" + self.tm_fname,
            "--dist=exact-base",
            "--qtype=0", "--qnum=100",
            "--output-h5=" + self.post_fname + '.hdf5',
            "--overwrite"
        ])
        self.assertFalse( outsig )
        # Variance diagnostic (MC increased)
        outsig = call([
            "python", script_path,  "variance-diagnostic",
            "--input=" + self.tm_fname,
            "--dist=exact-base",
            "--qtype=0", "--qnum=1000",
            "--output-h5=" + self.post_fname + '.hdf5',
            "--overwrite"
        ])
        self.assertFalse( outsig )
        # Variance diagnostic (Quadrature)
        outsig = call([
            "python", script_path, "variance-diagnostic",
            "--input=" + self.tm_fname,
            "--dist=exact-base",
            "--qtype=3",
            "--qnum=%s" % ','.join(['3']*self.dim),
            "--output-h5=" + self.post_fname + '.hdf5',
            "--overwrite"
        ])
        self.assertFalse(outsig)

    def sampling(self):
        from TransportMaps import PYHMC_SUPPORT
        from distutils.spawn import find_executable
        from subprocess import call
        # Parameters
        self.post_fname = 'Sampling'
        self.fname_list.append( self.post_fname + '.hdf5' )
        self.fname_list.append( self.post_fname + '.hdf5.lock' )
        # Find path to script (to avoid long paths with sh..)
        script_path = find_executable("tmap-sampling")
        # Run sampling script with different options
        # Quadrature
        outsig = call([
            "python", script_path, "quadrature",
            "--input=" + self.tm_fname,
            "--dist=exact-base",
            "--qtype=0", "--qnum=1000",
            "--output-h5=" + self.post_fname + '.hdf5',
            "--overwrite"
        ])
        self.assertFalse(outsig)
        # Importance sampling
        outsig = call([
            "python", script_path, "importance-sampling",
            "--input=" + self.tm_fname,
            "--n-samples=1000",
            "--output-h5=" + self.post_fname + '.hdf5',
            "--overwrite"
        ])
        # MCMC Metropolis-Hastings
        outsig = call([
            "python", script_path, "mcmc",
            "--input=" + self.tm_fname,
            '--method=mh',
            "--n-samples=100",
            "--output-h5=" + self.post_fname + '.hdf5',
            "--overwrite"
        ])
        self.assertFalse(outsig)
        # MCMC Metropolis-Hastings with independent proposal
        outsig = call([
            "python", script_path, "mcmc",
            "--input=" + self.tm_fname,
            '--method=mhind',
            "--n-samples=100",
            "--output-h5=" + self.post_fname + '.hdf5',
            "--overwrite"
        ])
        self.assertFalse(outsig)
        if PYHMC_SUPPORT:
            # Hamiltonian Monte Carlo
            outsig = call([
                "python", script_path, "mcmc",
                "--input=" + self.tm_fname,
                '--method=hmc',
                "--n-samples=100",
                "--output-h5=" + self.post_fname + '.hdf5',
                "--overwrite"
            ])
            self.assertFalse(outsig)



    def test_laplace(self):
        from distutils.spawn import find_executable
        from subprocess import call
        # Parameters
        self.tm_fname = 'Laplace.pkl'
        self.fname_list.append( self.tm_fname )
        # Find path to script (to avoid long paths with sh..)
        script_path = find_executable("tmap-laplace")
        # Run laplace script
        outsig = call(["python", script_path, "--input=" + self.dist_fname,
                       "--output=" + self.tm_fname])
        self.assertFalse( outsig )
        # Test post-process
        self.sampling()
        self.postprocess()

    def test_direct(self):
        from distutils.spawn import find_executable
        from subprocess import call
        # Parameters
        self.tm_fname = './Direct.pkl'
        self.fname_list.append( self.tm_fname )
        # Find path to script (to avoid long paths with sh..)
        script_path = find_executable("tmap-tm")
        # Run direct script
        outsig = call(["python", script_path, "--input=" + self.dist_fname,
                       "--output=" + self.tm_fname,
                       "--mtype=intexp", "--span=total", "--btype=poly", "--order=1",
                       "--qtype=0", "--qnum=1000", '--maxit=1000', '--ders=2', '--tol=1e-3'])
        self.assertFalse( outsig )
        # Test post-process
        self.sampling()
        self.postprocess()

    # def test_direct_xml(self):
    #     # from distutils.spawn import find_executable
    #     # import os.path
    #     # from subprocess import call
    #     # # Parameters
    #     # tol = 1e-3
    #     # ders = 2
    #     # self.tm_fname = 'Direct.pkl'
    #     # self.fname_list.append( self.tm_fname )
    #     # # Find path to script (to avoid long paths with sh..)
    #     # script_path = find_executable("tmap-tm")
    #     # # Run direct script
    #     # test_map_xml_dir = os.path.dirname(os.path.realpath(__file__)) + \
    #     #                    '/xml/maps/'
    #     # xml_map_fname = 'TotalOrdIntExpLinearMap_5d.xml'
    #     # outsig = call(["python", script_path, "--input=" + self.dist_fname,
    #     #                "--output=" + self.tm_fname,
    #     #                "--map-descr=" + test_map_xml_dir + xml_map_fname,
    #     #                "--qtype=0", "--qnum=1000"])
    #     # self.assertFalse( outsig )
    #     # # Test post-process
    #     # self.postprocess()


def build_suite(ttype='all'):
    suites_list = []
    if ttype in ['all','serial']:
        scripts_suite = unittest.TestLoader().loadTestsFromTestCase( Scripts_unittest )
        suites_list.append( scripts_suite )
    all_suites = unittest.TestSuite(suites_list)
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
