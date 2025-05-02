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

import numpy as np

from ..MPI import mpi_map, ExpectationReduce

__all__ = [
    # L2 minimization
    'misfit_squared', 'grad_a_misfit_squared',
    'hess_a_misfit_squared',
    'L2_misfit',
    'L2squared_misfit', 'grad_a_L2squared_misfit',
    'hess_a_L2squared_misfit',
    'storage_hess_a_L2squared_misfit',
    'action_stored_hess_a_L2squared_misfit',
]

nax = np.newaxis


def misfit_squared(f1, f2, x, params1=None, params2=None, idxs_slice=None):
    r""" Compute :math:`\vert f_1 - f_2 \vert^2`

    Args:
      f1 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]):
        function :math:`f_1` or its functions values
      f2 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
        :math:`f_2` or its functions values
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      params1 (dict): parameters for function :math:`f_1`
      params2 (dict): parameters for function :math:`f_2`
      idxs_slice (:class:`slice<slice>`): slice of points to be

    Returns:
      (:class:`ndarray<numpy.ndarray>`) --  misfit :math:`\vert f_1 - f_2 \vert^2`
    """
    if idxs_slice is None:
        idxs_slice = slice(None)
    if isinstance(f1, np.ndarray):
        F1 = f1[idxs_slice]
    else:
        F1 = f1.evaluate(x, precomp=params1, idxs_slice=idxs_slice)[:, 0]
    if isinstance(f2, np.ndarray):
        F2 = f2[idxs_slice]
    else:
        F2 = f2.evaluate(x, precomp=params2, idxs_slice=idxs_slice)[:, 0]
    if F1.ndim == 2:
        mf = np.sum((F1 - F2) ** 2, axis=1)
    else:
        mf = (F1 - F2) ** 2.
    return mf


def grad_a_misfit_squared(f1, f2, x, params1=None, params2=None, idxs_slice=None):
    r""" Compute :math:`\nabla_{\bf a}\vert f_{1,{\bf a}} - f_2 \vert^2`

    Args:
      f1 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]):
        function :math:`f_1` or its functions values
      f2 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
        :math:`f_2` or its functions values
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      params1 (dict): parameters for function :math:`f_1`
      params2 (dict): parameters for function :math:`f_2`
      idxs_slice (:class:`slice<slice>`): slice of points to be

    Returns:
      (:class:`ndarray<numpy.ndarray>`) --  misfit
         :math:`\nabla_{\bf a}\vert f_{1,{\bf a}} - f_2 \vert^2`
    """
    if idxs_slice is None:
        idxs_slice = slice(None)
    # Evaluate f2
    if isinstance(f2, np.ndarray):
        F2 = f2[idxs_slice]
    else:
        F2 = f2.evaluate(x, precomp=params2, idxs_slice=idxs_slice)[:, 0]
    # Evaluate f1 and grad_a f1
    F1 = f1.evaluate(x, precomp=params1, idxs_slice=idxs_slice)[:, 0]
    ga_F1 = f1.grad_a(x, precomp=params1, idxs_slice=idxs_slice)[:, 0, :]
    mf2 = F1 - F2
    ga_mf2 = 2. * mf2[:, np.newaxis] * ga_F1
    return ga_mf2


def hess_a_misfit_squared(f1, f2, x, params1=None, params2=None, idxs_slice=None):
    r""" Compute :math:`\nabla^2_{\bf a}\vert f_{1,{\bf a}} - f_2 \vert^2`

    Args:
      f1 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]):
        function :math:`f_1` or its functions values
      f2 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
        :math:`f_2` or its functions values
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      params1 (dict): parameters for function :math:`f_1`
      params2 (dict): parameters for function :math:`f_2`
      idxs_slice (:class:`slice<slice>`): slice of points to be

    Returns:
      (:class:`ndarray<numpy.ndarray>`) --  misfit
         :math:`\nabla^2_{\bf a}\vert f_{1,{\bf a}} - f_2 \vert^2`
    """
    if idxs_slice is None:
        idxs_slice = slice(None)
    # Evaluate f2
    if isinstance(f2, np.ndarray):
        F2 = f2[idxs_slice]
    else:
        F2 = f2.evaluate(x, precomp=params2, idxs_slice=idxs_slice)[:, 0]
    # Evaluate f1, grad_a f1 and hess_a f1
    F1 = f1.evaluate(x, precomp=params1, idxs_slice=idxs_slice)[:, 0]
    ga_F1 = f1.grad_a(x, precomp=params1, idxs_slice=idxs_slice)[:, 0, :]
    ha_F1 = f1.hess_a(x, precomp=params1, idxs_slice=idxs_slice)[:, 0, :, :]
    mf2 = F1 - F2
    ha_mf2 = 2. * (mf2[:, np.newaxis, np.newaxis] * ha_F1 + \
                   ga_F1[:, :, np.newaxis] * ga_F1[:, np.newaxis, :])
    return ha_mf2


