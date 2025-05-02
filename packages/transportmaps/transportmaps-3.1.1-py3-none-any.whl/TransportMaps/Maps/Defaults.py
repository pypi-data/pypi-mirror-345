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
from typing import List

import SpectralToolbox.Spectral1D as S1D
from semilattices import CoordinateSemilattice

from .Functionals.LinearSpanTensorizedParametricFunctionalBase import \
    LinearSpanSemilattice, LinearSpanTensorizedParametricFunctional
from .Functionals.IntegratedExponentialParametricMonotoneFunctionalBase import \
    IntegratedExponentialParametricMonotoneFunctional
from .Functionals.IntegratedSquaredParametricMonotoneFunctionalBase import \
    IntegratedSquaredParametricMonotoneFunctional
from .Functionals.PointwiseMonotoneLinearSpanTensorizedParametricFunctionalBase import \
    PointwiseMonotoneLinearSpanTensorizedParametricFunctional

from .LinearSpanParametricTriangularComponentwiseMapBase import *
from .NonMonotoneLinearSpanParametricTriangularComponentwiseTransportMapBase import *
from .IntegratedSquaredParametricTriangularComponentwiseTransportMapBase import *
from .IntegratedExponentialParametricTriangularComponentwiseTransportMapBase import *

__all__ = [
    'assemble_IsotropicIntegratedExponentialTriangularTransportMap',
    'assemble_IsotropicIntegratedExponentialDiagonalTransportMap',
    'assemble_IsotropicIntegratedSquaredTriangularTransportMap',
    'assemble_IsotropicIntegratedSquaredDiagonalTransportMap',
    'assemble_IsotropicLinearSpanTriangularTransportMap',
    'assemble_IsotropicLinearSpanTriangularMap',
    'assemble_LinearSpanTriangularMap'
]


