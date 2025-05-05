import os, re, copy
import numpy as np
try:
    from scipy.integrate import cumtrapz, trapz
except:
    from scipy.integrate import cumulative_trapezoid as cumtrapz
    from scipy.integrate import trapezoid as trapz
from scipy.optimize import least_squares
from collections import OrderedDict
from grsq.debye import Debye

class RDF:
    ''' Class for representing a pair-RDF sampled between two atom types.

        r: np.ndarray (1, )
            r vector: The r vector defining the bins in which the RDF was sampled, in Å.
        g: np.ndarray, same dim as r
            g(r) values of each r bin
        name1: str
            Name of atomtype/element of 'left' atoms
        name2: str
            Name of atomtype/element of 'right' atoms
        region1: str, 'solute' or 'solvent'
            Which region does the 'left' atom belong to
        region2: str, 'solute', or 'solvent'
            Which region does the 'right' atom belong to.
        n1: int
            Number of atoms of this type 
        n2: int
            Number of atoms of this type
        damp: grsg.damping.Damping
            An instance of the `grsq.damping.Damping` class that provides the damping
            function used in the RDF calculations. See the documentation for
            :class:`~grsq.damping.Damping` for more information on the methods and attributes
            available in the Damping class.
        qvec: np.ndarray (1, )
            Scattering vector, in Å^-1
        rho_norm: str, 'KD' or 'N'
            | Specify which bulk density was used in in obtaining g(r)
            | '(N - KD_ij) / V': As in e.g. VMD
            | 'N/V': As in e.g. MDAnalysis
        r_max: float
            Specify at which r to stop the integration
        r_avg: float
            Use avg. g(r > r_avg) for g0
    '''

    def __init__(self, r, g, name1, name2,
                       region1, region2,
                       n1=None, n2=None,
                       damp=None, volume=None,
                       qvec=None, rho_norm='KD',
                       r_max=None, r_avg=None):
        self.r = r
        self.g = g
        self.name1 = name1
        self.name2 = name2
        self.region1 = region1
        self.region2 = region2

        self.n1 = n1  # number of 'left' atoms
        self.n2 = n2  # number of 'right' atoms

        self.f0_1 = None  # atomic form factors
        self.f0_2 = None

        self.diagonal = (name1 == name2) & (region1 == region2)
        self.cross = (region1 != region2)

        self.damp = damp  # Damping object

        self.volume = volume  # Volume used for the N/V RDF normalization
                              # (Volume of your sim. box)

        self.rho_norm = rho_norm  # Which bulk density has been used in
                                  # calculating g(r), N (MDAnalysis) or N-1 (VMD)

        self.r_max = r_max  # Stop integrating here
        self.r_avg = r_avg  # Use avg. g(r > r_avg) for g0

        self.qvec = qvec  # Wavevector transfer
        self.s = None  # Structure factor.


    def __str__(self):
        return self.get_info()

    def get_info(self):
        ''' Show contents of RDF object'''
        info = f'{self.name1}-{self.region1}--{self.name2}-{self.region2}: ' +\
               f'RDF with {self.n1} particles in {self.region1} and {self.n2} in {self.region2}. ' +\
               f'Volume: {self.volume}'
        return info

    def coordination_number(self, r_min, r_max):
        ''' Calculate the coordination number in the region: r_min >= r > r_max '''
        r = self.r
        g = self.g

        r_mask = np.zeros(len(r), bool)
        r_mask[(r >= r_min) & (r < r_max)] = True

        rho_m = self.n2 / self.volume
        return trapz(4 * np.pi * r[r_mask]**2 * rho_m * g[r_mask], dx=(r[1] - r[0]))

    def structure_factor(self):
        ''' Calculate the structure factor for a given RDF '''
        r = self.r
        g = self.g
        dr = r[1] - r[0]

        avg = 1
        if self.r_avg is not None:
            avg = np.mean(g[r > self.r_avg])

        if self.r_max is not None:
            mask = np.zeros(len(r), bool)
            mask[r < self.r_max] = True
            r = r[mask]
            g = g[mask]

        qr = self.qvec[:, None] * r[None, :]
        r2sin = 4 * np.pi * dr * (np.sinc(qr / np.pi)) * r[None, :]**2

        if (self.region1.lower() == 'solute') and (self.region2.lower() == 'solute'):
            g0 = 0
        else:
            g0 = 1

        h = g - g0 * avg
        if self.damp is not None:
            h *= self.damp.damp(r)

        s = 1 + ((self.n2) / self.volume) * (r2sin @ h)

        # update the rdf inplace with structure factor
        self.s = s

        return s

    def atomic_f0(self, custom_cm=False):
        ''' Calculate atomic form factors and
            update RDF object in place '''
        from grsq import Debye
        db = Debye(self.qvec, custom_cm=custom_cm)
        self.f0_1 = db.atomic_f0(self.name1)
        self.f0_2 = db.atomic_f0(self.name2)

    def i_term1(self, custom_cm=False):
        ''' Coherent X-Ray Scattering, atomic term'''
        kd = int((self.region1 == self.region2) and (self.name1 == self.name2))
        term_1 = np.zeros(len(self.qvec))
        if custom_cm: # reset f0s to recalculate with custom_cm
            self.f0_1 = None
            self.f0_2 = None
        if (self.f0_1 is None) or (self.f0_2 is None):
            self.atomic_f0(custom_cm)
        for n, f0 in zip((self.n1, self.n2), (self.f0_1, self.f0_2)):
            term_1 += (n - kd) * f0**2
        return term_1

    def i_term2(self, custom_cm=False):
        ''' Coherent X-Ray Scattering, interatomic term'''
        kd = int((self.region1 == self.region2) and (self.name1 == self.name2))
        s = self.structure_factor()
        
        # Get form factors
        if custom_cm: # reset f0s to recalculate with custom_cm
            self.f0_1 = None
            self.f0_2 = None
        if (self.f0_1 is None) or (self.f0_2 is None):
            self.atomic_f0(custom_cm=custom_cm)

        term_2 = (s - 1) * (self.n1 - kd) * self.f0_1 * self.f0_2

        self.term_2 = term_2

        return term_2

    def volume_correct(self, Ri):
        rdf = copy.deepcopy(self)
        V = rdf.volume
        N = rdf.n2

        kd = int( (rdf.region1 == rdf.region2) and (rdf.name1 == rdf.name2) )
        Vnew = V - (4 / 3) * Ri**3 * np.pi
        fac = (Vnew / V) * (N / (N - kd))
        return rdf.g * fac

    def perera_correct(self, Ri, r_avg):
        ''' See 10.1016/j.molliq.2010.05.006

            Ri: float
                | Radius of exluced volume - paper recommends kappa is 2 x this.
            r_avg: float
                | Use avg g(r > r_avg)
        '''
        rdf = copy.deepcopy(self)
        kappa = 2 * Ri
        alpha = kappa
        g0_avg = np.mean(rdf.g[(rdf.r > r_avg)])
        fac = 1 + ((1 - g0_avg) / 2) * (1 + np.tanh((rdf.r - kappa) / alpha))
        return rdf.g * fac

    def vdv_correct(self):
        ''' See 10.1080/08927022.2017.1416114
            For best explanation. Only implemented for
            g(r)'s sampled to r_max <= 1/2 x boxsize
        '''
        Nb = self.n2  # Number of b particles in g_ab(r)
        L3 = self.volume  # Volume of square simulation box.
        r = self.r
        g = self.g
        V = (4 / 3) * np.pi * r**3  #  Displaced volume

        kd = int( (self.region1 == self.region2) and
                  (self.name1 == self.name2) ) * int(self.rho_norm == 'N')
        rho_b = Nb / L3

        dNab = cumtrapz(4 * np.pi * r**2 * rho_b * (g - 1),
                        dx=(r[1] - r[0]), initial=0)

        fac = (Nb * (1 - V / L3)) / (Nb * (1 - V / L3) - dNab - kd)
        self.fac = fac
        return g * fac

    def correct(self, method='volume', **kwargs):
        ''' Correct for finite size sampling.

            See 10.1063/5.0164365 for an overview, but please
            cite the original papers of the method(s) you use also.

            method: str: 'volume', 'perera', or 'vegt'
                | volume: Uses the volume-correction. See: 10.1063/5.0164365
                | perera: See 10.1016/j.molliq.2010.05.006
                | vegt: 10.1021/ct301017q
        '''
        if method.lower() == 'volume':
            return self.volume_correct(kwargs['Ri'])
        elif method.lower() == 'perera':
            return self.perera_correct(kwargs['Ri'], kwargs['R_avg'])
        elif method.lower() == 'vegt':
            return self.vdv_correct()

    def fit(self, Ri_guess, fit_start=25, fit_stop=50):
        ''' Fit the exluded volume by minimizing g(r) - 1 in
            the range from fit_start to fit_stop  '''
        self.fit_start = fit_start
        self.fit_stop = fit_stop

        x0 = np.array([Ri_guess])
        opt = least_squares(self._residual, x0)
        return opt

    def _residual(self, x0):
        g = self.volume_correct(x0[0])
        rdf_fit = RDF(self.r, g, self.name1, self.name2,
                     self.region1, self.region2,
                     n1=self.n1, n2=self.n2)
        mask = np.zeros(len(rdf_fit.g), bool)
        mask[(rdf_fit.r > self.fit_start) & (rdf_fit.r < self.fit_stop)] = True
        res = (rdf_fit.g[mask]  - 1)
        return res


