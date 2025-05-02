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
import time
from functools import wraps
import numpy as np

__all__ = [
    'cmdinput', 'read_and_cast_input',
    'LOG_LEVEL', 'logger', 'deprecate', 'setLogLevel', 'counted',
    'required_kwargs',
    'generate_total_order_midxs',
    'no_cost_function', 'total_time_cost_function',
    'cached', 'cached_tuple', 'get_sub_cache',
    'taylor_test',
    'argsort',
    'DataStorageObject',
    'state_loader',
]

def process_time():
    if sys.version_info >= (3, 3):
        return time.process_time()
    else:
        return time.time()


def cmdinput(instr, default=''):
    out = input(instr)
    if out == '':
        out = default
    return out

def read_and_cast_input(field_name, cast_type, current_value=None):
    success_input = False
    query_str = "Provide a value for the " + field_name
    if current_value is not None:
        query_str += " [current: " + str(current_value) + "]"
    query_str += " or (q)uit: "
    while not success_input:
        instr = cmdinput(query_str)
        if instr == 'q':
            return None, success_input
        try:
            val = cast_type(instr)
        except ValueError:
            print("The value could not be casted to a " + str(cast_type))
        else:
            success_input = True
    return val, success_input
        
####### LOGGING #########
LOG_LEVEL = logging.getLogger().getEffectiveLevel()

logger = logging.getLogger('TransportMaps')
logger.propagate = False
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(name)s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")
ch.setFormatter(formatter)
logger.addHandler(ch)

def deprecate(name, version, msg):
    def deprecate_decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            logger.warning("%s DEPRECATED since v%s. %s" % (name, version, msg))
            return f(*args, **kwargs)
        return wrapped
    return deprecate_decorator

def setLogLevel(level):
    r""" Set the log level for all existing and new objects related to the TransportMaps module

    Args:
      level (int): logging level

    .. see:: the :module:`logging` module.
    """
    import TransportMaps as TM
    TM.LOG_LEVEL = level
    for lname, logger in logging.Logger.manager.loggerDict.items():
        if "TM." in lname or "TransportMaps" in lname:
            logger.setLevel(level)

def counted(f): # Decorator used to count function calls
    @wraps(f)
    def wrapped(slf, *args, **kwargs):
        try:
            x = args[0]
        except IndexError:
            x = kwargs['x']
        try:
            slf.ncalls[f.__name__] += 1
            slf.nevals[f.__name__] += x.shape[0]
        except AttributeError:
            slf.ncalls = {}
            slf.nevals = {}
            slf.ncalls[f.__name__] = 1
            slf.nevals[f.__name__] = x.shape[0]
        except KeyError:
            slf.ncalls[f.__name__] = 1
            slf.nevals[f.__name__] = x.shape[0]
        start = process_time()
        out = f(slf, *args, **kwargs)
        stop = process_time()
        try:
            slf.teval[f.__name__] += (stop-start)
        except AttributeError:
            slf.teval = {}
            slf.teval[f.__name__] = (stop-start)
        except KeyError:
            slf.teval[f.__name__] = (stop-start)
        return out
    return wrapped

def required_kwargs(*keys):
    def the_decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            for key in keys:
                if key not in kwargs:
                    raise ValueError(
                        "The required argument " + key + \
                        " is missing."
                    )
            return f(*args, **kwargs)
        return wrapped
    return the_decorator

#
# Total order multi index generation
#
def generate_total_order_midxs(max_order_list):
    r""" Generate a total order multi-index

    Given the list of maximums :math:`{\bf m}`, the returned set of
    multi-index :math:`I` is such that :math:`\sum_j^d {\bf_i}_j <= max {\bf m}`
    and :math:`{\bf i}_j <= {\bf m}_j`.
    """
    # Improve performances by writing it in cython.
    dim = len(max_order_list)
    max_order = max(max_order_list)
    # Zeros multi-index
    midxs_set = set()
    midx_new = tuple([0]*dim)
    if sum(midx_new) < max_order:
        midxs_old_set = set([ midx_new ]) # Containing increasable multi-indices
    else:
        midxs_old_set = set()
    midxs_set.add(midx_new)
    # Higher order multi-indices
    for i in range(1,max_order+1):
        midxs_new_set = set()
        for midx_old in midxs_old_set:
            for d in range(dim):
                if midx_old[d] < max_order_list[d]:
                    midx_new = list(midx_old)
                    midx_new[d] += 1
                    midxs_set.add( tuple(midx_new) )
                    if sum(midx_new) < max_order:
                        midxs_new_set.add( tuple(midx_new) )
        midxs_old_set = midxs_new_set
    # Transform to list of tuples
    midxs_list = list(midxs_set)
    return midxs_list

