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

import logging
from typing import List

import click
import numpy.random as npr

import sys
import unittest

import TransportMaps as TM
from TransportMaps.tests import test_distributions
from TransportMaps.tests import test_laplace
from TransportMaps.tests import test_transportmaps
from TransportMaps.tests import test_transportmap_distributions
from TransportMaps.tests import test_transportmap_distributions_sampling
from TransportMaps.tests import test_kl_divergence
from TransportMaps.tests import test_kl_minimization
from TransportMaps.tests import test_L2_misfit
from TransportMaps.tests import test_L2_minimization
from TransportMaps.tests import test_scripts
from TransportMaps.tests import test_sequential_inference


D_TESTS = {
    'distributions': test_distributions,
    'laplace': test_laplace,
    'transportmaps': test_transportmaps,
    'transportmap_distributions': test_transportmap_distributions,
    'transportmap_distributions_sampling': test_transportmap_distributions_sampling,
    'kl_divergence': test_kl_divergence,
    'kl_minimization': test_kl_minimization,
    'L2_misfit': test_L2_misfit,
    'L2_minimization': test_L2_minimization,
    'scripts': test_scripts,
    'sequential_inference': test_sequential_inference
}


@click.command(
    name='tmap-run-tests',
    help='Run the unit tests'
)
@click.option(
    '--ttype', type=click.Choice(['serial', 'parallel', 'all']), default='serial',
    help='Whether to run serial, parallel or all tests'
)
@click.option(
    '--failfast', type=bool, is_flag=True,
    help='Whether to fail at the first error'
)
@click.option(
    '--log', type=int, default=logging.WARNING,
    help='Logging level'
)
@click.option(
    '-v', '--verbosity', 'verbosity', type=int, default=2,
    help='Verbosity level of unittest'
)
@click.argument(
    'lst_tests', nargs=-1, type=click.Choice(
        [
            'distributions',
            'laplace',
            'transportmaps',
            'transportmap_distributions',
            'transportmap_distributions_sampling',
            'kl_divergence',
            'kl_minimization',
            'L2_misfit',
            'L2_minimization',
            'scripts',
            'sequential_inference'
        ]
    )
)
def run_tests(
        ttype: str,
        failfast: bool,
        log: int,
        verbosity: int,
        lst_tests: List[str],
):
    npr.seed(1)
    TM.setLogLevel(log)

    if len(lst_tests) > 0:
        d_tests = {
            k: D_TESTS[k]
            for k in lst_tests
        }
    else:
        d_tests = D_TESTS

    suites_list = [
        t.build_suite(ttype)
        for t in d_tests.values()
    ]

    all_suites = unittest.TestSuite(suites_list)
    # RUN
    tr = unittest.TextTestRunner(
        verbosity=verbosity,
        failfast=failfast
    ).run(all_suites)
    # Raise error if some tests failed or exited with error state
    nerr = len(tr.errors)
    nfail = len(tr.failures)
    if nerr + nfail > 0:
        print("Errors: %d, Failures: %d" % (nerr, nfail))
        sys.exit(1)


if __name__ == '__main__':
    run_tests()
