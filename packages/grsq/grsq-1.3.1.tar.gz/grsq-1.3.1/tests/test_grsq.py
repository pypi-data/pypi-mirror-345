"""
Unit and regression test for the grsq package.

run:
    `python -m pytest --cov-report=html --cov=src .`
in the root dir of the package to generate covereage report
"""

# Import package, test suite, and other packages as needed
import sys, copy, glob
import pytest
import numpy as np
from ase.io import read

try: # this is NOT how this is supposed to be done I think...
    from grsq import Debye, Damping
    from grsq import RDF, RDFSet, rdfset_from_dir
except:
    sys.path.append('src/')
    from grsq import Debye
    from grsq import Debye, Damping
    from grsq import RDF, RDFSet, rdfset_from_dir


def test_grsq_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "grsq" in sys.modules


def test_twoparticle_solute():
    atoms = read('tests/data/xray_2particle/test.xyz')
    deb = Debye(qvec=np.arange(0, 20, 0.01))
    i_deb = deb.debye(atoms)

    stoich = {'Pt_u':2}
    V = 10**3

    rdf_dat = np.genfromtxt('tests/data/xray_2particle/gPt_u-Pt_u.dat')

    rdf = RDF(rdf_dat[:, 0], rdf_dat[:, 1], 'Pt', 'Pt', 'solute', 'solute', qvec=deb.qvec)
    rdf.n1 = 2
    rdf.n2 = 2
    rdf.volume = V

    iq = rdf.i_term1()
    iq += rdf.i_term2()
    assert np.max(np.abs(deb.qvec, i_deb - iq)) < 20


def test_threeparticle_solute():
    ''' Tests the loader function and the RDFset Class '''
    qvec = np.arange(0, 20, 0.01)

    rdfs = rdfset_from_dir('tests/data/xray_3particle/',
                           'tests/data/xray_3particle/ptptar.xyz', volume=10**3)

    atoms = read('tests/data/xray_3particle/ptptar.xyz')
    deb = Debye(qvec=qvec)
    i_deb = deb.debye(atoms)
    num_electrons_squared = sum(atoms.get_atomic_numbers())**2

    i_g_u = rdfs.get_solute(qvec)  # solute-only (of solute only RDFs)
    i_g = rdfs.get_iq(qvec)

    assert np.sum(np.abs(i_g_u - i_g)) < 1e-9
    assert np.max(np.abs(deb.qvec, i_deb - i_g)) < 20
    assert np.abs(i_deb[0] - num_electrons_squared) < 25
    assert np.abs(i_g[0] - num_electrons_squared) < 25

def test_coordnum():
    ''' Test that the coordination number method gets counts 2 Pt from Ar 
        in the PtPtAr system
    '''

    rdfs = rdfset_from_dir('tests/data/xray_3particle/',
                           'tests/data/xray_3particle/ptptar.xyz', volume=10**3)

    rdf = rdfs[0]
    assert rdf.coordination_number(0, 100) - 2 < 1e-6

def test_water():
    ''' Testing versus reference values saved in npy '''
    ig_v_correct, ig_a_correct, igc_v_correct = np.load('tests/data/xray_water/watertest.npy')
    V = 122900.85207774633
    stoich = {'H_v': 8190, 'O_v': 4095}
    qvec = np.arange(0, 10, 0.05)

    rdfs = rdfset_from_dir('tests/data/xray_water/', volume=V, stoich=stoich)
    ig_v = rdfs.get_solvent(qvec)
    ig_a = rdfs.get_iq(qvec)

    # Test vdv correction against reference
    rdfs.vdv_correct()
    igc_v = rdfs.get_solvent(qvec)

    assert np.sum(ig_v_correct - ig_v) < 1e-9
    assert np.sum(ig_a_correct - ig_a) < 1e-9
    assert np.sum(igc_v_correct - igc_v) < 1e-9

def test_adding():
    ''' Testing addition (and slicing) '''
    ig_v_correct, ig_a_correct, igc_v_correct = np.load('tests/data/xray_water/watertest.npy')
    V = 122900.85207774633
    stoich = {'H_v': 8190, 'O_v': 4095}
    qvec = np.arange(0, 10, 0.05)

    rdfs = rdfset_from_dir('tests/data/xray_water/', volume=V, stoich=stoich)
    rdfs_new = rdfs[:2] + rdfs[2:]  # slice and add

    old = rdfs.get_iq(qvec)
    new = rdfs_new.get_iq(qvec)

    assert ((old - new ) == 0).all()