class RDFSet(OrderedDict):
    ''' Container object for a set of RDFs.

        For more information, see the :ref:`tutorials-label` page in the project documentation.

        Can be used to calculate the solute-solute, cross, and solvent-solvent
        scattering terms. Given an ``rdfs = RDFSet(...)``

        .. code-block:: python

            >>> qvec = np.arange(0, 10, 0.01)  # define your q range
            >>> damp = Damping('lorch', L=25)  # use a damping window
            >>> I_v = rdfs.get_solvent(qvec=qvec, damp=damp)
            >>> I_c = rdfs.get_cross(qvec=qvec, damp=damp)
            >>> I_u = rdfs.get_solute(qvec=qvec)  # no damping for solute

        You can also apply the van der Vegt finite size correction to all
        (cross and solvent) RDFs:

        .. code-block:: python

            >>> rdfs.vdv_correct()

        And calculate the displaced-volume scattering:

        .. code-block:: python

            >>> rdfs.get_dv(qvec=qvec, damp=damp)

    '''

    def __init__(self, *arg, **kwargs):
        self.rdfs = {}
        super(RDFSet, self).__init__(*arg, **kwargs)

    def __len__(self):
        return len(self.keys())

    def __getitem__(self, key):
        if type(key) == slice:
            tmp = RDFSet()
            if key.step is None:
                step = 1
            else:
                step = key.step
            start = key.start
            if start is None:
                start = 0
            stop = key.stop
            if stop is None:
                stop = len(self.keys())
            if stop < 0:
                stop = len(self.keys()) + stop
            include = list(range(start, stop, step))
            for i, (rdfkey, rdf) in enumerate(self.items()):
                if i in include:
                    tmp[rdfkey] = rdf
            return tmp
        elif key in self.keys():
            return self.get(key)
        elif type(key) == int:  # use numbered indices.
            tmp = [item for i, item in enumerate(self.items()) if i == key][0]
            real_key, rdf = tmp
            return rdf
        else:
            raise Exception("RDF not in set")

    def __setitem__(self, key, rdf):
        if isinstance(key, tuple) and len(key) == 4:
            expected_key = (rdf.name1, rdf.region1, rdf.name2, rdf.region2)
            if key == expected_key:
                super().__setitem__(key, rdf)

    def __add__(self, add):
        tmp = RDFSet()
        for key, rdf in self.items():
            tmp[(rdf.name1, rdf.region1, rdf.name2, rdf.region2)] = rdf
        for key, rdf in add.items():
            tmp[(rdf.name1, rdf.region1, rdf.name2, rdf.region2)] = rdf
        return tmp

    def __eq__(self, other):
        if not isinstance(other, RDFSet):
            return False
        if not len(self) == len(other):
            print(f'Different number of RDFs in sets, {len(self), len(other)}')
            return False
        # compare RDF attributes
        for (key_self, rdf_self), (key_other, rdf_other) in zip(self.items(), other.items()):
            if key_self != key_other:
                print(f'{key_self} != {key_other}')
                return False
            if not (rdf_self.name1 == rdf_other.name1 and
                    rdf_self.region1 == rdf_other.region1 and
                    rdf_self.name2 == rdf_other.name2 and
                    rdf_self.region2 == rdf_other.region2 and
                    rdf_self.volume == rdf_other.volume):
                print('Differences:')
                print(rdf_self.get_info())
                print(rdf_other.get_info())
                return False
            if not (rdf_self.n1 == rdf_other.n1 and
                    rdf_self.n2 == rdf_other.n2):
                print('Different number of atoms:')
                print(rdf_self.get_info())
                print(rdf_other.get_info())
                return False
            if len(rdf_self.g) != len(rdf_other.g):
                print('g(r)s have different length')
                print(rdf_self.get_info())
                print(rdf_other.get_info())
                return False
            if len(rdf_self.r) != len(rdf_other.r):
                print('r has different length')
                print(rdf_self.get_info())
                print(rdf_other.get_info())
                return False
            if not (rdf_self.r == rdf_other.r).all():
                print('g(r) different in')
                print(rdf_self.get_info())
                return False
            if not (rdf_self.g == rdf_other.g).all():
                print('r different in')
                print(rdf_self.get_info())
                return False
        return True


    def add_rdf(self, rdf):
        self[(rdf.name1, rdf.region1, rdf.name2, rdf.region2)] = rdf

    def add_flipped(self, rdf):
        r_rdf = copy.copy(rdf)
        r_rdf.name2 = rdf.name1
        r_rdf.name1 = rdf.name2
        r_rdf.region2 = rdf.region1
        r_rdf.region1 = rdf.region2
        r_rdf.n1 = rdf.n2
        r_rdf.n2 = rdf.n1
        self[(r_rdf.name1, r_rdf.region1,
                   r_rdf.name2, r_rdf.region2)] = r_rdf

    def show(self):
        ''' Show contents of RDFSet. '''
        print(f'|  #  | KEY                     |     STOICHOMETRY     | REGION1, REGION2 | VOLUME ')
        for i, (key, rdf) in enumerate(self.items()):
            key1 = '-'.join(k for k in key[:2])
            key2 = '-'.join(k for k in key[2:])
            keyfmt = f'{key1}--{key2} '
            print(f'| {i:03d} | {keyfmt:24s}| N1: {rdf.n1:5d}, N2: {rdf.n2:5d} | ' +
                  f'{rdf.region1:7s}, {rdf.region2:7s} | {rdf.volume:6.4f} |')


    def get_iq(self, qvec=None, cross=False, damping=None, custom_cm=False):
        ''' Calculate Coherent Scattering from set '''

        V = np.unique([rdf.volume for rdf in self.values()])
        assert len(V) == 1, 'RDFs in set have different volumes!'

        left = set([('-'.join(key[:2]), rdf.n1) for (key,rdf) in self.items()])
        right = set([('-'.join(key[2:]), rdf.n2) for (key,rdf) in self.items()])
        if left != right:
            print('Asymmetric RDF set: not equal amount of XY and YX pairs')
        total_atom_types = left | right

        if qvec is None:
            qvec = self[0].qvec  # take qvec from first RDF

        icoh = np.zeros(len(qvec))
        if not cross:
            deb = Debye(qvec=qvec, custom_cm=custom_cm)
            for atm, n in total_atom_types:
                element = atm.split('-')[0]
                icoh += n * deb.atomic_f0(element)**2

        # 2nd term: Interatomic
        for _, rdf in self.items():
            rdf.qvec = qvec
            if damping is not None:
                rdf.damp = damping
            icoh += rdf.i_term2(custom_cm=custom_cm)
        return icoh

    def vdv_correct(self):
        ''' Apply van der Vegt correction to all
            solute-solvent and solvent-solvent rdfs '''
        for rdf in self.values():
            if (((rdf.region1 == 'solute') and (rdf.region2 == 'solvent')) |
                ((rdf.region1 == 'solvent') and (rdf.region2 == 'solute')) |
                ((rdf.region1 == 'solvent') and (rdf.region2 == 'solvent'))):
                rdf.g = rdf.vdv_correct()
                self.add_rdf(rdf)

    def get_solute(self, qvec=None, damping=None, custom_cm=False):
        ''' Get solute-solute scattering from subset of RDFSet
            It will automatically add Y-X to a set that only has X-Y.
            Which is what you normally want.

            The option to use damping is included for consistency, 
            but be aware that it does not make much sense to use 
            it for the solute-solute term, as all RDFs should 
            go to zero at long r values. 
        '''
        solu = RDFSet()
        for rdf in self.values():
            if (rdf.region1 == 'solute') and (rdf.region2 == 'solute'):
                solu.add_rdf(copy.deepcopy(rdf))
                solu.add_flipped(copy.deepcopy(rdf))
        return solu.get_iq(qvec=qvec, damping=damping, custom_cm=custom_cm)

    def get_solvent(self, qvec=None, damping=None, custom_cm=False):
        ''' Get solvent-only from subset of RDFSet
            It will automatically add Y-X to a set that only has X-Y.
            Which is what you normally want.
        '''
        solv = RDFSet()
        for rdf in self.values():
            if (rdf.region1 == 'solvent') and (rdf.region2 == 'solvent'):
                solv.add_rdf(copy.deepcopy(rdf))
                solv.add_flipped(copy.deepcopy(rdf))
        return solv.get_iq(qvec=qvec, damping=damping, custom_cm=custom_cm)

    def get_cross(self, qvec=None, damping=None, custom_cm=False):
        ''' Get cross-term from subset of RDFSet.
            It will automatically add Y-X to a set that only has X-Y.
            Which is what you normally want. '''
        solu = RDFSet()
        for rdf in self.values():
            if (rdf.region1 == 'solute') and (rdf.region2 == 'solvent'):
                solu.add_rdf(copy.deepcopy(rdf))
                solu.add_flipped(copy.deepcopy(rdf))
            elif (rdf.region1 == 'solvent') and (rdf.region2 == 'solute'):
                solu.add_rdf(copy.deepcopy(rdf))
                solu.add_flipped(copy.deepcopy(rdf))
        return solu.get_iq(qvec=qvec, damping=damping, cross=True, custom_cm=custom_cm)


    def get_dv(self, qvec=None, alpha=1, damping=None, custom_cm=False):
        ''' Displaced Volume Scattering

            1. Make f_dv form factors for all solute types.

            2. Calculate total S_dv
        '''
        solvent_types = []
        solute_types = []
        for key, rdf in self.items():
            if qvec is not None:
                rdf.qvec = qvec
            if damping is not None:
                rdf.damp = damping
            for i in (1, 3):
                if key[i] == 'solvent':
                    solvent_types.append(key[i - 1])
            for i in (1, 3):
                if key[i] == 'solute':
                    solute_types.append(key[i - 1])
        solvent_types = np.unique(solvent_types)
        solute_types = np.unique(solute_types)

        db = Debye(self[0].qvec, custom_cm=custom_cm)  # use qvec of first RDF. They should all be the same anyway.
        f0_solvs = {}
        for st in solvent_types:
            f0_solvs[st] = db.atomic_f0(st)

        f_dvs = {}
        for ut in solute_types:
            fdv = np.zeros(len(self[0].qvec))
            for vt in solvent_types:
                rdf = self[(ut, 'solute', vt, 'solvent')]

                r, g = rdf.r, rdf.g
                dr = r[1] - r[0]
                qr = rdf.qvec[:, None] * r[None, :]
                r2sin = 4 * np.pi * dr * (np.sinc(qr / np.pi)) * r[None, :]**2
                g0 = 1
                h = g - g0
                if rdf.damp is not None:
                    h *= rdf.damp.damp(r)
                fdv += alpha * (rdf.n2 / rdf.volume) * (r2sin @ h) * f0_solvs[vt]
            f_dvs[ut] = (rdf.n1, fdv)

        i_dv = np.zeros(len(self[0].qvec))

        # first term
        for n_l, f_ldv in f_dvs.values():
            i_dv += n_l * f_ldv**2

        # second term - find only solute-solute
        for key, rdf in self.items():
            if 'solvent' in key:
                continue
            n_l, f_ldv = f_dvs[key[0]]
            n_m, f_mdv = f_dvs[key[2]]
            kd = int(key[0] == key[2])

            r, g = rdf.r, rdf.g
            dr = r[1] - r[0]
            qr = rdf.qvec[:, None] * r[None, :]
            r2sin = 4 * np.pi * dr * (np.sinc(qr / np.pi)) * r[None, :]**2
            g0 = 1
            h = g - g0
            if rdf.damp is not None:
                h *= rdf.damp.damp(r)

            i_dv += (f_ldv * f_mdv * n_l * n_m * kd / rdf.volume ) * (r2sin @ h)

        return i_dv

