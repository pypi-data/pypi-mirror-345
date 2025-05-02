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

import numpy as np
from scipy.special import erf
from TransportMaps.Misc import counted, cached, deprecate

from TransportMaps.Distributions.ConditionalDistributions import \
    MeanConditionallyNormalDistribution
from TransportMaps.Distributions.DistributionBase import Distribution
from TransportMaps.Distributions.FactorizedDistributionBase import FactorizedDistribution
from TransportMaps.Distributions.FrozenDistributions import \
    UniformDistribution, LogNormalDistribution, NormalDistribution
from TransportMaps.Distributions.TransportMapDistributions import \
    PushForwardTransportMapDistribution
from TransportMaps.Distributions.Inference.InferenceBase import \
    BayesPosteriorDistribution

from TransportMaps.Likelihoods.LikelihoodBase import \
    AdditiveLogLikelihood
from TransportMaps.Maps import Map
from TransportMaps.Maps import \
    FrozenLinearDiagonalTransportMap

__all__ = ['BODjoint', 'JointDistribution', 'PosteriorDistribution',
           'JointDistributionUniformPrior', 'JointDistributionLogNormalPrior',
           'PosteriorDistributionUniformPrior', 'PosteriorDistributionLogNormalPrior']

nax = np.newaxis

class BODjoint(Distribution):

    @deprecate("TransportMaps.Distributions.Examples.BiochemicalOxygenDemand.BODjoint", "> v2.0b1",
               "Use TransportMaps.Distributions.Examples.BiochemicalOxygenDemand.JointDistribution")
    def __init__(self, numY, sigma = np.sqrt(1e-3), a_range=(0.4,1.2), b_range=(0.01,0.31) ):
        timeY=np.arange(numY)+1.
        dimDistribution = numY+2
        super(BODjoint,self).__init__(dimDistribution)
        self.numY = numY
        self.timeY  = timeY
        self.sigma = sigma
        self.a_range = a_range
        self.a_min = a_range[0]
        self.a_half = (a_range[1] - a_range[0]) / 2.
        self.b_range = b_range
        self.b_min = b_range[0]
        self.b_half = (b_range[1] - b_range[0]) / 2.
    def pdf(self, x, params=None):
        return np.exp(self.log_pdf(x, params))

    @cached()
    @counted
    def log_pdf(self, x, params=None, **kwargs):
        # x is a 2-d array of points. The first dimension corresponds to the number of points.
        #The first numY columns of x refer to the data
        numY = self.numY
        Y = x[:,0:numY]
        theta1=x[:,numY] #The last two components refer to the parameters
        theta2=x[:,numY+1]
        a = .4  + .4*( 1 + erf( theta1/np.sqrt(2) )  )
        b = .01 + .15*( 1 + erf( theta2/np.sqrt(2) )  )
        return -1.0/(2*self.sigma**2) * \
            np.sum( (Y - a[:,np.newaxis] * \
                     ( 1 - np.exp( -np.outer(b, self.timeY) ) ) )**2 , axis=1) + \
            -.5*( theta1**2 + theta2**2 )

    @cached()
    @counted
    def grad_x_log_pdf(self, x, params=None, **kwargs):
        numY = self.numY
        Y = x[:,0:numY]
        theta1=x[:,numY] #The last two components refer to the parameters
        theta2=x[:,numY+1]
        a = .4  + .4*( 1 + erf( theta1/np.sqrt(2) )  )
        b = .01 + .15*( 1 + erf( theta2/np.sqrt(2) )  )
        da_theta1 = .4*np.sqrt(2/np.pi)*np.exp( -theta1**2/2.)
        db_theta2 = .15*np.sqrt(2/np.pi)*np.exp( -theta2**2/2.)
        grad = np.zeros( x.shape )
        for jj in np.arange(numY):
            grad[:,numY] -= -da_theta1/(self.sigma**2) * \
                            ( 1 - np.exp( - b*self.timeY[jj])  ) * \
                            ( Y[:,jj] - a*(1- np.exp(-b*self.timeY[jj])) )
            grad[:,numY+1] -= -1.0/(self.sigma**2)*self.timeY[jj]*db_theta2*a * \
                              np.exp(-b*self.timeY[jj]) * \
                              ( Y[:,jj] - a*(1- np.exp(-b*self.timeY[jj])) )
            grad[:,jj] = -1.0/self.sigma**2 * \
                         ( Y[:,jj] - a*(1-np.exp(-b*self.timeY[jj])) )
        grad[:,-2] -=  theta1
        grad[:,-1] -=  theta2
        return grad

    @counted
    def hess_x_log_pdf(self, x, params=None, **kwargs):
        numY = self.numY
        Y = x[:,0:numY]
        theta1=x[:,numY] #The last two components refer to the parameters
        theta2=x[:,numY+1]
        a = .4  + .4*( 1 + erf( theta1/np.sqrt(2) )  )
        b = .01 + .15*( 1 + erf( theta2/np.sqrt(2) )  )
        da_theta1 = .4*np.sqrt(2/np.pi)*np.exp( -theta1**2/2.)
        db_theta2 = .15*np.sqrt(2/np.pi)*np.exp( -theta2**2/2.)
        d2a_theta1 = -theta1*da_theta1
        d2b_theta2 = -theta2*db_theta2
        Hess_x = np.zeros( (x.shape[0], x.shape[1],  x.shape[1]) )
        for jj in np.arange(numY):
            Hess_x[:,numY,numY]-= \
                -(1-np.exp(-b*self.timeY[jj]))/(self.sigma**2) * \
                ( d2a_theta1*( Y[:,jj] - a*(1- np.exp(-b*self.timeY[jj])) ) - \
                  da_theta1**2*(1-np.exp(-b*self.timeY[jj]))  )
            Hess_x[:,numY+1,numY]-= \
                -da_theta1/(self.sigma**2) * \
                ( db_theta2*self.timeY[jj]*np.exp(-b*self.timeY[jj]) * \
                  (Y[:,jj]-a+a*np.exp(-b*self.timeY[jj])) + \
                  (1-np.exp(-b*self.timeY[jj])) * \
                  (-a*self.timeY[jj]*db_theta2*np.exp(-b*self.timeY[jj])))
            Hess_x[:,numY+1,numY+1]-= \
                -self.timeY[jj]*a/(self.sigma**2) * \
                np.exp(-b*self.timeY[jj]) * \
                ( ( Y[:,jj] - a*(1- np.exp(-b*self.timeY[jj])) ) * \
                  ( d2b_theta2 - self.timeY[jj]*db_theta2**2 ) - \
                  db_theta2**2 *self.timeY[jj]*a*np.exp(-b*self.timeY[jj]))
            Hess_x[:,numY,jj] = da_theta1/(self.sigma**2)*(1-np.exp(-b*self.timeY[jj]))
            Hess_x[:,numY+1,jj] = 1/(self.sigma**2)*self.timeY[jj] * \
                                  db_theta2*a*np.exp(-b*self.timeY[jj])
            Hess_x[:,jj, numY] = Hess_x[:,numY,jj]
            Hess_x[:,jj, numY+1] = Hess_x[:,numY+1, jj]
        Hess_x[:,numY, numY+1] = Hess_x[:,numY+1, numY]
        Hess_x[:,numY,numY]-=1
        Hess_x[:,numY+1,numY+1]-=1
        for kk in np.arange(x.shape[0]):
            for jj in np.arange(numY):
                Hess_x[ kk , jj, jj]  = -1/(self.sigma**2)
        return Hess_x