#
# Cost functions
#
def no_cost_function(*args, **kwargs):
    return 0.
    
def total_time_cost_function(
        ncalls, nevals, teval, ncalls_x_solve=None, new_nx=None):
    # Compute elapsed cost as total time
    t = teval.get('log_pdf',0)
    t += teval.get('grad_a_log_pdf',0)
    t += teval.get('tuple_grad_a_log_pdf',0)
    t += teval.get('hess_a_log_pdf',0)
    t += teval.get('action_hess_a_log_pdf',0)
    if new_nx is not None:
        # Compute forecasted time accordingly
        t += ncalls_x_solve.get('log_pdf',0) * new_nx * \
             teval.get('log_pdf',0) / nevals.get('log_pdf',1)
        t += ncalls_x_solve.get('grad_a_log_pdf',0) * new_nx * \
             teval.get('grad_a_log_pdf',0) / nevals.get('grad_a_log_pdf',1)
        t += ncalls_x_solve.get('tuple_grad_a_log_pdf',0) * new_nx * \
             teval.get('tuple_grad_a_log_pdf',0) / nevals.get('tuple_grad_a_log_pdf',1)
        t += ncalls_x_solve.get('hess_a_log_pdf',0) * new_nx * \
             teval.get('hess_a_log_pdf',0) / nevals.get('hess_a_log_pdf',1)
        t += ncalls_x_solve.get('action_hess_a_log_pdf',0) * new_nx * \
             teval.get('action_hess_a_log_pdf',0) / nevals.get('action_hess_a_log_pdf',1)
    return t
    
#
# Caching capabilities (decorator)
#
class cached(object):
    def __init__(self, sub_cache_list=[], caching=True):
        self.sub_cache_list = sub_cache_list
        self.caching = caching
    def __call__(self, f):
        @wraps(f)
        def wrapped(slf, *args, **kwargs):
            try:
                x = args[0]
            except IndexError:
                x = kwargs['x']
            idxs_slice = kwargs.get('idxs_slice', slice(None))
            cache = kwargs.get('cache', None)
            # Decide whether to cache output
            caching = (cache is not None) and self.caching
            # Retrieve from cache
            if caching:
                try:
                    (batch_set, vals) = cache[f.__name__]
                except KeyError as e:
                    new_cache = True
                else:
                    new_cache = False
                    if batch_set[idxs_slice][0]: # Checking only the first
                        return vals[idxs_slice]
            if cache is not None:
                # Init sub-cache if necessary
                for sub_name, sub_len in self.sub_cache_list:
                    try:
                        cache[sub_name + '_cache']
                    except KeyError:
                        if sub_len is None:
                            cache[sub_name + '_cache'] = {'tot_size': cache['tot_size']}
                        elif isinstance(sub_len, int):
                            cache[sub_name + '_cache'] = [
                                {'tot_size': cache['tot_size']}
                                for i in range(sub_len)]
                        elif isinstance(sub_len, str):
                            ll = getattr(slf, sub_len)
                            cache[sub_name + '_cache'] = [
                                {'tot_size': cache['tot_size']}
                                for i in range(ll)]
                        else:
                            raise TypeError("Type of sub_len not recognized")
            # Evaluate function
            out = f(slf, *args, **kwargs)
            # Store in cache
            if caching:
                if new_cache:
                    tot_size = cache['tot_size']
                    cache[f.__name__] = (
                        np.zeros(tot_size, dtype=bool),
                        np.empty((tot_size,)+out.shape[1:], dtype=np.float64))
                    (batch_set, vals) = cache[f.__name__]
                vals[idxs_slice] = out
                batch_set[idxs_slice] = True
            return out
        return wrapped

