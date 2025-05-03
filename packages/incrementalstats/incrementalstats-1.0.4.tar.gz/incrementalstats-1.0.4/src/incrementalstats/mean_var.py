from __future__ import annotations
import numpy as np

class IncrementalMeanVariance:
    """Incrementally computes vectorized mean and variance.

    When feeding every row of an MxN matrix, this code
    computes the mean/variance over axis 0 of this matrix, as
    demonstrated in the example below.

    This code is useful when the matrix cannot be not present
    in memory at one given time.

    ```
    import numpy as np
    from risca.statistics import IncrementalMeanVariance

    nX = 100
    nY = 10
    m = np.random.randn(nX, nY)

    im = IncrementalMeanVariance(nY)
    for row in range(nX):
        im.update(m[row,:])

    reference_mean = m._mean(axis=0)
    reference_variance = m._var(axis=0, ddof=1)
    assert np.allclose(im.getMean(), reference_mean)
    assert np.allclose(im.getVariance(), reference_variance)
    ```

    """

    def __init__(self, ncolumns):
        """Initialize with the #columns of the hypothetical matrix M over
        which we will compute the mean / variance"""
        nX = ncolumns
        self._nX = nX
        self._mean = np.zeros(nX, dtype=np.float64)
        self._var = np.zeros(nX, dtype=np.float64)
        self._n = 0

    def add(self, other: IncrementalMeanVariance):
        """Merges another object of IncrementalMeanVariance into this mean/variance. This is useful in
        parallelized computations, where different nodes compute mean/variance over different
        ranges of rows"""
        x = other
        n = self._n + x._n
        delta = x._mean - self._mean
        self._mean += x._n * (delta / n)
        self._var += x._var + self._n * x._n * delta ** 2 / n
        self._n = n

    def update(self, row):
        x = row
        """Updates the mean/variance with a single row. """
        if len(x) != self._nX:
            raise Exception("wrong length")

        self._n += 1
        y1 = x - self._mean
        self._mean += y1 / self._n
        y2 = x - self._mean
        self._var += y1 * y2

    def getMean(self):
        """Returns the current mean"""
        return self._mean.copy()

    def getVariance(self):
        """Returns the current variance"""
        if self._n < 2:
            raise Exception("not enough data")
        return 1/(self._n - 1) * self._var

    def getN(self):
        """Number of observations"""
        return self._n