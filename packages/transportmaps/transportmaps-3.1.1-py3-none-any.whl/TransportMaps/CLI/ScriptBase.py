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
import getopt
import os
import os.path
import shutil
import time
import datetime
import pickle

from TransportMaps import DataStorageObject
from TransportMaps.ObjectBase import TMO

__all__ = ['Script']


class Script(TMO):

    def tstamp_print(self, msg, *args, **kwargs):
        tstamp = datetime.datetime.fromtimestamp(
            time.time()
        ).strftime('%Y-%m-%d %H:%M:%S')
        print(tstamp + " " + msg, *args, **kwargs)

    def filter_tstamp_print(self, msg, *args, **kwargs):
        if self.VERBOSE:
            self.tstamp_print(msg, *args, **kwargs)

    def filter_print(self, *args, **kwargs):
        if self.VERBOSE:
            print(*args, **kwargs)

    def safe_store(self, data, fname):
        # Backup copy
        file_exists = os.path.exists(fname)
        if file_exists:
            shutil.copyfile(fname, str(fname) + '.bak')
        # Store data
        with open(fname, 'wb') as out_stream:
            pickle.dump(data, out_stream);
        # Remove backup
        if file_exists:
            os.remove(str(fname) + '.bak')

    def _load_opts(self, **kwargs):
        self.VERBOSE = kwargs['verbose']
        self.INTERACTIVE = kwargs['interactive']
        self.INPUT = kwargs['input']
        self.OUTPUT = kwargs['output']
        self.LOGGING_LEVEL = kwargs['log']
        self.NPROCS = kwargs['nprocs']
                
    def __init__(self, **kwargs):
        super(Script, self).__init__()

        self.stg = DataStorageObject()

        self._load_opts(**kwargs)

        self._check_required_args()

    def _check_required_args(self):
        # Check for required arguments
        if None in [self.INPUT, self.OUTPUT]:
            self.usage()
            self.tstamp_print("ERROR: Option --input and --output must be specified")
            sys.exit(3)

    def load(self):
        raise NotImplementedError("To be implemented in sub-classes")

    def run(self, mpi_pool):
        raise NotImplementedError("To be implemented in sub-classes")
