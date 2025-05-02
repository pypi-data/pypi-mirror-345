import pickle
import numpy as np

from .Misc import deprecate
from .External import MPI_SUPPORT
from .ObjectBase import TMO

__all__ = [
    'get_mpi_pool', 'MPIPoolContext', 'mpi_eval',
    'mpi_map', 'mpi_map_alloc_dmem',
    'mpi_alloc_dmem', 'mpi_bcast_dmem', 'mpi_scatter_dmem',
    'SumChunkReduce', 'TupleSumChunkReduce',
    'TensorDotReduce', 'ExpectationReduce',
    'AbsExpectationReduce', 'TupleExpectationReduce',
    'distributed_sampling',
]


def get_mpi_pool():
    r""" Get a pool of ``n`` processors

    Returns:
      (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`) -- pool of processors

    Usage example::

        import numpy as np
        import numpy.random as npr
        from TransportMaps import get_mpi_pool, mpi_map

        class Operator(object):
            def __init__(self, a):
                self.a = a
            def sum(self, x, n=1):
                out = x
                for i in range(n):
                    out += self.a
                return out

        op = Operator(2.)
        x = npr.randn(100,5)
        n = 2

        pool = get_mpi_pool()
        pool.start(3)
        try:
            xsum = mpi_map("sum", op, x, (n,), mpi_pool=pool)
        finally:
            pool.stop()
    """
    if MPI_SUPPORT:
        import mpi_map as mpi_map_mod
        return mpi_map_mod.MPI_Pool_v2()
    else:
        raise RuntimeError("MPI is not supported")


class MPIPoolContext(object):
    def __init__(self, nprocs):
        if nprocs > 1:
            self.mpi_pool = get_mpi_pool()
            self.mpi_pool.start(nprocs)
        else:
            self.mpi_pool = None

    def __enter__(self):
        return self.mpi_pool

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.mpi_pool is not None:
            self.mpi_pool.stop()


@deprecate('mpi_eval', 'v2.0', 'mpi_map')
def mpi_eval(f, scatter_tuple=None, bcast_tuple=None,
             dmem_key_in_list=None, dmem_arg_in_list=None, dmem_val_in_list=None,
             dmem_key_out_list=None,
             obj=None, reduce_obj=None, reduce_tuple=None, import_set=None,
             mpi_pool=None, splitted=False, concatenate=True):
    r""" Interface for the parallel evaluation of a generic function on points ``x``

    Args:
      f (:class:`object` or :class:`str`): function or string identifying the
        function in object ``obj``
      scatter_tuple (tuple): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be scattered to the processes.
      bcast_tuple (tuple): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be broadcasted to the processes.
      dmem_key_in_list (list): list of string containing the keys
        to be fetched (or created with default ``None`` if missing) from the
        distributed memory and provided as input to ``f``.
      dmem_val_in_list (list): list of objects corresponding to the keys defined
        in ``dmem_key_in_list``, used in case we are not executing in parallel
      dmem_key_out_list (list): list of keys to be assigned to the outputs
        beside the first one
      obj (object): object where the function ``f_name`` is defined
      reduce_obj (object): object :class:`ReduceObject` defining the reduce
        method to be applied (if any)
      reduce_tuple (object): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be scattered to the processes to be used by ``reduce_obj``
      import_set (set): list of couples ``(module_name,as_field)`` to be imported
        as ``import module_name as as_field``
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processors
      splitted (bool): whether the scattering input is already splitted or not
      concatenate (bool): whether to concatenate the output (the output of ``f``
        must be a :class:`numpy.ndarray<numpy.ndarray>` object
    """
    if dmem_key_out_list is None:
        return mpi_map(f=f, scatter_tuple=scatter_tuple, bcast_tuple=bcast_tuple,
                       dmem_key_in_list=dmem_key_in_list,
                       dmem_arg_in_list=dmem_arg_in_list,
                       dmem_val_in_list=dmem_val_in_list,
                       obj=obj, reduce_obj=reduce_obj, reduce_tuple=reduce_tuple,
                       import_set=import_set, mpi_pool=mpi_pool,
                       splitted=splitted, concatenate=concatenate)
    else:
        out = mpi_map_alloc_dmem(
            f=f, scatter_tuple=scatter_tuple, bcast_tuple=bcast_tuple,
            dmem_key_in_list=dmem_key_in_list,
            dmem_arg_in_list=dmem_arg_in_list,
            dmem_val_in_list=dmem_val_in_list,
            dmem_key_out_list=dmem_key_out_list,
            obj=obj, reduce_obj=reduce_obj, reduce_tuple=reduce_tuple,
            import_set=import_set, mpi_pool=mpi_pool,
            splitted=splitted, concatenate=concatenate)
        return (None,) + out