def assemble_IsotropicIntegratedExponentialTriangularTransportMap(
        dim,
        order,
        span='total',
        SemilatticeConstructor=LinearSpanSemilattice,
        active_vars=None,
        btype='poly',
        common_basis_flag=True
):
    r""" Generate a triangular transport map with default settings.

    Args:
      dim (int): dimension :math:`d` of the map
      order (int): isotropic order of the map
      span (str): 'full' for full order approximations, 'total' for total order
        approximations. If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the approximation type fore each component
        :math:`T^{(k)}`.
      SemilatticeConstructor (:class:`class`): constructor for the semilattices
        of each function approximation. It must be a sub-class of 
        :class:`LinearSpanSemilattice`.
      active_vars (list): list of :math:`d` lists containing the row sparsity
        pattern of the transport, i.e. the active variables for each component.
        Default ``None`` will generate a full triangular map.
      btype (string): ``poly`` uses Hermite polynomials, ``fun`` uses Hermite functions,
        ``rbf`` uses radial basis functions.
        If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the basis type fore each component
        :math:`T^{(k)}`.
      common_basis_flag (bool): use acceleration provided by common basis among the
        components (``span`` and ``btype`` must be a string or a list with all equal
        elements).

    Returns:
      (:class:`IntegratedExponentialTriangularTransportMap<IntegratedExponentialTriangularTransportMap>`)
      -- the constructed transport map
    """
    # Initialize the list of components
    approx_list = []
    # Initialize the list of active variables
    if active_vars is None:
        active_vars = [ list(range(i+1)) for i in range(dim) ]
    else:
        if len(active_vars) != dim:
            raise ValueError("List of active variables must be dim long.")
        for d, avars in enumerate(active_vars):
            if sorted(avars) != avars:
                raise ValueError("List of active components must be provided in " + \
                                 "sorted order.")
            if avars[-1] != d:
                raise ValueError("List of active components must include at least" + \
                                 "the diagonal term.")
    # Initialize the span type
    if isinstance(span,str):
        span_list = [span] * dim
    else:
        if len(span) != dim:
            raise ValueError("List of span types must be dim long.")
        else:
            span_list = span
    # Initialize the basis type
    if isinstance(btype, str):
        btype_list = [btype] * dim
    else:
        if len(btype) != dim:
            raise AttributeError("List of basis types must be dim long.")
        else:
            btype_list = btype
    # Check whether it is possible to use common basis
    common_basis_flag = common_basis_flag and all(x==span_list[0] for x in span_list) and \
                        all(x==btype_list[0] for x in btype_list)

    full_c_basis_list = []
    full_h_basis_list = []
    for d, btype in enumerate(btype_list):
        if btype == 'poly':
            full_c_basis_list.append( [S1D.HermiteProbabilistsPolynomial()] * (d+1) )
            full_h_basis_list.append(
                [S1D.HermiteProbabilistsPolynomial()] * d + \
                [S1D.ConstantExtendedHermiteProbabilistsFunction()] )
        elif btype == 'fun':
            full_c_basis_list.append(
                [S1D.LinearExtendedHermiteProbabilistsFunction()] * (d+1) )
            full_h_basis_list.append(
                [S1D.LinearExtendedHermiteProbabilistsFunction()] * d + \
                [S1D.ConstantExtendedHermiteProbabilistsFunction()] )
        elif btype == 'rbf':
            full_c_basis_list.append(
                [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(order,0.9)]*(d+1))
            full_h_basis_list.append(
                [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(order,0.9)] * d + \
                [S1D.ConstantExtendedHermiteProbabilistsRadialBasisFunction(order, 0.9)] )
        else:
            raise ValueError("Input btype is invalid.")
    
    # Prepare basis in case common_basis
    if common_basis_flag:
        if btype_list[0] == 'poly':
            c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(dim)]
            h_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(dim-1)] + \
                           [S1D.ConstantExtendedHermiteProbabilistsFunction()]
        elif btype_list[0] == 'fun':
            c_basis_list = [S1D.LinearExtendedHermiteProbabilistsFunction()] * (dim)
            h_basis_list = [S1D.LinearExtendedHermiteProbabilistsFunction()] * (dim-1) + \
                           [S1D.ConstantExtendedHermiteProbabilistsFunction()]
        elif btype_list[0] == 'rbf':
            if span_list[0] != 'full':
                raise ValueError("The basis span must be 'full' for basis type 'rbf'")
            c_basis_list = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                order, 0.9) for i in range(dim)]
            h_basis_list = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                order, 0.9) for i in range(dim-1)] + \
                [S1D.ConstantExtendedHermiteProbabilistsRadialBasisFunction(order, 0.9)]

    # Instantiate the components
    for d, (avars, span, btype) in enumerate(zip(active_vars, span_list, btype_list)):
        c_orders_list = [order]*(len(avars)-1)+[0]
        if common_basis_flag:
            c_basis_comp = [c_basis_list[a] for a in avars]
            h_basis_comp = [h_basis_list[a] for a in avars]
        else:
            c_basis_comp = [full_c_basis_list[d][a] for a in avars]
            h_basis_comp = [full_h_basis_list[d][a] for a in avars]
                
        c_approx = LinearSpanTensorizedParametricFunctional(
            c_basis_comp,
            SemilatticeConstructor=SemilatticeConstructor,
            spantype=span,
            order_list=c_orders_list,
            full_basis_list=full_c_basis_list[d])
        h_orders_list = [order-1]*len(avars)
        h_approx = LinearSpanTensorizedParametricFunctional(
            h_basis_comp,
            SemilatticeConstructor=SemilatticeConstructor,
            spantype=span,
            order_list=h_orders_list,
            full_basis_list=full_h_basis_list[d])
        approx = IntegratedExponentialParametricMonotoneFunctional(c_approx, h_approx)
        approx_list.append( approx )

    # Instantiate the map
    if common_basis_flag:    
        tm_approx = CommonBasisIntegratedExponentialParametricTriangularComponentwiseTransportMap(
            active_vars = active_vars,
            approx_list = approx_list
        )
    else:
        tm_approx = IntegratedExponentialParametricTriangularComponentwiseTransportMap(
            active_vars = active_vars,
            approx_list = approx_list
        )
    return tm_approx

def assemble_IsotropicIntegratedExponentialDiagonalTransportMap(
        dim,
        order,
        *args,
        **kwargs):
    r""" Generate a diagonal transport map with default settings.

    Args:
      dim (int): dimension :math:`d` of the map
      order (int): isotropic order of the map

    Returns:
      (:class:`IntegratedExponentialTriangularTransportMap<IntegratedExponentialTriangularTransportMap>`)
      -- the constructed transport map
    """
    active_vars = [[d] for d in range(dim)]
    kwargs['common_basis_flag'] = False
    kwargs['active_vars'] = active_vars
    return assemble_IsotropicIntegratedExponentialTriangularTransportMap(
        dim, order, *args, **kwargs)

