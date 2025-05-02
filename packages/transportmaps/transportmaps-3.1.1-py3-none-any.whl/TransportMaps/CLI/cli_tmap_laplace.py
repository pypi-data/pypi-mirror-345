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
import pickle
import sys
from pathlib import Path
import click
import numpy as np

from ..Misc import DataStorageObject, setLogLevel
from .. import Distributions
from .. import Maps
from ..LaplaceApproximationRoutines import laplace_approximation
from ._utils import logged, _ask_overwrite
from . import AvailableOptions as AO

__all__ = [
    'tmap_laplace'
]


@click.command(
    name='tmap-laplace',
    help="""
    Given a file (--input) storing the target distribution, generate the linear map
    corresponding to the Laplace approximation of it.
    All files involved are stored and loaded using the python package pickle.
    """
)
@click.option(
    '--input', 'input_pkl', required=True, type=Path,
    help='path to the file containing the target distribution'
)
@click.option(
    '--output', 'output_pkl', required=True, type=Path,
    help='path to the output file containing the transport map, '
         'the base distribution, the target distribution and all '
         'the additional parameters used for the construction'
)
@click.option(
    '--tol', type=float, default=1e-4,
    help='optimization tolerance'
)
@click.option(
    '--ders', default=1,
    help=f'order of derivatives to be used in the optimization {AO.AVAIL_DERS}'
)
@click.option(
    '--fungrad', is_flag=True,
    help='whether the distributions provide a method to compute '
         'the log pdf and its gradient at the same time'
)
@click.option(
    '--hessact', is_flag=True,
    help='whether to use the action of the Hessian'
)
@click.option(
    '--x0', type=click.Choice(list(AO.AVAIL_LAPLACE_X0.keys())), default='rnd',
    help=f'Initial value to be used for the search of the MAP point. Options are {AO.AVAIL_LAPLACE_X0}'
)
@click.option(
    '--sqrt', type=click.Choice(list(AO.AVAIL_LAPLACE_SQRT.keys())), default='sym',
    help='Type of factorization to build the linear term of the Laplace map '
         'from the Laplace distribution'
)
@click.option(
    '--hess-approx', type=click.Choice(list(AO.AVAIL_LAPLACE_HESS_APPROX.keys())), default='low-rank',
    help='how to approximate the Hessian'
)
@click.option(
    '--low-rank-rnd-eps', type=float, default=1e-5,
    help='tolerance to be used in the pursue of a randomized '
         'low-rank approximation of the prior preconditioned '
         'Hessian of the log-likelihood'
)
@click.option(
    '--low-rank-rnd-pow-n', type=int, default=0,
    help='number of power iterations to be used in the pursue of a randomized '
         'low-rank approximation of the prior preconditioned '
         'Hessian of the log-likelihood'
)
@click.option(
    '--low-rank-rnd-ovsamp', type=int, default=10,
    help='oversampling to be used in the pursue of a randomized '
         'low-rank approximation of the prior preconditioned '
         'Hessian of the log-likelihood'
)
@click.option(
    '--fd-eps', type=float, default=1e-6,
    help='Tolerance to be used for the finite difference approximation of the Hessian'
)
@click.option(
    '--overwrite', is_flag=True,
    help='overwrite file if it exists'
)
@click.option(
    '--log', type=int, default=20,
    help='logging level (see logging)'
)
@logged
def tmap_laplace(
        input_pkl: Path,
        output_pkl: Path,
        tol: float,
        ders: int,
        fungrad: bool,
        hessact: bool,
        x0: str,
        sqrt: str,
        hess_approx: str,
        low_rank_rnd_eps: float,
        low_rank_rnd_pow_n: int,
        low_rank_rnd_ovsamp: int,
        fd_eps: float,
        overwrite: bool,
        log: int
):
    kwargs = locals()
    stg = DataStorageObject()
    for k, v in kwargs.items():
        setattr(stg, k, v)

    if not overwrite and output_pkl.is_file() and not _ask_overwrite():
        logging.info("Terminating")
        sys.exit(0)

    setLogLevel(log)

    with open(input_pkl, 'rb') as in_stream:
        stg.target_distribution = pickle.load(in_stream)
    if x0 == 'rnd':
        x0 = None
    elif x0 == 'zero':
        x0 = np.zeros(stg.target_distribution.dim)

    dim = stg.target_distribution.dim
    stg.base_distribution = Distributions.StandardNormalDistribution(dim)

    logging.info('Compute Laplace approximation')
    laplace_approx = laplace_approximation(
        stg.target_distribution,
        x0=x0, tol=tol, ders=ders,
        fungrad=fungrad,
        hessact=hessact,
        hess_approx=hess_approx,
        hess_fd_eps=fd_eps,
        low_rank_rnd_eps=low_rank_rnd_eps,
        low_rank_rnd_ovsamp=low_rank_rnd_ovsamp,
        low_rank_rnd_pow_n=low_rank_rnd_pow_n
    )

    logging.info('Build Laplace map')
    stg.tmap = Maps.AffineTransportMap.build_from_Normal(
        laplace_approx, typeMap=sqrt)

    stg.approx_base_distribution = Distributions.PullBackTransportMapDistribution(
        stg.tmap, stg.target_distribution)
    stg.approx_target_distribution = Distributions.PushForwardTransportMapDistribution(
        stg.tmap, stg.base_distribution)

    logging.info('Build Identity Laplace')
    stg.laplace_id = Maps.AffineTransportMap(
        c=laplace_approx.mu,
        L=np.eye(dim)
    )

    logging.info('Store tmap-laplace data')
    with open(output_pkl, 'wb') as out_stream:
        pickle.dump(stg, out_stream)


if __name__ == '__main__':
    tmap_laplace()
