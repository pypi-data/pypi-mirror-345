#!/usr/bin/env python

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

import logging
import sys
from pathlib import Path
from typing import List
import numpy as np
import click

from TransportMaps import MPIPoolContext, Samplers, Distributions, Maps
from TransportMaps.Distributions import Inference

from . import AvailableOptions as AO
from ._utils import _general_options, _lambda_str_to_list_argument, _load_input, _select_dist, _ask_overwrite, H5, \
    logged

__all__ = [
    'tmap_sampling'
]


@click.group(
    name='tmap-sampling',
    help="""
    Given a file (--input) storing the transport map pushing forward a base distribution
    to a target distribution, provides a number of sampling routines.
    All the generated outputs are stored in a hdf5 file.
    """
)
def tmap_sampling():
    pass

@tmap_sampling.command(
    name='quadrature',
    help='compute quadrature points using the sampling distribution --dist'
)
@_general_options
@click.option(
    '--dist', type=click.Choice(AO.AVAIL_DISTRIBUTIONS), required=True,
    help='distribution for which are plotted/computed aligned slices'
)
@click.option(
    '--output-h5', 'path_output_h5', required=True, type=Path,
    help='path to the hdf5 file storing big size postprocess data.'
)
@click.option(
    '--qtype', required=True, type=click.IntRange(0, 3),
    help=f'quadrature type for the discretization of the KL-divergence {AO.AVAIL_QTYPE}'
)
@click.option(
    '--qnum', required=True, type=_lambda_str_to_list_argument(int),
    help='quadrature level (must be a comma separated list if qtype requires it)'
)
@logged
def quadrature(
        path_input: Path,
        path_output_h5: Path,
        overwrite: bool,
        nprocs: int,
        dist: str,
        qtype: int,
        qnum: List[int],
        log: int
):
    stg = _load_input(path_input)
    d = _select_dist(stg, dist)
    if not overwrite and path_output_h5.is_file() and not _ask_overwrite():
        logging.info('Terminating')
        sys.exit(0)
    with MPIPoolContext(nprocs) as mpi_pool:
        (x, w) = d.quadrature(qtype, qnum, mpi_pool=mpi_pool)
    with H5(path_output_h5, 'w') as h5_root:
        h5_root.create_dataset('x', data=x, chunks=True)
        h5_root.create_dataset('w', data=w, chunks=True)
    logging.info('Quadrature generated and stored')


@tmap_sampling.command(
    name='importance-sampling',
    help='compute quadrature points of the target distribution '
         'using importance sampling from approximate base distribution  '
         'using the corresponding exact base distribution as bias.'
)
@_general_options
@click.option(
    '--output-h5', 'path_output_h5', required=True, type=Path,
    help='path to the hdf5 file storing big size postprocess data.'
)
@click.option(
    '--n-samples', type=int, required=True,
    help='Number of samples to generate'
)
@logged
def importance_sampling(
        path_input: Path,
        n_samples: int,
        path_output_h5: Path,
        overwrite: bool,
        nprocs: int,
        log: int
):
    stg = _load_input(path_input)
    if not overwrite and path_output_h5.is_file() and not _ask_overwrite():
        logging.info('Terminating')
        sys.exit(0)
    with MPIPoolContext(nprocs) as mpi_pool:
        sampler = Samplers.ImportanceSampler(
            stg.approx_base_distribution,
            stg.base_distribution
        )
        (x, w) = sampler.rvs(n_samples, mpi_pool_tuple=(mpi_pool, None))
        x = stg.approx_target_distribution.map_samples_base_to_target(
            x, mpi_pool=mpi_pool
        )
    with H5(path_output_h5, 'w') as h5_root:
        h5_root.create_dataset('x', data=x, chunks=True)
        h5_root.create_dataset('w', data=w, chunks=True)
    logging.info('Importance sampling quadrature generated and stored')


