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

from .ConstructionScriptBase import ConstructionScript

import TransportMaps as TM
import TransportMaps.Algorithms.DeepLazyMaps as ALGDEEP

__all__ = ['DeepLazyMapsConstructionScript']

class DeepLazyMapsConstructionScript( ConstructionScript ):

    cmd_usage_str = "Usage: tmap-deep-lazy-tm "
    opts_usage_str = \
        ConstructionScript.opts_usage_str + \
        "  [--lazy-eps=FLOAT --lazy-maxit=INT \n" + \
        "   --lazy-random-rotations --lazy-random-rotations-step=INT \n" + \
        "   --lazy-rank-max=INT --lazy-rank-eps=FLOAT \n" + \
        "   --lazy-rank-qtype=INT --lazy-rank-qnum=INT,.. \n" + \
        "   --lazy-hard-truncation \n" + \
        "   --lazy-ht-qtype=INT --lazy-ht-qnum=INT,.. \n" + \
        "   --lazy-var-diag-qtype=INT --lazy-var-diag-qnum=INT,.. \n" + \
        "   --lazy-plot] \n"

    docs_descr_str = """DESCRIPTION
Given a file (--input) storing the target distribution, produce the transport map that
pushes forward the base distribution (standard normal) to the target distribution,
using the composition (deep) of lazy (low-rank) maps.
All files involved are stored and loaded using the python package pickle."""

    docs_options_str = \
        ConstructionScript.docs_options_str + \
        """
OPTIONS -- deep-lazy construction:
  --lazy-eps=FLOAT        target tolerance 
  --lazy-maxit=INT        maximum number of iterations of the algorithm
  --lazy-random-rotations apply random rotations instead of target informed ones
  --lazy-random-rorations-step=INT number of greedy steps between each random rotation (default: 1)
  --lazy-rank-max=INT     maximum rank allowed for the lazy maps
  --lazy-rank-eps=FLOAT   cumulative power of the ignored sub-space, or
                          'manual' for manual selection at each iteration
  --lazy-rank-qtype=INT   quadrature type for computing the low-rank sub-space
  --lazy-rank-qnum=INT,.. quadrature parameters for computing the low-rank subspace
  --lazy-hard-truncation  whether to use the pi^\star formulation of the algorithm
  --lazy-ht-qtype=INT     quadrature type to use in the evaluation of the conditional expectation
  --lazy-ht-qnum=INT,..   quadrature parameters in the conditional expectation
  --lazy-var-diag-qtype=INT quadrature type to estimate convergence
  --lazy-var-diag-qnum=INT,.. quadrature parameters to estimate convergence
  --lazy-plot             whether to plot progress
"""

    @property
    def long_options(self):
        return super(DeepLazyMapsConstructionScript, self).long_options + \
            [
                'lazy-eps=',
                'lazy-maxit=',
                'lazy-random-rotations',
                'lazy-random-rotations-step=',
                'lazy-rank-max=',
                'lazy-rank-eps=',
                'lazy-rank-qtype=',
                'lazy-rank-qnum=',
                'lazy-hard-truncation',
                'lazy-ht-qtype=',
                'lazy-ht-qnum=',
                'lazy-var-diag-qtype=',
                'lazy-var-diag-qnum=',
                'lazy-plot'
            ]

    def _load_opts(self, opts):
        super(DeepLazyMapsConstructionScript, self)._load_opts( opts )
        
        for opt, arg in opts:
            if opt == '--lazy-eps':
                self.stg.LAZY_EPS = float(arg)
            elif opt == '--lazy-maxit':
                self.stg.LAZY_MAXIT = int(arg)
            elif opt == '--lazy-random-rotations':
                self.stg.LAZY_RANDOM_ROTATIONS = True
            elif opt == '--lazy-random-rotations-step':
                self.stg.LAZY_RANDOM_ROTATIONS_STEP = int(arg)
            elif opt == '--lazy-rank-max':
                self.stg.LAZY_RANK_MAX = int(arg)
            elif opt == '--lazy-rank-eps':
                try:
                    self.stg.LAZY_RANK_EPS = float(arg)
                except ValueError:
                    if arg != 'manual':
                        self.usage()
                        self.tstamp_print(
                            "ERROR: Unrecognized option for --lazy-rank-eps")
                        sys.exit(3)
                    self.stg.LAZY_RANK_EPS = arg
            elif opt == '--lazy-rank-qtype':
                self.stg.LAZY_RANK_QTYPE = int(arg)
            elif opt == '--lazy-rank-qnum':
                self.stg.LAZY_RANK_QNUM = [int(q) for q in arg.split(',')]
            elif opt == '--lazy-hard-truncation':
                self.stg.LAZY_HARD_TRUNCATION = True
            elif opt == '--lazy-ht-qtype':
                self.stg.LAZY_HT_QTYPE = int(arg)
            elif opt == '--lazy-ht-qnum':
                self.stg.LAZY_HT_QNUM = [int(q) for q in arg.split(',')]
            elif opt == '--lazy-var-diag-qtype':
                self.stg.LAZY_VAR_DIAG_QTYPE = int(arg)
            elif opt == '--lazy-var-diag-qnum':
                self.stg.LAZY_VAR_DIAG_QNUM = [int(q) for q in arg.split(',')]
            elif opt == '--lazy-plot':
                self.LAZY_PLOT = True

    def _init_self_variables(self):
        super(DeepLazyMapsConstructionScript, self)._init_self_variables()

        self.stg.LAZY_EPS            = 1e-2
        self.stg.LAZY_MAXIT          = 20
        self.stg.LAZY_RANDOM_ROTATIONS = False
        self.stg.LAZY_RANDOM_ROTATIONS_STEP = 1
        self.stg.LAZY_RANK_MAX       = 3
        self.stg.LAZY_RANK_EPS       = 1e-2
        self.stg.LAZY_RANK_QTYPE     = 0
        self.stg.LAZY_RANK_QNUM      = [20]
        self.stg.LAZY_HARD_TRUNCATION = False
        self.stg.LAZY_HT_QTYPE       = 0
        self.stg.LAZY_HT_QNUM        = [100]
        self.stg.LAZY_VAR_DIAG_QTYPE = 0
        self.stg.LAZY_VAR_DIAG_QNUM  = [100]

        self.LAZY_PLOT = False        

    def _check_required_args(self):
        super(DeepLazyMapsConstructionScript, self)._check_required_args()
        
        if self.stg.LAZY_RANK_QTYPE < 3:
            self.stg.LAZY_RANK_QNUM = self.stg.LAZY_RANK_QNUM[0]
        if self.stg.LAZY_HT_QTYPE < 3:
            self.stg.LAZY_HT_QNUM = self.stg.LAZY_HT_QNUM[0]
        if self.stg.LAZY_VAR_DIAG_QTYPE < 3:
            self.stg.LAZY_VAR_DIAG_QNUM = self.stg.LAZY_VAR_DIAG_QNUM[0]
        
    def load(self):
        super(DeepLazyMapsConstructionScript, self).load()

        if not self.stg.LAZY_HARD_TRUNCATION:
            if not issubclass(type(self.stg.tm_factory), ALGDEEP.DeepLazyMapFactory):
                raise ValueError(
                    "The provided map factory must be a subclass of DeepLazyMapFactory"
                )

        if self.RELOAD:
            self.stg.assembler.callback = self.safe_store
            self.stg.assembler.callback_kwargs = {}
        else:
            self.stg.assembler_state = TM.DataStorageObject()
        
            # Build the assembler
            self.stg.assembler = ALGDEEP.DeepLazyMapsAssembler(
                builder               = self.stg.builder,
                map_factory           = self.stg.tm_factory,
                eps                   = self.stg.LAZY_EPS,
                maxit                 = self.stg.LAZY_MAXIT,
                random_rotations      = self.stg.LAZY_RANDOM_ROTATIONS,
                random_rotations_step = self.stg.LAZY_RANDOM_ROTATIONS_STEP,
                rank_max              = self.stg.LAZY_RANK_MAX,
                rank_eps              = self.stg.LAZY_RANK_EPS,
                rank_qtype            = self.stg.LAZY_RANK_QTYPE,
                rank_qparams          = self.stg.LAZY_RANK_QNUM,
                hard_truncation       = self.stg.LAZY_HARD_TRUNCATION,
                ht_qtype              = self.stg.LAZY_HT_QTYPE,
                ht_qparams            = self.stg.LAZY_HT_QNUM,
                var_diag_qtype        = self.stg.LAZY_VAR_DIAG_QTYPE,
                var_diag_qparams      = self.stg.LAZY_VAR_DIAG_QNUM,
                callback              = self.safe_store,
                callback_kwargs       = {}
            )

    def _solve(self, mpi_pool=None):
        if not self.RELOAD:
            # Assemble function kwargs
            self.stg.assembler_assemble_kwargs = {
                'target_distribution': self.stg.preconditioned_target_distribution,
                'builder_solve_params': self.stg.solve_params
            }
                
        return self.stg.assembler.assemble(
            state    = self.stg.assembler_state,
            mpi_pool = mpi_pool,
            plotting = self.LAZY_PLOT,
            **self.stg.assembler_assemble_kwargs
        )