def assemble_IsotropicIntegratedSquaredTriangularTransportMap(
        dim,
        order,
        span='total',
        SemilatticeConstructor=LinearSpanSemilattice,
        active_vars=None,
        btype='poly',
        common_basis_flag=False):
    r""" Generate a triangular transport map with default settings.

    Args:
      dim (int): dimension :math:`d` of the map
      order (int): isotropic order of the map
      span (str): 'full' for full order approximations, 'total' for total order
        approximations. If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the approximation type fore each component
        :math:`T^{(k)}`.
      SemilatticeConstructor (:class:`class`): constructor for the semilattices
        of each function approximation. It must be a sub-class of 
        :class:`LinearSpanSemilattice`.
      active_vars (list): list of :math:`d` lists containing the row sparsity
        pattern of the transport, i.e. the active variables for each component.
        Default ``None`` will generate a full triangular map.
      btype (string): ``poly`` uses Hermite polynomials, ``fun`` uses Hermite functions,
        ``rbf`` uses radial basis functions.
        If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the basis type fore each component
        :math:`T^{(k)}`.
      common_basis_flag (bool): use acceleration provided by common basis among the
        components (``span`` and ``btype`` must be a string or a list with all equal
        elements).

    Returns:
      (:class:`IntegratedSquaredTriangularTransportMap<IntegratedSquaredTriangularTransportMap>`)
      -- the constructed transport map
    """
    # Initialize the list of components
    approx_list = []
    # Initialize the list of active variables
    if active_vars is None:
        active_vars = [ list(range(i+1)) for i in range(dim) ]
    else:
        if len(active_vars) != dim:
            raise ValueError("List of active variables must be dim long.")
        for d, avars in enumerate(active_vars):
            if sorted(avars) != avars:
                raise ValueError("List of active components must be provided in " + \
                                 "sorted order.")
            if avars[-1] != d:
                raise ValueError("List of active components must include at least" + \
                                 "the diagonal term.")
    # Initialize the span type
    if isinstance(span,str):
        span_list = [span] * dim
    else:
        if len(span) != dim:
            raise ValueError("List of span types must be dim long.")
        else:
            span_list = span
    # Initialize the basis type
    if isinstance(btype, str):
        btype_list = [btype] * dim
    else:
        if len(btype) != dim:
            raise AttributeError("List of basis types must be dim long.")
        else:
            btype_list = btype
    # Check whether it is possible to use common basis
    common_basis_flag = common_basis_flag and all(x==span_list[0] for x in span_list) and \
                        all(x==btype_list[0] for x in btype_list)

    full_c_basis_list = []
    full_h_basis_list = []
    for d, btype in enumerate(btype_list):
        if btype == 'poly':
            full_c_basis_list.append( [S1D.HermiteProbabilistsPolynomial()] * (d+1) )
            full_h_basis_list.append(
                [S1D.HermiteProbabilistsPolynomial()] * d + \
                [S1D.ConstantExtendedHermiteProbabilistsFunction()] )
        elif btype == 'fun':
            full_c_basis_list.append(
                [S1D.LinearExtendedHermiteProbabilistsFunction()] * (d+1) )
            full_h_basis_list.append(
                [S1D.LinearExtendedHermiteProbabilistsFunction()] * d + \
                [S1D.ConstantExtendedHermiteProbabilistsFunction()] )
        elif btype == 'rbf':
            full_c_basis_list.append(
                [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(order,0.9)]*(d+1))
            full_h_basis_list.append(
                [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(order,0.9)] * d + \
                [S1D.ConstantExtendedHermiteProbabilistsRadialBasisFunction(order, 0.9)] )
        else:
            raise ValueError("Input btype is invalid.")
    
    # Prepare basis in case common_basis
    if common_basis_flag:
        if btype_list[0] == 'poly':
            c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(dim)]
            h_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(dim-1)] + \
                           [S1D.ConstantExtendedHermiteProbabilistsFunction()]
        elif btype == 'fun':
            c_basis_list = [S1D.LinearExtendedHermiteProbabilistsFunction()] * dim
            h_basis_list = [S1D.LinearExtendedHermiteProbabilistsFunction()] * (dim-1) + \
                           [S1D.ConstantExtendedHermiteProbabilistsFunction()]
        elif btype_list[0] == 'rbf':
            if span[0] != 'full':
                raise ValueError("The basis span must be 'full' for basis type 'rbf'")
            c_basis_list = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                order, 0.9) for i in range(dim)]
            h_basis_list = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                order, 0.9) for i in range(dim-1)] + \
                [ S1D.ConstantExtendedHermiteProbabilistsRadialBasisFunction(
                    order, 0.9) ]

    # Instantiate the components
    for d, (avars, span, btype) in enumerate(zip(active_vars, span_list, btype_list)):
        c_orders_list = [order]*(len(avars)-1)+[0]
        if common_basis_flag:
            c_basis_comp = [c_basis_list[a] for a in avars]
            h_basis_comp = [h_basis_list[a] for a in avars]
        else:
            c_basis_comp = [full_c_basis_list[d][a] for a in avars]
            h_basis_comp = [full_h_basis_list[d][a] for a in avars]
                
        c_approx = LinearSpanTensorizedParametricFunctional(
            c_basis_comp,
            SemilatticeConstructor=SemilatticeConstructor,
            spantype=span,
            order_list=c_orders_list,
            full_basis_list=full_c_basis_list[d])
        h_orders_list = [order-1]*len(avars)
        h_approx = LinearSpanTensorizedParametricFunctional(
            h_basis_comp,
            SemilatticeConstructor=SemilatticeConstructor,
            spantype=span,
            order_list=h_orders_list,
            full_basis_list=full_h_basis_list[d])
        approx = IntegratedSquaredParametricMonotoneFunctional(c_approx, h_approx)
        approx_list.append( approx )

    # Instantiate the map
    if common_basis_flag:
        raise NotImplementedError(
            "The common basis construct of this type of map is not implemented yet. "
            "Use common_basis_flag=False."
        )
        # tm_approx = CommonBasisIntegratedSquaredParametricTriangularComponentwiseTransportMap(
        #     active_vars = active_vars,
        #     approx_list = approx_list
        # )
    else:
        tm_approx = IntegratedSquaredParametricTriangularComponentwiseTransportMap(
            active_vars = active_vars,
            approx_list = approx_list
        )
    return tm_approx