class TranslatedUniformDistribution(PushForwardTransportMapDistribution):
    def __init__(self, amin, amax):
        tm = FrozenLinearDiagonalTransportMap([amin], [amax-amin])
        d = UniformDistribution()
        super(TranslatedUniformDistribution, self).__init__(tm, d)


class MeasurementMap(Map):
    def __init__(self, times):
        self.times = np.asarray(times)
        super(MeasurementMap, self).__init__(
            dim_in=2, dim_out=len(self.times))
    @cached()
    @counted
    def evaluate(self, x, *args, **kwargs):
        A = x[:,[0]]
        B = x[:,[1]]
        return A * (1. - np.exp( - B * self.times[nax,:] ))
    @cached()
    @counted
    def grad_x(self, x, *args, **kwargs):
        A = x[:,[0]]
        B = x[:,[1]]
        out = np.zeros((x.shape[0], self.dim_out, self.dim_in))
        out[:,:,0] = 1. - np.exp( - B * self.times[nax,:] )
        out[:,:,1] = A * np.exp( - B * self.times[nax,:] ) * self.times[nax,:]
        return out
    @counted
    def hess_x(self, x, *args, **kwargs):
        A = x[:,[0]]
        B = x[:,[1]]
        out = np.zeros((x.shape[0], self.dim_out, self.dim_in, self.dim_in))
        out[:,:,0,1] = np.exp( - B * self.times[nax,:] ) * self.times[nax,:]
        out[:,:,1,0] = out[:,:,0,1]
        out[:,:,1,1] = - A * np.exp( - B * self.times[nax,:] ) * self.times[nax,:]**2
        return out


