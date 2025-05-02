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
import scipy.linalg as scila
from TransportMaps.Distributions import PullBackTransportMapDistribution, ParametricTransportMapDistribution

from ..MPI import mpi_map, ExpectationReduce, TupleExpectationReduce
from ..Distributions import Distribution
from ..Maps.Functionals import ProductDistributionParametricPullbackComponentFunction

__all__ = [
    # KL divergence functions
    'kl_divergence', 'grad_a_kl_divergence',
    'hess_a_kl_divergence',
    'tuple_grad_a_kl_divergence',
    'action_stored_hess_a_kl_divergence',
    'storage_hess_a_kl_divergence',
    'action_hess_a_kl_divergence',
    # Product measures pullback KL divergence functions
    'kl_divergence_component',
    'grad_a_kl_divergence_component',
    'hess_a_kl_divergence_component',
    # First variations
    'grad_t_kl_divergence',
    'grad_x_grad_t_kl_divergence',
    'tuple_grad_x_grad_t_kl_divergence',
]

nax = np.newaxis


def kl_divergence(
        d1: Distribution,
        d2: Distribution,
        params1=None, params2=None, cache=None,
        qtype=None, qparams=None, x=None, w=None,
        batch_size=None, mpi_pool_tuple=(None, None),
        d1_entropy=True):
    r""" Compute :math:`\mathcal{D}_{KL}(\pi_1 | \pi_2)`

    Args:
      d1 (Distribution): distribution :math:`\pi_1`
      d2 (Distribution): distribution :math:`\pi_2`
      params1 (dict): parameters for distribution :math:`\pi_1`
      params2 (dict): parameters for distribution :math:`\pi_2`
      cache (dict): cached values
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi_1}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``d1`` and ``d2``
      d1_entropy (bool): whether to include the entropy term
        :math:`\mathbb{E}_{\pi_1}[\log \pi_1]` in the KL divergence

    Returns:
      (:class:`float<float>`) -- :math:`\mathcal{D}_{KL}(\pi_1 | \pi_2)`

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    if ((qtype is not None) and (qparams is not None)
            and (x is None) and (w is None)):
        (x, w) = d1.quadrature(qtype, qparams, mpi_pool=mpi_pool_tuple[0])
    elif ((qtype is None) and (qparams is None)
          and (x is not None) and (w is not None)):
        pass
    else:
        raise ValueError("Parameters (qtype,qparams) and (x,w) are mutually " +
                         "exclusive, but one pair of them is necessary.")
    reduce_obj = ExpectationReduce()
    # d1.log_pdf
    mean_log_d1 = 0.
    if d1_entropy:
        try:
            mean_log_d1 = d1.mean_log_pdf()
        except NotImplementedError as e:
            scatter_tuple = (['x'], [x])
            reduce_tuple = (['w'], [w])
            dmem_key_in_list = ['params1']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params1]
            mean_log_d1 = mpi_map("log_pdf", scatter_tuple=scatter_tuple,
                                  dmem_key_in_list=dmem_key_in_list,
                                  dmem_arg_in_list=dmem_arg_in_list,
                                  dmem_val_in_list=dmem_val_in_list,
                                  obj=d1, reduce_obj=reduce_obj,
                                  reduce_tuple=reduce_tuple,
                                  mpi_pool=mpi_pool_tuple[0])
    # d2.log_pdf
    if batch_size is None:
        scatter_tuple = (['x'], [x])
        reduce_tuple = (['w'], [w])
        dmem_key_in_list = ['params2', 'cache']
        dmem_arg_in_list = ['params', 'cache']
        dmem_val_in_list = [params2, cache]
        mean_log_d2 = mpi_map("log_pdf", scatter_tuple=scatter_tuple,
                              dmem_key_in_list=dmem_key_in_list,
                              dmem_arg_in_list=dmem_arg_in_list,
                              dmem_val_in_list=dmem_val_in_list,
                              obj=d2, reduce_obj=reduce_obj,
                              reduce_tuple=reduce_tuple,
                              mpi_pool=mpi_pool_tuple[1])
    else:
        mean_log_d2 = 0.
        # Split data
        if mpi_pool_tuple[1] is None:
            x_list = [x]
            w_list = [w]
        else:
            split_dict = mpi_pool_tuple[1].split_data([x, w], ['x', 'w'])
            x_list = [sd['x'] for sd in split_dict]
            w_list = [sd['w'] for sd in split_dict]
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
            x_in = [xs[idxs_slice, :] for xs, idxs_slice in zip(x_list, idxs_slice_list)]
            w_in = [ws[idxs_slice] for ws, idxs_slice in zip(w_list, idxs_slice_list)]
            # Evaluate
            scatter_tuple = (['x', 'idxs_slice'], [x_in, idxs_slice_list])
            reduce_tuple = (['w'], [w_in])
            dmem_key_in_list = ['params2', 'cache']
            dmem_arg_in_list = ['params', 'cache']
            dmem_val_in_list = [params2, cache]
            mean_log_d2 += mpi_map("log_pdf", scatter_tuple=scatter_tuple,
                                   dmem_key_in_list=dmem_key_in_list,
                                   dmem_arg_in_list=dmem_arg_in_list,
                                   dmem_val_in_list=dmem_val_in_list,
                                   obj=d2, reduce_obj=reduce_obj,
                                   reduce_tuple=reduce_tuple,
                                   mpi_pool=mpi_pool_tuple[1], splitted=True)
    out = mean_log_d1 - mean_log_d2
    return out


def grad_a_kl_divergence(
        d1: Distribution,
        d2: ParametricTransportMapDistribution,
        params1=None, params2=None, cache=None,
        qtype=None, qparams=None, x=None, w=None,
        batch_size=None, mpi_pool_tuple=(None, None)):
    r""" Compute :math:`\nabla_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}})`

    Args:
      d1 (Distribution): distribution :math:`\pi_1`
      d2 (ParametricTransportMapDistribution): distribution :math:`\pi_2`
      params1 (dict): parameters for distribution :math:`\pi_1`
      params2 (dict): parameters for distribution :math:`\pi_2`
      cache (dict): cached values
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi_1}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one.
      mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``d1`` and ``d2`

    Returns:
      (:class:`ndarray<numpy.ndarray>` [:math:`N`] --
        :math:`\nabla_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}})`

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    if ((qtype is not None) and (qparams is not None)
            and (x is None) and (w is None)):
        (x, w) = d1.quadrature(qtype, qparams, mpi_pool=mpi_pool_tuple[0])
    elif ((qtype is None) and (qparams is None)
          and (x is not None) and (w is not None)):
        pass
    else:
        raise ValueError("Parameters (qtype,qparams) and (x,w) are mutually " +
                         "exclusive, but one pair of them is necessary.")
    reduce_obj = ExpectationReduce()
    if batch_size is None:
        scatter_tuple = (['x'], [x])
        reduce_tuple = (['w'], [w])
        dmem_key_in_list = ['params2', 'cache']
        dmem_arg_in_list = ['params', 'cache']
        dmem_val_in_list = [params2, cache]
        out = - mpi_map("grad_a_log_pdf", scatter_tuple=scatter_tuple,
                        dmem_key_in_list=dmem_key_in_list,
                        dmem_arg_in_list=dmem_arg_in_list,
                        dmem_val_in_list=dmem_val_in_list,
                        obj=d2, reduce_obj=reduce_obj,
                        reduce_tuple=reduce_tuple,
                        mpi_pool=mpi_pool_tuple[1])
    else:
        out = np.zeros(d2.n_coeffs)
        # Split data and get maximum length of chunk
        if mpi_pool_tuple[1] is None:
            x_list, ns = ([x], [0, len(x)])
            w_list = [w]
        else:
            split_dict = mpi_pool_tuple[1].split_data([x, w], ['x', 'w'])
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
            x_in = [xs[idxs_slice, :] for xs, idxs_slice in zip(x_list, idxs_slice_list)]
            w_in = [ws[idxs_slice] for ws, idxs_slice in zip(w_list, idxs_slice_list)]
            # Evaluate
            scatter_tuple = (['x', 'idxs_slice'], [x_in, idxs_slice_list])
            reduce_tuple = (['w'], [w_in])
            dmem_key_in_list = ['params2', 'cache']
            dmem_arg_in_list = ['params', 'cache']
            dmem_val_in_list = [params2, cache]
            out -= mpi_map("grad_a_log_pdf", scatter_tuple=scatter_tuple,
                           dmem_key_in_list=dmem_key_in_list,
                           dmem_arg_in_list=dmem_arg_in_list,
                           dmem_val_in_list=dmem_val_in_list,
                           obj=d2, reduce_obj=reduce_obj,
                           reduce_tuple=reduce_tuple,
                           mpi_pool=mpi_pool_tuple[1], splitted=True)
    return out


def tuple_grad_a_kl_divergence(
        d1: Distribution,
        d2: ParametricTransportMapDistribution,
        params1=None, params2=None, cache=None,
        qtype=None, qparams=None, x=None, w=None,
        batch_size=None, mpi_pool_tuple=(None, None),
        d1_entropy=True):
    r""" Compute :math:`\left(\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}}),\nabla_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}})\right)`

    Args:
      d1 (Distribution): distribution :math:`\pi_1`
      d2 (Distribution): distribution :math:`\pi_2`
      params1 (dict): parameters for distribution :math:`\pi_1`
      params2 (dict): parameters for distribution :math:`\pi_2`
      cache (dict): cached values
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi_1}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one.
      mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``d1`` and ``d2`

    Returns:
      (:class:`tuple`) --
        :math:`\left(\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}}),\nabla_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}})\right)`

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    if ((qtype is not None) and (qparams is not None)
            and (x is None) and (w is None)):
        (x, w) = d1.quadrature(qtype, qparams, mpi_pool=mpi_pool_tuple[0])
    elif ((qtype is None) and (qparams is None)
          and (x is not None) and (w is not None)):
        pass
    else:
        raise ValueError("Parameters (qtype,qparams) and (x,w) are mutually " +
                         "exclusive, but one pair of them is necessary.")
    reduce_obj = TupleExpectationReduce()
    # d1.log_pdf
    mean_log_d1 = 0.
    if d1_entropy:
        try:
            mean_log_d1 = d1.mean_log_pdf()
        except NotImplementedError as e:
            scatter_tuple = (['x'], [x])
            reduce_tuple = (['w'], [w])
            dmem_key_in_list = ['params1']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params1]
            mean_log_d1 = mpi_map("log_pdf", scatter_tuple=scatter_tuple,
                                  dmem_key_in_list=dmem_key_in_list,
                                  dmem_arg_in_list=dmem_arg_in_list,
                                  dmem_val_in_list=dmem_val_in_list,
                                  obj=d1, reduce_obj=reduce_obj,
                                  reduce_tuple=reduce_tuple,
                                  mpi_pool=mpi_pool_tuple[0])
    if batch_size is None:
        scatter_tuple = (['x'], [x])
        reduce_tuple = (['w'], [w])
        dmem_key_in_list = ['params2', 'cache']
        dmem_arg_in_list = ['params', 'cache']
        dmem_val_in_list = [params2, cache]
        o1, o2 = mpi_map("tuple_grad_a_log_pdf", scatter_tuple=scatter_tuple,
                         dmem_key_in_list=dmem_key_in_list,
                         dmem_arg_in_list=dmem_arg_in_list,
                         dmem_val_in_list=dmem_val_in_list,
                         obj=d2, reduce_obj=reduce_obj,
                         reduce_tuple=reduce_tuple,
                         mpi_pool=mpi_pool_tuple[1])
        mean_log_d2 = o1
        ga = -o2
    else:
        mean_log_d2 = 0.
        ga = np.zeros(d2.n_coeffs)
        # Split data and get maximum length of chunk
        if mpi_pool_tuple[1] is None:
            x_list, ns = ([x], [0, len(x)])
            w_list = [w]
        else:
            split_dict = mpi_pool_tuple[1].split_data([x, w], ['x', 'w'])
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
            x_in = [xs[idxs_slice, :] for xs, idxs_slice in zip(x_list, idxs_slice_list)]
            w_in = [ws[idxs_slice] for ws, idxs_slice in zip(w_list, idxs_slice_list)]
            # Evaluate
            scatter_tuple = (['x', 'idxs_slice'], [x_in, idxs_slice_list])
            reduce_tuple = (['w'], [w_in])
            dmem_key_in_list = ['params2', 'cache']
            dmem_arg_in_list = ['params', 'cache']
            dmem_val_in_list = [params2, cache]
            o1, o2 = mpi_map("tuple_grad_a_log_pdf", scatter_tuple=scatter_tuple,
                             dmem_key_in_list=dmem_key_in_list,
                             dmem_arg_in_list=dmem_arg_in_list,
                             dmem_val_in_list=dmem_val_in_list,
                             obj=d2, reduce_obj=reduce_obj,
                             reduce_tuple=reduce_tuple,
                             mpi_pool=mpi_pool_tuple[1], splitted=True)
            mean_log_d2 += o1
            ga -= o2
    ev = mean_log_d1 - mean_log_d2
    return ev, ga