def mpi_map(f, scatter_tuple=None, bcast_tuple=None,
            dmem_key_in_list=None, dmem_arg_in_list=None, dmem_val_in_list=None,
            obj=None, obj_val=None,
            reduce_obj=None, reduce_tuple=None,
            mpi_pool=None, splitted=False, concatenate=True):
    r""" Interface for the parallel evaluation of a generic function on points ``x``

    Args:
      f (:class:`object` or :class:`str`): function or string identifying the
        function in object ``obj``
      scatter_tuple (tuple): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be scattered to the processes.
      bcast_tuple (tuple): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be broadcasted to the processes.
      dmem_key_in_list (list): list of string containing the keys
        to be fetched (or created with default ``None`` if missing) from the
        distributed memory and provided as input to ``f``.
      dmem_val_in_list (list): list of objects corresponding to the keys defined
        in ``dmem_key_in_list``, used in case we are not executing in parallel
      obj (object or str): object where the function ``f_name`` is defined
      obj_val (object): object to be used in case not executing in parallel and
        ``obj`` is a string
      reduce_obj (object): object :class:`ReduceObject` defining the reduce
        method to be applied (if any)
      reduce_tuple (object): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be scattered to the processes to be used by ``reduce_obj``
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processors
      splitted (bool): whether the scattering input is already splitted or not
      concatenate (bool): whether to concatenate the output (the output of ``f``
        must be a :class:`numpy.ndarray<numpy.ndarray>` object
    """
    # Init un-set arguments
    if scatter_tuple is None:
        scatter_tuple = ([], [])
    if bcast_tuple is None:
        bcast_tuple = ([], [])
    if dmem_key_in_list is None:
        dmem_key_in_list = []
    if dmem_arg_in_list is None:
        dmem_arg_in_list = []
    if dmem_val_in_list is None:
        dmem_val_in_list = []
    if reduce_tuple is None:
        reduce_tuple = ([], [])

    # Start evaluation
    if mpi_pool is None:
        # Prepare arguments
        args = {}
        for key, val in zip(scatter_tuple[0], scatter_tuple[1]):
            if splitted:
                if len(val) != 1:
                    raise ValueError("Serial execution but splitted input is %d long" % len(val))
                args[key] = val[0]
            else:
                args[key] = val
        for key, val in zip(bcast_tuple[0], bcast_tuple[1]):
            args[key] = val
        for key, val in zip(dmem_arg_in_list, dmem_val_in_list):
            args[key] = val
        reduce_args = {}
        for key, val in zip(reduce_tuple[0], reduce_tuple[1]):
            if splitted:
                if len(val) != 1:
                    raise ValueError("Serial execution but splitted input is %d long" % len(val))
                reduce_args[key] = val[0]
            else:
                reduce_args[key] = val
        # Retrieve function
        if obj is not None:
            if isinstance(obj, str):
                f = getattr(obj_val, f)
            else:
                f = getattr(obj, f)
        # Evaluate
        fval = f(**args)
        # Reduce if necessary
        if reduce_obj is not None:
            fval = reduce_obj.outer_reduce(
                [reduce_obj.inner_reduce(fval, **reduce_args)], **reduce_args)
    else:
        # If object is not None and is not a string, first broadcast the object
        obj_in = obj
        if obj is not None and not isinstance(obj, str):
            obj_distr = pickle.loads(pickle.dumps(obj_in))
            if issubclass(type(obj), TMO):
                obj_distr.reset_counters()
            mpi_bcast_dmem(obj=obj_distr, mpi_pool=mpi_pool, reserved=True)
            obj_in = 'obj'

        # Prepare arguments
        obj_scatter = mpi_pool.split_data(scatter_tuple[1], scatter_tuple[0],
                                          splitted=splitted)
        obj_bcast = {}
        for key, val in zip(bcast_tuple[0], bcast_tuple[1]):
            obj_bcast[key] = val
        obj_args_reduce = mpi_pool.split_data(reduce_tuple[1], reduce_tuple[0],
                                              splitted=splitted)

        # Evaluate
        fval = mpi_pool.map(f,
                            obj_scatter=obj_scatter, obj_bcast=obj_bcast,
                            dmem_key_in_list=dmem_key_in_list,
                            dmem_arg_in_list=dmem_arg_in_list,
                            obj=obj_in,
                            reduce_obj=reduce_obj, reduce_args=obj_args_reduce)

        # Put pieces together
        if reduce_obj is None and concatenate:
            if isinstance(fval[0], tuple):
                out = []
                for i in range(len(fval[0])):
                    out.append(np.concatenate([fv[i] for fv in fval]))
                fval = tuple(out)
            else:
                fval = np.concatenate(fval, axis=0)

        # If the input object was not a string, clear it from memory
        if obj is not None and not isinstance(obj, str):
            obj_child_lst = mpi_pool.pop_dmem(obj_in)
            if issubclass(type(obj), TMO):
                # Update counters
                obj.update_ncalls_tree(obj_child_lst[0][0])
                for (obj_child,) in obj_child_lst:
                    obj.update_nevals_tree(obj_child)
                    obj.update_teval_tree(obj_child)

    return fval


