"""
Unit and regression test for the grsq package.
"""

# Import package, test suite, and other packages as needed
import sys
import numpy as np
from ase.io import read
from ase import Atoms

try: 
    from grsq import Debye
    from grsq import RDF, RDFSet, rdfset_from_dir
    from grsq.debye import old_cm, populate_cm, get_cm
except:
    sys.path.append('src/')
    from grsq import Debye
    from grsq import RDF, RDFSet, rdfset_from_dir
    from grsq.debye import old_cm, populate_cm, get_cm


def test_debye_numba():
    ''' Test that the Debye and numba implementations give the same result '''
    atoms = read('tests/data/testmol.xyz')
    deb = Debye()
    slow = deb.debye(atoms)
    fast = deb.debye_numba(atoms)
    assert np.sum(np.abs(slow - fast)) / slow[0] < 1e-10  
    print(np.sum(np.abs(slow - fast)) / slow[0]) 


def test_debye_f0_update():
    ''' Test that an update of the atomic FFs is being triggered
        if the atoms in the atoms object change.
    '''
    fw_atoms = read('tests/data/testmol.xyz')
    syms = fw_atoms.get_chemical_symbols()
    syms.reverse()
    rw_atoms = Atoms(''.join(syms), positions=np.flip(fw_atoms.positions))
    deb = Debye()
    s_fw = deb.debye(fw_atoms)
    s_rw = deb.debye(rw_atoms)
    assert np.sum(np.abs(s_fw - s_rw)) < 1e-8

def test_custom_cm():
    ''' Check that putting in the same FF as custom FF
        gives the same result as using FFs from the periodictable package
    '''
    qvec = np.arange(0, 20, 0.01)
    atoms = read('tests/data/xray_2particle/test.xyz')
    deb = Debye(qvec=qvec)
    i_deb = deb.debye(atoms)
    custom_cm = {'Pt':old_cm['Pt']}
    deb_ccm = Debye(qvec=qvec, custom_cm=custom_cm)
    i_ccm = deb_ccm.debye(atoms)
    assert (np.abs((i_deb - i_ccm) / i_deb) < 5e-3).all()

def test_custom_elements():
    ''' Test calculating scattering with different
        species of the same element, e.g. I0 and I-
    '''
    from ase import Atoms
    atoms = Atoms('I2', positions=[[0, 0, -1],[0, 0, 1]])
    custom_elements = ['I0', 'I']  # 'I' is I- in old_cm
    deb = Debye(custom_cm=old_cm)  # contains both I- and I0
    deb.debye(atoms, custom_elements=custom_elements)


def test_debye_selective():
    ''' Test the debye implementation that only calculates
        terms between list1 and list2
    '''
    atoms = read('tests/data/testmol.xyz')
    subset_atoms = atoms[:3]
    deb = Debye()
    full_on_subset = deb.debye(subset_atoms)
    idx1 = [0, 1, 2]
    idx2 = [0, 1, 2]
    subset_on_full = deb.debye_selective(atoms, idx1, idx2)
    assert np.sum(subset_on_full - full_on_subset) < 1e-9


def test_debye_hist():
    from ase.spacegroup import crystal
    # Create heteroatomic nanoparticle for testing
    a = b = 2.81  
    c = 13.91  
    lico2 = crystal(['Li', 'Co', 'O'],
                    basis=[(0, 0, 0), 
                        (1/3, 2/3, 1/6),
                        (0, 0, 0.24)],
                    spacegroup='R-3m', 
                    cellpar=[a, b, c, 90, 90, 120])
    lico2_chunk = lico2 * (20, 20, 10)
    center = lico2_chunk.get_center_of_mass()
    np_radius = 10 # 1 nm np
    atoms = Atoms(cell=lico2_chunk.get_cell(), pbc=False)
    for atom in lico2_chunk:
        if np.linalg.norm(atom.position - center) <= np_radius:
            atoms += atom

    # assert that the full debye and histogrammed debye gives the same
    qvec = np.arange(0, 4, 0.02)
    deb = Debye(qvec)

    s_full = deb.debye_numba(atoms)
    s_hist1 = deb.debye_histogrammed(atoms, dr=0.0001, use_numba=False)
    s_hist2 = deb.debye_histogrammed(atoms, dr=0.0001, use_numba=True)

    assert (s_hist1 == s_hist2).all(), 'Numba and Python distances differ!'
    assert np.abs(s_full - s_hist1).sum() / s_full.sum() < 1e-5


def test_cm_tools():
    cm = populate_cm()
    get_cm('Na2+')
    get_cm('Na1+')
