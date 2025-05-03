from __future__ import annotations
import numpy as np

from .mean_var import IncrementalMeanVariance

class IncrementalWelcht:
    """
    Incremental Welch-t between 2 groups (0 and not 0)
    """

    def __init__(self, nsamples):
        """Initialize with the #samples we're computing Welch-t over"""
        nX = nsamples
        self._mv0 = IncrementalMeanVariance(nX)
        self._mv1 = IncrementalMeanVariance(nX)
        self._n = 0

    def add(self, other: IncrementalWelcht):
        """Merges another object of IncrementalWelcht into this object. This is useful in
            parallelized computations, where different nodes compute Welcht-t over different
            ranges of rows"""
        self._mv0.add(other.mv0)
        self._mv1.add(other.mv1)
    
    def update(self, group, row):
        """Updates the Welch-t state with a group id (0 or not 0) and a single row of samples"""
        if group == 0:
            self._mv0.update(row)
        else:
            self._mv1.update(row)
  
    def getWelcht(self):
        """Returns the Welch-t statistic. NaNs are zero'd and a small factor is added in the 
        denominator to prevent infinities"""
        m0 = self._mv0.getMean()
        v0 = self._mv0.getVariance()
        n0 = self._mv0.getN()
        m1 = self._mv1.getMean()
        v1 = self._mv1.getVariance()
        n1 = self._mv1.getN()

        x = (m0 - m1) / np.sqrt((v0 / n0) + (v1 / n1) + 1e-12)

        x = np.nan_to_num(x, copy = False)

        return x

    def getN(self):
        """Number of observations"""
        return self._mv0.getN() + self._mv1.getN()

