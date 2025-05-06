cimport numpy as cnp
import numpy as np
cimport cython
from libc.math cimport sqrt

from cython cimport boundscheck, wraparound

# Define types for NumPy arrays
ctypedef cnp.float64_t DTYPE_t

@cython.boundscheck(False)  # Disable bounds checking for speed
@cython.wraparound(False)   # Disable negative indexing
cdef double compute_point_biserial(DTYPE_t[:, :] distances, cnp.int64_t[:] labels, int n_samples):
    cdef int i, j, k, cluster
    cdef int n_clusters = len(set(labels))
    cdef double[:] within = np.zeros(n_samples * n_samples, dtype=np.float64)
    cdef double[:] between = np.zeros(n_samples * n_samples, dtype=np.float64)
    cdef int within_count = 0
    cdef int between_count = 0
    cdef double within_sum = 0.0, between_sum = 0.0
    cdef double mean_diff, std_dev, total_sum = 0.0, total_sq_sum = 0.0
    cdef int total_count = 0

    # Collect within- and between-cluster distances
    for cluster in range(1, n_clusters + 1):  # Assuming labels start at 1
        for i in range(n_samples):
            if labels[i] == cluster:
                for j in range(n_samples):
                    if labels[j] == cluster:
                        within[within_count] = distances[i, j]
                        within_sum += distances[i, j]
                        within_count += 1
                    else:
                        between[between_count] = distances[i, j]
                        between_sum += distances[i, j]
                        between_count += 1

    # Compute means
    if within_count == 0 or between_count == 0:
        return np.nan

    cdef double within_mean = within_sum / within_count
    cdef double between_mean = between_sum / between_count

    # Compute standard deviation of combined distances
    for i in range(within_count):
        total_sum += within[i]
        total_sq_sum += within[i] * within[i]
        total_count += 1
    for i in range(between_count):
        total_sum += between[i]
        total_sq_sum += between[i] * between[i]
        total_count += 1

    cdef double mean = total_sum / total_count
    std_dev = sqrt((total_sq_sum / total_count) - (mean * mean))

    if std_dev == 0:
        return np.nan

    return (between_mean - within_mean) / std_dev

# Python wrapper
def point_biserial(double[:, :] distances, labels):
    return compute_point_biserial(distances, labels, distances.shape[0])
