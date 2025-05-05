import numpy as np
from math import factorial as fac
from numba import njit, prange

@njit(parallel=True)
def numbye(qvec, natoms, f0, rs, s): # pragma: no cover
    ''' Used by Debye().debye_numba()'''
    for i in prange(natoms):
        for j in prange(i + 1, natoms):
            d = ((rs[i] - rs[j])**2).sum()**0.5
            s += 2 * f0[i, :] * f0[j, :] * np.sinc(qvec * d / np.pi)
        s += f0[i, :]**2
    return s

# pytest coverage doesn't record these properly.


@njit(parallel=True)
def get_dists_numba(pos_l, pos_m): # pragma: no cover
    ''' Get interatomic distances between l and m atoms
        Using numba's parallelisation.
    '''
    n_l = pos_l.shape[0]
    n_m = pos_m.shape[0]
    
    distances = np.zeros((n_l, n_m), dtype=np.float64)
    for i in prange(n_l):
        for j in range(n_m):
            dist = np.sqrt(np.sum((pos_l[i] - pos_m[j])**2))
            distances[i, j] = dist
    return distances