def test_corrections_dampings():
    ''' Test that all volume corrections and FT windows
        gives results within 12 % of each other when tuned
        correctly.  On MDAnalysis sampled water. '''
    V = 122900.85207774633
    stoich = {'H_v': 8190, 'O_v': 4095}
    rdfs_raw = rdfset_from_dir('tests/data/mda_water/', volume=V, stoich=stoich)
    r_max = rdfs_raw[0].r[-1]

    lrh = Damping('lorch', L=r_max)
    zkf = Damping('zederkof', r_max=r_max, r_cut=r_max-1)
    dhb = Damping('dhabal', r_max=r_max)
    fad = Damping('panman', L=10)
    dampings = [lrh, zkf, dhb, fad]
    corrections = ('volume', 'perera', 'vegt')

    qvec = np.arange(0, 6, 0.01)
    results = np.zeros((len(qvec), 13))

    ct = 0
    for c, corr in enumerate(corrections):
        for d, damp in enumerate(dampings):
            rdfs = copy.deepcopy(rdfs_raw)
            for rdf in rdfs.values():
                rdf.rho_norm = 'N'
                r_first_nonzero = rdf.r[np.where(rdf.g > 0)[0]][0]
                r_c = r_first_nonzero - 0.5
                corr_vars = ({'Ri':r_c}, {'Ri':r_first_nonzero, 'R_avg':10.6579}, {})
                rdf.g = rdf.correct(method=corr, **(corr_vars[c]))
                rdf.damp = damp

            iq = rdfs.get_solvent(qvec=qvec)
            results[:, ct] = iq
            ct += 1

    rdfs = copy.deepcopy(rdfs_raw)
    for rdf in rdfs.values():
        rdf.rho_norm = 'N'
        r_first_nonzero = rdf.r[np.where(rdf.g > 0)[0]][0]
        r_c = r_first_nonzero - 0.5
        opt = rdf.fit(r_c, fit_start=15, fit_stop=r_max)
        print(opt.x[0], r_c)
        rdf.g = rdf.correct(method='volume', Ri=opt.x[0])
        rdf.damp = lrh
    iq = rdfs.get_solvent(qvec=qvec)
    results[:, ct] = iq

    assert np.max(np.abs(np.diff(results, axis=-1) / np.mean(results, axis=-1)[:, None])) < 0.12


def test_cross_dv():
    ''' Assert that the cross term and DV term of an LJ fluid
        are the same as at the point of publication
    '''
    def get_data(fdir):
        uv_files = sorted(glob.glob(fdir + '/*gAr_u-Ar_v.dat'))
        vv_files = sorted(glob.glob(fdir + '/*gAr_v-Ar_v.dat'))
        out = []
        for files in (uv_files, vv_files):
            tmp = np.genfromtxt(files[0])
            rdfs = np.zeros((tmp.shape[0], tmp.shape[1], len(files)))
            for f, fil in enumerate(files):
                dat = np.genfromtxt(fil)
                rdfs[:, :, f] = dat
            out.append(np.mean(rdfs, axis=-1))
        return out

    qvec = np.arange(0, 6, 0.005)
    dat = get_data('tests/data/xray_lj/')
    V = 100**3
    rdf_uv = RDF(r=dat[0][:, 0], g=dat[0][:, 1],
                    name1='Ar', name2='Ar', region1='solute', region2='solvent',
                    n1=1, n2=20712, volume=V, qvec=qvec)

    rdf_vv = RDF(r=dat[1][:, 0], g=dat[1][:, 1],
                    name1='Ar', name2='Ar', region1='solvent', region2='solvent',
                    n1=20712, n2=20712, volume=V, qvec=qvec)

    rdfs = RDFSet()

    rdfs.add_rdf(rdf_uv)
    rdfs.add_flipped(rdf_uv)
    rdfs.add_rdf(rdf_vv)
    rdfs.vdv_correct()

    cross_clc = rdfs.get_cross(qvec=qvec)
    dispv_clc = rdfs.get_dv(qvec=qvec)

    cross_ref = np.load('tests/data/xray_lj/cross.npy')
    dispv_ref = np.load('tests/data/xray_lj/dv.npy')

    assert (np.abs(cross_clc - cross_ref) < 1e-10).all()
    assert (np.abs(dispv_clc - dispv_ref) < 1e-10).all()


