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

import sys
import logging
import os.path
import pickle

__all__ = ['TMO']

from .Misc import cmdinput


class TMO(object):
    r""" Base object for every object in the module.

    This object provides functions for storage and parallelization.
    """
    def __init__(self):
        self.set_logger()

    def set_logger(self):
        import TransportMaps as TM
        self.logger = logging.getLogger("TM." + self.__class__.__name__)
        self.logger.setLevel(TM.LOG_LEVEL)
        # self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)
        if len(self.logger.handlers) == 0:
            self.logger.propagate = False
            ch = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter("%(asctime)s %(levelname)s: %(name)s: %(message)s",
                                          "%Y-%m-%d %H:%M:%S")
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def __getstate__(self):
        # Avoid pickling un-pickable objects:
        # logger
        odict = self.__dict__.copy()
        odict.pop('logger', None)
        return odict

    def __setstate__(self, idict):
        # Reset removed fields:
        # logger
        self.set_logger()
        self.__dict__.update(idict)

    def store(self, fname, force=False):
        r""" Store the object with the selected file name ``fname``

        Args:
          fname (str): file name
          force (bool): whether to force overwriting
        """
        if os.path.exists(fname) and not force:
            sel = cmdinput(
                "The file %s already exists. " % fname +
                "Do you want to overwrite? [y/N] "
            )
            if sel != 'y' and sel != 'Y':
                print("Not storing")
                return
        with open(fname, 'wb') as out_stream:
            pickle.dump(self, out_stream)

    def get_ncalls_tree(self, indent=""):
        out = ""
        for key, val in getattr(self, 'ncalls', {}).items():
            out += indent + self.__class__.__name__ + " - " + key + ": " + str(val) + "\n"
        return out

    def get_nevals_tree(self, indent=""):
        out = ""
        for key, val in getattr(self, 'nevals', {}).items():
            out += indent + self.__class__.__name__ + " - " + key + ": " + str(val) + "\n"
        return out

    def get_teval_tree(self, indent=""):
        out = ""
        for key, val in getattr(self, 'teval', {}).items():
            out += indent + self.__class__.__name__ + " - " + key + ": %.4f s \n" % val
        return out

    def update_ncalls_tree(self, obj):
        if not hasattr(self, 'ncalls'):
            self.ncalls = {}
        for obj_key, obj_val in getattr(obj, 'ncalls', {}).items():
            try:
                self.ncalls[obj_key] += obj_val
            except KeyError:
                self.ncalls[obj_key] = obj_val

    def update_nevals_tree(self, obj):
        if not hasattr(self, 'teval'):
            self.nevals = {}
        for obj_key, obj_val in getattr(obj, 'nevals', {}).items():
            try:
                self.nevals[obj_key] += obj_val
            except KeyError:
                self.nevals[obj_key] = obj_val

    def update_teval_tree(self, obj):
        if not hasattr(self, 'teval'):
            self.teval = {}
        for obj_key, obj_val in getattr(obj, 'teval', {}).items():
            try:
                self.teval[obj_key] += obj_val
            except KeyError:
                self.teval[obj_key] = obj_val
                
    def reset_counters(self):
        try:
            del self.ncalls
        except AttributeError:
            pass
        try:
            del self.nevals
        except AttributeError:
            pass
        try:
            del self.teval
        except AttributeError:
            pass