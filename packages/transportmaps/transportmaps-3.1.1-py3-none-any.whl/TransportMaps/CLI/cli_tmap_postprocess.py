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

import functools
import logging
import pickle
import numpy as np
import sys
from pathlib import Path
from typing import Union, List, Tuple

import click

from TransportMaps import MPIPoolContext, Samplers
from TransportMaps import Diagnostics

from . import AvailableOptions as AO
from ._utils import _lambda_str_to_list_argument, _general_options, _ask_overwrite, _load_input, _select_dist, \
    _select_dist_tuple, H5, logged

__all__ = [
    'tmap_postprocess'
]


_PLOT_OPTIONS = [
    click.option(
        '--store-fig-dir', required=False, type=Path,
        help='path to the directory where to store figures'
    ),
    click.option(
        '--store-fig-fmats', default='png,svg', type=lambda s: s.split(','),
        help='figure formats - see matplotlib for supported formats'
    ),
    click.option(
        '--extra-tit', type=str,
        help='additional title for the figures\' file names'
    ),
    click.option(
        '--no-plotting', is_flag=True,
        help='do not plot figures, but only store their data'
    ),
]


def _plot_options(f):
    return functools.reduce(lambda x, opt: opt(x), _PLOT_OPTIONS, f)


def _store_figures(fig, fname, fmats):
    for fmat in fmats:
        fig.savefig(fname + '.' + fmat, format=fmat, bbox_inches='tight');


@click.group(
    name='tmap-postprocess',
    help="""
    Given a file (--input) storing the transport map pushing forward a base distribution
    to a target distribution, provides a number of diagnositic routines.
    All files involved are stored and loaded using the python package pickle and
    an extra file OUTPUT.hdf5 is created to store big datasets in the hdf5 format.
    """
)
def tmap_postprocess():
    pass


@tmap_postprocess.command(
    name='aligned-conditionals',
    help='plot aligned slices of the selected distribution'
)
@_general_options
@click.option(
    '--dist', type=click.Choice(AO.AVAIL_DISTRIBUTIONS), required=True,
    help='distribution for which are plotted/computed aligned slices'
)
@_plot_options
@click.option(
    '--output-pkl', 'path_output_pkl', required=True, type=Path,
    help='path to the pickle file storing small size postprocess data.'
)
@click.option(
    '--n-points-x-ax', type=int, default=40,
    help='number of discretization points per axis',
)
@click.option(
    '--n-tri-plots', type=_lambda_str_to_list_argument(int), default=0,
    help='list of dimensions to be in the subplots'
)
@click.option(
    '--range', 'plot_range', type=float, nargs=2, default=(-5., 5.),
    help='list of two floats for the range'
)
@logged
def aligned_conditionals(
        path_input: Path,
        path_output_pkl: Path,
        store_fig_dir: Union[None, Path],
        store_fig_fmats: List[str],
        extra_tit: Union[None, str],
        no_plotting: bool,
        overwrite: bool,
        nprocs: int,
        dist: str,
        n_points_x_ax: int,
        n_tri_plots: List[int],
        plot_range: Tuple[float, float],
        log: int
):
    if not overwrite and path_output_pkl.is_file() and not _ask_overwrite():
        print('Terminating')
        sys.exit(0)
    with MPIPoolContext(nprocs) as mpi_pool:
        stg = _load_input(path_input)
        d = _select_dist(stg, dist)
        data = Diagnostics.computeAlignedConditionals(
            d, dimensions_vec=n_tri_plots,
            numPointsXax=n_points_x_ax,
            range_vec=plot_range,
            mpi_pool=mpi_pool)
        with open(path_output_pkl, 'wb') as ostr:
            pickle.dump(data, ostr)
        if not no_plotting:
            fig = Diagnostics.plotAlignedConditionals(
                data=data, show_flag=(store_fig_dir is None));
            if store_fig_dir is not None:
                _store_figures(
                    fig,
                    store_fig_dir / f'aligned-conditionals-{dist}-{extra_tit}',
                    fmats=store_fig_fmats
                )


