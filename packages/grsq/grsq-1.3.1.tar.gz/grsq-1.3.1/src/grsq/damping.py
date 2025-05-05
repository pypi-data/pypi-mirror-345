import numpy as np 

class Damping:
    '''
    Class that applies a damping window function to ( g(r) - 1 ) in the
    generalized debye integral. 

    Instantiate the object and add it to your RDF(), 
    e.g. 

    .. code-block:: python 

        >>> L = 25  # for a 50 Å cell
        >>> damp = Damping('lorch', L=L)
        >>> rdf = RDF(..., damp=damp)

        
    You can also instruct an ``RDFSet`` to use the same damping 
    for each RDF to calculate the full scattering signal 

    .. code-block:: python   
    
        >>> rdfs = RDFSet(...)
        >>> damp = Damping('lorch', L=25)
        >>> rdfs.get_iq(damping=damp)

    Parameters:
        style (str): can be either of these:
            | 'lorch': sin(pi*L) / pi*L
            | 'dhabal': as in 10.1039/c6cp07599a
            | 'zederkof': as above but with an r_cut as well. 10.1021/jacs.2c04505
            | 'panman': Exponential fade function, e.g. PhysRevLett.125.226001

        L: Float (for Lorch damping)
            | Damping factor for the lorch damping, usually 1/2 of
            | the box length.
        r_max: Float  (for Dhabal, Zederkof, Panman)
            | The r-value where the rdf should be 0
        r_cut: Float (only for zederkof damping)
            | When to start the smooth cutoff. Everything before
            | is untouched.
    '''
    def __init__(self, style, L=None, r_max=None, r_cut=None):
        self.style = style
        self.L = L
        self.r_max = r_max
        self.r_cut = r_cut

    def lorch(self, R):
        ''' Lorch-like damping '''
        damp = self.L
        return np.sinc(R / damp)

    def panman(self, R):
        ''' Damping like in PhysRevLett.125.226001 '''
        fade = self.L
        mask = R > fade
        damping = np.ones(len(R))
        damping[mask] = np.exp(-(R[mask] / fade - 1)**2)
        return damping

    def dhabal(self, R):
        ''' Damping like in 10.1039/c6cp07599a '''
        r_max = self.r_max
        fac = (1 - 3*(R/r_max)**2) * (R <= r_max/3) +\
               3 / 2 * (1-2*(R/r_max) +\
               (R/r_max)**2) * ((r_max / 3 < R) & (r_max > R))

        return fac

    def zederkof(self, R):
        ''' Damping like in 10.1021/jacs.2c04505 '''
        r_max = self.r_max
        r_cut = self.r_cut

        fac = 1 * (R < r_cut) +\
              (1 - 3 * ((R - r_cut) / (r_max - r_cut))**2) * ((R <= 2 * r_cut / 3 + r_max / 3) & (R >= r_cut)) +\
              3 / 2 * (1 - 2 * ((R - r_cut) / (r_max - r_cut)) +
              (( R - r_cut) / (r_max - r_cut))**2) * ((R > 2 * r_cut / 3 + r_max / 3) & (r_max > R))
        return fac

    def damp(self, R):
        ''' Apply the chosen damping '''
        if self.style == 'lorch':
            damping = self.lorch
        elif self.style == 'dhabal':
            damping = self.dhabal
        elif self.style == 'zederkof':
            damping = self.zederkof
        elif self.style == 'panman':
            damping = self.panman
        else:
            raise RuntimeError(f'Damping style not understood: {self.style}')

        return damping(R)