def hess_a_kl_divergence(
        d1: Distribution,
        d2: ParametricTransportMapDistribution,
        params1=None, params2=None, cache=None,
        qtype=None, qparams=None, x=None, w=None,
        batch_size=None, mpi_pool_tuple=(None, None)):
    r""" Compute :math:`\nabla^2_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}})`

    Args:
      d1 (Distribution): distribution :math:`\pi_1`
      d2 (Distribution): distribution :math:`\pi_2`
      params1 (dict): parameters for distribution :math:`\pi_1`
      params2 (dict): parameters for distribution :math:`\pi_2`
      cache (dict): cached values
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi_1}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one.
      mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``d1`` and ``d2`

    Returns:
      (:class:`ndarray<numpy.ndarray>` [:math:`N,N`] --
        :math:`\nabla^2_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}})`

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    if ((qtype is not None) and (qparams is not None)
            and (x is None) and (w is None)):
        (x, w) = d1.quadrature(qtype, qparams, mpi_pool=mpi_pool_tuple[0])
    elif ((qtype is None) and (qparams is None)
          and (x is not None) and (w is not None)):
        pass
    else:
        raise ValueError("Parameters (qtype,qparams) and (x,w) are mutually " +
                         "exclusive, but one pair of them is necessary.")
    reduce_obj = ExpectationReduce()
    if batch_size is None:
        scatter_tuple = (['x'], [x])
        reduce_tuple = (['w'], [w])
        dmem_key_in_list = ['params2', 'cache']
        dmem_arg_in_list = ['params', 'cache']
        dmem_val_in_list = [params2, cache]
        out = - mpi_map("hess_a_log_pdf", scatter_tuple=scatter_tuple,
                        dmem_key_in_list=dmem_key_in_list,
                        dmem_arg_in_list=dmem_arg_in_list,
                        dmem_val_in_list=dmem_val_in_list,
                        obj=d2, reduce_obj=reduce_obj,
                        reduce_tuple=reduce_tuple,
                        mpi_pool=mpi_pool_tuple[1])
    else:
        nc = d2.n_coeffs
        out = np.zeros((nc, nc))
        # Split data and get maximum length of chunk
        if mpi_pool_tuple[1] is None:
            x_list, ns = ([x], [0, len(x)])
            w_list = [w]
        else:
            split_dict = mpi_pool_tuple[1].split_data([x, w], ['x', 'w'])
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
            x_in = [xs[idxs_slice, :] for xs, idxs_slice in zip(x_list, idxs_slice_list)]
            w_in = [ws[idxs_slice] for ws, idxs_slice in zip(w_list, idxs_slice_list)]
            # Evaluate
            scatter_tuple = (['x', 'idxs_slice'], [x_in, idxs_slice_list])
            reduce_tuple = (['w'], [w_in])
            dmem_key_in_list = ['params2', 'cache']
            dmem_arg_in_list = ['params', 'cache']
            dmem_val_in_list = [params2, cache]
            out -= mpi_map("hess_a_log_pdf", scatter_tuple=scatter_tuple,
                           dmem_key_in_list=dmem_key_in_list,
                           dmem_arg_in_list=dmem_arg_in_list,
                           dmem_val_in_list=dmem_val_in_list,
                           obj=d2, reduce_obj=reduce_obj,
                           reduce_tuple=reduce_tuple,
                           mpi_pool=mpi_pool_tuple[1], splitted=True)
    return out


def action_hess_a_kl_divergence(
        da,
        d1: Distribution,
        d2: ParametricTransportMapDistribution,
        params1=None, params2=None, cache=None,
        qtype=None, qparams=None, x=None, w=None,
        batch_size=None, mpi_pool_tuple=(None, None)):
    r""" Compute :math:`\langle\nabla^2_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}}),\delta{\bf }\rangle`

    Args:
      da (:class:`ndarray<numpy.ndarray>` [:math:`N`]):
        vector on which to apply the Hessian
      d1 (Distribution): distribution :math:`\pi_1`
      d2 (Distribution): distribution :math:`\pi_2`
      params1 (dict): parameters for distribution :math:`\pi_1`
      params2 (dict): parameters for distribution :math:`\pi_2`
      cache (dict): cached values
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi_1}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one.
      mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``d1`` and ``d2`

    Returns:
      (:class:`ndarray<numpy.ndarray>` [:math:`N,N`] --
        :math:`\nabla^2_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}})`

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    if ((qtype is not None) and (qparams is not None)
            and (x is None) and (w is None)):
        (x, w) = d1.quadrature(qtype, qparams, mpi_pool=mpi_pool_tuple[0])
    elif ((qtype is None) and (qparams is None)
          and (x is not None) and (w is not None)):
        pass
    else:
        raise ValueError("Parameters (qtype,qparams) and (x,w) are mutually " +
                         "exclusive, but one pair of them is necessary.")
    reduce_obj = ExpectationReduce()
    if batch_size is None:
        bcast_tuple = (['da'], [da])
        scatter_tuple = (['x'], [x])
        reduce_tuple = (['w'], [w])
        dmem_key_in_list = ['params2', 'cache']
        dmem_arg_in_list = ['params', 'cache']
        dmem_val_in_list = [params2, cache]
        out = - mpi_map("action_hess_a_log_pdf", scatter_tuple=scatter_tuple,
                        bcast_tuple=bcast_tuple,
                        dmem_key_in_list=dmem_key_in_list,
                        dmem_arg_in_list=dmem_arg_in_list,
                        dmem_val_in_list=dmem_val_in_list,
                        obj=d2, reduce_obj=reduce_obj,
                        reduce_tuple=reduce_tuple,
                        mpi_pool=mpi_pool_tuple[1])
    else:
        nc = d2.n_coeffs
        out = np.zeros(nc)
        # Split data and get maximum length of chunk
        if mpi_pool_tuple[1] is None:
            x_list, ns = ([x], [0, len(x)])
            w_list = [w]
        else:
            split_dict = mpi_pool_tuple[1].split_data([x, w], ['x', 'w'])
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
            x_in = [xs[idxs_slice, :] for xs, idxs_slice in zip(x_list, idxs_slice_list)]
            w_in = [ws[idxs_slice] for ws, idxs_slice in zip(w_list, idxs_slice_list)]
            # Evaluate
            bcast_tuple = (['da'], [da])
            scatter_tuple = (['x', 'idxs_slice'], [x_in, idxs_slice_list])
            reduce_tuple = (['w'], [w_in])
            dmem_key_in_list = ['params2', 'cache']
            dmem_arg_in_list = ['params', 'cache']
            dmem_val_in_list = [params2, cache]
            out -= mpi_map("action_hess_a_log_pdf", scatter_tuple=scatter_tuple,
                           bcast_tuple=bcast_tuple,
                           dmem_key_in_list=dmem_key_in_list,
                           dmem_arg_in_list=dmem_arg_in_list,
                           dmem_val_in_list=dmem_val_in_list,
                           obj=d2, reduce_obj=reduce_obj,
                           reduce_tuple=reduce_tuple,
                           mpi_pool=mpi_pool_tuple[1], splitted=True)
    return out


def storage_hess_a_kl_divergence(
        d1: Distribution,
        d2: ParametricTransportMapDistribution,
        params1=None, params2=None, cache=None,
        qtype=None, qparams=None, x=None, w=None,
        batch_size=None, mpi_pool_tuple=(None, None)):
    r""" Assemble :math:`\nabla^2_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}})`.

    Args:
      d1 (Distribution): distribution :math:`\pi_1`
      d2 (Distribution): distribution :math:`\pi_2`
      params1 (dict): parameters for distribution :math:`\pi_1`
      params2 (dict): parameters for distribution :math:`\pi_2`
      cache (dict): cached values
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi_1}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one.
      mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``d1`` and ``d2`

    Returns:
      (None) -- the result is stored in ``params2['hess_a_kl_divergence']``

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.

    .. note:: the dictionary ``params2`` must be provided
    """
    # assemble/fetch Hessian
    H = hess_a_kl_divergence(
        d1, d2, params1=params1, params2=params2,
        cache=cache,
        qtype=qtype, qparams=qparams, x=x, w=w,
        batch_size=batch_size,
        mpi_pool_tuple=mpi_pool_tuple)
    return (H,)


def action_stored_hess_a_kl_divergence(H, v):
    r""" Evaluate action of :math:`\nabla^2_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}})` on vector :math:`v`.

    Args:
      v (:class:`ndarray<numpy.ndarray>` [:math:`N`]): vector :math:`v`
      H (:class:`ndarray<numpy.ndarray>` [:math:`N,N`]): Hessian
        :math:`\nabla^2_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}})`

    Returns:
      (:class:`ndarray<numpy.ndarray>` [:math:`N`]) --
        :math:`\langle\nabla^2_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}}),v\rangle`
    """
    return np.dot(H, v)


def kl_divergence_component(f, params=None, cache=None,
                            x=None, w=None,
                            batch_size=None, mpi_pool=None):
    r""" Compute :math:`-\sum_{i=0}^m f(x_i) = -\sum_{i=0}^m \log\pi\circ T_k(x_i) + \log\partial_{x_k}T_k(x_i)`

    Args:
      f (ProductDistributionParametricPullbackComponentFunction): function :math:`f`
      params (dict): parameters for function :math:`f`
      cache (dict): cached values
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``f``

    Returns:
      (:class:`float<float>`) -- value
    """
    reduce_obj = ExpectationReduce()
    if batch_size is None:
        scatter_tuple = (['x'], [x])
        reduce_tuple = (['w'], [w])
        dmem_key_in_list = ['params', 'cache']
        dmem_arg_in_list = ['params', 'cache']
        dmem_val_in_list = [params, cache]
        out = - mpi_map("evaluate", scatter_tuple=scatter_tuple,
                        dmem_key_in_list=dmem_key_in_list,
                        dmem_arg_in_list=dmem_arg_in_list,
                        dmem_val_in_list=dmem_val_in_list,
                        obj=f, reduce_obj=reduce_obj,
                        reduce_tuple=reduce_tuple,
                        mpi_pool=mpi_pool)[0]
    else:
        out = 0.
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
            x_in = [xs[idxs_slice, :] for xs, idxs_slice in zip(x_list, idxs_slice_list)]
            w_in = [ws[idxs_slice] for ws, idxs_slice in zip(w_list, idxs_slice_list)]
            # Evaluate
            scatter_tuple = (['x', 'idxs_slice'], [x_in, idxs_slice_list])
            reduce_tuple = (['w'], [w_in])
            dmem_key_in_list = ['params', 'cache']
            dmem_arg_in_list = ['params', 'cache']
            dmem_val_in_list = [params, cache]
            out += - mpi_map("evaluate", scatter_tuple=scatter_tuple,
                             dmem_key_in_list=dmem_key_in_list,
                             dmem_arg_in_list=dmem_arg_in_list,
                             dmem_val_in_list=dmem_val_in_list,
                             obj=d2, reduce_obj=reduce_obj,
                             reduce_tuple=reduce_tuple,
                             mpi_pool=mpi_pool, splitted=True)[0]
    return out


def grad_a_kl_divergence_component(f, params=None, cache=None,
                                   x=None, w=None,
                                   batch_size=None, mpi_pool=None):
    r""" Compute :math:`-\sum_{i=0}^m \nabla_{\bf a}f[{\bf a}](x_i) = -\sum_{i=0}^m \nabla_{\bf a} \left(\log\pi\circ T_k[{\bf a}](x_i) + \log\partial_{x_k}T_k[{\bf a}](x_i)\right)`

    Args:
      f (ProductDistributionParametricPullbackComponentFunction): function :math:`f`
      params (dict): parameters for function :math:`f`
      cache (dict): cached values
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``f``

    Returns:
      (:class:`float<float>`) -- value
    """
    reduce_obj = ExpectationReduce()
    if batch_size is None:
        scatter_tuple = (['x'], [x])
        reduce_tuple = (['w'], [w])
        dmem_key_in_list = ['params', 'cache']
        dmem_arg_in_list = ['params', 'cache']
        dmem_val_in_list = [params, cache]
        out = - mpi_map("grad_a", scatter_tuple=scatter_tuple,
                        dmem_key_in_list=dmem_key_in_list,
                        dmem_arg_in_list=dmem_arg_in_list,
                        dmem_val_in_list=dmem_val_in_list,
                        obj=f, reduce_obj=reduce_obj,
                        reduce_tuple=reduce_tuple,
                        mpi_pool=mpi_pool)[0, :]
    else:
        out = 0.
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
            x_in = [xs[idxs_slice, :] for xs, idxs_slice in zip(x_list, idxs_slice_list)]
            w_in = [ws[idxs_slice] for ws, idxs_slice in zip(w_list, idxs_slice_list)]
            # Evaluate
            scatter_tuple = (['x', 'idxs_slice'], [x_in, idxs_slice_list])
            reduce_tuple = (['w'], [w_in])
            dmem_key_in_list = ['params', 'cache']
            dmem_arg_in_list = ['params', 'cache']
            dmem_val_in_list = [params, cache]
            out += - mpi_map("grad_a", scatter_tuple=scatter_tuple,
                             dmem_key_in_list=dmem_key_in_list,
                             dmem_arg_in_list=dmem_arg_in_list,
                             dmem_val_in_list=dmem_val_in_list,
                             obj=d2, reduce_obj=reduce_obj,
                             reduce_tuple=reduce_tuple,
                             mpi_pool=mpi_pool, splitted=True)[0, :]
    return out


def hess_a_kl_divergence_component(f, params=None, cache=None,
                                   x=None, w=None,
                                   batch_size=None, mpi_pool=None):
    r""" Compute :math:`-\sum_{i=0}^m \nabla^2_{\bf a}f[{\bf a}](x_i) = -\sum_{i=0}^m \nabla^2_{\bf a} \left(\log\pi\circ T_k[{\bf a}](x_i) + \log\partial_{x_k}T_k[{\bf a}](x_i)\right)`

    Args:
      f (ProductDistributionParametricPullbackComponentFunction): function :math:`f`
      params (dict): parameters for function :math:`f`
      cache (dict): cached values
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``f``

    Returns:
      (:class:`float<float>`) -- value
    """
    reduce_obj = ExpectationReduce()
    if batch_size is None:
        scatter_tuple = (['x'], [x])
        reduce_tuple = (['w'], [w])
        dmem_key_in_list = ['params', 'cache']
        dmem_arg_in_list = ['params', 'cache']
        dmem_val_in_list = [params, cache]
        out = - mpi_map("hess_a", scatter_tuple=scatter_tuple,
                        dmem_key_in_list=dmem_key_in_list,
                        dmem_arg_in_list=dmem_arg_in_list,
                        dmem_val_in_list=dmem_val_in_list,
                        obj=f, reduce_obj=reduce_obj,
                        reduce_tuple=reduce_tuple,
                        mpi_pool=mpi_pool)[0, :, :]
    else:
        out = 0.
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
            x_in = [xs[idxs_slice, :] for xs, idxs_slice in zip(x_list, idxs_slice_list)]
            w_in = [ws[idxs_slice] for ws, idxs_slice in zip(w_list, idxs_slice_list)]
            # Evaluate
            scatter_tuple = (['x', 'idxs_slice'], [x_in, idxs_slice_list])
            reduce_tuple = (['w'], [w_in])
            dmem_key_in_list = ['params', 'cache']
            dmem_arg_in_list = ['params', 'cache']
            dmem_val_in_list = [params, cache]
            out += - mpi_map("hess_a", scatter_tuple=scatter_tuple,
                             dmem_key_in_list=dmem_key_in_list,
                             dmem_arg_in_list=dmem_arg_in_list,
                             dmem_val_in_list=dmem_val_in_list,
                             obj=d2, reduce_obj=reduce_obj,
                             reduce_tuple=reduce_tuple,
                             mpi_pool=mpi_pool, splitted=True)[:, 0, :, :]
    return out


def grad_t_kl_divergence(
        x,
        d1: Distribution,
        d2: PullBackTransportMapDistribution,
        params1=None, params2=None,
        cache1=None, cache2=None, grad_x_tm=None,
        batch_size=None,
        # mpi_pool_tuple=(None,None)
):
    r""" Compute :math:`\nabla_T \mathcal{D}_{KL}(\pi_1, \pi_2(T))`.

    This corresponds to:

    .. math:

       \nabla_T \mathcal{D}_{KL}(\pi_1, \pi_2(T)) = (\nabla_x T)^{-\top} \left[ \nabla_x \log \frac{\pi_1}{\pi_2(T)} \right]

    Args:
      d1 (Distribution): distribution :math:`\pi_1`
      d2 (PullBackTransportMapDistribution): distribution :math:`\pi_2`
      params1 (dict): parameters for distribution :math:`\pi_1`
      params2 (dict): parameters for distribution :math:`\pi_2`
      cache1 (dict): cache for distribution :math:`\pi_1`
      cache2 (dict): cache for distribution :math:`\pi_2`
      grad_x_tm: optional argument passed if :math:`\nabla_x T(x)` has been already computed
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      # mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
      #   pool of processes to be used for the evaluation of ``d1`` and ``d2``

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    tm = d2.transport_map
    bsize = batch_size if batch_size else x.shape[0]
    grad_t = np.zeros((x.shape))

    for n in range(0, x.shape[0], bsize):
        nend = min(x.shape[0], n + bsize)
        xx = x[n:nend, :]
        if grad_x_tm is not None:
            gx_tm = grad_x_tm[n:nend, :, :]
        else:
            gx_tm = tm.grad_x(xx)

        gx_lpdf_d1 = d1.grad_x_log_pdf(
            xx, idxs_slice=slice(n, nend), cache=cache1
        )

        gx_lpdf_d2 = d2.grad_x_log_pdf(
            xx, idxs_slice=slice(n, nend), cache=cache2
        )

        grad_t[n:nend, :] = gx_lpdf_d1 - gx_lpdf_d2

        for ii, i in enumerate(range(n, nend)):
            grad_t[i, :] = scila.solve_triangular(
                gx_tm[ii, :, :], grad_t[i, :], lower=True, trans='T')

    return grad_t

    # if not cache1:
    #     if mpi_pool_tuple[0]:
    #         cache1 = [None] * mpi_pool_tuple[0].nprocs
    #     else:
    #         cache1 = None
    # mpi_scatter_dmem(cache1=cache1, mpi_pool=mpi_pool_tuple[0])

    # if not cache2:
    #     if mpi_pool_tuple[1]:
    #         cache2 = [None] * mpi_pool_tuple[1].nprocs
    #     else:
    #         cache2 = None
    # mpi_scatter_dmem(cache2=cache2, mpi_pool=mpi_pool_tuple[1])

    # for n in range(0, x.shape[0], bsize):
    #     nend = min(x.shape[0], n+bsize)
    #     scatter_tuple = (['x'], [ x[n:nend,:] ])

    #     if grad_x_tm is None:
    #         gx_tm = mpi_map(
    #             "grad_x", obj=tm,
    #             scatter_tuple=scatter_tuple,
    #             mpi_pool=mpi_pool_tuple[1]
    #         )
    #     else:
    #         gx_tm = grad_x_tm[n:nend,:,:]

    #     gx_lpdf_d1 = mpi_map(
    #         "grad_x_log_pdf", obj=d1,
    #         scatter_tuple=scatter_tuple,
    #         dmem_key_in_list=['cache1'],
    #         dmem_arg_in_list=['cache'],
    #         dmem_val_in_list=cache1,
    #         mpi_pool=mpi_pool_tuple[0]
    #     )

    #     gx_lpdf_d2 = mpi_map(
    #         "grad_x_log_pdf", obj=d2,
    #         scatter_tuple=scatter_tuple,
    #         dmem_key_in_list=['cache2'],
    #         dmem_arg_in_list=['cache'],
    #         dmem_val_in_list=cache2,
    #         mpi_pool=mpi_pool_tuple[1]
    #     )

    #     grad_t[n:nend,:] = gx_lpdf_d1 - gx_lpdf_d2

    #     for ii, i in enumerate(range(n,nend)):
    #         grad_t[i,:] = scila.solve_triangular(
    #             gx_tm[ii,:,:], grad_t[ii,:], lower=True, trans='T')

    # return grad_t