def L2_misfit(*args, **kwargs):
    r""" Compute :math:`\Vert f_1 - f_2 \Vert_{L^2_\pi}`

    Args:
      f1 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]):
        function :math:`f_1` or its functions values
      f2 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
        :math:`f_2` or its functions values
      d (Distribution): distribution :math:`\pi`
      params1 (dict): parameters for function :math:`f_1`
      params2 (dict): parameters for function :math:`f_2`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      batch_size (int): this defines whether to evaluate in batches or not.
        A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``f1`` and ``f2`

    Returns:
      (:class:`float<float>`) --  misfit :math:`\Vert f_1 - f_2 \Vert_{L^2_\pi}`

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    l2squared = L2squared_misfit(*args, **kwargs)
    return np.sqrt(l2squared)


def L2squared_misfit(f1, f2, d=None, params1=None, params2=None,
                     qtype=None, qparams=None, x=None, w=None,
                     batch_size=None, mpi_pool=None):
    r""" Compute :math:`\Vert f_1 - f_2 \Vert^2_{L^2_\pi}`

    Args:
      f1 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]):
        function :math:`f_1` or its functions values
      f2 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
        :math:`f_2` or its functions values
      d (Distribution): distribution :math:`\pi`
      params1 (dict): parameters for function :math:`f_1`
      params2 (dict): parameters for function :math:`f_2`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      batch_size (int): this defines whether to evaluate in batches or not.
        A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``f1`` and ``f2`

    Returns:
      (:class:`float<float>`) --  misfit :math:`\Vert f_1 - f_2 \Vert^2_{L^2_\pi}`

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    if (isinstance(f1, np.ndarray) and isinstance(f2, np.ndarray)
            and isinstance(w, np.ndarray)):
        F1 = f1
        F2 = f2
        err = np.abs(F1 - F2)
        L2err = np.dot(err ** 2., w)
    else:
        if (x is None) and (w is None):
            (x, w) = d.quadrature(qtype, qparams)
        reduce_obj = ExpectationReduce()
        if batch_size is None:
            scatter_tuple = (['x'], [x])
            reduce_tuple = (['w'], [w])
            bcast_tuple = (['f1', 'f2'], [f1, f2])
            dmem_key_in_list = ['params1', 'params2']
            dmem_arg_in_list = ['params1', 'params2']
            dmem_val_in_list = [params1, params2]
            L2err = mpi_map(misfit_squared, scatter_tuple=scatter_tuple,
                            bcast_tuple=bcast_tuple,
                            reduce_obj=reduce_obj, reduce_tuple=reduce_tuple,
                            dmem_key_in_list=dmem_key_in_list,
                            dmem_arg_in_list=dmem_arg_in_list,
                            dmem_val_in_list=dmem_val_in_list,
                            mpi_pool=mpi_pool)
        else:  # Batching
            L2err = 0.
            # Split data and get maximum length of chunk
            if mpi_pool is None:
                x_list, ns = ([x], [0, len(x)])
                w_list = [w]
            else:
                split_dict = mpi_pool.split_data([x, w], ['x', 'w'])
                x_list = [sd['x'] for sd in split_dict]
                w_list = [sd['w'] for sd in split_dict]
                ns = [0] + [len(xi) for xi in x_list]
                ns = list(np.cumsum(ns))
            max_len = x_list[0].shape[0]
            # Compute the number of iterations necessary for batching
            niter = max_len // batch_size + (1 if max_len % batch_size > 0 else 0)
            # Iterate
            idx0_list = [0] * len(x_list)
            for it in range(niter):
                # Prepare batch-slicing for each chunk
                idxs_slice_list = []
                for i, (xs, idx0) in enumerate(zip(x_list, idx0_list)):
                    incr = min(batch_size, xs.shape[0] - idx0)
                    idxs_slice_list.append(slice(idx0, idx0 + incr, None))
                    idx0_list[i] += incr
                # Prepare input x and w
                x_in = [xs[idxs_slice, :]
                        for xs, idxs_slice in zip(x_list, idxs_slice_list)]
                w_in = [ws[idxs_slice]
                        for ws, idxs_slice in zip(w_list, idxs_slice_list)]
                # Evaluate
                scatter_tuple = (['x', 'idxs_slice'], [x_in, idxs_slice_list])
                reduce_tuple = (['w'], [w_in])
                bcast_tuple = (['f1', 'f2'], [f1, f2])
                dmem_key_in_list = ['params1', 'params2']
                dmem_arg_in_list = ['params1', 'params2']
                dmem_val_in_list = [params1, params2]
                L2err += mpi_map(misfit_squared, scatter_tuple=scatter_tuple,
                                 bcast_tuple=bcast_tuple,
                                 dmem_key_in_list=dmem_key_in_list,
                                 dmem_arg_in_list=dmem_arg_in_list,
                                 dmem_val_in_list=dmem_val_in_list,
                                 reduce_obj=reduce_obj, reduce_tuple=reduce_tuple,
                                 mpi_pool=mpi_pool, splitted=True)
    return L2err


def grad_a_L2squared_misfit(f1, f2, d=None, params1=None, params2=None,
                            qtype=None, qparams=None, x=None, w=None,
                            batch_size=None, mpi_pool=None):
    r""" Compute :math:`\nabla_{\bf a}\Vert f_{1,{\bf a}} - f_2 \Vert^2_{L^2_\pi}`

    Args:
      f1 (:class:`ParametricFunctionApproximation`): function
        :math:`f_1`
      f2 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
        :math:`f_2` or its functions values
      d (Distribution): distribution :math:`\pi`
      params1 (dict): parameters for function :math:`f_1`
      params2 (dict): parameters for function :math:`f_2`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      batch_size (int): this defines whether to evaluate in batches or not.
        A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``f1`` and ``f2`

    Returns:
      (:class:`ndarray<numpy.ndarray>` [:math:`N`]) --  misfit gradient
        :math:`\nabla_{\bf a}\Vert f_1 - f_2 \Vert_{L^2_\pi}`

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    if (x is None) and (w is None):
        (x, w) = d.quadrature(qtype, qparams)
    reduce_obj = ExpectationReduce()
    if batch_size is None:
        scatter_tuple = (['x'], [x])
        reduce_tuple = (['w'], [w])
        bcast_tuple = (['f1', 'f2'], [f1, f2])
        dmem_key_in_list = ['params1', 'params2']
        dmem_arg_in_list = ['params1', 'params2']
        dmem_val_in_list = [params1, params2]
        ga_L2err = mpi_map(grad_a_misfit_squared, scatter_tuple=scatter_tuple,
                           bcast_tuple=bcast_tuple,
                           reduce_obj=reduce_obj, reduce_tuple=reduce_tuple,
                           dmem_key_in_list=dmem_key_in_list,
                           dmem_arg_in_list=dmem_arg_in_list,
                           dmem_val_in_list=dmem_val_in_list,
                           mpi_pool=mpi_pool)
    else:  # Batching
        ga_L2err = np.zeros(f1.n_coeffs)
        # Split data and get maximum length of chunk
        if mpi_pool is None:
            x_list, ns = ([x], [0, len(x)])
            w_list = [w]
        else:
            split_dict = mpi_pool.split_data([x, w], ['x', 'w'])
            x_list = [sd['x'] for sd in split_dict]
            w_list = [sd['w'] for sd in split_dict]
            ns = [0] + [len(xi) for xi in x_list]
            ns = list(np.cumsum(ns))
        max_len = x_list[0].shape[0]
        # Compute the number of iterations necessary for batching
        niter = max_len // batch_size + (1 if max_len % batch_size > 0 else 0)
        # Iterate
        idx0_list = [0] * len(x_list)
        for it in range(niter):
            # Prepare batch-slicing for each chunk
            idxs_slice_list = []
            for i, (xs, idx0) in enumerate(zip(x_list, idx0_list)):
                incr = min(batch_size, xs.shape[0] - idx0)
                idxs_slice_list.append(slice(idx0, idx0 + incr, None))
                idx0_list[i] += incr
            # Prepare input x and w
            x_in = [xs[idxs_slice, :]
                    for xs, idxs_slice in zip(x_list, idxs_slice_list)]
            w_in = [ws[idxs_slice]
                    for ws, idxs_slice in zip(w_list, idxs_slice_list)]
            # Evaluate
            scatter_tuple = (['x', 'idxs_slice'], [x_in, idxs_slice_list])
            reduce_tuple = (['w'], [w_in])
            bcast_tuple = (['f1', 'f2'], [f1, f2])
            dmem_key_in_list = ['params1', 'params2']
            dmem_arg_in_list = ['params1', 'params2']
            dmem_val_in_list = [params1, params2]
            ga_L2err += mpi_map(grad_a_misfit_squared,
                                scatter_tuple=scatter_tuple,
                                bcast_tuple=bcast_tuple,
                                dmem_key_in_list=dmem_key_in_list,
                                dmem_arg_in_list=dmem_arg_in_list,
                                dmem_val_in_list=dmem_val_in_list,
                                reduce_obj=reduce_obj,
                                reduce_tuple=reduce_tuple,
                                mpi_pool=mpi_pool, splitted=True)
    return ga_L2err


