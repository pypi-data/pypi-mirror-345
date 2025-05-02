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

from TransportMaps.External import DARKSPARK_SUPPORT
from TransportMaps import mpi_map, logger

if DARKSPARK_SUPPORT:
    from DARKSparK.multiDimensionalFunction import MultiDimensionalFunction,Reals64

__all__ = ['compute_vals_variance_approx_kl', 'variance_approx_kl']

def compute_vals_variance_approx_kl( d1, d2, params1=None, params2=None, x=None,
                                     mpi_pool_tuple=(None,None), import_set=set() ):
    r""" Compute values necessary for the evaluation of the variance diagnostic :func:`variance_approx_kl`

    Returns:
      (:class:`tuple` [2] :class:`ndarray<numpy.ndarray>` [:math:`m`]) --
        computed values of :math:`\log\pi_1` and :math:`\log\pi_2`

    .. seealso:: :func:`variance_approx_kl`
    """
    # d1
    scatter_tuple = (['x'], [x])
    vals_d1 = mpi_map("log_pdf", obj=d1, scatter_tuple=scatter_tuple,
                       mpi_pool=mpi_pool_tuple[0])
    # d2
    vals_d2 = mpi_map("log_pdf", obj=d2, scatter_tuple=scatter_tuple,
                       mpi_pool=mpi_pool_tuple[1])
    return (vals_d1, vals_d2)

def difference_and_squared_difference(vals_d1,vals_d2):
    return [(vals_d1 - vals_d2)**2.,vals_d1 - vals_d2]

def difference_and_squared_difference_call(d1, d2, params1=None, params2=None,
                                           mpi_pool_tuple=(None,None), import_set=set()): 
    return lambda x: difference_and_squared_difference(*compute_vals_variance_approx_kl(
        d1, d2, params1, params2, x=x,\
        mpi_pool_tuple=mpi_pool_tuple, import_set=import_set))


def variance_approx_kl( d1, d2, params1=None, params2=None, vals_d1=None, vals_d2=None,
                        qtype=None, qparams=None, x=None, w=None,
                        mpi_pool_tuple=(None,None), import_set=set() ):
    r""" Variance diagnositc

    Statistical analysis of the variance diagnostic

    .. math::

       \mathcal{D}_{KL}(\pi_1 \Vert \pi_2) \approx \frac{1}{2} \mathbb{V}_{\pi_1} \left( \log \frac{\pi_1}{\pi_2}\right)

    Args:
      d1 (Distribution): distribution :math:`\pi_1`
      d2 (Distribution): distribution :math:`\pi_2`
      params1 (dict): parameters for distribution :math:`\pi_1`
      params2 (dict): parameters for distribution :math:`\pi_2`
      vals_d1 (:class:`ndarray<numpy.ndarray>` [:math:`m`]):
        computed values of :math:`\log\pi_1`
      vals_d2 (:class:`ndarray<numpy.ndarray>` [:math:`m`]):
        computed values of:math:`\log\pi_2`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi_1}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``d1`` and ``d2``
      import_set (set): list of couples ``(module_name,as_field)`` to be imported
        as ``import module_name as as_field`` (for MPI purposes)

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    if vals_d1 is None or vals_d2 is None:
        if x is None and w is None:
            if qtype in [4]:
                if not DARKSPARK_SUPPORT:
                    raise RuntimeError("Sparse Grid is not supported (install DARKSparK).")
                logger.warning("Using MC for variance diagnostic even if qtype==4.")
                (x,w) = d1.quadrature(0, 10000, mpi_pool=mpi_pool_tuple[0])
                
                # # print("This choice of abs_tol is ad-hoc for the adaptivity. " + \
                #     #       "It should be changed.")
                # # qparams = {'abs_tol': qparams['eps_bull']/5.0}
                # qparams = {'abs_tol': qparams['eps_bull']/5.0}
                # x, w = d1.quadrature(
                #     qtype, 
                #     qparams, 
                #     mpi_pool=mpi_pool_tuple[0], 
                #     f=MultiDimensionalFunction(
                #         difference_and_squared_difference_call(d1, d2, params1, params2,\
                #                                                mpi_pool_tuple,import_set),
                #         Reals64(d2.dim),
                #         Reals64(2)))
                # integrals = qparams['adapter'].vector_valued_integrals[-1]
                # var = 0.5*(integrals[0]-integrals[1]**2.0)

                # if True:
                #     import matplotlib.pyplot as plt

                #     # integrals = []
                #     # for i in range(1,x.shape[0]*2,max(1,round(x.shape[0]/100.))):
                #     #   #need a way to check if laplace approx 
                #     #     x_mc,w_mc = d1.quadrature(qtype=0, qparams=i,mpi_pool=mpi_pool_tuple[0])
                #     #     vals_d1, vals_d2 = compute_vals_variance_approx_kl(
                #     #     d1, d2, params1, params2, x=x_mc,
                #     #     mpi_pool_tuple=mpi_pool_tuple, import_set=import_set)
                #     #     vals = vals_d1 - vals_d2
                #     #     expect = np.dot( vals, w_mc )
                #     #     integrals.append(0.5 *np.dot( (vals - expect)**2., w_mc ))
                #     # plt.plot(np.arange(1,x.shape[0]*2,max(1,round(x.shape[0]/100.))),
                #     #          integrals,label="MC, by # pts",c='orange')
                #     plt.semilogy(qparams['adapter'].num_grid_pts_history,
                #                  [0.5*(integral[0]-integral[1]**2.0)
                #                   for integral in qparams['adapter'].vector_valued_integrals],
                #                  label="SG, by # pts",c='blue')
                #     plt.xlabel("# samples")
                #     plt.ylabel("integral")
                #     plt.title("Variance Diagnostic: 1/2 Var_{rho}(log (rho / pi))")
                #     plt.legend()
                #     plt.show()
                # return var
            else:
                (x,w) = d1.quadrature(qtype, qparams, mpi_pool=mpi_pool_tuple[0])
        elif x is None or w is None:
            raise ValueError("Provide quadrature points and weights or quadrature " + \
                             "type and parameters")

        vals_d1, vals_d2 = compute_vals_variance_approx_kl(
            d1, d2, params1, params2, x=x,
            mpi_pool_tuple=mpi_pool_tuple, import_set=import_set)

    vals = vals_d1 - vals_d2
    expect = np.dot( vals, w )
    var = .5 * np.dot( (vals - expect)**2., w )
    return var
