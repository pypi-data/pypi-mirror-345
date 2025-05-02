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

from ..Maps import TransportMap
from .DistributionBase import Distribution

__all__ = [
    'TransportMapDistribution',
]


class TransportMapDistribution(Distribution):
    r""" Abstract class for distributions of the transport map type (:math:`T^\sharp \pi` or :math:`T_\sharp \pi`)

    .. seealso:: :class:`PushForwardTransportMapDistribution` and :class:`PullBackTransportMapDistribution`.
    """    
    def __init__(
            self,
            transport_map: TransportMap,
            base_distribution: Distribution
    ):
        r"""
        Args:
          transport_map (:class:`TransportMap<TransportMaps.Maps.TransportMap>`): transport map :math:`T`
          base_distribution (:class:`Distribution`): distribution :math:`\pi`
        """
        if transport_map.dim != base_distribution.dim:
            raise ValueError(
                "The transport_map and the base_distribution should have " +
                "the same dimension"
            )
        super(TransportMapDistribution,self).__init__(dim=transport_map.dim)
        self.transport_map = transport_map
        self.base_distribution = base_distribution

    def get_ncalls_tree(self, indent=""):
        out = super(TransportMapDistribution, self).get_ncalls_tree(indent)
        out += self.transport_map.get_ncalls_tree(indent + "  ")
        out += self.base_distribution.get_ncalls_tree(indent + '  ')
        return out

    def get_nevals_tree(self, indent=""):
        out = super(TransportMapDistribution, self).get_nevals_tree(indent)
        out += self.transport_map.get_nevals_tree(indent + "  ")
        out += self.base_distribution.get_nevals_tree(indent + '  ')
        return out

    def get_teval_tree(self, indent=""):
        out = super(TransportMapDistribution, self).get_teval_tree(indent)
        out += self.transport_map.get_teval_tree(indent + "  ")
        out += self.base_distribution.get_teval_tree(indent + '  ')
        return out

    def update_ncalls_tree(self, obj):
        super(TransportMapDistribution, self).update_ncalls_tree(obj)
        self.transport_map.update_ncalls_tree(obj.transport_map)
        self.base_distribution.update_ncalls_tree(obj.base_distribution)

    def update_nevals_tree(self, obj):
        super(TransportMapDistribution, self).update_nevals_tree(obj)
        self.transport_map.update_nevals_tree(obj.transport_map)
        self.base_distribution.update_nevals_tree(obj.base_distribution)

    def update_teval_tree(self, obj):
        super(TransportMapDistribution, self).update_teval_tree(obj)
        self.transport_map.update_teval_tree(obj.transport_map)
        self.base_distribution.update_teval_tree(obj.base_distribution)

    def reset_counters(self):
        super(TransportMapDistribution, self).reset_counters()
        self.transport_map.reset_counters()
        self.base_distribution.reset_counters()

    def rvs(self, m, mpi_pool=None, batch_size=None):
        r""" Generate :math:`m` samples from the distribution.

        Args:
          m (int): number of samples to generate
          mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processes
          batch_size (int): whether to generate samples in batches

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- :math:`m`
             :math:`d`-dimensional samples
        """
        x, w = self.quadrature(0, m, mpi_pool=mpi_pool, batch_size=batch_size)
        return x

    def quadrature(self, qtype, qparams, mass=1.,
                   mpi_pool=None, **kwargs):
        r""" Generate quadrature points and weights.

        Args:
          qtype (int): quadrature type number. The different types are defined in
            the associated sub-classes.
          qparams (object): inputs necessary to the generation of the selected
            quadrature
          mass (float): total mass of the quadrature (1 for probability measures)
          mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processes

        Return:
          (:class:`tuple` (:class:`ndarray<numpy.ndarray>` [:math:`m,d`],
            :class:`ndarray<numpy.ndarray>` [:math:`m`])) -- list of quadrature
            points and weights
        """
        if qtype in [4]:
            return self.adaptive_quadrature(
                qtype, qparams, mass=mass, mpi_pool=mpi_pool, **kwargs)
        else:
            (x, w) = self.base_distribution.quadrature(
                qtype, qparams, mass=mass, mpi_pool=mpi_pool,**kwargs)
            x = self.map_samples_base_to_target(x, mpi_pool=mpi_pool)
            return (x, w)

    def adaptive_quadrature(self, qtype, qparams, mass=1., mpi_pool=None, **kwargs):
        if qtype in [4]:
            if 'f' not in kwargs:
                raise ValueError(
                    "This kind of adaptive quadrature requires the argument " + \
                    "integrand function to be provided as the argument f.")
            f = kwargs['f']
            kwargs['f'] = self.map_function_base_to_target(kwargs['f'])
            x, w = self.base_distribution.quadrature(
                qtype, qparams, mass=mass, mpi_pool=mpi_pool, **kwargs)
            kwargs['f'] = f
        else:
            raise ValueError("Quadrature type not recognized")
        x = self.map_samples_base_to_target(x, mpi_pool=mpi_pool)
        return (x, w)
            
    def map_samples_base_to_target(self, x, mpi_pool=None):
        r""" [Abstract] Map input samples (assumed to be from :math:`\pi`) to the corresponding samples from :math:`T^\sharp \pi` or :math:`T_\sharp \pi`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): input samples
          mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processes

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- corresponding samples
        """
        raise NotImplementedError("Abstract method. Implement in sub-class.")

    def map_samples_target_to_base(self, x, mpi_pool=None):
        r""" [Abstract] Map input samples (assumed to be from :math:`T^\sharp \pi` or :math:`T_\sharp \pi`) to the corresponding samples from :math:`\pi`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): input samples
          mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processes

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- corresponding samples
        """
        raise NotImplementedError("Abstract method. Implement in sub-class.")

    @staticmethod
    def _evaluate_log_transport(lpdf, ldgx):
        return lpdf + ldgx

    @staticmethod
    def _evaluate_grad_x_log_transport(gxlpdf, gx, gxldgx):
        return np.einsum('...i,...ij->...j', gxlpdf, gx) + gxldgx