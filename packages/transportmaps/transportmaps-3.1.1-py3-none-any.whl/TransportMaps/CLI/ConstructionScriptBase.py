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
import os.path
import pickle
import logging
import numpy.random as npr
from TransportMaps import laplace_approximation

from ._utils import CLIException
from .ScriptBase import Script

from ..Misc import DataStorageObject, total_time_cost_function
from ..MPI import get_mpi_pool
from .. import Maps
from .. import Distributions
from .. import Diagnostics
from .. import Builders
from ..Algorithms import Adaptivity


__all__ = ['ConstructionScript']


class ConstructionScript(Script):

    def _load_opts(self, **kwargs):
        super(ConstructionScript, self)._load_opts(**kwargs)

        # I/O
        self.BASE_DIST_FNAME = kwargs['base_dist']
        # Map type
        self.MONOTONE = kwargs['mtype']
        self.SPAN = kwargs['span']
        self.BTYPE = kwargs['btype']
        self.ORDER = kwargs['order']
        self.SPARSITY = kwargs['sparsity']
        self.MAP_PKL = kwargs['map_pkl']
        self.MAP_FACTORY_PKL = kwargs['map_factory_pkl']
        # Quadrature type
        self.stg.QTYPE = kwargs['qtype']
        self.stg.QNUM = kwargs['qnum']
        # Solver options
        self.stg.TOL = kwargs['tol']
        self.stg.MAXIT = kwargs['maxit']
        self.stg.REG = kwargs['reg']
        self.stg.DERS = kwargs['ders']
        self.stg.FUNGRAD = kwargs['fungrad']
        self.stg.HESSACT = kwargs['hessact']
        # Validation
        self.stg.VALIDATOR = kwargs['validator']
        self.stg.VAL_EPS = kwargs['val_eps']
        self.stg.VAL_COST_FUN = kwargs['val_cost_fun']
        self.stg.VAL_MAX_COST = kwargs['val_max_cost']
        self.stg.VAL_MAX_NSAMPS = kwargs['val_max_nsamps']
        self.stg.VAL_STOP_ON_FCAST = kwargs['val_stop_on_fcast']
        # Sample average approximation validator
        self.stg.VAL_SAA_EPS_ABS = kwargs['val_saa_eps_abs']
        self.stg.VAL_SAA_UPPER_MULT = kwargs['val_saa_upper_mult']
        self.stg.VAL_SAA_LOWER_N = kwargs['val_saa_lower_n']
        self.stg.VAL_SAA_ALPHA = kwargs['val_saa_alpha']
        self.stg.VAL_SAA_LMB_DEF = kwargs['val_saa_lmb_def']
        self.stg.VAL_SAA_LMB_MAX = kwargs['val_saa_lmb_max']
        # Gradient bootstrap validator
        self.stg.VAL_GRADBOOT_DELTA = kwargs['val_gradboot_delta']
        self.stg.VAL_GRADBOOT_N_GRAD = kwargs['val_gradboot_n_grad']
        self.stg.VAL_GRADBOOT_N_BOOT = kwargs['val_gradboot_n_boot']
        self.stg.VAL_GRADBOOT_ALPHA = kwargs['val_gradboot_alpha']
        self.stg.VAL_GRADBOOT_LMB_MIN = kwargs['val_gradboot_lmb_min']
        self.stg.VAL_GRADBOOT_LMB_MAX = kwargs['val_gradboot_lmb_max']
        # Adaptivity
        self.stg.ADAPT = kwargs['adapt']
        self.stg.ADAPT_TOL = kwargs['adapt_tol']
        self.stg.ADAPT_VERB = kwargs['adapt_verbosity']
        self.stg.ADAPT_REGR = kwargs['adapt_regr']
        self.stg.ADAPT_REGR_REG = kwargs['adapt_regr_reg']
        self.stg.ADAPT_REGR_TOL = kwargs['adapt_regr_tol']
        self.stg.ADAPT_REGR_MAX_IT = kwargs['adapt_regr_maxit']
        self.stg.ADAPT_FV_MAX_IT = kwargs['adapt_fv_maxit']
        self.stg.ADAPT_FV_PRUNE_TRUNC_TYPE = kwargs['adapt_fv_prune_trunc_type']
        self.stg.ADAPT_FV_PRUNE_TRUNC_VAL = kwargs['adapt_fv_prune_trunc_val']
        self.stg.ADAPT_FV_AVAR_TRUNC_TYPE = kwargs['adapt_fv_avar_trunc_type']
        self.stg.ADAPT_FV_AVAR_TRUNC_VAL = kwargs['adapt_fv_avar_trunc_val']
        self.stg.ADAPT_FV_COEFF_TRUNC_TYPE = kwargs['adapt_fv_coeff_trunc_type']
        self.stg.ADAPT_FV_COEFF_TRUNC_VAL = kwargs['adapt_fv_coeff_trunc_val']
        self.stg.ADAPT_FV_LS_MAXIT = kwargs['adapt_fv_ls_maxit']
        self.stg.ADAPT_FV_LS_DELTA = kwargs['adapt_fv_ls_delta']
        self.stg.ADAPT_FV_INTERACTIVE = kwargs['adapt_fv_interactive']
        # Pre-pull Laplace
        self.stg.LAPLACE_PULL = kwargs['laplace_pull']
        self.stg.MAP_PULL = kwargs['map_pull']
        # Overwriting/reloading
        self.OVERWRITE = kwargs['overwrite']
        self.RELOAD = kwargs['reload']
        # Random seed
        self.stg.SEED = kwargs['seed']
        # Batching
        self.BATCH_SIZE = kwargs['batch']

    def _check_required_args(self):
        super(ConstructionScript, self)._check_required_args()
            
        # Check for required arguments
        if self.OVERWRITE and self.RELOAD:
            raise CLIException("ERROR: options --overwrite and --reload are mutually esclusive")
        if not os.path.exists(self.OUTPUT.parent):
            raise CLIException(f"ERROR: path '{self.OUTPUT}' does not exist.")
        if not self.OVERWRITE and not self.RELOAD and os.path.exists(self.OUTPUT):
            sel = ''
            while sel not in ['o', 'r', 'q']:
                sel = input(f"The file {self.OUTPUT} already exists. " + \
                            "Do you want to overwrite (o), reload (r) or quit (q)? [o/r/q] ")
            if sel == 'o':
                while sel not in ['y', 'n']:
                    sel = input("Please, confirm that you want overwrite. [y/n] ")
                if sel == 'n':
                    self.tstamp_print("Terminating.")
                    sys.exit(0)
            elif sel == 'r':
                self.RELOAD = True
            else:
                self.tstamp_print("Terminating.")
                sys.exit(0)
        if self.RELOAD:
            if self.stg.SEED is not None:
                self.tstamp_print(
                    "WARNING: a seed is defined in the reloaded options. " + \
                    "Reloading with a fixed seed does not correspond to a single run " + \
                    "with the same seed.")
        else:
            if self.stg.QTYPE < 3:
                self.stg.QNUM = self.stg.QNUM[0]
            map_descr_list = [self.MONOTONE, self.SPAN, self.BTYPE, self.ORDER]
            is_not_subclass = (type(self) == ConstructionScript)
            if is_not_subclass and \
               self.MAP_PKL is None and \
               None in map_descr_list:
                raise CLIException("ERROR: Either --map-pkl or --mtype, --span, --btype, "
                      "--order must be specified")
            elif is_not_subclass and \
                    self.MAP_PKL is not None and \
                    not all([s is None for s in map_descr_list]):
                raise CLIException("ERROR: Either --map-pkl or --mtype, --span, --btype, "
                      "--order must be specified")
            if self.stg.ADAPT_FV_COEFF_TRUNC_TYPE == 'manual':
                self.stg.ADAPT_FV_COEFF_TRUNC_VAL = None
            elif self.stg.ADAPT_FV_COEFF_TRUNC_TYPE == 'percentage':
                self.stg.ADAPT_FV_COEFF_TRUNC_VAL = float(self.stg.ADAPT_FV_COEFF_TRUNC_VAL)
            elif self.stg.ADAPT_FV_COEFF_TRUNC_TYPE == 'constant':
                self.stg.ADAPT_FV_COEFF_TRUNC_VAL = int(self.stg.ADAPT_FV_COEFF_TRUNC_VAL)
            if self.stg.ADAPT_FV_AVAR_TRUNC_TYPE == 'manual':
                self.stg.ADAPT_FV_AVAR_TRUNC_VAL = None
            elif self.stg.ADAPT_FV_AVAR_TRUNC_TYPE == 'percentage':
                self.stg.ADAPT_FV_AVAR_TRUNC_VAL = float(self.stg.ADAPT_FV_AVAR_TRUNC_VAL)
            elif self.stg.ADAPT_FV_AVAR_TRUNC_TYPE == 'constant':
                self.stg.ADAPT_FV_AVAR_TRUNC_VAL = int(self.stg.ADAPT_FV_AVAR_TRUNC_VAL)
            if self.stg.ADAPT_FV_PRUNE_TRUNC_TYPE == 'manual':
                self.stg.ADAPT_FV_PRUNE_TRUNC_VAL = None
            elif self.stg.ADAPT_FV_PRUNE_TRUNC_TYPE == 'percentage':
                self.stg.ADAPT_FV_PRUNE_TRUNC_VAL = float(self.stg.ADAPT_FV_PRUNE_TRUNC_VAL)
            elif self.stg.ADAPT_FV_PRUNE_TRUNC_TYPE == 'constant':
                self.stg.ADAPT_FV_PRUNE_TRUNC_VAL = int(self.stg.ADAPT_FV_PRUNE_TRUNC_VAL)

    def safe_store(self, tm):
        precond_map = []
        if self.stg.LAPLACE_PULL:
            precond_map.append( self.stg.lapmap )
        if self.stg.MAP_PULL is not None:
            precond_map.append( self.stg.map_pull )

        if len(precond_map) == 0:
            self.stg.tmap = tm
        else:
            self.stg.precond_map = Maps.ListCompositeTransportMap(
                map_list=precond_map )
            self.stg.tmap = Maps.CompositeTransportMap(self.stg.precond_map, tm)

        self.stg.approx_base_distribution = Distributions.PullBackParametricTransportMapDistribution(
            self.stg.tmap, self.stg.target_distribution)
        self.stg.approx_target_distribution = Distributions.PushForwardParametricTransportMapDistribution(
            self.stg.tmap, self.stg.base_distribution)

        super().safe_store( self.stg, self.OUTPUT )
                    
    def load(self):
        # Setting the seed if any
        if self.stg.SEED is not None:
            npr.seed(self.stg.SEED)

        ##################### DATA LOADING #####################
        if self.RELOAD:
            with open(self.OUTPUT, 'rb') as istr:
                self.stg = pickle.load(istr)

            # Set callback in builder
            self.stg.builder.callback = self.safe_store
            self.stg.builder.callback_kwargs = {}

        else:
            # Create an object to store the state of the builder
            self.stg.builder_state = DataStorageObject()
            
            # Load target distribution
            with open(self.INPUT,'rb') as istr:
                self.stg.target_distribution = pickle.load(istr)
            dim = self.stg.target_distribution.dim

            # Load base distribution
            if self.BASE_DIST_FNAME is None:
                self.stg.base_distribution = Distributions.StandardNormalDistribution(dim)
            else:
                with open(self.BASE_DIST_FNAME,'rb') as istr:
                    self.stg.base_distribution = pickle.load(istr)

            if self.MAP_PKL is not None:
                with open(self.MAP_PKL, 'rb') as istr:
                    self.stg.tm = pickle.load( istr )
            elif self.MAP_FACTORY_PKL is not None:
                with open(self.MAP_FACTORY_PKL, 'rb') as istr:
                    self.stg.tm_factory = pickle.load( istr )
            else:
                if self.MONOTONE == 'linspan':
                    if self.SPARSITY == 'tri':
                        map_constructor = \
                            Maps.assemble_IsotropicLinearSpanTriangularTransportMap
                    elif self.SPARSITY == 'diag':
                        map_constructor = \
                            Maps.assemble_IsotropicLinearSpanDiagonalTransportMap
                elif self.MONOTONE == 'intexp':
                    if self.SPARSITY == 'tri':
                        map_constructor = \
                            Maps.assemble_IsotropicIntegratedExponentialTriangularTransportMap
                    elif self.SPARSITY == 'diag':
                        map_constructor = \
                            Maps.assemble_IsotropicIntegratedExponentialDiagonalTransportMap
                elif self.MONOTONE == 'intsq':
                    if self.SPARSITY == 'tri':
                        map_constructor = \
                            Maps.assemble_IsotropicIntegratedSquaredTriangularTransportMap
                    elif self.SPARSITY == 'diag':
                        map_constructor = \
                            Maps.assemble_IsotropicIntegratedSquaredDiagonalTransportMap
                else:
                    raise ValueError("Monotone type not recognized (linspan|intexp|intsq)")
                if self.stg.ADAPT in ['none','fv']:
                    self.stg.tm = map_constructor(dim, self.ORDER, span=self.SPAN, btype=self.BTYPE)
                    logging.info("Number coefficients: %d" % self.stg.tm.n_coeffs)
                elif self.stg.ADAPT in ['sequential', 'tol-sequential']:
                    self.stg.tm_list = [
                        map_constructor(dim, o, span=self.SPAN, btype=self.BTYPE)
                        for o in range(1,self.ORDER+1) ]
                    n_coeffs = sum( tm.n_coeffs for tm in self.stg.tm_list )
                    logging.info("Number coefficients: %d" % n_coeffs )

            # Set up validator
            if self.stg.VALIDATOR == 'none':
                self.stg.validator = None
            else:
                if self.stg.VAL_COST_FUN == 'tot-time':
                    cost_fun = total_time_cost_function
                if self.stg.VALIDATOR == 'saa':
                    self.stg.validator = Diagnostics.SampleAverageApproximationKLMinimizationValidator(
                        self.stg.VAL_EPS,
                        self.stg.VAL_SAA_EPS_ABS,
                        cost_fun,
                        self.stg.VAL_MAX_COST,
                        max_nsamps=self.stg.VAL_MAX_NSAMPS,
                        stop_on_fcast=self.stg.VAL_STOP_ON_FCAST,
                        upper_mult=self.stg.VAL_SAA_UPPER_MULT,
                        lower_n=self.stg.VAL_SAA_LOWER_N,
                        alpha=self.stg.VAL_SAA_ALPHA,
                        lmb_def=self.stg.VAL_SAA_LMB_DEF,
                        lmb_max=self.stg.VAL_SAA_LMB_MAX)
                elif self.stg.VALIDATOR == 'gradboot':
                    self.stg.validator = Diagnostics.GradientBootstrapKLMinimizationValidator(
                        self.stg.VAL_EPS,
                        delta=self.stg.VAL_GRADBOOT_DELTA,
                        cost_function=cost_fun,
                        max_cost=self.stg.VAL_MAX_COST,
                        max_nsamps=self.stg.VAL_MAX_NSAMPS,
                        stop_on_fcast=self.stg.VAL_STOP_ON_FCAST,
                        n_grad_samps=self.stg.VAL_GRADBOOT_N_GRAD,
                        n_bootstrap=self.stg.VAL_GRADBOOT_N_BOOT,
                        alpha=self.stg.VAL_GRADBOOT_ALPHA,
                        lmb_min=self.stg.VAL_GRADBOOT_LMB_MIN,
                        lmb_max=self.stg.VAL_GRADBOOT_LMB_MAX)

            # Set up solve parameters
            if self.stg.ADAPT in ['none', 'fv']:
                self.stg.solve_params = {
                    'qtype': self.stg.QTYPE,
                    'qparams': self.stg.QNUM,
                    'tol': self.stg.TOL,
                    'maxit': self.stg.MAXIT,
                    'regularization': None if self.stg.REG is None else self.stg.REG[0],
                    'ders': self.stg.DERS,
                    'fungrad': self.stg.FUNGRAD,
                    'hessact': self.stg.HESSACT,
                    'batch_size': self.BATCH_SIZE
                }
            elif self.stg.ADAPT in ['sequential', 'tol-sequential']:
                if self.stg.REG is not None and len(self.stg.REG) == 1:
                    self.stg.REG = self.stg.REG * self.ORDER
                self.stg.solve_params_list = []
                for i in range(len(self.stg.tm_list)):
                    self.stg.solve_params_list.append( {
                        'qtype': self.stg.QTYPE, 'qparams': self.stg.QNUM,
                        'tol': self.stg.TOL, 'maxit': self.stg.MAXIT,
                        'regularization': None if self.stg.REG is None else self.stg.REG[i],
                        'ders': self.stg.DERS, 'fungrad': self.stg.FUNGRAD, 'hessact': self.stg.HESSACT,
                        'batch_size': self.BATCH_SIZE
                    } )
                if self.stg.ADAPT == 'tol-sequential':
                    self.stg.var_diag_params = {
                        'qtype': self.MONITOR_QTYPE,
                        'qparams': self.MONITOR_QNUM
                    }

            # Set up adaptivity algorithm
            callback_kwargs = {}  # Define callback (storage) arguments
            if self.stg.ADAPT == 'none':
                self.stg.builder = Builders.KullbackLeiblerBuilder(
                    self.stg.validator,
                    callback=self.safe_store,
                    callback_kwargs=callback_kwargs,
                    verbosity=self.stg.ADAPT_VERB)
            else:
                regression_params = {
                    'regularization': self.stg.ADAPT_REGR_REG,
                    'tol': self.stg.ADAPT_REGR_TOL,
                    'maxit': self.stg.ADAPT_REGR_MAX_IT }
                if self.stg.ADAPT_REGR == 'none':
                    regressor = Builders.L2RegressionBuilder(regression_params)
                elif self.stg.ADAPT_REGR == 'tol-sequential':
                    raise NotImplementedError(
                        "--adapt-regr=tol-sequential not supported by this script")

                if self.stg.ADAPT == 'sequential':
                    self.stg.builder = Adaptivity.SequentialKullbackLeiblerBuilder(
                        validator=self.stg.validator,
                        callback=self.safe_store,
                        callback_kwargs=callback_kwargs,
                        verbosity=self.stg.ADAPT_VERB)
                elif self.stg.ADAPT == 'tol-sequential':
                    self.stg.builder = Adaptivity.ToleranceSequentialKullbackLeiblerBuilder(
                        validator=self.stg.validator,
                        tol=self.stg.ADAPT_TOL,
                        callback=self.safe_store,
                        callback_kwargs=callback_kwargs,
                        verbosity=self.stg.ADAPT_VERB)
                elif self.stg.ADAPT == 'fv':
                    line_search_params = {'maxiter': self.stg.ADAPT_FV_LS_MAXIT,
                                          'delta': self.stg.ADAPT_FV_LS_DELTA}
                    prune_trunc = {'type': self.stg.ADAPT_FV_PRUNE_TRUNC_TYPE,
                                   'val': self.stg.ADAPT_FV_PRUNE_TRUNC_VAL}
                    avar_trunc = {'type': self.stg.ADAPT_FV_AVAR_TRUNC_TYPE,
                                  'val': self.stg.ADAPT_FV_AVAR_TRUNC_VAL}
                    coeff_trunc = {'type': self.stg.ADAPT_FV_COEFF_TRUNC_TYPE,
                                   'val': self.stg.ADAPT_FV_COEFF_TRUNC_VAL}
                    self.stg.builder = Adaptivity.FirstVariationKullbackLeiblerBuilder(
                        validator=self.stg.validator,
                        eps_bull=self.stg.ADAPT_TOL,
                        regression_builder=regressor,
                        line_search_params=line_search_params,
                        max_it=self.stg.ADAPT_FV_MAX_IT,
                        prune_trunc=prune_trunc,
                        avar_trunc=avar_trunc,
                        coeff_trunc=coeff_trunc,
                        interactive=self.stg.ADAPT_FV_INTERACTIVE,
                        callback=self.safe_store,
                        callback_kwargs=callback_kwargs,
                        verbosity=self.stg.ADAPT_VERB)

    def _precondition(self, *args, **kwargs):
        tar = self.stg.target_distribution

        # Map pullback
        self.stg.map_pull = None
        if self.stg.MAP_PULL is not None:
            with open(self.stg.MAP_PULL, 'rb') as istr:
                self.stg.map_pull = pickle.load(istr)
            if not issubclass(type(self.stg.map_pull), Maps.Map):
                self.stg.map_pull = self.stg.map_pull.tmap
            tar = Distributions.PullBackTransportMapDistribution(
                self.stg.map_pull, tar )

        # Laplace pullback
        self.stg.lapmap = None
        if self.stg.LAPLACE_PULL:
            laplace_approx = laplace_approximation( tar )
            self.stg.lapmap = Maps.LinearTransportMap.build_from_Gaussian(laplace_approx)
            tar = Distributions.PullBackTransportMapDistribution(
                self.stg.lapmap, tar )

        return tar

    def _solve(self, mpi_pool=None):
        if not self.RELOAD:
            # Set up builder_solve_kwargs
            if self.stg.ADAPT in ['none', 'fv']:
                self.stg.builder_solve_kwargs = {
                    'transport_map': self.stg.tm,
                    'base_distribution': self.stg.base_distribution,
                    'target_distribution': self.stg.preconditioned_target_distribution,
                    'solve_params': self.stg.solve_params
                }
            elif self.stg.ADAPT in ['sequential', 'tol-sequential']:
                self.stg.builder_solve_kwargs = {
                    'transport_map': self.stg.tm_list,
                    'base_distribution': self.stg.base_distribution,
                    'target_distribution': self.stg.preconditioned_target_distribution,
                    'solve_params': self.stg.solve_params_list
                }
                if self.stg.ADAPT == 'tol-sequential':
                    self.stg.builder_solve_kwargs['var_diag_params'] = self.stg.var_diag_params
            
        return self.stg.builder.solve(
            state=self.stg.builder_state,
            mpi_pool=mpi_pool,
            **self.stg.builder_solve_kwargs
        )
                
    def run(self, *args, **kwargs):

        if not self.RELOAD:
            self.stg.preconditioned_target_distribution = \
                self._precondition()
                
        # Start mpi pool
        mpi_pool = None
        if self.NPROCS > 1:
            mpi_pool = get_mpi_pool()
            mpi_pool.start(self.NPROCS)

        try:

            # Solve
            (tm, log) = self._solve(mpi_pool=mpi_pool)

            # Store
            self.safe_store(tm)
            
        finally:
            if mpi_pool is not None:
                mpi_pool.stop()
            if self.INTERACTIVE:
                from IPython import embed
                embed()