@tmap_sampling.command(
    name='mcmc',
    help='compute quadrature points of the target distribution '
         'using Markov Chain Monte Carlo from approximate base distribution  '
         'using the corresponding exact base distribution as bias.'
)
@_general_options
@click.option(
    '--output-h5', 'path_output_h5', required=True, type=Path,
    help='path to the hdf5 file storing big size postprocess data.'
)
@click.option(
    '--method', type=click.Choice(list(AO.AVAIL_MCMC_ALGORITHMS.keys())),
    default='mh',
    help=f'MCMC method to be used for sampling. Options are {AO.AVAIL_MCMC_ALGORITHMS}'
)
@click.option(
    '--n-samples', type=int, required=True,
    help='Number of samples to generate'
)
@click.option(
    '--burnin', type=int, default=0,
    help='Number of samples to be used as burn-in'
)
@click.option(
    '--skip', type=int, default=0,
    help='number of sample to be skipped (>=0) in storage (a NSAMP*SKIP chain is subsampled)'
)
@click.option(
    '--mh-eps', type=float, default=0.1,
    help='variance of the Standard Normal proposal in Metropolis-Hasting'
)
@click.option(
    '--mh-pcn', type=bool, is_flag=True,
    help='Use the preconditioned Crank-Nicolson proposal '
         'N(sqrt(1-eps**2)u,eps**2 * Sigma) '
         'where Sigma is the covariance of the prior (has to be Gaussian).'
)
@click.option(
    '--hmc-eps', type=float, default=0.2,
    help='epsilon value in Hamiltonian Monte Carlo'
)
@click.option(
    '--hmc-nsteps', type=int, default=1,
    help='number of steps per sample in Hamiltonian Monte Carlo'
)
@logged
def mcmc(
        path_input: Path,
        path_output_h5: Path,
        method: str,
        n_samples: int,
        burnin: int,
        skip: int,
        mh_eps: float,
        mh_pcn: bool,
        hmc_eps: float,
        hmc_nsteps: int,
        overwrite: bool,
        nprocs: int,
        log: int
):
    stg = _load_input(path_input)
    if not overwrite and path_output_h5.is_file() and not _ask_overwrite():
        logging.info('Terminating')
        sys.exit(0)
    if method == 'mh':
        if mh_pcn:
            if isinstance(stg.target_distribution, Inference.BayesPosteriorDistribution) and \
                    (
                        isinstance(stg.target_distribution.prior, Distributions.NormalDistribution) or \
                        isinstance(stg.target_distribution.prior, Distributions.StandardNormalDistribution)
                    ):
                prop_distribution = Distributions.MeanConditionallyGaussianDistribution(
                    Maps.PreconditionedCrankNicolsonMap(
                        stg.base_distribution.dim, mh_eps),
                    mh_eps ** 2 * stg.target_distribution.prior.covariance
                )
            else:
                raise ValueError(
                    "In order to use preconditioned Crank-Nicolson " + \
                    "the target distribution must be a Bayesian posterior with " + \
                    "normal prior"
                )
        else:
            prop_distribution = Distributions.MeanConditionallyNormalDistribution(
                Maps.IdentityTransportMap(stg.base_distribution.dim),
                mh_eps * np.eye(stg.base_distribution.dim)
            )
        sampler = Samplers.MetropolisHastingsSampler(
            stg.approx_base_distribution, prop_distribution)
    elif method == 'mhind':
        sampler = Samplers.MetropolisHastingsIndependentProposalsSampler(
            stg.approx_base_distribution, stg.base_distribution)
    elif method == 'hmc':
        if not isinstance(stg.base_distribution, Distributions.StandardNormalDistribution):
            logging.warning(
                "The HMC algorithm uses a Standard Normal distribution "
                "as default proposal"
            )
        sampler = Samplers.HamiltonianMonteCarloSampler(stg.approx_base_distribution)
    else:
        raise NotImplementedError(f'Method {method} not implemented')
    if method in ['mh', 'mhind']:
        with MPIPoolContext(nprocs) as mpi_pool:
            (s, _) = sampler.rvs(n_samples * (skip + 1), x0=None,
                                 mpi_pool_tuple=(mpi_pool, None))
    elif method == 'hmc':
        (s, _) = sampler.rvs(
            n_samples * (skip + 1), x0=None,
            epsilon=hmc_eps, n_steps=hmc_nsteps)
    s = s[burnin::(skip + 1), :]  # Skip burnin and subsampling
    with MPIPoolContext(nprocs) as mpi_pool:
        x = stg.approx_target_distribution.map_samples_base_to_target(
            s, mpi_pool=mpi_pool)
    with H5(path_output_h5, 'w') as h5_root:
        h5_root.create_dataset('s', data=s, chunks=True)
        h5_root.create_dataset('x', data=x, chunks=True)
    logging.info('Markov chain generated and stored')


if __name__ == '__main__':
    tmap_sampling()