@tmap_postprocess.command(
    name='random-conditionals',
    help='plot random slices of the selected distribution'
)
@_general_options
@click.option(
    '--dist', type=click.Choice(AO.AVAIL_DISTRIBUTIONS), required=True,
    help='distribution for which are plotted/computed aligned slices'
)
@_plot_options
@click.option(
    '--output-pkl', 'path_output_pkl', required=True, type=Path,
    help='path to the pickle file storing small size postprocess data.'
)
@click.option(
    '--n-points-x-ax', type=int, default=40,
    help='number of discretization points per axis',
)
@click.option(
    '--anchor', type=_lambda_str_to_list_argument(float),
    help='list of floats f1,f2,f3,... for the anchor point '
         '(the list should be consistent with the dimension of the distribution)'
)
@click.option(
    '--range', 'plot_range', type=float, nargs=2, default=(-5., 5.),
    help='list of two floats for the range'
)
@click.option(
    '--n-plots-x-ax', type=int, default=6,
    help='number of subplots'
)
@logged
def random_conditionals(
        path_input: Path,
        path_output_pkl: Path,
        store_fig_dir: Union[None, Path],
        store_fig_fmats: List[str],
        extra_tit: Union[None, str],
        no_plotting: bool,
        overwrite: bool,
        nprocs: int,
        dist: str,
        n_points_x_ax: int,
        anchor: Tuple[float],
        plot_range: Tuple[float, float],
        n_plots_x_ax: int,
        log: int
):
    if not overwrite and path_output_pkl.is_file() and not _ask_overwrite():
        print('Terminating')
        sys.exit(0)
    with MPIPoolContext(nprocs) as mpi_pool:
        stg = _load_input(path_input)
        d = _select_dist(stg, dist)
        data = Diagnostics.computeRandomConditionals(
            d, num_conditionalsXax=n_plots_x_ax,
            numPointsXax=n_points_x_ax,
            pointEval=anchor, range_vec=plot_range,
            mpi_pool=mpi_pool)
        with open(path_output_pkl, 'wb') as ostr:
            pickle.dump(data, ostr)
        if not no_plotting:
            fig = Diagnostics.plotAlignedConditionals(
                data=data, show_flag=(store_fig_dir is None));
            if store_fig_dir is not None:
                _store_figures(
                    fig,
                    store_fig_dir / f'random-conditionals-{dist}-{extra_tit}',
                    fmats=store_fig_fmats
                )