def assemble_IsotropicIntegratedSquaredDiagonalTransportMap(
        dim, order, *args, **kwargs):
    r""" Generate a diagonal transport map with default settings.

    Args:
      dim (int): dimension :math:`d` of the map
      order (int): isotropic order of the map

    Returns:
      (:class:`IntegratedSquaredTriangularTransportMap<IntegratedSquaredTriangularTransportMap>`)
      -- the constructed transport map
    """
    active_vars = [[d] for d in range(dim)]
    kwargs['common_basis_flag'] = False
    kwargs['active_vars'] = active_vars
    return assemble_IsotropicIntegratedSquaredTriangularTransportMap(
        dim, order, *args, **kwargs)
    
def assemble_IsotropicLinearSpanTriangularTransportMap(
        dim,
        order,
        span='total', 
        SemilatticeConstructor=LinearSpanSemilattice,
        active_vars=None,
        btype='poly',
        common_basis_flag=True):
    r""" Generate a triangular transport map with default settings.

    Args:
      dim (int): dimension of the map
      order (int): isotropic order of the map
      span (str): 'full' for full order approximations, 'total' for total order
        approximations. If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the approximation type fore each component
        :math:`T^{(k)}`.
      SemilatticeConstructor (:class:`class`): constructor for the semilattices
        of each function approximation. It must be a sub-class of 
        :class:`LinearSpanSemilattice`.
      active_vars (list): list of :math:`d` lists containing the row sparsity
        pattern of the transport, i.e. the active variables for each component.
        Default ``None`` will generate a full triangular map.
      btype (string): ``poly`` uses Hermite polynomials, ``fun`` uses Hermite functions,
        ``rbf`` uses radial basis functions.
        If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the basis type fore each component
        :math:`T^{(k)}`.
      common_basis_flag (bool): use acceleration provided by common basis among the
        components (``span`` and ``btype`` must be a string or a list with all equal
        elements).

    Returns:
      (:class:`LinearSpanTriangularTransportMap<LinearSpanTriangularTransportMap>`) -- the constructed transport map
    """
    return assemble_IsotropicLinearSpanTriangularMap(
        dim,
        order,
        span=span,
        SemilatticeConstructor=LinearSpanSemilattice,
        active_vars=active_vars,
        btype=btype,
        common_basis_flag=common_basis_flag,
        monotone=True)