def hess_a_L2squared_misfit(f1, f2, d=None, params1=None, params2=None,
                            qtype=None, qparams=None, x=None, w=None,
                            batch_size=None, mpi_pool=None):
    r""" Compute :math:`\nabla^2_{\bf a}\Vert f_{1,{\bf a}} - f_2 \Vert^2_{L^2_\pi}`

    Args:
      f1 (:class:`ParametricFunctionApproximation`): function
        :math:`f_1`
      f2 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
        :math:`f_2` or its functions values
      d (Distribution): distribution :math:`\pi`
      params1 (dict): parameters for function :math:`f_1`
      params2 (dict): parameters for function :math:`f_2`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      batch_size (int): this defines whether to evaluate in batches or not.
        A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``f1`` and ``f2`

    Returns:
      (:class:`ndarray<numpy.ndarray>` [:math:`N,N`]) --  misfit Hessian
        :math:`\nabla^2_{\bf a}\Vert f_1 - f_2 \Vert_{L^2_\pi}`

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    if (x is None) and (w is None):
        (x, w) = d.quadrature(qtype, qparams)
    reduce_obj = ExpectationReduce()
    if batch_size is None:
        scatter_tuple = (['x'], [x])
        reduce_tuple = (['w'], [w])
        bcast_tuple = (['f1', 'f2'], [f1, f2])
        dmem_key_in_list = ['params1', 'params2']
        dmem_arg_in_list = ['params1', 'params2']
        dmem_val_in_list = [params1, params2]
        ha_L2err = mpi_map(hess_a_misfit_squared, scatter_tuple=scatter_tuple,
                           bcast_tuple=bcast_tuple,
                           reduce_obj=reduce_obj, reduce_tuple=reduce_tuple,
                           dmem_key_in_list=dmem_key_in_list,
                           dmem_arg_in_list=dmem_arg_in_list,
                           dmem_val_in_list=dmem_val_in_list,
                           mpi_pool=mpi_pool)
    else:  # Batching
        nc = f1.n_coeffs
        ha_L2err = np.zeros((nc, nc))
        # Split data and get maximum length of chunk
        if mpi_pool is None:
            x_list, ns = ([x], [0, len(x)])
            w_list = [w]
        else:
            split_dict = mpi_pool.split_data([x, w], ['x', 'w'])
            x_list = [sd['x'] for sd in split_dict]
            w_list = [sd['w'] for sd in split_dict]
            ns = [0] + [len(xi) for xi in x_list]
            ns = list(np.cumsum(ns))
        max_len = x_list[0].shape[0]
        # Compute the number of iterations necessary for batching
        niter = max_len // batch_size + (1 if max_len % batch_size > 0 else 0)
        # Iterate
        idx0_list = [0] * len(x_list)
        for it in range(niter):
            # Prepare batch-slicing for each chunk
            idxs_slice_list = []
            for i, (xs, idx0) in enumerate(zip(x_list, idx0_list)):
                incr = min(batch_size, xs.shape[0] - idx0)
                idxs_slice_list.append(slice(idx0, idx0 + incr, None))
                idx0_list[i] += incr
            # Prepare input x and w
            x_in = [xs[idxs_slice, :]
                    for xs, idxs_slice in zip(x_list, idxs_slice_list)]
            w_in = [ws[idxs_slice]
                    for ws, idxs_slice in zip(w_list, idxs_slice_list)]
            # Evaluate
            scatter_tuple = (['x', 'idxs_slice'], [x_in, idxs_slice_list])
            reduce_tuple = (['w'], [w_in])
            bcast_tuple = (['f1', 'f2'], [f1, f2])
            dmem_key_in_list = ['params1', 'params2']
            dmem_arg_in_list = ['params1', 'params2']
            dmem_val_in_list = [params1, params2]
            ha_L2err += mpi_map(hess_a_misfit_squared,
                                scatter_tuple=scatter_tuple,
                                bcast_tuple=bcast_tuple,
                                dmem_key_in_list=dmem_key_in_list,
                                dmem_arg_in_list=dmem_arg_in_list,
                                dmem_val_in_list=dmem_val_in_list,
                                reduce_obj=reduce_obj,
                                reduce_tuple=reduce_tuple,
                                mpi_pool=mpi_pool, splitted=True)
    return ha_L2err


def storage_hess_a_L2squared_misfit(f1, f2, d=None, params1=None, params2=None,
                                    qtype=None, qparams=None, x=None, w=None,
                                    batch_size=None, mpi_pool=None):
    r""" Assemble :math:`\nabla^2_{\bf a}\Vert f_{1,{\bf a}} - f_2 \Vert^2_{L^2_\pi}`.

    Args:
      f1 (:class:`ParametricFunctionApproximation`): function
        :math:`f_1`
      f2 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
        :math:`f_2` or its functions values
      d (Distribution): distribution :math:`\pi`
      params1 (dict): parameters for function :math:`f_1`
      params2 (dict): parameters for function :math:`f_2`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      batch_size (int): this defines whether to evaluate in batches or not.
        A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``f1`` and ``f2`

    Returns:
      (None) -- the result is stored in ``params1['hess_a_L2_misfit']``

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.

    .. note:: the dictionary ``params1`` must be provided
    """
    H = hess_a_L2squared_misfit(
        f1, f2, d=d, params1=params1, params2=params2,
        qtype=qtype, qparams=qparams, x=x, w=w,
        batch_size=batch_size, mpi_pool=mpi_pool)
    return (H,)


def action_stored_hess_a_L2squared_misfit(H, v):
    r""" Evaluate the action of :math:`\nabla^2_{\bf a}\Vert f_{1,{\bf a}} - f_2 \Vert^2_{L^2_\pi}` on :math:`v`.

    Args:
      v (:class:`ndarray<numpy.ndarray>` [:math:`N`]): vector :math:`v`
      v (:class:`ndarray<numpy.ndarray>` [:math:`N,N`]): Hessian
        :math:`\nabla^2_{\bf a}\Vert f_{1,{\bf a}} - f_2 \Vert^2_{L^2_\pi}`

    Returns:
      (:class:`ndarray<numpy.ndarray>` [:math:`N`]) --
        :math:`\langle\nabla^2_{\bf a}\Vert f_{1,{\bf a}} - f_2 \Vert^2_{L^2_\pi},v\rangle`
    """
    return np.dot(H, v)