class JointDistribution(FactorizedDistribution):
    def __init__(self, times, sigma2=1e-3,
                 amin=0.4, amax=1.2, bmin=0.01, bmax=0.31):
        # Set up parameters distributions
        A = TranslatedUniformDistribution(amin, amax)
        B = TranslatedUniformDistribution(bmin, bmax)
        # Set up measurements distributions
        nobs = len(times)
        M = MeanConditionallyNormalDistribution(
            MeasurementMap( times ), np.eye(nobs) * sigma2 )
        # Assemble factorized distribution (measurements first)
        factors = [ (M, list(range(nobs)), [nobs, nobs+1]),
                    (A, [nobs], []),
                    (B, [nobs+1], []) ]
        super(JointDistribution, self).__init__(factors)
    @property
    def times(self):
        return self.factors[0][1].muMap.times


JointDistributionUniformPrior = JointDistribution


class JointDistributionLogNormalPrior(FactorizedDistribution):
    def __init__(self, times, sigma2=1e-3,
                 muA=.9, sigA=.3, muB=.16, sigB=.3):
        # Set up prior distributions
        A = LogNormalDistribution(sigA, 0., muA)
        B = LogNormalDistribution(sigB, 0., muB)
        # Set up measurements distributions
        nobs = len(times)
        M = MeanConditionallyNormalDistribution(
            MeasurementMap( times ), np.eye(nobs) * sigma2 )
        # Assemble factorized distribution (measurements first)
        factors = [ (M, list(range(nobs)), [nobs, nobs+1]),
                    (A, [nobs], []),
                    (B, [nobs+1], []) ]
        super(JointDistributionLogNormalPrior, self).__init__(factors)
    @property
    def times(self):
        return self.factors[0][1].muMap.times


class PosteriorDistribution(BayesPosteriorDistribution):
    def __init__(self, obs, times, sigma2=1e-3,
                 amin=0.4, amax=1.2, bmin=0.01, bmax=0.31):
        # Set up prior distributions
        A = TranslatedUniformDistribution(amin, amax)
        B = TranslatedUniformDistribution(bmin, bmax)
        prior = FactorizedDistribution(
            [ (A, [0], []),
              (B, [1], []) ] )
        # Set up likelihood
        nobs = len(times)
        mmap = MeasurementMap( times )
        noise = NormalDistribution(np.zeros(nobs), sigma2 * np.eye(nobs))
        logL = AdditiveLogLikelihood(obs, noise, mmap)
        # Set up posterior
        super(PosteriorDistribution, self).__init__(logL, prior)


PosteriorDistributionUniformPrior = PosteriorDistribution


class PosteriorDistributionLogNormalPrior(BayesPosteriorDistribution):
    def __init__(self, obs, times, sigma2=1e-3,
                 muA=.9, sigA=.3, muB=.16, sigB=.3):
        # Set up prior distributions
        A = LogNormalDistribution(sigA, 0., muA)
        B = LogNormalDistribution(sigB, 0., muB)
        prior = FactorizedDistribution(
            [ (A, [0], []),
              (B, [1], []) ] )
        # Set up likelihood
        nobs = len(times)
        mmap = MeasurementMap( times )
        noise = NormalDistribution(np.zeros(nobs), sigma2 * np.eye(nobs))
        logL = AdditiveLogLikelihood(obs, noise, mmap)
        # Set up posterior
        super(PosteriorDistributionLogNormalPrior, self).__init__(logL, prior)