def assemble_IsotropicLinearSpanTriangularMap(
        dim,
        order,
        span='total',
        SemilatticeConstructor=LinearSpanSemilattice,
        active_vars=None,
        btype='poly',
        common_basis_flag=True,
        monotone=False):
    r""" Generate a triangular transport map with default settings.

    Args:
      dim (int): dimension of the map
      order (int): isotropic order of the map
      span (str): 'full' for full order approximations, 'total' for total order
        approximations. If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the approximation type fore each component
        :math:`T^{(k)}`.
      SemilatticeConstructor (:class:`class`): constructor for the semilattices
        of each function approximation. It must be a sub-class of 
        :class:`LinearSpanSemilattice`.
      active_vars (list): list of :math:`d` lists containing the row sparsity
        pattern of the transport, i.e. the active variables for each component.
        Default ``None`` will generate a full triangular map.
      btype (string): ``poly`` uses Hermite polynomials, ``fun`` uses Hermite functions,
        ``rbf`` uses radial basis functions.
        If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the basis type fore each component
        :math:`T^{(k)}`.
      common_basis_flag (bool): use acceleration provided by common basis among the
        components (``span`` and ``btype`` must be a string or a list with all equal
        elements).

    Returns:
      (:class:`LinearSpanTriangularTransportMap<LinearSpanTriangularTransportMap>`) -- the constructed transport map
    """
    # Initialize the list of components
    approx_list = []
    # Initialize the list of active variables
    if active_vars is None:
        active_vars = [ list(range(i+1)) for i in range(dim) ]
    else:
        if len(active_vars) != dim:
            raise ValueError("List of active variables must be dim long.")
        for d, avars in enumerate(active_vars):
            if sorted(avars) != avars:
                raise ValueError("List of active components must be provided in " + \
                                 "sorted order.")
            if avars[-1] != d:
                raise ValueError("List of active components must include at least" + \
                                 "the diagonal term.")
    # Initialize the span type
    if isinstance(span,str):
        span_list = [span] * dim
    else:
        if len(span) != dim:
            raise ValueError("List of span types must be dim long.")
        else:
            span_list = span
    # Initialize the basis type
    if isinstance(btype, str):
        btype_list = [btype] * dim
    else:
        if len(btype) != dim:
            raise AttributeError("List of basis types must be dim long.")
        else:
            btype_list = btype
    # Check whether it is possible to use common basis
    common_basis_flag = common_basis_flag and all(x==span_list[0] for x in span_list) and \
                        all(x==btype_list[0] for x in btype_list)

    full_basis_list = []
    for d, btype in enumerate(btype_list):
        if btype == 'poly':
            full_basis_list.append( [S1D.HermiteProbabilistsPolynomial()] * (d+1) )
        elif btype == 'fun':
            full_basis_list.append(
                [S1D.LinearExtendedHermiteProbabilistsFunction()] * (d+1) )
        elif btype == 'rbf':
            full_basis_list.append(
                [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(order,0.9)]*(d+1))
        else:
            raise ValueError("Input btype is invalid.")
    
    # Prepare basis in case common_basis
    if common_basis_flag:
        if btype_list[0] == 'poly':
            basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(dim)]
        elif btype_list[0] == 'fun':
            basis_list = [S1D.LinearExtendedHermiteProbabilistsFunction()] * dim
        elif btype_list[0] == 'rbf':
            if span_list[0] != 'full':
                raise ValueError("The basis span must be 'full' for basis type 'rbf'")
            basis_list = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                order, 0.9) for i in range(dim)]
            
    # Instantiate the components
    for d, (avars, span, btype) in enumerate(zip(active_vars, span_list, btype_list)):
        orders_list = [order]*len(avars)
        if common_basis_flag:
            basis_comp = [basis_list[a] for a in avars]
        else:
            basis_comp = [full_basis_list[d][a] for a in avars]

        if monotone:
            approx = PointwiseMonotoneLinearSpanTensorizedParametricFunctional(
                basis_comp,
                SemilatticeConstructor=SemilatticeConstructor,
                spantype=span,
                order_list=orders_list,
                full_basis_list=full_basis_list[d])
        else:
            approx = LinearSpanTensorizedParametricFunctional(
                basis_comp,
                SemilatticeConstructor=SemilatticeConstructor,
                spantype=span,
                order_list=orders_list,
                full_basis_list=full_basis_list[d])
        approx_list.append( approx )

    # Instantiate the map
    if common_basis_flag:
        if monotone:
            tm_approx = NonMonotoneCommonBasisLinearSpanParametricTriangularComponentwiseTransportMap(
                active_vars = active_vars,
                approx_list = approx_list
            )
        else:
            tm_approx = CommonBasisLinearSpanParametricTriangularComponentwiseMap(
                active_vars = active_vars,
                approx_list = approx_list
            )
    else:
        if monotone:
            tm_approx = NonMonotoneLinearSpanParametricTriangularComponentwiseTransportMap(
                active_vars = active_vars,
                approx_list = approx_list
            )
        else:
            tm_approx = LinearSpanParametricTriangularComponentwiseMap(
                active_vars = active_vars,
                approx_list = approx_list
            )
    return tm_approx

    