class cached_tuple(object):
    def __init__(self, commands=[], sub_cache_list=[], caching=True):
        if len(commands) == 0:
            raise AttributeError("You must provide at least one command, " + \
                                 "corresponding to the output on the tuple.")
        self.commands = commands
        self.sub_cache_list = sub_cache_list
        self.caching = caching
    def __call__(self, f):
        @wraps(f)
        def wrapped(slf, *args, **kwargs):
            try:
                x = args[0]
            except IndexError:
                x = kwargs['x']
            idxs_slice = kwargs.get('idxs_slice', slice(None))
            cache = kwargs.get('cache', None)
            # Decide whether to cache output
            caching = (cache is not None) and self.caching
            # Retrieve from cache
            if caching:
                out = [None for i in range(len(self.commands))]
                new_cache = [None for i in range(len(self.commands))]
                out_flag = True
                for i, cmd in enumerate(self.commands):
                    try:
                        (batch_set, vals) = cache[cmd]
                    except KeyError as e:
                        new_cache[i] = True
                        out_flag = False
                    else:
                        new_cache[i] = False
                        if batch_set[idxs_slice][0]: # Checking only the first
                            out[i] = vals[idxs_slice]
                        else:
                            out_flag = False
                if out_flag:
                    return tuple(out)
                else:
                    del out
            if cache is not None:
                # Init sub-cache if necessary
                for sub_name, sub_len in self.sub_cache_list:
                    try:
                        cache[sub_name + '_cache']
                    except KeyError:
                        if sub_len is None:
                            cache[sub_name + '_cache'] = {'tot_size': cache['tot_size']}
                        elif isinstance(sub_len, int):
                            cache[sub_name + '_cache'] = [
                                {'tot_size': cache['tot_size']}
                                for i in range(sub_len)]
                        elif isinstance(sub_len, str):
                            ll = getattr(slf, sub_len)
                            cache[sub_name + '_cache'] = [
                                {'tot_size': cache['tot_size']}
                                for i in range(ll)]
                        else:
                            raise TypeError("Type of sub_len not recognized")
            # Evaluate function
            feval_tuple = f(slf, *args, **kwargs)
            # Store in cache
            if caching:
                for i, (feval, cmd) in enumerate(zip(feval_tuple, self.commands)):
                    if new_cache[i]:
                        tot_size = cache['tot_size']
                        cache[cmd] = (
                            np.zeros(tot_size, dtype=bool),
                            np.empty((tot_size,)+feval.shape[1:], dtype=np.float64))
                    (batch_set, vals) = cache[cmd]
                    vals[idxs_slice] = feval
                    batch_set[idxs_slice] = True
            return feval_tuple
        return wrapped
        
def get_sub_cache(cache, *args):
    out = []
    for arg, dflt in args:
        try:
            out.append( cache[arg + "_cache"] )
        except TypeError:
            out.append( None if dflt is None else [None]*dflt )
    if len(out) > 1:
        return out
    else:
        return out[0]

