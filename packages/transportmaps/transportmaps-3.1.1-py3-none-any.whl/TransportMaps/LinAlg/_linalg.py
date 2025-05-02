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
import numpy.linalg as npla
import scipy.linalg as scila

__all__ = [
    'square_root',
    'inverse_square_root',
    'matrix_inverse',
    'solve_linear_system',
    'solve_square_root_linear_system',
    'log_det'
]

nax = np.newaxis    


def square_root(A, square_root_type='sym'):
    r""" Factorizes :math:`A` and returns the square root it

    Args:
      A (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]): matrix 

    Kwargs:
      square_root_type (str): type of square root.
         For ``square_root_type=='sym'``, :math:`L=U\Lambda^{\frac{1}{2}}U^T`
         where :math:`A = U\Lambda U^T` is the eigenvalue decomposition
         of :math:`A`.
         For ``square_root_type=='tri'`` or ``square_root_type=='chol'``,
         :math:`L=C` where :math:`A=CC^T` is
         the Cholesky decomposition of :math:`A`.
         For ``square_root_type=='kl'``, :math:`L=U\Lambda^{\frac{1}{2}}`
         where :math:`A = U\Lambda U^T` is the eigenvalue decomposition
         of :math:`A` (this corresponds to the Karuenen-Loeve expansion).
         The eigenvalues and eigenvectors are ordered with :math:`\lambda_i\geq\lambda_{i+1}`.

    Returns:
       :math:`L` -- square root
    """
    if square_root_type in ['sym', 'kl']:
        lmb, V = npla.eigh(A)
        L = V * np.sqrt(lmb)[nax,:]
        if square_root_type == 'sym':
            L = np.dot( L, V.T )
    elif square_root_type in ['tri', 'chol']:
        try:
            L = scila.cholesky(A, lower=True)
        except scila.LinAlgError:
            lmb, V = npla.eigh(A)
            L = V * np.sqrt(lmb)[nax,:]
            (L,) = scila.qr(L, mode='r')
            L = L.T
    else:
        raise ValueError("Square root type not recognized")
    return L

def inverse_square_root(A, square_root_type='sym'):
    r""" Factorizes :math:`A` and returns the square root of :math:`A^{-1}`

    Args:
      A (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]): matrix 

    Kwargs:
      square_root_type (str): type of square root.
         For ``square_root_type=='sym'``, :math:`L=U\Lambda^{\frac{1}{2}}U^T`
         where :math:`A = U\Lambda U^T` is the eigenvalue decomposition
         of :math:`A`.
         For ``square_root_type=='tri'`` or ``square_root_type=='chol'``,
         :math:`L=C` where :math:`A=CC^T` is
         the Cholesky decomposition of :math:`A`.
         For ``square_root_type=='kl'``, :math:`L=U\Lambda^{\frac{1}{2}}`
         where :math:`A = U\Lambda U^T` is the eigenvalue decomposition
         of :math:`A` (this corresponds to the Karuenen-Loeve expansion).
         The eigenvalues and eigenvectors are ordered with :math:`\lambda_i\geq\lambda_{i+1}`.

    Returns:
       :math:`L^{-1}` -- square root of the inverse
    """
    if square_root_type in ['sym', 'kl']:
        lmb, V = npla.eigh(A)
        L = V * np.sqrt(1./lmb)[nax,:]
        if square_root_type == 'sym':
            L = np.dot( L, V.T )
    elif square_root_type in ['tri', 'chol']:
        try:
            L = scila.cholesky(A, lower=True)
            L = scila.solve_triangular(L, np.eye(L.shape[0]), lower=True)
        except scila.LinAlgError:
            lmb, V = npla.eigh(A)
            L = V * np.sqrt(1./lmb)[nax,:]
            (L,) = scila.qr(L, mode='r')
            L = L.T
    else:
        raise ValueError("Square root type not recognized")
    return L

def matrix_inverse(A):
    return solve_linear_system(A, np.eye(A.shape[0]))

def solve_linear_system(A, b, transposed=False):
    r""" Solve the system :math:`Ax = b`

    It checks whether A has some good properties.
    """
    if np.all( A == np.tril(A) ):
        x = scila.solve_triangular(A, b, lower=True, trans=transposed)
    elif np.all( A == np.triu(A) ):
        x = scila.solve_triangular(A, b, lower=False, trans=transposed)
    elif np.all( A == A.T ): # Symmetric
        try: # Try with cholesky
            L = scila.cholesky(A, lower=True)
            x = scila.solve_triangular(L, b, lower=True)
            x = scila.solve_triangular(L, x, lower=True, trans='T')
        except scila.LinAlgError:
            x = scila.solve(A, b, assume_a='sym')
    else:
        x = scila.solve(A, b, transposed=transposed)
    return x

def solve_square_root_linear_system(A, b):
    r""" Solve the system :math:`AA^{\top}x = b`
    """
    if np.all( A == np.tril(A) ):
        x = scila.solve_triangular(A, b, lower=True)
        x = scila.solve_triangular(A, x, lower=True, trans='T')
    elif np.all( A == np.triu(A) ):
        x = scila.solve_triangular(A, b, lower=False)
        x = scila.solve_triangular(A, x, lower=False, trans='T')
    else:
        AAT = np.dot(A, A.T)
        x = scila.solve(AAT, b, assume_a='sym')
    return x

def log_det(A):
    r""" Compute :math:`\log\det A`
    """
    if np.all( A == np.tril(A) ) or np.all( A == np.triu(A) ):
        pass
    else: # Symmetric
        _, A = npla.qr(A, mode='r')
    return np.sum(np.diag(A))
