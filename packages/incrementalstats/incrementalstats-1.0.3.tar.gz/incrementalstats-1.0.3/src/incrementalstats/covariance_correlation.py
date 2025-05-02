from __future__ import annotations
import numpy as np

from .mean_var import IncrementalMeanVariance

class IncrementalCovarianceCorrelation:
    """Incrementally computes vectorized covariance and correlation.

    When feeding every row of an MxN matrix A and every row of an MxO matrix B, this code
    updates a co-variance NxO matrix C where every cell C[r,c] is the covariance between
    A[:,r] and B[:,c].

    This code is useful when the matrixes A and B cannot be not present
    in memory at one given time.

    ```
    nX = 100
    nY1 = 30
    nY2 = 50

    m1 = np.random.randn(nX, nY1)
    m2 = np.random.randn(nX, nY2)

    ic = IncrementalCovarianceCorrelation(nY1, nY2)

    for row in range(nX):
        ic.update(m1[row,:], m2[row,:])

    reference_covariance = (1 / (nX - 1)) * np.matmul((m1 - np.mean(m1, axis=0)).T, (m2 - np.mean(m2, axis=0)))
    reference_m1_stddev = np.std(m1, axis=0, ddof=1)
    reference_m2_stddev = np.std(m2, axis=0, ddof=1)
    reference_1_over_m1_stddev = (1 / numpy_m1_stddev).reshape(numpy_m1_stddev.size, 1)
    reference_1_over_m2_stddev = (1 / numpy_m2_stddev).reshape(1,numpy_m2_stddev.size)
    reference_correlation = numpy_covariance * numpy_1_over_m1_stddev * numpy_1_over_m2_stddev

    assert (np.allclose(ic.getCovariance(), reference_covariance))
    assert (np.allclose(ic.getCorrelation(), reference_correlation))

    ```
    """

    def __init__(self, nX, nY):
        """Initialize with the #columns for matrices A and B"""
        self.nX = nX
        self.nY = nY
        self.imX = IncrementalMeanVariance(nX)
        self.imY = IncrementalMeanVariance(nY)
        self.cov = np.zeros((nX, nY), dtype=np.float64)
        self.n = 0

    def update(self, x, y):
        """Updates the covariance matrix with a single row of matrix A and a single row of matrix B"""
        if len(x) != self.nX:
            raise Exception("wrong x length")
        if len(y) != self.nY:
            raise Exception("wrong y length")

        self.n += 1
        f = (self.n - 1) / self.n

        mfX = (x - self.imX.mean) * f
        mfY = y - self.imY.mean

        self.cov += np.tensordot(mfX, mfY, axes=0)

        self.imX.update(x)
        self.imY.update(y)

    def add(self, x: IncrementalCovarianceCorrelation):
        """Merges another object of IncrementalCovarianceCorrelation into this co-variance matrix. This is useful in
        parallelized computations, where different nodes compute co-variances over different
        ranges of rows"""
        n = self.n + x.n
        f = (self.n * x.n ** 2 + x.n * self.n ** 2) / (n ** 2)

        deltaX = self.imX.mean - x.imX.mean
        deltaX = deltaX.reshape(deltaX.size, 1) * f

        deltaY = self.imY.mean - x.imY.mean
        deltaY = deltaY.reshape(1, deltaY.size)

        self.cov += x.cov + deltaX * deltaY
        self.n = n
        self.imX.add(x.imX)
        self.imY.add(x.imY)

    def getCovariance(self):
        """Returns the scaled co-variance matrix with 1 degree of freedom"""
        return 1 / (self.n - 1) * self.cov

    def getCorrelation(self):
        """Returns Pearson's correlation matrix"""
        sX = 1 / np.sqrt(self.imX.getVariance())
        sX = sX.reshape(sX.size, 1)
        sY = 1 / np.sqrt(self.imY.getVariance())
        sY = sY.reshape(1, sY.size)
        return 1 / (self.n - 1) * self.cov * sX * sY
