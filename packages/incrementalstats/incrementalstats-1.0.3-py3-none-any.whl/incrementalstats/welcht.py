# function tval(m1, m2, v1, v2, n1, n2)
#     x = (m1 - m2) / sqrt((v1 / n1) + (v2 / n2) + eps(0.0))
#     if isnan(x)
#         return 0.0
#     else
#         return x
#     end
# end


from __future__ import annotations
import numpy as np

from .mean_var import IncrementalMeanVariance

class IncrementalWelcht:
    """
    Incremental Welch-t between 2 groups
    """

    def __init__(self, nsamples):
        """Initialize with the #samples we're computing Welch-t over"""
        nX = nsamples
        self.mv0 = IncrementalMeanVariance(nX)
        self.mv1 = IncrementalMeanVariance(nX)
        self.n = 0

    def add(self, other: IncrementalWelcht):
        self.mv0.add(other.mv0)
        self.mv1.add(other.mv1)
    
    def update(self, group, row):
        if group == 0:
            self.mv0.update(row)
        else:
            self.mv1.update(row)
  
    def getWelcht(self):
        m0 = self.mv0.getMean()
        v0 = self.mv0.getVariance()
        n0 = self.mv0.n
        m1 = self.mv1.getMean()
        v1 = self.mv1.getVariance()
        n1 = self.mv1.n

        x = (m0 - m1) / np.sqrt((v0 / n0) + (v1 / n1) + 1e-12)

        x = np.nan_to_num(x, copy = False)

        return x
