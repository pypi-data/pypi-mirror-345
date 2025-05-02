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

import sys
from pathlib import Path
import click
import logging

from ._utils import CLIException, _lambda_str_to_list_argument

from . import AvailableOptions as AO
from ..Misc import setLogLevel
from .ConstructionScriptBase import ConstructionScript


__all__ = [
    'tmap_tm'
]


@click.command(
    name='tmap-tm',
    help="""
    Given a file (--input) storing the target distribution, produce the transport map that
    pushes forward the base distribution (default: standard normal) to the target distribution.
    All files involved are stored and loaded using the python package pickle.
    """
)
@click.option(
    '--input', required=True, type=Path,
    help='path to the file containing the target distribution'
)
@click.option(
    '--output', required=True, type=Path,
    help='path to the output file containing the transport map, '
         'the base distribution, the target distribution and all '
         'the additional parameters used for the construction'
)
@click.option(
    '--base-dist', required=False, type=Path,
    help='path to the file containing the base distribution '
         '(default: a standard normal of suitable dimension)'
)
@click.option(
    '--mtype', required=False, type=click.Choice([k for k in AO.AVAIL_MONOTONE]),
    help=f'monotone format for the transport {AO.AVAIL_MONOTONE}'
)
@click.option(
    '--span', required=False, type=click.Choice([k for k in AO.AVAIL_SPAN]),
    help=f'span type for all the components of the map {AO.AVAIL_SPAN}'
)
@click.option(
    '--btype', required=False, type=click.Choice([k for k in AO.AVAIL_BTYPE]),
    help=f'basis types for all the components of the map {AO.AVAIL_BTYPE}'
)
@click.option(
    '--order', required=False, type=int,
    help='order of the transport map'
)
@click.option(
    '--sparsity', required=False, type=click.Choice([k for k in AO.AVAIL_SPARSITY]), default='tri',
    help=f'sparsity pattern {AO.AVAIL_SPARSITY}'
)
@click.option(
    '--map-pkl', required=False, type=Path,
    help='unpickable (pickle) file containing the map to be used.'
         'It may be a comma separated list of files, containing the '
         'maps to be used for sequential adaptation schemes. '
         'In the latter case the maps must be nested (i.e. the next '
         'map must be an enrichment of the previous map). '
         'The map must be of the correct dimension'
)
@click.option(
    '--map-factory-pkl', required=False, type=Path,
    help='unpickable (pickle) file containing a map factory '
         '(instance of MapFactory or MapListFactory) used to '
         'generate maps (or list of maps). This is used for only '
         'algorithms based on tmap-tm, not by tmap-tm itself. '
         'Therefore this option is not sufficient/necessary '
         'to run tmap-tm itself.'
)
@click.option(
    '--qtype', required=True, type=click.IntRange(0, 3),
    help=f'quadrature type for the discretization of the KL-divergence {AO.AVAIL_QTYPE}'
)
@click.option(
    '--qnum', required=True, type=_lambda_str_to_list_argument(int),
    help='quadrature level (must be a comma separated list if qtype requires it)'
)
@click.option(
    '--tol', default=1e-4, type=float,
    help='kl minimization tolerance'
)
@click.option(
    '--maxit', default=100, type=int,
    help='maximum number of iterations for kl minimization'
)
@click.option(
    '--reg', type=float, default=None,
    help='a float L2 regularization parameter'
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
    '--validator', default='none', type=click.Choice([k for k in AO.AVAIL_VALIDATOR]),
    help=f'valiator to be used {AO.AVAIL_VALIDATOR}'
)
@click.option(
    '--val-eps', default=1e-2, type=float,
    help='target tolerance for solution of the stochastic program'
)
@click.option(
    '--val-cost-fun', default='tot-time', type=click.Choice([k for k in AO.AVAIL_COST_FUNCTION]),
    help=f'validator cost function {AO.AVAIL_COST_FUNCTION}'
)
@click.option(
    '--val-max-cost', default=1000, type=float,
    help='validator total cost limit'
)
@click.option(
    '--val-max-nsamps', default=10000, type=float,
    help='maximum number of samples to use in the approximation of the expecations'
)
@click.option(
    '--val-stop-on-fcast', is_flag=True,
    help='whether to stop on a forecast to exceed the cost limit '
         '(by default it stops only after exceeding the cost limit)'
)
@click.option(
    '--val-saa-eps-abs', default=1e-5, type=float,
    help='[SAA] absolute error to be used (--val-eps is relative)'
)
@click.option(
    '--val-saa-upper-mult', default=10, type=float,
    help='[SAA] upper multiplier'
)
@click.option(
    '--val-saa-lower-n', default=2, type=int,
    help='[SAA] number of samples for lower bound'
)
@click.option(
    '--val-saa-alpha', default=0.05, type=float,
    help='[SAA] quantile'
)
@click.option(
    '--val-saa-lmb-def', default=2, type=int,
    help='[SAA] default refinement multiplier'
)
@click.option(
    '--val-saa-lmb-max', default=10, type=int,
    help='[SAA] maximum refinement multiplier'
)
@click.option(
    '--val-gradboot-delta', default=5.0, type=float,
    help='[GRADBOOT] multiplicative factor of the gradient obtained'
)
@click.option(
    '--val-gradboot-n-grad', default=1, type=int,
    help='[GRADBOOT] multiplicative factor for the bootstrap sample size'
)
@click.option(
    '--val-gradboot-n-boot', default=2000, type=int,
    help='[GRADBOOT] number of bootstrap repicas'
)
@click.option(
    '--val-gradboot-alpha', default=0.95, type=float,
    help='[GRADBOOT] tolerance interval quantile'
)
@click.option(
    '--val-gradboot-lmb-min', default=2, type=int,
    help='[GRADBOOT] minimum refinement multiplier'
)
@click.option(
    '--val-gradboot-lmb-max', default=10, type=int,
    help='[GRADBOOT] maximum refinement multiplier'
)
@click.option(
    '--adapt', default='none', type=click.Choice([k for k in AO.AVAIL_ADAPTIVITY]),
    help=f'adaptivity algorithm for map construction {AO.AVAIL_ADAPTIVITY}'
)
@click.option(
    '--adapt-tol', type=float, default=5e-2,
    help='target variance diagnostic tolerance'
)
@click.option(
    '--adapt-verbosity', type=int, default=0,
    help='This regulates the amount of information printed by the logger. '
         'Values are >0 with higher values corresponding to higher verbosity.'
)
@click.option(
    '--adapt-regr', default='none', type=click.Choice([k for k in AO.AVAIL_REGRESSION_ADAPTIVITY]),
    help=f'regression algorithm to be used within adaptivity {AO.AVAIL_REGRESSION_ADAPTIVITY}'
)
@click.option(
    '--adapt-regr-reg', type=str, default=None,
    help='regularization to be used in regression'
)
@click.option(
    '--adapt-regr-tol', type=float, default=1e-6,
    help='regression tolerance'
)
@click.option(
    '--adapt-regr-maxit', type=int, default=100,
    help='maximum number of iteration in regression'
)
@click.option(
    '--adapt-fv-maxit', default=20, type=int,
    help='[FV] maximum number of iterations'
)
@click.option(
    '--adapt-fv-prune-trunc-type', default='manual', type=click.Choice([k for k in AO.AVAIL_ADAPT_TRUNC]),
    help=f'[FV] type of pruning truncation {AO.AVAIL_ADAPT_TRUNC}'
)
@click.option(
    '--adapt-fv-prune-trunc-val', type=float, default=None,
    help='[FV] prune truncation parameter'
)
@click.option(
    '--adapt-fv-avar-trunc-type', default='manual', type=click.Choice([k for k in AO.AVAIL_ADAPT_TRUNC]),
    help=f'[FV] type of active variable truncation {AO.AVAIL_ADAPT_TRUNC}'
)
@click.option(
    '--adapt-fv-avar-trunc-val', default=None, type=float,
    help='[FV] active variables trunc parameter'
)
@click.option(
    '--adapt-fv-coeff-trunc-type', default='manual', type=click.Choice([k for k in AO.AVAIL_ADAPT_TRUNC]),
    help=f'[FV] type of enrichment truncation {AO.AVAIL_ADAPT_TRUNC}'
)
@click.option(
    '--adapt-fv-coeff-trunc-val', type=int, default=None,
    help='[FV] coefficient truncation parameter'
)
@click.option(
    '--adapt-fv-ls-maxit', type=int, default=20,
    help='[FV] maximum number of line search iterations'
)
@click.option(
    '--adapt-fv-ls-delta', type=float, default=2.0,
    help='[FV] initial step size for line search'
)
@click.option(
    '--adapt-fv-interactive', is_flag=True,
    help='[FV] whether to query the user for approval to continue'
)
@click.option(
    '--laplace-pull', is_flag=True,
    help='whether to precondition pulling back the target through its Laplace approximation'
)
@click.option(
    '--map-pull', type=Path,
    help='path to file containing a map through which to pullback '
         'the target (this is done before pulling back thorugh '
         'the Laplace, if --laplace-pull is provided). '
         'The file may cointain just the map or may be the output '
         'of any other map construction scripts (tmap-tm, ...)'
)
@click.option(
    '--overwrite', is_flag=True,
    help='overwrite file if it exists'
)
@click.option(
    '--reload', is_flag=True,
    help='reload file if it exists'
)
@click.option(
    '--seed', type=int,
    help='random seed to be used'
)
@click.option(
    '--log', default=30,
    help='log level'
)
@click.option(
    '--nprocs', default=1, type=int,
    help='number of processors to be used (MPI support needed)'
)
@click.option(
    '--batch', type=_lambda_str_to_list_argument(int),
    help='batch size for evaluation of function, gradient and Hessian'
)
@click.option(
    '--interactive', is_flag=True,
    help='enter interactive mode after finishing'
)
@click.option(
    '--verbose', is_flag=True,
    help='whether to run in verbose mode'
)
def tmap_tm(**kwargs):
    try:
        script = ConstructionScript(**kwargs)
        logging.basicConfig(level=script.LOGGING_LEVEL)
        setLogLevel(level=script.LOGGING_LEVEL)
        script.load()
        script.run()
    except CLIException as e:
        print(f"CLI ERROR: {str(e)}")
        with click.Context(tmap_tm) as ctx:
            click.echo(tmap_tm.get_help(ctx))
        sys.exit(1)


if __name__ == '__main__':
    tmap_tm()