@tmap_postprocess.command(
    name='variance-diagnostic',
    help='compute variance diagostic using the sampling distribution --dist'
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
def variance_diagnostic(
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
    d1, d2 = _select_dist_tuple(stg, dist)
    if not overwrite and path_output_h5.is_file() and not _ask_overwrite():
        with H5(path_output_h5, 'r') as h5_root:
            vals_d1 = h5_root['d1'][:]
            vals_d2 = h5_root['d2'][:]
            w = h5_root['w'][:]
    else:
        with MPIPoolContext(nprocs) as mpi_pool:
            (x, w) = d1.quadrature(qtype, qnum, mpi_pool=mpi_pool)
            vals_d1, vals_d2 = Diagnostics.compute_vals_variance_approx_kl(
                d1, d2, x=x, mpi_pool_tuple=(None, mpi_pool))
        with H5(path_output_h5, 'w') as h5_root:
            h5_root.create_dataset('d1', data=vals_d1, chunks=True)
            h5_root.create_dataset('d2', data=vals_d2, chunks=True)
            h5_root.create_dataset('w', data=w, chunks=True)
    var_diag_tm = Diagnostics.variance_approx_kl(
        d1, d2,
        vals_d1=vals_d1, vals_d2=vals_d2, w=w
    )
    print(f"Variance diagnostics {var_diag_tm}")


@tmap_postprocess.command(
    name='aligned-marginals',
    help='compute aligned marginals of the distribution --dist'
)
@_general_options
@click.option(
    '--dist', type=click.Choice(AO.AVAIL_DISTRIBUTIONS), required=True,
    help='distribution for which are plotted/computed aligned slices'
)
@_plot_options
@click.option(
    '--output-h5', 'path_output_h5', required=True, type=Path,
    help='path to the hdf5 file storing big size postprocess data.'
)
@click.option(
    '--n-points', type=int, default=1000,
    help='number of samples to be used for the kernel density estimation'
)
@click.option(
    '--n-tri-plots', type=_lambda_str_to_list_argument(int), default=0,
    help='list of dimensions to be in the subplots'
)
@click.option(
    '--scatter', is_flag=True,
    help='produce scatter plots instead of contours'
)
@logged
def aligned_marginals(
        path_input: Path,
        path_output_h5: Path,
        store_fig_dir: Union[None, Path],
        store_fig_fmats: List[str],
        extra_tit: Union[None, str],
        no_plotting: bool,
        overwrite: bool,
        nprocs: int,
        dist: str,
        n_points: int,
        n_tri_plots: List[int],
        scatter: bool,
        log: int
):
    stg = _load_input(path_input)
    d = _select_dist(stg, dist)
    if not overwrite and path_output_h5.is_file() and not _ask_overwrite():
        with H5(path_output_h5, 'r') as h5_root:
            x = h5_root['x']
    else:
        with MPIPoolContext(nprocs) as mpi_pool:
            x = d.rvs(n_points, mpi_pool=mpi_pool)
        with H5(path_output_h5, 'w') as h5_root:
            h5_root.create_dataset('x', data=x, chunks=True)
    if not no_plotting:
        fig = Diagnostics.plotAlignedMarginals(
            x, dimensions_vec=n_tri_plots,
            scatter=scatter,
            show_flag=(store_fig_dir is None)
        )
        if store_fig_dir is not None:
            _store_figures(
                fig,
                store_fig_dir / f'aligned-conditionals-{dist}-{extra_tit}',
                fmats=store_fig_fmats
            )


@tmap_postprocess.command(
    name='ess',
    help='compute the effective sample size of a Markov Chain'
)
@click.option(
    '--input-h5', 'path_input_h5', required=True, type=Path,
    help='path to the hdf5 file storing the Markov Chain'
)
@_plot_options
@click.option(
    '--method', type=click.Choice(list(AO.AVAIL_MCMC_ESS_METHODS.keys())), default='uw',
    help=f'Method for computing the ESS. Options are {AO.AVAIL_MCMC_ESS_METHODS}'
)
@click.option(
    '--skip', type=int, default=1,
    help='number of samples to be skipped in the effective sample size estimation'
)
@click.option(
    '--q', type=float, default=0.99,
    help='Quantile used for the estimation of the sample size. '
         'This is estimated over the worst decaying autocorrelation rate.'
)
@click.option(
    '--corr-plot-lag', type=int, default=100,
    help='maximum lag to be plotted'
)
@logged
def ess(
        path_input_h5: Path,
        method: str,
        skip: int,
        q: float,
        corr_plot_lag: int,
        store_fig_dir: Union[None, Path],
        store_fig_fmats: List[str],
        extra_tit: Union[None, str],
        no_plotting: bool,
        log: int
):
    if not no_plotting:
        import matplotlib.pyplot as plt
    with H5(path_input_h5, 'r') as h5_root:
        s = h5_root['s']
    fig = None if not no_plotting else plt.figure()
    if method == 'acor':
        lst_ess = Samplers.ess(
            s[::skip, :],
            quantile=q,
            plotting=not no_plotting,
            plot_lag=corr_plot_lag,
            fig=fig
        )
    elif method == 'uw':
        lst_ess = Samplers.uwerr(
            s[::skip, :],
            plotting=not no_plotting,
        )
    if not no_plotting:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(ess, drawstyle='steps-mid')
        ax.set_ylabel("ESS")
        ax.set_xlable("Dimension")
        if store_fig_dir is None:
            plt.show(False)
        else:
            _store_figures(
                fig, 
                store_fig_dir / f'metropolis-ess-hist-{extra_tit}',
                store_fig_fmats
            )
    amin_ess = np.argmin(lst_ess)
    amax_ess = np.argmax(lst_ess)
    min_ess = lst_ess[amin_ess]
    max_ess = lst_ess[amax_ess]
    mean_ess = np.mean(lst_ess)
    tot_samps = len(s)
    logging.info(
        f"- ESS: {min_ess}/{tot_samps} "
        f"-- worst {min_ess/float(tot_samps)*100:2.3f} - d: {amin_ess} "
        f"-- best {max_ess/float(tot_samps)*100:2.3f} - d: {amax_ess} " 
        f"-- avg {mean_ess/float(tot_samps)*100:2.3f}"
    )


if __name__ == '__main__':
    tmap_postprocess()
