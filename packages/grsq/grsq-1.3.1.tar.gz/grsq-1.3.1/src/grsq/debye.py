import numpy as np
from periodictable import cromermann
from grsq.accel import numbye
from grsq.histogramming import calc_debhist
import periodictable as pt

class Debye:
    ''' Discrete Interatomic-Distance Debye Scattering. 

    .. code-block:: none   

            ___N  ___N
            \    \                       sin(q · r_ij)
      I(q) = )    )   f_i(q) · f_j(q) · ---------------
            /__  /__                       q · r_ij
            i=1  j=1

    where:
       | I(q)    : Scattering intensity as a function of the momentum transfer q.
       | N       : Total number of atoms.
       | f_i, f_j: Atomic form actors for atoms i and j, respectively.
       | r_ij    : Distance between atoms i and j.
       | q       : Momentum transfer, or scattering vector.

       The atomic form factors are generated from the Cromer Mann parameters
       from Waasmaier, A. Kirfel Acta Cryst. A51, 416-431 (1995), using 
       the python library ``periodictable``  
       NB: This assumes neutral atoms. See the tutorials for how to
       use parameters for charged atoms. 
    
       
       Usage:

       .. code-block:: python   
       
           >>> from grsq.debye import Debye
           >>> from ase.io import read
           >>> atoms = read('./tests/data/xray_2particle/test.xyz')  # read e.g. xyz file as ASE atoms object
           >>> deb = Debye(qvec=np.arange(0, 20, 0.01))
           >>> i_deb = deb.debye(atoms)

   
    Parameters:
        qvec: np.ndarray (1, )
               your Q vector
        custom_cm: None or dict
               Will use either the standard Waasmeier & Kirfel
               Cromer-Mann parameters from periodictable
               or you can enter your own dictionary of CM parameters
               in the following format:

              .. code-block:: python   

                      >>> cm = {'Pt': {'a': np.array([27.00590, 17.76390, 15.71310, 5.783700]),
                      >>>              'b': np.array([1.512930, 8.811740, 0.4245930, 38.61030]),
                      >>>              'c': 11.68830}}


    '''

    def __init__(self, qvec=None, custom_cm=None):
        if qvec is None:
            qvec = np.arange(0.0001, 10, 0.01)
        self.qvec = qvec  # q vector
        self.f0 = None
        self.f0_elements = None
        self.custom_cm = custom_cm

        assert len(qvec.shape) == 1, 'Q-vector shape must be (N, )'

    def atomic_f0(self, atom):
        ''' Calculate atomic form factor for a single atom type. 
       
            atom: str
              Name of the atom type
        '''
        if self.custom_cm:
            f0 = self.custom_cm[atom]['c']
            a = self.custom_cm[atom]['a']
            b = - self.custom_cm[atom]['b']

            q2 = (self.qvec / (4 * np.pi))**2
            for n in range(len(a)):
                f0 += a[n] * np.exp(b[n] * q2)
        else:
            f0 = cromermann.fxrayatq(atom, self.qvec)

        return f0

    def update_f0(self, atoms, custom_elements=None):
        ''' Update atomic form factors in the object '''
        if self.f0 is None:
            self.f0_elements = atoms.get_chemical_symbols()
            if custom_elements:
                self.f0_elements = custom_elements
            f0 = np.array([self.atomic_f0(sym) for sym in self.f0_elements])
            self.f0 = f0
        else:  # if the atoms have changed:
            these_syms = atoms.get_chemical_symbols()
            if these_syms != self.f0_elements:
                self.f0_elements = these_syms
                f0 = np.array([self.atomic_f0(sym) for sym in self.f0_elements])
                self.f0 = f0

    def debye_numba(self, atoms, custom_elements=None):
        ''' Faster implementation, using numba. 
            Useful if you need to do a _lot_ of evaluations. 
        '''

        self.update_f0(atoms, custom_elements)
        f0 = self.f0

        rs = atoms.get_positions()
        s = numbye(self.qvec, len(atoms), f0, rs, np.zeros(len(self.qvec)))
        return s

    def debye(self, atoms, custom_elements=None):
        ''' Debye Scattering from ASE atoms object
        
            atoms: ase.Atoms object
                atoms to calculate the scattering from
            custom_elements: list
                list of strings defining the atom types 
                in your Atoms object. If None, the elements 
                from the Atoms object will be used.
        '''

        s = np.zeros(len(self.qvec))
        self.update_f0(atoms, custom_elements)
        f0 = self.f0

        rs = atoms.get_all_distances()
        for q, qq in enumerate(self.qvec):
            for i in range(len(atoms)):
                s[q] += np.sum(f0[i, q] * f0[:, q] *
                               np.sinc(qq * rs[i, :] / np.pi))

        return s

    def debye_selective(self, atoms, idx1, idx2, custom_elements=None):
        ''' Only terms between atoms in lists idx1 and idx2
            (but not between atoms in either list) '''

        s = np.zeros(len(self.qvec))
        self.update_f0(atoms, custom_elements)
        f0 = self.f0

        rs = atoms.get_all_distances()
        for q, qq in enumerate(self.qvec):
            for i in idx1:
                s[q] += np.sum(f0[i, q] * f0[idx2, q] *
                               np.sinc(qq * rs[i, idx2] / np.pi))

        return s
    
    def debye_histogrammed(self, atoms, dr=0.05, use_numba=False):
       ''' Histogrammed Debye Approximation. 

       Parameters:
           atoms: (ASE Atoms object)
              The atoms to calculate the scattering from
           dr: (float)
              Histogram bin size. Smaller -> slower, more accurate
           numba: (bool)
              True: Calculate distances with parallal numba implementation,
              or False: with simple numpy broadcasting. 
              Numba might speed up _very_ large calculations slightly. 
       '''

       # Get atom types, currently simply elements
       syms = np.array(atoms.get_chemical_symbols())
       atom_types = np.unique(syms)

       # Only need 1 f0 for each atom type
       f0s = {el:self.atomic_f0(el) for el in atom_types}

       # Loop over all atom type combos, AB, AC, BC, ... 
       # (but not BA, CA, CB since XY = YX)
       i_tot = np.zeros(len(self.qvec))
       for l, el1 in enumerate(atom_types):
              for m, el2 in enumerate(atom_types[l:]):
                     mask_l = syms == el1
                     mask_m = syms == el2

                     x = 1 if el1 == el2 else 2
                     this_i = calc_debhist(self.qvec, 
                                           atoms[mask_l], atoms[mask_m], 
                                           f0s[el1], f0s[el2], 
                                           l_is_m=el1 == el2, dr=dr,
                                           use_numba=use_numba)
                     i_tot += this_i * x
       return i_tot
    