def assemble_LinearSpanTriangularMap(
        dim,
        sl_list: List[CoordinateSemilattice],
        active_vars,
        btype='poly',
        common_basis_flag=True
):
    r""" Generate a linear span triangular transport map with default settings and user defined sparsity and orders.

    Args:
      dim (int): dimension of the map
      sl_list (list): list of :class:`CoordinateSemilattice<semilattices.CoordinateSemilattice>`,
        one for each component of the linear map.
      active_vars (list): list of :math:`d` lists containing the row sparsity
        pattern of the transport, i.e. the active variables for each component.
      btype (string): ``poly`` uses Hermite polynomials, ``fun`` uses Hermite functions,
        ``rbf`` uses radial basis functions.
        If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the basis type fore each component
        :math:`T^{(k)}`.
      common_basis_flag (bool): use acceleration provided by common basis among the
        components (``btype`` must be a string or a list with all equal
        elements).

    Returns:
      (:class:`LinearSpanTriangularTransportMap<LinearSpanTriangularTransportMap>`) -- the constructed transport map
    """
    # Initialize the list of components
    approx_list = []
    # Initialize the list of active variables
    if len(active_vars) != dim:
        raise ValueError("List of active variables must be dim long.")
    for d, avars in enumerate(active_vars):
        if sorted(avars) != avars:
            raise ValueError("List of active components must be provided in " + \
                             "sorted order.")
        if avars[-1] != d:
            raise ValueError("List of active components must include at least" + \
                             "the diagonal term.")
    # Initialize the basis type
    if isinstance(btype, str):
        btype_list = [btype] * dim
    else:
        if len(btype) != dim:
            raise AttributeError("List of basis types must be dim long.")
        else:
            btype_list = btype
    # Check whether it is possible to use common basis
    common_basis_flag = common_basis_flag and all(x==btype_list[0] for x in btype_list)

    full_basis_list = []
    for d, btype in enumerate(btype_list):
        if btype == 'poly':
            full_basis_list.append( [S1D.HermiteProbabilistsPolynomial()] * (d+1) )
        elif btype == 'fun':
            full_basis_list.append(
                [S1D.LinearExtendedHermiteProbabilistsFunction()] * (d+1) )
        elif btype == 'rbf':
            full_basis_list.append(
                [
                    S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(order, 0.9)
                    for order in sl_list[d].max_coordinates
                ]
            )
        else:
            raise ValueError("Input btype is invalid.")
    
    # Prepare basis in case common_basis
    if common_basis_flag:
        if btype_list[0] == 'poly':
            basis_list = [S1D.HermiteProbabilistsPolynomial()] * dim
        elif btype_list[0] == 'fun':
            basis_list = [S1D.LinearExtendedHermiteProbabilistsFunction()] * dim
        elif btype_list[0] == 'rbf':
            basis_list = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                sl.max_l1_norm, 0.9) for sl in sl_list]
            
    # Instantiate the components
    for d, (avars, sl, btype) in enumerate(zip(active_vars, sl_list, btype_list)):
        if common_basis_flag:
            basis_comp = [basis_list[a] for a in avars]
        else:
            basis_comp = [full_basis_list[d][a] for a in avars]

        approx = LinearSpanTensorizedParametricFunctional(
            basis_comp,
            semilattice=sl,
            full_basis_list=full_basis_list[d])
        approx_list.append( approx )

    # Instantiate the map
    if common_basis_flag:    
        tm_approx = CommonBasisLinearSpanParametricTriangularComponentwiseMap(
            active_vars = active_vars,
            approx_list = approx_list
        )
    else:
        tm_approx = LinearSpanParametricTriangularComponentwiseMap(
            active_vars = active_vars,
            approx_list = approx_list
        )
    return tm_approx