def mpi_map_alloc_dmem(f, scatter_tuple=None, bcast_tuple=None,
                       dmem_key_in_list=None, dmem_arg_in_list=None, dmem_val_in_list=None,
                       dmem_key_out_list=None,
                       obj=None, obj_val=None,
                       reduce_obj=None, reduce_tuple=None,
                       mpi_pool=None, splitted=False, concatenate=True):
    r""" Interface for the parallel evaluation of a generic function on points ``x``

    Args:
      f (:class:`object` or :class:`str`): function or string identifying the
        function in object ``obj``
      scatter_tuple (tuple): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be scattered to the processes.
      bcast_tuple (tuple): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be broadcasted to the processes.
      dmem_key_in_list (list): list of string containing the keys
        to be fetched (or created with default ``None`` if missing) from the
        distributed memory and provided as input to ``f``.
      dmem_val_in_list (list): list of objects corresponding to the keys defined
        in ``dmem_key_in_list``, used in case we are not executing in parallel
      dmem_key_out_list (list): list of keys to be assigned to the outputs
        beside the first one
      obj (object): object where the function ``f_name`` is defined
      obj_val (object): object to be used in case not executing in parallel and
        ``obj`` is a string
      reduce_obj (object): object :class:`ReduceObject` defining the reduce
        method to be applied (if any)
      reduce_tuple (object): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be scattered to the processes to be used by ``reduce_obj``
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processors
      splitted (bool): whether the scattering input is already splitted or not
      concatenate (bool): whether to concatenate the output (the output of ``f``
        must be a :class:`numpy.ndarray<numpy.ndarray>` object
    """
    # Init un-set arguments
    if scatter_tuple is None:
        scatter_tuple = ([], [])
    if bcast_tuple is None:
        bcast_tuple = ([], [])
    if dmem_key_in_list is None:
        dmem_key_in_list = []
    if dmem_arg_in_list is None:
        dmem_arg_in_list = []
    if dmem_val_in_list is None:
        dmem_val_in_list = []
    if dmem_key_out_list is None:
        dmem_key_out_list = []
    if reduce_tuple is None:
        reduce_tuple = ([], [])

    # Start evaluation
    if mpi_pool is None:
        # Prepare arguments
        args = {}
        for key, val in zip(scatter_tuple[0], scatter_tuple[1]):
            if splitted:
                if len(val) != 1:
                    raise ValueError("Serial execution but splitted input is %d long" % len(val))
                args[key] = val[0]
            else:
                args[key] = val
        for key, val in zip(bcast_tuple[0], bcast_tuple[1]):
            args[key] = val
        for key, val in zip(dmem_arg_in_list, dmem_val_in_list):
            args[key] = val
        reduce_args = {}
        for key, val in zip(reduce_tuple[0], reduce_tuple[1]):
            if splitted:
                if len(val) != 1:
                    raise ValueError("Serial execution but splitted input is %d long" % len(val))
                reduce_args[key] = val[0]
            else:
                reduce_args[key] = val
        # Retrieve function
        if obj is not None:
            if isinstance(obj, str):
                f = getattr(obj_val, f)
            else:
                f = getattr(obj, f)
        # Evaluate
        pars = f(**args)
        if not isinstance(pars, tuple):
            pars = (pars,)
    else:
        # Prepare arguments
        obj_scatter = mpi_pool.split_data(scatter_tuple[1], scatter_tuple[0],
                                          splitted=splitted)
        obj_bcast = {}
        for key, val in zip(bcast_tuple[0], bcast_tuple[1]):
            obj_bcast[key] = val
        obj_args_reduce = mpi_pool.split_data(reduce_tuple[1], reduce_tuple[0],
                                              splitted=splitted)
        # Evaluate
        pars = tuple([None] * len(dmem_key_out_list))
        mpi_pool.map_alloc_dmem(
            f, obj_scatter=obj_scatter, obj_bcast=obj_bcast,
            dmem_key_in_list=dmem_key_in_list,
            dmem_arg_in_list=dmem_arg_in_list,
            dmem_key_out_list=dmem_key_out_list,
            obj=obj,
            reduce_obj=reduce_obj, reduce_args=obj_args_reduce)
    return pars


@deprecate("mpi_alloc_dmem", ">2.0b2", "Use mpi_bcast_dmem instead.")
def mpi_alloc_dmem(mpi_pool=None, **kwargs):
    mpi_bcast_dmem(mpi_pool=mpi_pool, **kwargs)