def populate_cm():
    ''' Helper method to get all Cromer Mann parameters
        from the periodictable library
    '''
    all_cm = {}
    for el in pt.elements:
       try:
           cm = cromermann.getCMformula(str(el))
           all_cm[str(el)] = {'a':cm.a, 'b':cm.b, 'c':cm.c}
       except:
           pass
    return all_cm

def get_cm(species):
    cm = {species:{}}
    try:
        pt_cm = cromermann.getCMformula(str(species))
        cm[str(species)] = {'a':pt_cm.a, 'b':pt_cm.b, 'c':pt_cm.c}
    except:
        print(f'{species} not found in periodictable database')
        print('periodictable expects charged atoms in this format: Na1+')
        print('Maybe check https://www.classe.cornell.edu/~dms79/x-rays/f0_CromerMann.txt')
    return cm


# Cromer mann coefficients from an older parametrization:
# look in f0_cromermann.txt here:
# https://www.classe.cornell.edu/~dms79/x-rays/f0_CromerMann.txt
# These are only here for consistency with previous work, and will
# only be used if specifically asked for:
# >>> from grsq.debye import old_cm
# >>> deb = Debye(custom_cm=old_cm)
old_cm = {
       'Pt': {'a': np.array([27.00590, 17.76390, 15.71310, 5.783700]),
              'b': np.array([1.512930, 8.811740, 0.4245930, 38.61030]),
              'c': 11.68830},
       'Ag': {'a': np.array([19.28080, 16.68850, 4.804500, 1.046300]),
              'b': np.array([0.6446000, 7.472600, 24.66050, 99.81560]),
              'c': 5.179000},
       'Ir': {'a': np.array([30.70580, 15.55120, 14.23260, 5.536720]),
              'b': np.array([1.309230, 6.719830, 0.1672520, 17.49110]),
              'c': 6.968240},  # TODO: This is Ir4+.
       'Fe': {'a': np.array([11.04240, 7.374000, 4.134600, 0.4399000]),
              'b': np.array([4.653800, 0.3053000, 12.05460, 31.28090]),
              'c': 1.009700},  # TODO: This is Fe2+. Needs flexibility
       'P':  {'a': np.array([6.434500, 4.179100, 1.780000, 1.490800]),
              'b': np.array([1.906700, 27.15700, 0.5260000, 68.16450]),
              'c': 1.114900},
       'O':  {'a': np.array([3.048500, 2.286800, 1.546300, 0.8670000]),
              'b': np.array([13.27710, 5.701100, 0.3239000, 32.90890]),
              'c': 0.2508000},
       'C':  {'a': np.array([2.310000, 1.020000, 1.588600, 0.8650000]),
              'b': np.array([20.84390, 10.20750, 0.5687000, 51.65120]),
              'c': 0.2156000},
       'N':  {'a': np.array([12.21260, 3.13220, 2.01250, 1.166300]),
              'b': np.array([5.701e-3, 9.89330, 28.9975, 0.582600]),
              'c': -11.52900},
       'H':  {'a': np.array([0.4930020, 0.3229120, 0.1401910, 4.081e-2]),
              'b': np.array([10.51090, 26.12570, 3.142360, 57.79970]),
              'c': 3.0380001e-03},
       'Na': {'a': np.array([3.256500, 3.936200, 1.399800, 1.003200]),
              'b': np.array([2.667100, 6.115300, 0.2001000, 14.03900]),
              'c': 0.4040000},
       'I':  {'a': np.array([20.23320, 18.99700, 7.806900, 2.886800]),  # I-
              'b': np.array([4.347000, 0.3814000, 27.76600, 66.87760]),
              'c': 4.071200},
       'I0': {'a': np.array([20.14720, 18.99490, 7.513800, 2.273500]),
              'b': np.array([4.347000, 0.3814000, 27.76600, 66.87760]),
              'c': 4.071200},
       'Tl': {'a': np.array([21.39850, 20.47230, 18.74780, 6.828470]),   # Tl+
              'b': np.array([1.471100, 0.5173940, 7.434630, 28.84820]),
              'c': 12.52580},
       'Si': {'a': np.array([4.439180, 3.203450, 1.194530, 0.4165300]),   # Si4+
              'b': np.array([1.641670, 3.437570, 0.2149000, 6.653650]),
              'c': 0.7462970},
       'B':  {'a': np.array([2.054500, 1.332600, 1.097900, 0.7068000]),
              'b': np.array([23.21850, 1.021000, 60.34980, 0.1403000]),
              'c': -0.1932000},
       'S':  {'a': np.array([6.905300, 5.203400, 1.437900, 1.58630]),
              'b': np.array([1.467900, 22.21510, 0.2536000, 56.17200]),
              'c': 0.8669000},
       'Cl': {'a': np.array([11.46040, 7.196400, 6.255600, 1.645500]),
              'b': np.array([1.0400000E-02, 1.166200, 18.51940, 47.77840]),
              'c': -9.557400},
       'Ar': {'a': np.array([7.484500, 6.772300, 0.6539000, 1.644200]),
              'b': np.array([0.9072000, 14.84070, 43.89830, 33.39290]),
              'c': 1.444500}
              }