def test_custom_cm():
    ''' Check that custom_cms are being used when specified '''
    from grsq.debye import populate_cm
    def get_data(fdir):
        uv_files = sorted(glob.glob(fdir + '/*gAr_u-Ar_v.dat'))
        vv_files = sorted(glob.glob(fdir + '/*gAr_v-Ar_v.dat'))
        out = []
        for files in (uv_files, vv_files):
            tmp = np.genfromtxt(files[0])
            rdfs = np.zeros((tmp.shape[0], tmp.shape[1], len(files)))
            for f, fil in enumerate(files):
                dat = np.genfromtxt(fil)
                rdfs[:, :, f] = dat
            out.append(np.mean(rdfs, axis=-1))
        return out

    qvec = np.arange(0, 1, 0.1)
    dat = get_data('tests/data/xray_lj/')
    V = 100**3
    rdf_uv = RDF(r=dat[0][:, 0], g=dat[0][:, 1],
                    name1='Ar', name2='Ar', region1='solute', region2='solvent',
                    n1=1, n2=20712, volume=V, qvec=qvec)

    rdf_vv = RDF(r=dat[1][:, 0], g=dat[1][:, 1],
                    name1='Ar', name2='Ar', region1='solvent', region2='solvent',
                    n1=20712, n2=20712, volume=V, qvec=qvec)

    rdfs = RDFSet()
    rdfs.add_rdf(rdf_uv)
    rdfs.add_flipped(rdf_uv)
    rdfs.add_rdf(rdf_vv)
    rdfs.vdv_correct()

    custom_cm = copy.deepcopy(populate_cm())
    custom_cm['Ar']['a'] *= 2

    cross_clc = rdfs.get_cross(qvec=qvec)
    cross_clc_custom = rdfs.get_cross(qvec=qvec, custom_cm=custom_cm)
    v_clc = rdfs.get_solvent(qvec=qvec)
    v_clc_custom = rdfs.get_solvent(qvec=qvec, custom_cm=custom_cm)
    t_clc = rdfs.get_iq(qvec=qvec)
    t_clc_custom = rdfs.get_iq(qvec=qvec, custom_cm=custom_cm)

    assert (np.abs(cross_clc - cross_clc_custom) > 1000).all()
    assert (np.abs(v_clc - v_clc_custom) > 1000).all()
    assert (np.abs(t_clc - t_clc_custom) > 1000).all()


def test_classes():
    ''' Test base funcionality '''
    V = 122900.85207774633
    stoich = {'H_v': 8190, 'O_v': 4095}

    rdfs = rdfset_from_dir('tests/data/mda_water/', volume=V, stoich=stoich)
    rdfs.show()
    rdfs[0].get_info()
    assert len(rdfs) == 4
    print(rdfs[0])
    repr(rdfs[0])
    print(rdfs[0])
    print(rdfs[:2])
    print(rdfs[2:-1])
    print(rdfs[2:])
    print(rdfs[0::2])


def test_builtins():
    ''' Testing setitem and eq '''
    V = 122900.85207774633
    stoich = {'H_v': 8190, 'O_v': 4095}

    rdfs_1 = rdfset_from_dir('tests/data/mda_water/', volume=V, stoich=stoich)
    rdfs_2 = RDFSet()
    for key, rdf in rdfs_1.items():
        rdfs_2[key] = copy.deepcopy(rdf) 
    assert rdfs_1 == rdfs_2

    rdfs_2 = copy.deepcopy(rdfs_1)
    rdfs_2[0].n1 = 9999
    assert not (rdfs_1 == rdfs_2)

    rdfs_2 = copy.deepcopy(rdfs_1)
    rdfs_2[0].name1 = 'XX'
    assert not (rdfs_1 == rdfs_2 )

    rdfs_2 = copy.deepcopy(rdfs_1)
    rdfs_2[0].g = np.zeros(3)
    assert not (rdfs_1 == rdfs_2)

    rdfs_2 = copy.deepcopy(rdfs_1)
    rdfs_2[0].r = np.zeros(3)
    assert not (rdfs_1 == rdfs_2)

    rdfs_2 = copy.deepcopy(rdfs_1)
    rdfs_2[0].r *= 0 
    assert not (rdfs_1 == rdfs_2) 

    rdfs_2 = copy.deepcopy(rdfs_1)
    rdfs_2[0].g *= 0 
    assert not (rdfs_1 == rdfs_2) 

    rdfs_2 = RDFSet()
    for key, rdf in rdfs_1[:1].items():
        rdfs_2[key] = copy.deepcopy(rdf) 
    assert not (rdfs_1 == rdfs_2)

    # test instance type
    assert not (rdfs_1 == rdf)

    # test sequence
    rdfs_2 = rdfs_1[1:]
    assert not (rdfs_1 == rdfs_2)

# WIP: Test on whole molecule and prmtop reading
def test_molecule():
    rdfs = rdfset_from_dir('tests/data/molecule/febpy_densities_00/', 
                           prmtop='tests/data/molecule/FEBPY_solv.prmtop')
    rdfs.get_dv(qvec=np.arange(0, 6, 0.1))