''' Helper Functions'''
def rdfset_from_dir(dirname, prmtop=None, volume=None, stoich=None):
    ''' Read in a directory of rdf files with the naming convention:
            gEl1_w1-El2_w2.dat
        where:
            | El1: Element name 1 (also used for the IAM)
            | El2: Element name 2 (also used for the IAM)
            | w1:  Region of element 1 (u, v) (i.e. solUte, solVent)
            | w2:  Region of element 2 (u, v)

            So e.g. water would have the RDFs: gO_v-O_v.dat, gO_v-H_v.dat, etc..

        prmtop (str): path to structure file for a single frame:
            | The method can read the stoichometry from either a prmtop or an xyzfile.
            | If an xyz file is used, you need to specify the volume in which the RDFs
            | where sampled manually.

        volume (float): RDF sampling volume. Only use if xyz is specified in prmtop

        stoich (dict):
            | {'El1_w1':N1, 'El2_w2:N2 ...}
            | Dictionary containing number of atoms of each element/atom type.
            | Use if no prmtop/xyz is used at all
        '''
    import MDAnalysis as mda
    import glob

    rdf_files = sorted(glob.glob(dirname + os.sep + '*dat'))
    assert len(rdf_files) > 0, f'Found no .dat files in {dirname + os.sep} '

    whered = {'u':'solute', 'v':'solvent'}
    if prmtop is not None:
        # Load universe to get stoichometry.
        u = mda.Universe(prmtop)

    if volume is None:
        # Unfortunately mda cannot get the box size from the prmtop, even though it is there
        with open(prmtop, 'r') as f:
            lines = f.readlines()
        for l, line in enumerate(lines):
            if 'FLAG BOX_DIMENSIONS' in line:
                box = lines[l + 2]
        box = [float(x) for x in box.split()[1:] ]
        V = np.prod(box)
    else:
        V = volume

    set_uc = RDFSet()

    for f, file in enumerate(rdf_files):
        data = np.genfromtxt(file)
        r = data[:, 0]
        g = data[:, 1]

        # find elements from file name. This is very specific to this exact naming scheme...
        file = file.split(os.sep)[-1]
        el1 = re.search('g(.*?)_', file).group(1)
        part1 = re.search(el1 + '_(.*?)-', file).group(1)
        where1 = whered[part1]

        el2 = re.search('-(.*?)_', file).group(1)
        part2 = re.search('-' +  el2 + '_(.*).dat', file).group(1)
        where2 = whered[part2]

        if prmtop is not None:
            Ni = len([atom for atom in u.atoms if el1 == atom.element])
            Nj = len([atom for atom in u.atoms if el2 == atom.element])
        else:
            Ni = stoich[el1 + '_' + part1]
            Nj = stoich[el2 + '_' + part2]

        rdf = RDF(r, g, el1, el2, where1, where2, n1=Ni, n2=Nj)
        rdf.volume = V
        set_uc[(rdf.name1, rdf.region1, rdf.name2, rdf.region2)] = rdf

    return set_uc

