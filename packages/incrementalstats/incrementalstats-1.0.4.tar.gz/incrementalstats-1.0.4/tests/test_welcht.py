import unittest
import numpy as np
import scipy

from incrementalstats import IncrementalWelcht

class IncrementalWelchtTest(unittest.TestCase):
    def testCorrectness(self):
        nsamples = 5
        x = np.random.randn(100,nsamples)
        y = np.random.randn(110,nsamples)

        t_stat, p_value = scipy.stats.ttest_ind(x, y, equal_var=False)

        iw = IncrementalWelcht(nsamples)

        for v in x:
            iw.update(0, v)
        
        for v in y:
            iw.update(1, v)
        
        t_stat2 = iw.getWelcht()

        self.assertTrue(np.allclose(t_stat, t_stat2)) 


if __name__ == "__main__":
    unittest.main(verbosity=2)