#
# Taylor test for gradient and Hessian implementations
#
def taylor_test(x, dx, f, gf=None, hf=None, ahf=None, h=1e-4,
                fungrad=False, caching=False,
                args={}):
    r""" Test the gradient and Hessian of a function using the Taylor test.

    Using a Taylor expansion around :math:`{\bf x}`, we have

    .. math::

       f({\bf x}+h \delta{\bf x}) = f({\bf x})
           + h (\nabla f({\bf x}))^\top \delta{\bf x} 
           + \frac{h^2}{2} (\delta{\bf x})^\top \nabla^2 f({\bf x}) \delta{\bf x}
           + \mathcal{O}(h^3)

    Therefore
    
    .. math::

       \vert f({\bf x}+h \delta{\bf x}) - f({\bf x})
       - h (\nabla f({\bf x}))^\top \delta{\bf x} \vert = \mathcal{O}(h^2)

    and
    
    .. math::

       \vert f({\bf x}+h \delta{\bf x}) - f({\bf x})
       - h (\nabla f({\bf x}))^\top \delta{\bf x}
       - \frac{h^2}{2} (\delta{\bf x})^\top \nabla^2 f({\bf x}) \delta{\bf x} \vert
       = \mathcal{O}(h^3)

    Args:
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points :math:`{\bf x}`
      dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): perturbation direction
        :math:`\delta{\bf x}`
      f (function): function :math:`{\bf x} \mapsto f({\bf x})`. If ``fungrad==True``, then
        ``f`` is the mapping :math:`{\bf x} \mapsto (\nabla f({\bf x}), f({\bf x}))`.
      gf (function): gradient function :math:`{\bf x} \mapsto \nabla f({\bf x})`
      hf (function): Hessian function :math:`{\bf x} \mapsto \nabla^2 f({\bf x})`
      ahf (function): action of the Hessian function
        :math:`{\bf x},\delta{\bf x} \mapsto (\nabla f({\bf x}))^\top \delta{\bf x}`
      h (float): perturbation step
      fungrad (bool): whether ``f`` returns also the gradient or not.
      caching (bool): whether to pass a cache dictionary to the functions.
      args (dict): arguments to be passed to functions
    """
    if caching:
        args['cache'] = {'tot_size': x.shape[0]}
    # Compute at x
    if fungrad:
        fx, gfx = f(x, **args)
    else:
        fx = f(x, **args)
        gfx = gf(x, **args)
    if hf is not None:
        hfx = hf(x, **args)
        ahfx = np.einsum('...ij,...j->...i', hfx, dx)
    elif ahf is not None:
        ahfx = ahf(x, dx, **args)
    # Compute at x + h * dx
    if caching:
        args['cache'] = {'tot_size': x.shape[0]}
    if fungrad:
        fxhdx, _ = f(x + h * dx, **args)
    else:
        fxhdx = f(x + h * dx, **args)
    err_gx1 = np.abs( fxhdx - fx - h * np.einsum('...j,...j->...', gfx, dx) )
    if hf is not None or ahf is not None:
        err_hx1 = np.abs(
            fxhdx - fx - h * np.einsum('...j,...j->...', gfx, dx) - \
            h**2/2 * np.einsum('...i,...i->...', ahfx, dx) )
    # Halve the step
    h /= 2
    if caching:
        args['cache'] = {'tot_size': x.shape[0]}
    if fungrad:
        fxhdx, _ = f(x + h * dx, **args)
    else:
        fxhdx = f(x + h * dx, **args)
    err_gx2 = np.abs( fxhdx - fx - h * np.einsum('...j,...j->...', gfx, dx) )
    if hf is not None or ahf is not None:
        err_hx2 = np.abs(
            fxhdx - fx - h * np.einsum('...j,...j->...', gfx, dx) - \
            h**2/2 * np.einsum('...i,...i->...', ahfx, dx) )
    mrateg = np.min( np.log2(err_gx1/err_gx2) )
    print("Worst convergence rate gradient (should be 2): %.2f" % mrateg)
    if hf is not None or ahf is not None:
        mrateh = np.min( np.log2(err_hx1/err_hx2) )
        print("Worst convergence rate Hessian  (should be 3): %.2f" % mrateh)

def argsort(seq):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__)

class DataStorageObject(object):
    pass

class state_loader(object):
    r""" Loader of state provided to functions
    """
    def __init__(
            self,
            keys=None ):
        self.keys = [] if keys is None else keys
    def __call__(self, f):
        @wraps(f)
        def wrapped(slf, *args, **kwargs):
            if kwargs.get('state') is None:
                kwargs['state'] = DataStorageObject()
            else:
                if not ( all( hasattr(kwargs['state'], key) for key in self.keys ) or \
                         all( not hasattr(kwargs['state'], key) for key in self.keys ) ):
                    raise ValueError("A partial state was provied.")
            # Set up function argument keys
            for pos, key in enumerate(self.keys):
                setattr(
                    kwargs['state'],
                    key,
                    getattr(
                        kwargs['state'],
                        key,
                        kwargs.get(
                            key,
                            args[pos] if pos < len(args) else None
                        )
                    )
                )
            return f(slf, *args, **kwargs)
        return wrapped
