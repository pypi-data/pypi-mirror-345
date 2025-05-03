import unittest
import numpy as np

from incrementalstats import IncrementalMeanVariance, IncrementalCovarianceCorrelation

class IncrementalMeanVarianceTest(unittest.TestCase):
    def testCorrectness(self):
        nX = 10000
        nY = 10
        m = np.random.randn(nX, nY)
        numpy_mean = m.mean(axis=0)
        numpy_variance = m.var(axis=0, ddof=1)
 
        im = IncrementalMeanVariance(nY)
        im1 = IncrementalMeanVariance(nY)
        im2 = IncrementalMeanVariance(nY)
        for row in range(nX):
            im.update(m[row,:])
            if row < (nX // 2):
                im1.update(m[row,:])
            else:
                im2.update(m[row,:]) 
        
        self.assertTrue(np.allclose(im.getMean(), numpy_mean))
        self.assertTrue(np.allclose(im.getVariance(), numpy_variance))

        im1.add(im2)
        
        self.assertTrue(np.allclose(im1.getMean(), numpy_mean))
        self.assertTrue(np.allclose(im1.getVariance(), numpy_variance))        

class IncrementalCovarianceCorrelationTest(unittest.TestCase):
    def testCorrectness(self):
        nX = 10000
        nY1 = 3
        nY2 = 5

        m1 = np.random.randn(nX, nY1)
        m2 = np.random.randn(nX, nY2)
        
        numpy_covariance = (1 / (nX - 1)) * np.matmul((m1 - np.mean(m1, axis=0)).T, (m2 - np.mean(m2, axis=0)))
        numpy_m1_stddev = np.std(m1, axis=0, ddof=1)
        numpy_m2_stddev = np.std(m2, axis=0, ddof=1)
        numpy_1_over_m1_stddev = (1 / numpy_m1_stddev).reshape(numpy_m1_stddev.size, 1)
        numpy_1_over_m2_stddev = (1 / numpy_m2_stddev).reshape(1,numpy_m2_stddev.size)
        numpy_correlation = numpy_covariance * numpy_1_over_m1_stddev * numpy_1_over_m2_stddev
        
        ic = IncrementalCovarianceCorrelation(nY1, nY2)
        ic1 = IncrementalCovarianceCorrelation(nY1, nY2)
        ic2 = IncrementalCovarianceCorrelation(nY1, nY2)
        
        for row in range(nX):
            ic.update(m1[row,:], m2[row,:])
            if row < (nX // 2):
                ic1.update(m1[row,:], m2[row,:])
            else:
                ic2.update(m1[row,:], m2[row,:])                
        
        self.assertTrue(np.allclose(ic.getCovariance(), numpy_covariance))
        self.assertTrue(np.allclose(ic.getCorrelation(), numpy_correlation))
        
        ic1.add(ic2)
        
        self.assertTrue(np.allclose(ic1.getCovariance(), numpy_covariance))
        self.assertTrue(np.allclose(ic1.getCorrelation(), numpy_correlation))

        self.assertTrue(np.allclose(ic1._imX.getMean(), ic._imX.getMean()))
        self.assertTrue(np.allclose(ic1._imY.getMean(), ic._imY.getMean()))
        self.assertTrue(np.allclose(ic1._imX.getVariance(), ic._imX.getVariance()))
        self.assertTrue(np.allclose(ic1._imY.getVariance(), ic._imY.getVariance()))
        
if __name__ == "__main__":
    unittest.main(verbosity=2)