def grad_x_grad_t_kl_divergence(
        x,
        d1,
        d2: PullBackTransportMapDistribution,
        params1=None, params2=None, grad_x_tm=None, grad_t=None,
        batch_size=None, mpi_pool_tuple=(None, None)):
    r""" Compute :math:`\nabla_x \nabla_T \mathcal{D}_{KL}(\pi_1, \pi_2(T))`.

    This corresponds to:

    .. math:

       \partial_{x_i} \nabla_T \mathcal{D}_{KL}(\pi_1, \pi_2(T)) =
       (\nabla_x T)^{-\top} \left[
         \partial_{x_i} \nabla_x \log \frac{\pi_1}{\pi_2(T)} -
         \left(\partial_{x_i} (\nabla_x T)^\top\right)
           \left(\nabla_T \mathcal{D}_{KL}(\pi_1, \pi_2(T))\right) \right]

    Args:
      d1 (Distribution): distribution :math:`\pi_1`
      d2 (PullBackTransportMapDistribution): distribution :math:`\pi_2`
      params1 (dict): parameters for distribution :math:`\pi_1`
      params2 (dict): parameters for distribution :math:`\pi_2`
      grad_x_tm: optional argument passed if :math:`\nabla_x T(x)` has been already computed
      grad_t: optional argument passed if the first variation has been already computed
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``d1`` and ``d2``

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    # Note: this is a naive implementation. We should be able to reuse
    # T.grad_x in pbdistribution.grad_x_log_pdf and implement parallelization
    dim = d2.dim
    tm = d2.transport_map
    scatter_tuple = (['x'], [x])
    if grad_x_tm is None:
        grad_x_tm = mpi_map("grad_x", obj=tm, scatter_tuple=scatter_tuple,
                            mpi_pool=mpi_pool_tuple[1])

    if grad_t is None:
        grad_t = grad_t_kl_divergence(
            x, d1, d2, params1=params1, params2=params2, grad_x_tm=grad_x_tm,
            batch_size=batch_size, mpi_pool_tuple=mpi_pool_tuple)

    out = mpi_map("hess_x_log_pdf", obj=d1, scatter_tuple=scatter_tuple,
                  mpi_pool=mpi_pool_tuple[0]) - \
          mpi_map("hess_x_log_pdf", obj=d2, scatter_tuple=scatter_tuple,
                  mpi_pool=mpi_pool_tuple[1])

    for k, (a, avar) in enumerate(zip(tm.approx_list, tm.active_vars)):
        # numpy advanced indexing
        nvar = len(avar)
        rr, cc = np.meshgrid(avar, avar)
        rr = list(rr.flatten())
        cc = list(cc.flatten())
        idxs = (slice(None), rr, cc)
        out[idxs] -= (a.hess_x(x[:, avar])[:, 0, :, :] * grad_t[:, k][:, nax, nax]).reshape((x.shape[0], nvar ** 2))

    for i in range(x.shape[0]):
        out[i, :, :] = scila.solve_triangular(
            grad_x_tm[i, :, :], out[i, :, :], lower=True, trans='T')

    return out


def tuple_grad_x_grad_t_kl_divergence(
        x,
        d1,
        d2: PullBackTransportMapDistribution,
        params1=None, params2=None, grad_x_tm=None,
        batch_size=None, mpi_pool_tuple=(None, None)):
    r""" Compute :math:`\nabla_x \nabla_T \mathcal{D}_{KL}(\pi_1, \pi_2(T))`.

    This corresponds to:

    .. math:

       \partial_{x_i} \nabla_T \mathcal{D}_{KL}(\pi_1, \pi_2(T)) =
       (\nabla_x T)^{-\top} \left[
         \partial_{x_i} \nabla_x \log \frac{\pi_1}{\pi_2(T)} -
         \left(\partial_{x_i} (\nabla_x T)^\top\right)
           \left(\nabla_T \mathcal{D}_{KL}(\pi_1, \pi_2(T))\right) \right]

    Args:
      d1 (Distribution): distribution :math:`\pi_1`
      d2 (PullBackTransportMapDistribution): distribution :math:`\pi_2`
      params1 (dict): parameters for distribution :math:`\pi_1`
      params2 (dict): parameters for distribution :math:`\pi_2`
      grad_x_tm: optional argument passed if :math:`\nabla_x T(x)` has been already computed
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``d1`` and ``d2``

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    # Note: this is a naive implementation. We should be able to reuse
    # T.grad_x in pbdistribution.grad_x_log_pdf and implement parallelization
    dim = d2.dim
    tm = d2.transport_map
    scatter_tuple = (['x'], [x])
    if grad_x_tm is None:
        grad_x_tm = mpi_map("grad_x", obj=tm, scatter_tuple=scatter_tuple,
                            mpi_pool=mpi_pool_tuple[1])
    grad_t = grad_t_kl_divergence(
        x, d1, d2, params1=params1, params2=params2, grad_x_tm=grad_x_tm,
        batch_size=batch_size, mpi_pool_tuple=mpi_pool_tuple)
    grad_x_grad_t = grad_x_grad_t_kl_divergence(
        x, d1, d2, params1=params1, params2=params2, grad_x_tm=grad_x_tm,
        grad_t=grad_t, batch_size=batch_size, mpi_pool_tuple=mpi_pool_tuple)
    return grad_t, grad_x_grad_t