def mpi_bcast_dmem(mpi_pool=None, reserved=False, **kwargs):
    r""" List of keyworded arguments to be allocated in the distributed memory.

    This executes only if an mpi_pool is provided.

    Args:
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processors
      reserved (bool): whether the ``kwargs`` dictionary can contain the
        reserved key ``obj``
    """
    if mpi_pool is not None:
        if not reserved and 'obj' in kwargs:
            raise ValueError(
                "The key obj is reserved for default argument passing. " + \
                "If you want to use it, pass reserved=True."
            )
        mpi_pool.bcast_dmem(**kwargs)


def mpi_scatter_dmem(mpi_pool=None, **kwargs):
    r""" List of keyworded arguments to be scattered in the distributed memory.

    This executes only if an mpi_pool is provided.

    Args:
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processors
    """
    if mpi_pool is not None:
        mpi_pool.scatter_dmem(**kwargs)


#
# MPI REDUCE OPERATIONS
#
class SumChunkReduce(object):
    r""" Define the summation of the chunks operation.

    The chunks resulting from the output of the MPI evaluation are summed along
    their ``axis``.

    Args:
      axis (tuple [2]): tuple containing list of axes to be used in the
        :func:`sum<numpy.sum>` operation
    """

    def __init__(self, axis=None):
        self.axis = axis

    def inner_reduce(self, x, *args, **kwargs):
        return x

    def outer_reduce(self, x, *args, **kwargs):
        return np.sum(x, axis=self.axis)


class TupleSumChunkReduce(SumChunkReduce):
    r""" Define the summation of the chunks operation over list of tuples.

    The chunks resulting from the output of the MPI evaluation are summed along
    their ``axis``.

    Args:
      axis (tuple [2]): tuple containing list of axes to be used in the
        :func:`sum<numpy.sum>` operation
    """

    def outer_reduce(self, x, *args, **kwargs):
        out = []
        for i in range(len(x[0])):
            xin = [xx[i] for xx in x]
            out.append(super(TupleSumChunkReduce, self).outer_reduce(xin, *args, **kwargs))
        return tuple(out)


class TensorDotReduce(object):
    r""" Define the reduce tensordot operation carried out through the mpi_map function

    Args:
      axis (tuple [2]): tuple containing list of axes to be used in the
        :func:`tensordot<numpy.tensordot>` operation
    """

    def __init__(self, axis):
        self.axis = axis

    def inner_reduce(self, x, w):
        if x.shape[self.axis[0]] > 0:
            return np.tensordot(x, w, self.axis)
        else:
            return 0.

    def outer_reduce(self, x, w):
        return sum(x)


class ExpectationReduce(TensorDotReduce):
    r""" Define the expectation operation carried out through the mpi_map function
    """

    def __init__(self):
        super(ExpectationReduce, self).__init__((0, 0))


class AbsExpectationReduce(ExpectationReduce):
    r""" Define the expectation of the absolute value: :math:`\mathbb{E}[\vert {\bf X} \vert]`
    """

    def inner_reduce(self, x, w):
        return super(AbsExpectationReduce, self).inner_reduce(np.abs(x), w)


class TupleExpectationReduce(ExpectationReduce):
    r""" Define the expectation operation applied on a tuple

    If we are given a tuple :math:`(x_1,x_2)`, the inner reduce
    returns :math:`(\langle x_1,w\rangle , \langle x_2, w\rangle)`.

    Given a list of tuples :math:`\{(x_i,y_i\}_{i=0}^n`, the outer reduce
    gives :math:`(\sum x_i, \sum y_i)`.
    """

    def inner_reduce(self, x, w):
        out = []
        for xx in x:
            out.append(super(TupleExpectationReduce, self).inner_reduce(xx, w))
        return tuple(out)

    def outer_reduce(self, x, w):
        out = []
        tdim = len(x[0])
        for i in range(tdim):
            xin = [xx[i] for xx in x]
            out.append(super(TupleExpectationReduce, self).outer_reduce(xin, w))
        return tuple(out)


#
# Distributed operations
#
def distributed_sampling(
        d, qtype, qparams, mpi_pool=None):
    nprocs = mpi_pool.nprocs if mpi_pool is not None else 1
    qparams_split = qparams // nprocs
    qparams_reminder = qparams % nprocs
    qparams_list = [
        qparams_split if i >= qparams_reminder else qparams_split + 1
        for i in range(nprocs)]
    mass_list = [float(n) / float(qparams) for n in qparams_list]
    scatter_tuple = (['qparams', 'mass'],
                     [qparams_list, mass_list])
    bcast_tuple = (['qtype'], [qtype])
    (x, w) = mpi_map_alloc_dmem(
        'quadrature',
        scatter_tuple=scatter_tuple, splitted=True,
        bcast_tuple=bcast_tuple,
        dmem_key_out_list=['x', 'w'],
        obj=d, mpi_pool=mpi_pool,
        concatenate=False)
    return (x, w)
