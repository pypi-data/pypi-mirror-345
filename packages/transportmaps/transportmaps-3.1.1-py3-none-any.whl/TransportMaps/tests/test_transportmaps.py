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

import unittest
import numpy as np
import numpy.random as npr
import numpy.linalg as npla
from TransportMaps import Maps

try:
    import mpi_map
    MPI_SUPPORT = True
except:
    MPI_SUPPORT = False

class TransportMap_DerivativeChecks(object):

    def setUp(self):
        npr.seed(1)
        import TransportMaps.Distributions as DIST
        self.dim = 2
        self.order = 3
        self.fd_eps = 1e-6
        self.qtype = 3
        self.qpar = [5]*self.dim
        self.distribution = DIST.StandardNormalDistribution(self.dim)
        (x,w) = self.distribution.quadrature(self.qtype, self.qpar)
        self.x = x
        self.w = w
        self.y = np.zeros((1,self.dim))
        self.build_tm_approx()

    def test_grad_a(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def tm(a, params_t):
            tm_approx.coeffs = a
            out = tm_approx.evaluate(x, params_t)
            return out
        def grad_a_tm(a, params_t):
            tm_approx.coeffs = a
            ncoeffs = tm_approx.n_coeffs
            grad_list = tm_approx.grad_a(x, params_t)
            out = np.zeros((len(x), tm_approx.dim, ncoeffs))
            start = 0
            for k, grad in enumerate(grad_list):
                stop = start + grad.shape[1]
                out[:,k,start:stop] = grad
                start = stop
            return out

        # Check gradient transport map
        flag = DC.fd_gradient_check(tm, grad_a_tm, coeffs, self.fd_eps,
                               params=params, verbose=False)
        self.assertTrue( flag )

    def test_hess_a(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport gradient and hessian
        def grad_a_tm(a, params_t):
            tm_approx.coeffs = a
            ncoeffs = tm_approx.n_coeffs
            grad_list = tm_approx.grad_a(x, params_t)
            out = np.zeros((len(x), tm_approx.dim, ncoeffs))
            start = 0
            for k, grad in enumerate(grad_list):
                stop = start + grad.shape[1]
                out[:,k,start:stop] = grad
                start = stop
            return out
        def hess_a_tm(a, params_t):
            tm_approx.coeffs = a
            ncoeffs = tm_approx.n_coeffs
            hess_list = tm_approx.hess_a(x, params_t)
            out = np.zeros((len(x), tm_approx.dim, ncoeffs, ncoeffs))
            start = 0
            for k, hess in enumerate(hess_list):
                stop = start + hess.shape[1]
                out[:,k,start:stop,start:stop] = hess
                start = stop
            return out

        # Check Hessian transport map
        flag = DC.fd_gradient_check(grad_a_tm, hess_a_tm, coeffs, self.fd_eps,
                                           params=params, verbose=False)
        self.assertTrue( flag )

    def test_action_hess_a(self):

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        da = 1e-1 * npr.randn(coeffs.size)
        params = self.params
        x = self.x

        # Define transport gradient and hessian
        def hess_a_dot_da(a, da, params_t):
            tm_approx.coeffs = a
            ncoeffs = tm_approx.n_coeffs
            hess_list = tm_approx.hess_a(x, params_t)
            A = np.zeros((len(x), tm_approx.dim, ncoeffs, ncoeffs))
            start = 0
            for k, hess in enumerate(hess_list):
                stop = start + hess.shape[1]
                A[:,k,start:stop,start:stop] = hess
                start = stop
            return np.dot(A, da)
        def action_hess_a(a, da, params_t):
            tm_approx.coeffs = a
            ncoeffs = tm_approx.n_coeffs
            action_hess_a_list = tm_approx.action_hess_a(x, da, params_t)
            out = np.zeros((len(x), tm_approx.dim, ncoeffs))
            start = 0
            for k, aha in enumerate(action_hess_a_list):
                stop = start + aha.shape[1]
                out[:,k,start:stop] = aha
                start = stop
            return out

        ha_dot_da = hess_a_dot_da(coeffs, da, **params)
        aha = action_hess_a(coeffs, da, **params)
        self.assertTrue( np.allclose(ha_dot_da, aha) )

    def test_grad_a_partial_xd(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def partial_xd_tm(a, params_t):
            tm_approx.coeffs = a
            out = tm_approx.partial_xd(x, params_t)
            return out
        def grad_a_partial_xd_tm(a, params_t):
            tm_approx.coeffs = a
            out = tm_approx.grad_a_partial_xd(x, params_t)
            return out

        # Check gradient transport map
        flag = DC.fd_gradient_check(partial_xd_tm, grad_a_partial_xd_tm,
                               coeffs, self.fd_eps,
                               params=params, verbose=False)
        self.assertTrue( flag )

    def test_grad_a_log_det_grad_x(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def log_det_grad_x_tm(a, params_t):
            tm_approx.coeffs = a
            out = tm_approx.log_det_grad_x(x, params_t)
            return out
        def grad_a_log_det_grad_x_tm(a, params_t):
            tm_approx.coeffs = a
            out = tm_approx.grad_a_log_det_grad_x(x, params_t)
            return out

        # Check gradient transport map
        flag = DC.fd_gradient_check(log_det_grad_x_tm, grad_a_log_det_grad_x_tm,
                               coeffs, self.fd_eps,
                               params=params, verbose=False)
        self.assertTrue( flag )

    def test_hess_a_log_det_grad_x(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def grad_a_log_det_grad_x_tm(a, params_t):
            tm_approx.coeffs = a
            out = tm_approx.grad_a_log_det_grad_x(x, params_t)
            return out
        def hess_a_log_det_grad_x_tm(a, params_t):
            tm_approx.coeffs = a
            out = tm_approx.hess_a_log_det_grad_x(x, params_t)
            return out

        # Check Hessian transport map
        flag = DC.fd_gradient_check(grad_a_log_det_grad_x_tm,
                                           hess_a_log_det_grad_x_tm,
                                           coeffs, self.fd_eps,
                                           params=params, verbose=False)
        self.assertTrue( flag )

    def test_action_hess_a_log_det_grad_x(self):

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        da = 1e-1 * npr.randn(coeffs.size)
        params = self.params
        x = self.x

        # Define transport gradient and hessian
        def hess_a_dot_da(a, da, params_t):
            tm_approx.coeffs = a
            haldgx = tm_approx.hess_a_log_det_grad_x(x, params_t)
            return np.dot(haldgx, da)
        def action_hess_a(a, da, params_t):
            tm_approx.coeffs = a
            return tm_approx.action_hess_a_log_det_grad_x(x, da, params_t)

        ha_dot_da = hess_a_dot_da(coeffs, da, **params)
        aha = action_hess_a(coeffs, da, **params)
        self.assertTrue( np.allclose(ha_dot_da, aha) )
        
    def test_inverse(self):
        tm_approx = self.tm_approx
        if hasattr(self,'coeffs'):
            coeffs = self.coeffs
            tm_approx.coeffs = coeffs
        y = self.y
        x = tm_approx.inverse(y)
        yrec = tm_approx.evaluate(x)
        self.assertTrue( np.allclose(y, yrec, rtol=1e-10, atol=1e-10) )

    def test_grad_a_inverse(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        y = self.y

        # Define transport map, gradient
        def tm_inverse(a, params_t):
            tm_approx.coeffs = a
            out = tm_approx.inverse(y)
            return out
        def grad_a_tm_inverse(a, params_t):
            tm_approx.coeffs = a
            out = tm_approx.grad_a_inverse(y)
            return out

        # Check gradient transport map
        flag = DC.fd_gradient_check(tm_inverse, grad_a_tm_inverse, coeffs, self.fd_eps,
                               params=params, verbose=False)
        self.assertTrue( flag )

class OnTheFly_TM_DerivativeChecks( TransportMap_DerivativeChecks ):
    """ Special test definitions for evaluation on-the-fly
    """

    def test_test_gradients(self):
        print()
        v = npr.randn(1, self.tm_approx.dim)
        success = self.tm_approx.test_gradients(self.x, v)
        self.assertTrue( success )
    
    def test_grad_x(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        if hasattr(self, 'coeffs'):
            tm_approx.coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def tm(x, params_t=None):
            out = tm_approx.evaluate(x)
            return out
        def grad_x_tm(x, params_t=None):
            out = tm_approx.grad_x(x)
            return out

        # Check gradient transport map
        flag = DC.fd_gradient_check(tm, grad_x_tm, x, self.fd_eps,
                               params=params, verbose=False)
        self.assertTrue( flag )

    def test_grad_x_inverse(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        if hasattr(self, 'coeffs'):
            tm_approx.coeffs = self.coeffs
        params = self.params
        y = self.y

        # Define transport map, gradient
        def tm(x, params_t=None):
            out = tm_approx.inverse(x)
            return out
        def grad_x_tm(x, params_t=None):
            out = tm_approx.grad_x_inverse(x)
            return out

        # Check gradient transport map
        flag = DC.fd_gradient_check(tm, grad_x_tm, y, self.fd_eps,
                               params=params, verbose=False)
        self.assertTrue( flag )

    def test_hess_x(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        if hasattr(self, 'coeffs'):
            tm_approx.coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport gradient and hessian
        def grad_x_tm(x, params_t=None):
            out = tm_approx.grad_x(x)
            return out
        def hess_x_tm(x, params_t=None):
            out = tm_approx.hess_x(x)
            return out

        # Check Hessian transport map
        flag = DC.fd_gradient_check(grad_x_tm, hess_x_tm,
                                           x, self.fd_eps,
                                           params=params, verbose=False)
        self.assertTrue( flag )

    def test_action_hess_x(self):

        tm_approx = self.tm_approx
        if hasattr(self, 'coeffs'):
            tm_approx.coeffs = self.coeffs
        params = self.params
        x = self.x
        dx = 1e-1 * npr.randn(*(x.shape))

        # Define transport gradient and hessian
        A = tm_approx.hess_x(x)
        hx_dot_dx = np.einsum('...ijk,...k->...ij', A, dx)
        ahx = tm_approx.action_hess_x(x, dx)
        self.assertTrue( np.allclose(hx_dot_dx, ahx) )

    def test_grad_a_grad_x(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport gradient and hessian
        def grad_a_tm(x, params_t):
            ncoeffs = tm_approx.n_coeffs
            grad_list = tm_approx.grad_a(x)
            out = np.zeros((len(x), ncoeffs, tm_approx.dim))
            start = 0
            for k, grad in enumerate(grad_list):
                stop = start + grad.shape[1]
                out[:,start:stop,k] = grad
                start = stop
            return out

        def grad_a_grad_x_tm(x, params_t):
            ncoeffs = tm_approx.n_coeffs
            grad_list = tm_approx.grad_a_grad_x(x)
            out = np.zeros((len(x), ncoeffs, tm_approx.dim, tm_approx.dim))
            start = 0
            for k, grad in enumerate(grad_list):
                stop = start + grad.shape[1]
                out[:,start:stop,k,:k+1] = grad
                start = stop
            return out

        # Check gradient transport map
        flag = DC.fd_gradient_check(grad_a_tm, grad_a_grad_x_tm, x, self.fd_eps,
                               params=params, verbose=False)
        self.assertTrue( flag )

    def test_grad_a_hess_x(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport gradient and hessian
        def grad_a_grad_x_tm(x, params_t):
            ncoeffs = tm_approx.n_coeffs
            grad_list = tm_approx.grad_a_grad_x(x)
            out = np.zeros((len(x), ncoeffs, tm_approx.dim, tm_approx.dim))
            start = 0
            for k, grad in enumerate(grad_list):
                stop = start + grad.shape[1]
                out[:,start:stop,k,:k+1] = grad
                start = stop
            return out

        def grad_a_hess_x_tm(x, params_t):
            ncoeffs = tm_approx.n_coeffs
            hess_list = tm_approx.grad_a_hess_x(x)
            out = np.zeros((len(x), ncoeffs, tm_approx.dim, tm_approx.dim, tm_approx.dim))
            start = 0
            for k, grad in enumerate(hess_list):
                stop = start + grad.shape[1]
                out[:,start:stop,k,:k+1,:k+1] = grad
                start = stop
            return out

        # Check gradient transport map
        flag = DC.fd_gradient_check(grad_a_grad_x_tm, grad_a_hess_x_tm, x, self.fd_eps,
                                           params=params, verbose=False)
        self.assertTrue( flag )

    def test_log_det_grad_x(self):
        tm_approx = self.tm_approx
        if hasattr(self, 'coeffs'):
            tm_approx.coeffs = self.coeffs
        params = self.params
        x = self.x

        # Compute \log\det\nabla_xT from \nabla_xT
        gx = tm_approx.grad_x(x)
        ldgx_from_gx = np.zeros(gx.shape[0])
        for i in range(gx.shape[0]):
            ldgx_from_gx[i] = np.log(npla.det(gx[i,:,:]))
        # Compute \log\det\nabla_xT directly
        ldgx = tm_approx.log_det_grad_x(x)

        # Check result
        flag = np.max(np.abs(ldgx - ldgx_from_gx)) < 1e-10
        self.assertTrue(flag)

    def test_grad_x_log_det_grad_x(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        if hasattr(self, 'coeffs'):
            tm_approx.coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def log_det_grad_x_tm(x, params_t=None):
            out = tm_approx.log_det_grad_x(x)
            return out
        def grad_x_log_det_grad_x_tm(x, params_t=None):
            out = tm_approx.grad_x_log_det_grad_x(x)
            return out

        # Check gradient transport map
        flag = DC.fd_gradient_check(log_det_grad_x_tm, grad_x_log_det_grad_x_tm,
                               x, self.fd_eps,
                               params=params, verbose=False)
        self.assertTrue( flag )

    def test_hess_x_log_det_grad_x(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        if hasattr(self,'coeffs'):
            coeffs = self.coeffs
            tm_approx.coeffs = coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def grad_x_log_det_grad_x_tm(x, params_t=None):
            out = tm_approx.grad_x_log_det_grad_x(x)
            return out
        def hess_x_log_det_grad_x_tm(x, params_t=None):
            out = tm_approx.hess_x_log_det_grad_x(x)
            return out

        # Check gradient transport map
        flag = DC.fd_gradient_check(grad_x_log_det_grad_x_tm,
                                           hess_x_log_det_grad_x_tm,
                                           x, self.fd_eps,
                                           params=params, verbose=False)
        self.assertTrue( flag )

    def test_action_hess_x_log_det_grad_x(self):

        tm_approx = self.tm_approx
        if hasattr(self,'coeffs'):
            coeffs = self.coeffs
            tm_approx.coeffs = coeffs
        params = self.params
        x = self.x
        dx = 1e-1 * npr.randn(*(x.shape))

        # Define transport map, gradient
        A = tm_approx.hess_x_log_det_grad_x(x)
        hx_dot_dx = np.einsum('...jk,...k->...j', A, dx)
        ahx = tm_approx.action_hess_x_log_det_grad_x(x, dx)
        self.assertTrue( np.allclose(hx_dot_dx, ahx) )

    def test_log_det_grad_x_inverse(self):
        tm_approx = self.tm_approx
        if hasattr(self, 'coeffs'):
            tm_approx.coeffs = self.coeffs
        params = self.params
        y = self.y

        # Compute \log\det\nabla_xT from \nabla_xT
        gx = tm_approx.grad_x_inverse(y)
        ldgx_from_gx = np.zeros(y.shape[0])
        for i in range(y.shape[0]):
            ldgx_from_gx[i] = np.log(npla.det(gx[i,:,:]))
        # Compute \log\det\nabla_xT directly
        ldgx = tm_approx.log_det_grad_x_inverse(y)

        # Check result
        flag = np.max(np.abs(ldgx - ldgx_from_gx)) < 1e-10
        self.assertTrue(flag)

    # def test_grad_x_log_det_grad_x_inverse(self):
    #     import TransportMaps.DerivativesChecks as DC

    #     tm_approx = self.tm_approx
    #     tm_approx.coeffs = self.coeffs
    #     params = self.params
    #     x = self.x

    #     # Define transport map, gradient
    #     def log_det_grad_x_tm(x, params_t=None):
    #         out = tm_approx.log_det_grad_x_inverse(x)
    #         return out
    #     def grad_x_log_det_grad_x_tm(x, params_t=None):
    #         out = tm_approx.grad_x_log_det_grad_x_inverse(x)
    #         return out

    #     # Check gradient transport map
    #     flag = DC.fd_gradient_check(log_det_grad_x_tm, grad_x_log_det_grad_x_tm,
    #                            x, self.fd_eps,
    #                            params=params, verbose=False)
    #     self.assertTrue( flag )

    # def test_hess_x_log_det_grad_x_inverse(self):
    #     import TransportMaps.DerivativesChecks as DC

    #     tm_approx = self.tm_approx
    #     coeffs = self.coeffs
    #     tm_approx.coeffs = coeffs
    #     params = self.params
    #     x = self.x

    #     # Define transport map, gradient
    #     def grad_x_log_det_grad_x_tm(x, params_t=None):
    #         out = tm_approx.grad_x_log_det_grad_x_inverse(x)
    #         return out
    #     def hess_x_log_det_grad_x_tm(x, params_t=None):
    #         out = tm_approx.hess_x_log_det_grad_x_inverse(x)
    #         return out

    #     # Check gradient transport map
    #     flag = DC.fd_gradient_check(grad_x_log_det_grad_x_tm,
    #                                        hess_x_log_det_grad_x_tm,
    #                                        x, self.fd_eps,
    #                                        params=params, verbose=False)
    #     self.assertTrue( flag )

    def test_grad_a_hess_x_log_det_grad_x(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        tm_approx.coeffs = coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def hess_x_log_det_grad_x_tm(a, params_t):
            tm_approx.coeffs = a
            out = tm_approx.hess_x_log_det_grad_x(x)
            return out
        def grad_a_hess_x_log_det_grad_x_tm(a, params_t):
            tm_approx.coeffs = a
            out = tm_approx.grad_a_hess_x_log_det_grad_x(x)
            return out

        # Check gradient transport map
        flag = DC.fd_gradient_check(hess_x_log_det_grad_x_tm, grad_a_hess_x_log_det_grad_x_tm,
                               coeffs, self.fd_eps, params=params, newdim=1, verbose=False)
        self.assertTrue( flag )

class OnTheFly_InverseTM_DerivativeChecks( TransportMap_DerivativeChecks ):
    def test_grad_x_inverse(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        if hasattr(self, 'coeffs'):
            tm_approx.coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def tm(x, params_t=None):
            out = tm_approx.inverse(x)
            return out
        def grad_x_tm(x, params_t=None):
            out = tm_approx.grad_x_inverse(x)
            return out

        # Check gradient transport map
        flag = DC.fd_gradient_check(tm, grad_x_tm, x, self.fd_eps,
                               params=params, verbose=False)
        self.assertTrue( flag )

    def test_grad_a_inverse(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def tm(a, params_t):
            tm_approx.coeffs = a
            out = tm_approx.inverse(x)
            return out
        def grad_a_tm(a, params_t):
            tm_approx.coeffs = a
            ncoeffs = tm_approx.n_coeffs
            grad_list = tm_approx.grad_a_inverse(x)
            out = np.zeros((len(x), tm_approx.dim, ncoeffs))
            start = 0
            for k, grad in enumerate(grad_list):
                stop = start + grad.shape[1]
                out[:,k,start:stop] = grad
                start = stop
            return out

        # Check gradient transport map
        flag = DC.fd_gradient_check(tm, grad_a_tm, coeffs, self.fd_eps,
                               params=params, verbose=False)
        self.assertTrue( flag )

    def test_grad_a(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def tm_inverse(a, params_t):
            tm_approx.coeffs = a
            out = tm_approx.evaluate(x)
            return out
        def grad_a_tm_inverse(a, params_t):
            tm_approx.coeffs = a
            out = tm_approx.grad_a(x)
            return out

        # Check gradient transport map
        flag = DC.fd_gradient_check(tm_inverse, grad_a_tm_inverse, coeffs, self.fd_eps,
                               params=params, verbose=False)
        self.assertTrue( flag )

    @unittest.skip("Not Implemented")
    def test_hess_a(self):
        pass

    @unittest.skip("Not Implemented")
    def test_action_hess_a(self):
        pass

    @unittest.skip("Not Implemented")
    def test_grad_a_log_det_grad_x(self):
        pass

    @unittest.skip("Not Implemented")
    def test_hess_a_log_det_grad_x(self):
        pass

    @unittest.skip("Not Implemented")
    def test_action_hess_a_log_det_grad_x(self):
        pass

    @unittest.skip("Not Implemented")
    def test_grad_a_partial_xd(self):
        pass

    @unittest.skip("Not Implemented")
    def test_grad_a_hess_x_log_det_grad_x(self):
        pass

class OnTheFly_CompositeTM_DerivativeChecks( OnTheFly_TM_DerivativeChecks ):
    @unittest.skip("Not Implemented")
    def test_grad_a(self):
        pass

    @unittest.skip("Not Implemented")
    def test_hess_a(self):
        pass

    @unittest.skip("Not Implemented")
    def test_action_hess_a(self):
        pass

    @unittest.skip("Not Implemented")
    def test_grad_a_inverse(self):
        pass

    @unittest.skip("Not Implemented")
    def test_grad_a_grad_x(self):
        pass

    @unittest.skip("Not Implemented")
    def test_grad_a_hess_x(self):
        pass

    @unittest.skip("Not Implemented")
    def test_grad_a_log_det_grad_x(self):
        pass

    @unittest.skip("Not Implemented")
    def test_hess_a_log_det_grad_x(self):
        pass

    @unittest.skip("Not Implemented")
    def test_action_hess_a_log_det_grad_x(self):
        pass

    @unittest.skip("Not Implemented")
    def test_grad_a_partial_xd(self):
        pass

    @unittest.skip("Not Implemented")
    def test_grad_a_hess_x_log_det_grad_x(self):
        pass

class Precomp_TM_DerivativeChecks( TransportMap_DerivativeChecks ):
    """ Special test definitions with precomputed Vandermonde matrices.
    """
    def test_grad_x(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        if hasattr(self, 'coeffs'):
            tm_approx.coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def tm(x, params_t=None):
            out = tm_approx.evaluate(x)
            return out
        def grad_x_tm(x, params_t=None):
            out = tm_approx.grad_x(x, params_t)
            return out

        # Check gradient transport map
        flag = DC.fd_gradient_check(tm, grad_x_tm, x, self.fd_eps,
                               params=params, verbose=False)
        self.assertTrue( flag )

    def test_hess_x(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        if hasattr(self, 'coeffs'):
            tm_approx.coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport gradient and hessian
        def grad_x_tm(x, params_t=None):
            out = tm_approx.grad_x(x)
            return out
        def hess_x_tm(x, params_t=None):
            out = tm_approx.hess_x(x, params_t)
            return out

        # Check Hessian transport map
        flag = DC.fd_gradient_check(grad_x_tm, hess_x_tm,
                                           x, self.fd_eps,
                                           params=params, verbose=False)
        self.assertTrue( flag )

    def test_action_hess_x(self):

        tm_approx = self.tm_approx
        if hasattr(self, 'coeffs'):
            tm_approx.coeffs = self.coeffs
        params = self.params
        x = self.x
        dx = 1e-1 * npr.randn(*(x.shape))

        # Define transport gradient and hessian
        A = tm_approx.hess_x(x)
        hx_dot_dx = np.einsum('...ijk,...k->...ij', A, dx)
        ahx = tm_approx.action_hess_x(x, dx)
        self.assertTrue( np.allclose(hx_dot_dx, ahx) )

    def test_grad_x_log_det_grad_x(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        if hasattr(self, 'coeffs'):
            tm_approx.coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def log_det_grad_x_tm(x, params_t=None):
            out = tm_approx.log_det_grad_x(x)
            return out
        def grad_x_log_det_grad_x_tm(x, params_t=None):
            out = tm_approx.grad_x_log_det_grad_x(x, params_t)
            return out

        # Check gradient transport map
        flag = DC.fd_gradient_check(log_det_grad_x_tm, grad_x_log_det_grad_x_tm,
                               x, self.fd_eps,
                               params=params, verbose=False)
        self.assertTrue( flag )

    def test_hess_x_log_det_grad_x(self):
        import TransportMaps.DerivativesChecks as DC

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        tm_approx.coeffs = coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def grad_x_log_det_grad_x_tm(x, params_t=None):
            out = tm_approx.grad_x_log_det_grad_x(x)
            return out
        def hess_x_log_det_grad_x_tm(x, params_t=None):
            out = tm_approx.hess_x_log_det_grad_x(x, params_t)
            return out

        # Check gradient transport map
        flag = DC.fd_gradient_check(grad_x_log_det_grad_x_tm,
                                           hess_x_log_det_grad_x_tm,
                                           x, self.fd_eps,
                                           params=params, verbose=False)
        self.assertTrue( flag )

    def test_action_hess_x_log_det_grad_x(self):

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        tm_approx.coeffs = coeffs
        params = self.params
        x = self.x
        dx = 1e-1 * npr.randn(*(x.shape))

        # Define transport map, gradient
        A = tm_approx.hess_x_log_det_grad_x(x)
        hx_dot_dx = np.einsum('...jk,...k->...j', A, dx)
        ahx = tm_approx.action_hess_x_log_det_grad_x(x, dx)
        self.assertTrue( np.allclose(hx_dot_dx, ahx) )

class PrecompUni_TM_DerivativeChecks( Precomp_TM_DerivativeChecks ):
    """ Precompute uni-variate Vandermonde matrices
    """
    def setUp(self):
        super(PrecompUni_TM_DerivativeChecks,self).setUp()
        x = self.x
        self.params['params_t'] = {'components': [{} for i in range(self.dim)]}
        self.tm_approx.precomp_evaluate(x, self.params['params_t'])
        self.tm_approx.precomp_partial_xd(x, self.params['params_t'])
        self.tm_approx.precomp_grad_x(x, self.params['params_t'])
        self.tm_approx.precomp_hess_x(x, self.params['params_t'])
        self.tm_approx.precomp_grad_x_partial_xd(x, self.params['params_t'])
        self.tm_approx.precomp_hess_x_partial_xd(x, self.params['params_t'])

class PrecompMulti_TM_DerivativeChecks( Precomp_TM_DerivativeChecks ):
    """ Precompute multi-variate Vandermonde matrices
    """
    def setUp(self):
        super(PrecompMulti_TM_DerivativeChecks,self).setUp()
        x = self.x
        self.params['params_t'] = {'components': [{} for i in range(self.dim)]}
        self.tm_approx.precomp_evaluate(x, self.params['params_t'],
                                        precomp_type='multi')
        self.tm_approx.precomp_partial_xd(x, self.params['params_t'],
                                        precomp_type='multi')
        self.tm_approx.precomp_grad_x(x, self.params['params_t'],
                                      precomp_type='multi')
        self.tm_approx.precomp_hess_x(x, self.params['params_t'],
                                      precomp_type='multi')
        self.tm_approx.precomp_grad_x_partial_xd(x, self.params['params_t'],
                                                 precomp_type='multi')
        self.tm_approx.precomp_hess_x_partial_xd(x, self.params['params_t'],
                                                 precomp_type='multi')

class LinearTM( object ):
    def build_tm_approx(self):
        ct = npr.randn(self.dim)
        s = npr.randn(self.dim, self.dim)
        s = np.dot(s, s.T)
        lt = npla.cholesky(s)
        self.tm_approx = Maps.LinearTransportMap(c=ct, L=lt)
        self.params = {}
        
class IntegratedExponentialTTM( object ):
    """ Integrated exponential approximation
    """
    def build_tm_approx(self):
        # Build the transport map (isotropic for each entry)
        self.tm_approx = Maps.assemble_IsotropicIntegratedExponentialTriangularTransportMap(
            self.dim, self.order, span='full', btype='poly', common_basis_flag=False)
        self.params = {}
        self.params['params_t'] = None
        # self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        self.coeffs = npr.randn(self.tm_approx.n_coeffs) / 10.


class CommonBasisIntegratedExponentialTTM( object ):
    """ Integrated exponential approximation
    """
    def build_tm_approx(self):
        # Build the transport map (isotropic for each entry)
        self.tm_approx = Maps.assemble_IsotropicIntegratedExponentialTriangularTransportMap(
            self.dim, self.order, span='full', btype='poly', common_basis_flag=True)
        self.params = {}
        self.params['params_t'] = None
        # self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        self.coeffs = npr.randn(self.tm_approx.n_coeffs) / 10.


class TotOrdIntegratedExponentialTTM( object ):
    """ Integrated exponential approximation
    """
    def build_tm_approx(self):
        # Build the transport map (isotropic for each entry)
        self.tm_approx = Maps.assemble_IsotropicIntegratedExponentialTriangularTransportMap(
            self.dim, self.order, span='total', btype='poly', common_basis_flag=False)
        self.params = {}
        self.params['params_t'] = None
        # self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        self.coeffs = npr.randn(self.tm_approx.n_coeffs) / 10.

class CommonBasisTotOrdIntegratedExponentialTTM( object ):
    """ Integrated exponential approximation
    """
    def build_tm_approx(self):
        # Build the transport map (isotropic for each entry)
        self.tm_approx = Maps.assemble_IsotropicIntegratedExponentialTriangularTransportMap(
            self.dim, self.order, span='total', btype='poly', common_basis_flag=False) 
        self.params = {}
        self.params['params_t'] = None
        # self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        self.coeffs = npr.randn(self.tm_approx.n_coeffs) / 10.

class IntegratedSquaredTTM( object ):
    """ Integrated squared approximation
    """
    def build_tm_approx(self):
        # Build the transport map (isotropic for each entry)
        self.tm_approx = Maps.assemble_IsotropicIntegratedSquaredTriangularTransportMap(
            self.dim, self.order, span='full', btype='poly', common_basis_flag=False)
        self.params = {}
        self.params['params_t'] = None
        coeffs = self.tm_approx.get_identity_coeffs()
        coeffs += npr.randn(len(coeffs)) / 100.
        self.coeffs = np.hstack(coeffs)

# class CommonBasisIntegratedSquaredTTM( object ):
#     """ Integrated squared approximation
#     """
#     def build_tm_approx(self):
#         import SpectralToolbox.Spectral1D as S1D
#         import TransportMaps as TM
#         import TransportMaps.Maps.Functionals as FUNC
#         import TransportMaps.Maps as MAPS
#         # Build the transport map (isotropic for each entry)
#         self.tm_approx = MAPS.assemble_IsotropicIntegratedSquaredTriangularTransportMap(
#             self.dim, self.order, span='full', btype='poly', common_basis_flag=True)
#         self.params = {}
#         self.params['params_t'] = None
#         coeffs = self.tm_approx.get_identity_coeffs()
#         coeffs += npr.randn(len(coeffs)) / 10.
#         self.coeffs = coeffs

class TotOrdIntegratedSquaredTTM( object ):
    """ Integrated squared approximation
    """
    def build_tm_approx(self):
        # Build the transport map (isotropic for each entry)
        self.tm_approx = Maps.assemble_IsotropicIntegratedSquaredTriangularTransportMap(
            self.dim, self.order, span='total', btype='poly', common_basis_flag=False)
        self.params = {}
        self.params['params_t'] = None
        coeffs = self.tm_approx.get_identity_coeffs()
        coeffs += npr.randn(len(coeffs)) / 10.
        self.coeffs = coeffs

# class CommonBasisTotOrdIntegratedSquaredTTM( object ):
#     """ Integrated squared approximation
#     """
#     def build_tm_approx(self):
#         import SpectralToolbox.Spectral1D as S1D
#         import TransportMaps as TM
#         import TransportMaps.Maps.Functionals as FUNC
#         import TransportMaps.Maps as MAPS
#         # Build the transport map (isotropic for each entry)
#         self.tm_approx = MAPS.assemble_IsotropicIntegratedSquaredTriangularTransportMap(
#             self.dim, self.order, span='total', btype='poly', common_basis_flag=True)
#         self.params = {}
#         self.params['params_t'] = None
#         coeffs = self.tm_approx.get_identity_coeffs()
#         coeffs += npr.randn(len(coeffs)) / 10.
#         self.coeffs = coeffs

# INTEGRATES SQUARED RBF

class IntegratedSquaredRBFTTM( object ):
    """ Integrated squared approximation
    """
    def build_tm_approx(self):
        # Build the transport map (isotropic for each entry)
        self.tm_approx = Maps.assemble_IsotropicIntegratedSquaredTriangularTransportMap(
            self.dim, self.order, span='full', btype='rbf', common_basis_flag=False)
        self.params = {}
        self.params['params_t'] = None
        coeffs = []
        for approx in self.tm_approx.approx_list:
            coeffs.append( npr.randn(approx.c.n_coeffs)/10. )
            coeffs.append( npr.randn(approx.h.n_coeffs) )
        self.coeffs = np.hstack(coeffs)

# class CommonBasisIntegratedSquaredRBFTTM( object ):
#     """ Integrated squared approximation
#     """
#     def build_tm_approx(self):
#         import SpectralToolbox.Spectral1D as S1D
#         import TransportMaps as TM
#         import TransportMaps.Maps.Functionals as FUNC
#         import TransportMaps.Maps as MAPS
#         # Build the transport map (isotropic for each entry)
#         self.tm_approx = MAPS.assemble_IsotropicIntegratedSquaredTriangularTransportMap(
#             self.dim, self.order, span='full', btype='rbf', common_basis_flag=True)
#         self.params = {}
#         self.params['params_t'] = None
#         self.coeffs = npr.randn(self.tm_approx.n_coeffs)

# LINEAR SPAN
        
class LinearSpanTTM( object ):
    """ Linear span approximation
    """
    def build_tm_approx(self):
        self.tm_approx = Maps.assemble_IsotropicLinearSpanTriangularTransportMap(
            self.dim, self.order, span='full', btype='poly', common_basis_flag=False)
        self.params = {}
        self.params['params_t'] = None
        # Set coefficients for linear map
        self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        all_midxs = []
        for tm_comp in self.tm_approx.approx_list:
            all_midxs.extend( tm_comp.multi_idxs )
        for d in range(self.tm_approx.dim):
            idx = all_midxs.index( tuple([0]*d + [1]) )
            self.coeffs[idx] = 1.

class CommonBasisLinearSpanTTM( object ):
    """ Linear span approximation
    """
    def build_tm_approx(self):
        self.tm_approx = Maps.assemble_IsotropicLinearSpanTriangularTransportMap(
            self.dim, self.order, span='full', btype='poly', common_basis_flag=True)
        self.params = {}
        self.params['params_t'] = None
        # Set coefficients for linear map
        self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        all_midxs = []
        for tm_comp in self.tm_approx.approx_list:
            all_midxs.extend( tm_comp.multi_idxs )
        for d in range(self.tm_approx.dim):
            idx = all_midxs.index( tuple([0]*d + [1]) )
            self.coeffs[idx] = 1.

class TotOrdLinearSpanTTM( object ):
    """ Linear span approximation
    """
    def build_tm_approx(self):
        self.tm_approx = Maps.assemble_IsotropicLinearSpanTriangularTransportMap(
            self.dim, self.order, span='total', btype='poly', common_basis_flag=False)
        self.params = {}
        self.params['params_t'] = None
        # Set coefficients for linear map
        self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        all_midxs = []
        for tm_comp in self.tm_approx.approx_list:
            all_midxs.extend( tm_comp.multi_idxs )
        for d in range(self.tm_approx.dim):
            idx = all_midxs.index( tuple([0]*d + [1]) )
            self.coeffs[idx] = 1.

class CommonBasisTotOrdLinearSpanTTM( object ):
    """ Linear span approximation
    """
    def build_tm_approx(self):
        self.tm_approx = Maps.assemble_IsotropicLinearSpanTriangularTransportMap(
            self.dim, self.order, span='total', btype='poly', common_basis_flag=True)
        self.params = {}
        self.params['params_t'] = None
        # Set coefficients for linear map
        self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        all_midxs = []
        for tm_comp in self.tm_approx.approx_list:
            all_midxs.extend( tm_comp.multi_idxs )
        for d in range(self.tm_approx.dim):
            idx = all_midxs.index( tuple([0]*d + [1]) )
            self.coeffs[idx] = 1.

#
# INVERSE MAP
#
class InverseCommonBasisTotOrdIntegratedExponentialTTM( object ):
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps.Maps.Functionals as FUNC
        # Build the transport map (isotropic for each entry)
        approx_list = []
        active_vars = []
        c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
        e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction(self.order)
                        for i in range(self.dim)]
        for i in range(self.dim):
            c_orders_list = ([self.order] * i) + [0]
            c_approx = FUNC.LinearSpanTensorizedParametricFunctional(c_basis_list[:i+1], spantype='total',
                                                             order_list=c_orders_list)
            e_orders_list = [self.order] * (i+1)
            e_approx = FUNC.LinearSpanTensorizedParametricFunctional(e_basis_list[:i+1], spantype='total',
                                                             order_list=e_orders_list)
            approx = FUNC.IntegratedExponentialParametricMonotoneFunctional(c_approx, e_approx)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        tm_approx = Maps.CommonBasisIntegratedExponentialParametricTriangularComponentwiseTransportMap(
            active_vars=active_vars,
            approx_list=approx_list
        )
        self.tm_approx = Maps.InverseParametricTransportMap(base_map=tm_approx)
        self.params = {}
        self.params['params_t'] = None
        # self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        self.coeffs = npr.randn(self.tm_approx.n_coeffs) / 10.

class InverseTotOrdIntegratedSquaredTTM( object ):
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps.Maps.Functionals as FUNC
        # Build the transport map (isotropic for each entry)
        approx_list = []
        active_vars = []
        c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
        e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction(self.order)
                        for i in range(self.dim)]
        for i in range(self.dim):
            c_orders_list = ([self.order] * i) + [0]
            c_approx = FUNC.LinearSpanTensorizedParametricFunctional(c_basis_list[:i+1], spantype='total',
                                                             order_list=c_orders_list)
            e_orders_list = [self.order] * (i+1)
            e_approx = FUNC.LinearSpanTensorizedParametricFunctional(e_basis_list[:i+1], spantype='total',
                                                             order_list=e_orders_list)
            approx = FUNC.MonotonicIntegratedSquaredApproximation(c_approx, e_approx)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        tm_approx = Maps.IntegratedSquaredTriangularTransportMap(
            active_vars=active_vars,
            approx_list=approx_list
        )
        self.tm_approx = Maps.InverseParametricTransportMap(base_map=tm_approx)
        self.params = {}
        self.params['params_t'] = None
        # self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        self.coeffs = npr.randn(self.tm_approx.n_coeffs) / 10.
        
#
# COMPOSITE MAP
#
class CompositeCommonBasisTotOrdIntegratedExponentialTTM( object ):
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps.Maps.Functionals as FUNC
        tm_approx_list = []
        for i in range(2):
            # Build the transport map (isotropic for each entry)
            approx_list = []
            active_vars = []
            c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
            e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction(self.order)
                            for i in range(self.dim)]
            for i in range(self.dim):
                c_orders_list = ([self.order] * i) + [0]
                c_approx = FUNC.LinearSpanTensorizedParametricFunctional(
                    c_basis_list[:i+1], spantype='total', order_list=c_orders_list)
                e_orders_list = [self.order] * (i+1)
                e_approx = FUNC.LinearSpanTensorizedParametricFunctional(
                    e_basis_list[:i+1], spantype='total', order_list=e_orders_list)
                approx = FUNC.IntegratedExponentialParametricMonotoneFunctional(
                    c_approx, e_approx)
                approx_list.append( approx )
                active_vars.append( range(i+1) )
            tm_approx = Maps.CommonBasisIntegratedExponentialParametricTriangularComponentwiseTransportMap(
                active_vars=active_vars,
                approx_list=approx_list
            )
            tm_approx_list.append( tm_approx )
        self.tm_approx = Maps.CompositeTransportMap(tm_approx_list[0], tm_approx_list[1])
        self.params = {}
        self.params['params_t'] = None
        # self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        for tm in self.tm_approx.map_list:
            tm.coeffs = npr.randn(tm.n_coeffs) / 10.

#
# LIST COMPOSITE MAP
#
class ListCompositeCommonBasisTotOrdIntegratedExponentialTTM( object ):
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps.Maps.Functionals as FUNC
        tm_approx_list = []
        for i in range(3):
            # Build the transport map (isotropic for each entry)
            approx_list = []
            active_vars = []
            c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
            e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction(self.order)
                            for i in range(self.dim)]
            for i in range(self.dim):
                c_orders_list = ([self.order] * i) + [0]
                c_approx = FUNC.LinearSpanTensorizedParametricFunctional(
                    c_basis_list[:i+1], spantype='total', order_list=c_orders_list)
                e_orders_list = [self.order] * (i+1)
                e_approx = FUNC.LinearSpanTensorizedParametricFunctional(
                    e_basis_list[:i+1], spantype='total', order_list=e_orders_list)
                approx = FUNC.IntegratedExponentialParametricMonotoneFunctional(
                    c_approx, e_approx)
                approx_list.append( approx )
                active_vars.append( range(i+1) )
            tm_approx = Maps.CommonBasisIntegratedExponentialParametricTriangularComponentwiseTransportMap(
                active_vars=active_vars,
                approx_list=approx_list
            )
            tm_approx_list.append( tm_approx )
        self.tm_approx = Maps.ListCompositeTransportMap(map_list=tm_approx_list)
        self.params = {}
        self.params['params_t'] = None
        # self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        for tm in self.tm_approx.map_list:
            tm.coeffs = npr.randn(tm.n_coeffs) / 10.

# LINEAR MAP
class OnTheFly_LinearTM_DerivativeChecks( LinearTM,
                                          OnTheFly_TM_DerivativeChecks,
                                          unittest.TestCase):
    @unittest.skip("Not implemented")
    def test_grad_a(self):
        pass
    @unittest.skip("Not implemented")
    def test_hess_a(self):
        pass
    @unittest.skip("Not implemented")
    def test_action_hess_a(self):
        pass
    @unittest.skip("Not implemented")
    def test_tuple_grad_a(self):
        pass
    @unittest.skip("Not implemented")
    def test_grad_a_partial_xd(self):
        pass
    @unittest.skip("Not implemented")
    def test_grad_a_log_det_grad_x(self):
        pass
    @unittest.skip("Not implemented")
    def test_hess_a_log_det_grad_x(self):
        pass
    @unittest.skip("Not implemented")
    def test_action_hess_a_log_det_grad_x(self):
        pass
    @unittest.skip("Not implemented")
    def test_grad_a_inverse(self):
        pass
    @unittest.skip("Not implemented")
    def test_grad_a_grad_x(self):
        pass
    @unittest.skip("Not implemented")
    def test_grad_a_hess_x(self):
        pass
    @unittest.skip("Not implemented")
    def test_grad_a_hess_x_log_det_grad_x(self):
        pass
        
# FULL ORDER LINEAR SPAN
class OnTheFly_LinearSpanTM_DerivativeChecks( LinearSpanTTM,
                                              OnTheFly_TM_DerivativeChecks,
                                          unittest.TestCase):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_x_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_log_det_grad_x_inverse(self):
        pass

class PrecompUni_LinearSpanTM_DerivativeChecks( LinearSpanTTM,
                                                PrecompUni_TM_DerivativeChecks,
                                          unittest.TestCase):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_x_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_log_det_grad_x_inverse(self):
        pass

class PrecompMulti_LinearSpanTM_DerivativeChecks( LinearSpanTTM,
                                                  PrecompMulti_TM_DerivativeChecks,
                                          unittest.TestCase):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass

class OnTheFly_CommonBasisLinearSpanTM_DerivativeChecks( CommonBasisLinearSpanTTM,
                                                         OnTheFly_TM_DerivativeChecks,
                                          unittest.TestCase):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_x_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_log_det_grad_x_inverse(self):
        pass

class PrecompUni_CommonBasisLinearSpanTM_DerivativeChecks( CommonBasisLinearSpanTTM,
                                                           PrecompUni_TM_DerivativeChecks,
                                          unittest.TestCase):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_x_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_log_det_grad_x_inverse(self):
        pass

# TOTAL ORDER LINEAR SPAN
class OnTheFly_TotOrdLinearSpanTM_DerivativeChecks( TotOrdLinearSpanTTM,
                                                    OnTheFly_TM_DerivativeChecks,
                                          unittest.TestCase):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_x_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_log_det_grad_x_inverse(self):
        pass

class PrecompUni_TotOrdLinearSpanTM_DerivativeChecks( TotOrdLinearSpanTTM,
                                                      PrecompUni_TM_DerivativeChecks,
                                          unittest.TestCase):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_x_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_log_det_grad_x_inverse(self):
        pass

class PrecompMulti_TotOrdLinearSpanTM_DerivativeChecks( TotOrdLinearSpanTTM,
                                                        PrecompMulti_TM_DerivativeChecks,
                                          unittest.TestCase):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_x_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_log_det_grad_x_inverse(self):
        pass

class OnTheFly_CommonBasisTotOrdLinearSpanTM_DerivativeChecks( CommonBasisTotOrdLinearSpanTTM,
                                                               OnTheFly_TM_DerivativeChecks,
                                          unittest.TestCase):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_x_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_log_det_grad_x_inverse(self):
        pass

class PrecompUni_CommonBasisTotOrdLinearSpanTM_DerivativeChecks( CommonBasisTotOrdLinearSpanTTM,
                                                                 PrecompUni_TM_DerivativeChecks,
                                          unittest.TestCase):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_x_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_log_det_grad_x_inverse(self):
        pass

# FULL ORDER INTEGRATED EXPONENTIAL
class OnTheFly_IntegratedExponentialTM_DerivativeChecks( IntegratedExponentialTTM,
                                                         OnTheFly_TM_DerivativeChecks,
                                          unittest.TestCase):
    pass

class PrecompUni_IntegratedExponentialTM_DerivativeChecks( IntegratedExponentialTTM,
                                                           PrecompUni_TM_DerivativeChecks,
                                          unittest.TestCase):
    pass

class PrecompMulti_IntegratedExponentialTM_DerivativeChecks( IntegratedExponentialTTM,
                                                             PrecompMulti_TM_DerivativeChecks,
                                          unittest.TestCase):
    pass

class OnTheFly_CommonBasisIntegratedExponentialTM_DerivativeChecks(
        CommonBasisIntegratedExponentialTTM,
        OnTheFly_TM_DerivativeChecks,
                                          unittest.TestCase):
    pass

class PrecompUni_CommonBasisIntegratedExponentialTM_DerivativeChecks(
        CommonBasisIntegratedExponentialTTM,
        PrecompUni_TM_DerivativeChecks,
                                          unittest.TestCase):
    pass

# TOTAL ORDER INTEGRATED EXPONENTIAL
class OnTheFly_TotOrdIntegratedExponentialTM_DerivativeChecks( TotOrdIntegratedExponentialTTM,
                                                               OnTheFly_TM_DerivativeChecks,
                                          unittest.TestCase):
    pass

class PrecompUni_TotOrdIntegratedExponentialTM_DerivativeChecks( TotOrdIntegratedExponentialTTM,
                                                                 PrecompUni_TM_DerivativeChecks,
                                          unittest.TestCase):
    pass

class PrecompMulti_TotOrdIntegratedExponentialTM_DerivativeChecks( TotOrdIntegratedExponentialTTM,
                                                                   PrecompMulti_TM_DerivativeChecks,
                                          unittest.TestCase):
    pass

class OnTheFly_CommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks(
        CommonBasisTotOrdIntegratedExponentialTTM,
        OnTheFly_TM_DerivativeChecks,
                                          unittest.TestCase):
    pass

class PrecompUni_CommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks(
        CommonBasisTotOrdIntegratedExponentialTTM,
        PrecompUni_TM_DerivativeChecks,
                                          unittest.TestCase):
    pass

# TOTAL ORDER INVERSE INTEGRATED EXPONENTIAL
class OnTheFly_InverseCommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks(
        InverseCommonBasisTotOrdIntegratedExponentialTTM,
        OnTheFly_InverseTM_DerivativeChecks,
                                          unittest.TestCase):
    pass

# TOTAL ORDER COMPOSITE INTEGRATED EXPONENTIAL
class OnTheFly_CompositeCommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks(
        CompositeCommonBasisTotOrdIntegratedExponentialTTM,
        OnTheFly_CompositeTM_DerivativeChecks,
                                          unittest.TestCase):
    pass

# TOTAL ORDER LIST COMPOSITE INTEGRATED EXPONENTIAL
class OnTheFly_ListCompositeCommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks(
        ListCompositeCommonBasisTotOrdIntegratedExponentialTTM,
        OnTheFly_CompositeTM_DerivativeChecks,
                                          unittest.TestCase):
    @unittest.skip("Not Implemented")
    def test_hess_x_log_det_grad_x(self):
        pass
    @unittest.skip("Not Implemented")
    def test_action_hess_x_log_det_grad_x(self):
        pass

# FULL ORDER INTEGRATED SQUARED
class OnTheFly_IntegratedSquaredTM_DerivativeChecks( IntegratedSquaredTTM,
                                                         OnTheFly_TM_DerivativeChecks,
                                          unittest.TestCase):
    pass

class PrecompUni_IntegratedSquaredTM_DerivativeChecks( IntegratedSquaredTTM,
                                                           PrecompUni_TM_DerivativeChecks,
                                          unittest.TestCase):
    pass

class PrecompMulti_IntegratedSquaredTM_DerivativeChecks( IntegratedSquaredTTM,
                                                             PrecompMulti_TM_DerivativeChecks,
                                          unittest.TestCase):
    pass

# class OnTheFly_CommonBasisIntegratedSquaredTM_DerivativeChecks(
#         CommonBasisIntegratedSquaredTTM,
#         OnTheFly_TM_DerivativeChecks,
#                                           unittest.TestCase):
#     pass

# class PrecompUni_CommonBasisIntegratedSquaredTM_DerivativeChecks(
#         CommonBasisIntegratedSquaredTTM,
#         PrecompUni_TM_DerivativeChecks,
#                                           unittest.TestCase):
#     pass

# TOTAL ORDER INTEGRATED SQUARED
class OnTheFly_TotOrdIntegratedSquaredTM_DerivativeChecks( TotOrdIntegratedSquaredTTM,
                                                               OnTheFly_TM_DerivativeChecks,
                                          unittest.TestCase):
    pass

class PrecompUni_TotOrdIntegratedSquaredTM_DerivativeChecks( TotOrdIntegratedSquaredTTM,
                                                                 PrecompUni_TM_DerivativeChecks,
                                          unittest.TestCase):
    pass

class PrecompMulti_TotOrdIntegratedSquaredTM_DerivativeChecks( TotOrdIntegratedSquaredTTM,
                                                                   PrecompMulti_TM_DerivativeChecks,
                                          unittest.TestCase):
    pass

# class OnTheFly_CommonBasisTotOrdIntegratedSquaredTM_DerivativeChecks(
#         CommonBasisTotOrdIntegratedSquaredTTM,
#         OnTheFly_TM_DerivativeChecks,
#                                           unittest.TestCase):
#     pass

# class PrecompUni_CommonBasisTotOrdIntegratedSquaredTM_DerivativeChecks(
#         CommonBasisTotOrdIntegratedSquaredTTM,
#         PrecompUni_TM_DerivativeChecks,
#                                           unittest.TestCase):
#     pass
    
# # TOTAL ORDER INVERSE INTEGRATED SQUARED
# class OnTheFly_InverseTotOrdIntegratedSquaredTM_DerivativeChecks(
#         InverseTotOrdIntegratedSquaredTTM,
#         OnTheFly_InverseTM_DerivativeChecks,
#         unittest.TestCase):
#     pass

# FULL ORDER INTEGRATED SQUARED RBF
class OnTheFly_IntegratedSquaredRBFTM_DerivativeChecks( IntegratedSquaredRBFTTM,
                                                         OnTheFly_TM_DerivativeChecks,
                                          unittest.TestCase):
    pass

class PrecompUni_IntegratedSquaredRBFTM_DerivativeChecks( IntegratedSquaredRBFTTM,
                                                           PrecompUni_TM_DerivativeChecks,
                                          unittest.TestCase):
    pass

class PrecompMulti_IntegratedSquaredRBFTM_DerivativeChecks( IntegratedSquaredRBFTTM,
                                                             PrecompMulti_TM_DerivativeChecks,
                                          unittest.TestCase):
    pass

# class OnTheFly_CommonBasisIntegratedSquaredRBFTM_DerivativeChecks(
#         CommonBasisIntegratedSquaredRBFTTM,
#         OnTheFly_TM_DerivativeChecks,
#                                           unittest.TestCase):
#     pass

# class PrecompUni_CommonBasisIntegratedSquaredRBFTM_DerivativeChecks(
#         CommonBasisIntegratedSquaredRBFTTM,
#         PrecompUni_TM_DerivativeChecks,
#                                           unittest.TestCase):
#     pass

    
def build_suite(ttype='all'):
    # Linear map
    suite_of_ltm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_LinearTM_DerivativeChecks )
    # Full order linear span
    suite_of_lstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_LinearSpanTM_DerivativeChecks )
    suite_pu_lstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_LinearSpanTM_DerivativeChecks )
    suite_pm_lstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompMulti_LinearSpanTM_DerivativeChecks )
    suite_of_cblstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_CommonBasisLinearSpanTM_DerivativeChecks )
    suite_pu_cblstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_CommonBasisLinearSpanTM_DerivativeChecks )
    # Total order linear span
    suite_of_tolstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_TotOrdLinearSpanTM_DerivativeChecks )
    suite_pu_tolstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_TotOrdLinearSpanTM_DerivativeChecks )
    suite_pm_tolstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompMulti_TotOrdLinearSpanTM_DerivativeChecks )
    suite_of_cbtolstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_CommonBasisTotOrdLinearSpanTM_DerivativeChecks )
    suite_pu_cbtolstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_CommonBasisTotOrdLinearSpanTM_DerivativeChecks )
    # Full order integrated exponential
    suite_of_ietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_IntegratedExponentialTM_DerivativeChecks )
    suite_pu_ietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_IntegratedExponentialTM_DerivativeChecks )
    suite_pm_ietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompMulti_IntegratedExponentialTM_DerivativeChecks )
    suite_of_cbietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_CommonBasisIntegratedExponentialTM_DerivativeChecks )
    suite_pu_cbietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_CommonBasisIntegratedExponentialTM_DerivativeChecks )
    # Total order integrated exponential
    suite_of_toietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_TotOrdIntegratedExponentialTM_DerivativeChecks )
    suite_pu_toietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_TotOrdIntegratedExponentialTM_DerivativeChecks )
    suite_pm_toietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompMulti_TotOrdIntegratedExponentialTM_DerivativeChecks )
    suite_of_cbtoietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_CommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks )
    suite_pu_cbtoietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_CommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks )
    # Inverse integrated exponential
    suite_of_icbtoietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_InverseCommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks )
    # Composite integrated exponential
    suite_of_ccbtoietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_CompositeCommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks )
    # List composite integrated exponential
    suite_of_lccbtoietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_ListCompositeCommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks )

    # Full order integrated squared
    suite_of_istm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_IntegratedSquaredTM_DerivativeChecks )
    suite_pu_istm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_IntegratedSquaredTM_DerivativeChecks )
    suite_pm_istm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompMulti_IntegratedSquaredTM_DerivativeChecks )
    # suite_of_cbistm_dc = unittest.TestLoader().loadTestsFromTestCase(
    #     OnTheFly_CommonBasisIntegratedSquaredTM_DerivativeChecks )
    # suite_pu_cbistm_dc = unittest.TestLoader().loadTestsFromTestCase(
    #     PrecompUni_CommonBasisIntegratedSquaredTM_DerivativeChecks )

    # Total order integrated squared
    suite_of_toistm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_TotOrdIntegratedSquaredTM_DerivativeChecks )
    suite_pu_toistm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_TotOrdIntegratedSquaredTM_DerivativeChecks )
    suite_pm_toistm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompMulti_TotOrdIntegratedSquaredTM_DerivativeChecks )
    # suite_of_cbtoistm_dc = unittest.TestLoader().loadTestsFromTestCase(
    #     OnTheFly_CommonBasisTotOrdIntegratedSquaredTM_DerivativeChecks )
    # suite_pu_cbtoistm_dc = unittest.TestLoader().loadTestsFromTestCase(
    #     PrecompUni_CommonBasisTotOrdIntegratedSquaredTM_DerivativeChecks )

    # Inverse integrated squared
    # suite_of_icbtoistm_dc = unittest.TestLoader().loadTestsFromTestCase(
    #     OnTheFly_InverseCommonBasisTotOrdIntegratedSquaredTM_DerivativeChecks )

    # Full order integrated squared rbf
    suite_of_isrbftm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_IntegratedSquaredRBFTM_DerivativeChecks )
    suite_pu_isrbftm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_IntegratedSquaredRBFTM_DerivativeChecks )
    suite_pm_isrbftm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompMulti_IntegratedSquaredRBFTM_DerivativeChecks )
    # suite_of_cbisrbftm_dc = unittest.TestLoader().loadTestsFromTestCase(
    #     OnTheFly_CommonBasisIntegratedSquaredRBFTM_DerivativeChecks )
    # suite_pu_cbisrbftm_dc = unittest.TestLoader().loadTestsFromTestCase(
    #     PrecompUni_CommonBasisIntegratedSquaredRBFTM_DerivativeChecks )

    # GROUP SUITES
    suites_list = []
    if ttype in ['all','serial']:
        suites_list += [
            # Linear map
            suite_of_ltm_dc,
            
            # Linear span
            suite_of_lstm_dc, suite_pu_lstm_dc, suite_pm_lstm_dc,
            suite_of_cblstm_dc, suite_pu_cblstm_dc,
            suite_of_tolstm_dc, suite_pu_tolstm_dc, suite_pm_tolstm_dc,
            suite_of_cbtolstm_dc, suite_pu_cbtolstm_dc,

            # Integrated squared
            suite_of_istm_dc, suite_pu_istm_dc, suite_pm_istm_dc,
            # suite_of_cbistm_dc, suite_pu_cbistm_dc,
            suite_of_toistm_dc, suite_pu_toistm_dc, suite_pm_toistm_dc,
            # suite_of_cbtoistm_dc, suite_pu_cbtoistm_dc,
            # suite_of_icbtoistm_dc

            # Integrated squared rbf
            suite_of_isrbftm_dc, suite_pu_isrbftm_dc, suite_pm_isrbftm_dc,
            # suite_of_cbisrbftm_dc, suite_pu_cbisrbftm_dc,

            # Integrated exponential
            suite_of_ietm_dc, suite_pu_ietm_dc, suite_pm_ietm_dc,
            suite_of_cbietm_dc, suite_pu_cbietm_dc,
            suite_of_toietm_dc, suite_pu_toietm_dc, suite_pm_toietm_dc,
            suite_of_cbtoietm_dc, suite_pu_cbtoietm_dc,
            suite_of_icbtoietm_dc,

            suite_of_ccbtoietm_dc,
            suite_of_lccbtoietm_dc,

        ]
    all_suites = unittest.TestSuite( suites_list )
    return all_suites


def run_tests(
        ttype='serial',
        failfast=False
):
    all_suites = build_suite(ttype)
    # RUN
    unittest.TextTestRunner(
        verbosity=2,
        failfast=failfast
    ).run(all_suites)


if __name__ == '__main__':
    run_tests()
