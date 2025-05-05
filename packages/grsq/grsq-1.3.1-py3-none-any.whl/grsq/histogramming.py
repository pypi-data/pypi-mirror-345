import numpy as np
from grsq.accel import get_dists_numba

def calc_debhist(qvec, atoms_l, atoms_m, fl, fm, dr=0.02, l_is_m=False, use_numba=False):
    ''' Calculate the Histogram Approximated Debye Scattering
        between ASE atoms_l and atoms_m, with optional Numba optimization.
    '''
    # Get distances
    pos_l = atoms_l.get_positions()
    pos_m = atoms_m.get_positions()
    if use_numba:
        d = get_dists_numba(pos_l, pos_m)  
    else:
        r = pos_l[:, np.newaxis, :] - pos_m[np.newaxis, :, :]
        r2 = np.sum(r**2, axis=-1)
        d = np.sqrt(r2)
    
    # Take histogram
    bins = np.arange(0, d.max() + dr, dr)
    n = d.shape[0]
    if l_is_m:  # speed up l = m histograms by only taking upper triangle
        n_k, bins = np.histogram(d[np.triu(np.ones((n, n), dtype=bool), k=1)], 
                                 bins=bins, density=False)
    else:
        n_k, bins = np.histogram(d, bins=bins, density=False)

    # Calculate the sum over r_k bins    
    bc = 0.5 * (bins[1:] + bins[:-1])  # center r_k in bin
    the_sum = np.sum(n_k * np.sinc(qvec[:, np.newaxis] * bc / np.pi), axis=1)
    if l_is_m:
        i_binned = fl * fm  * (n + 2 * the_sum)
    else:
        i_binned = fl * fm * (the_sum)
    return i_binned
