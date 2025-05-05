import sys
import numpy as np
from scipy.io import loadmat
from ase import Atoms

try: 
    from grsq.compton import compton_scattering
except:
    sys.path.append('src/')
    from grsq.compton import compton_scattering

def test_compton():
    # First test that the code gives the same results as 
    # our previous in-house implementation:
    org_data = loadmat('tests/data/compton/test_incoherent.mat')
    q_org = org_data['IncoherentIntensity'][:, 0]
    I_org = org_data['IncoherentIntensity'][:, 1]

    atom_list = ['O', 'P', 'K', 'H2O']
    number_list = [20, 8, 4, 4625]
    atoms = {key:value for key, value in zip(atom_list, number_list)}
    I = compton_scattering(atoms, q_org)
    # The difference is due to slightly different CM parameters
    # used in the test data, and the newer parameters taken
    # from the periodictable lib. 
    assert np.sum(np.abs(I - I_org)) / I.sum() < 2e-7

    # Then that the code gives the same if the input is an ASE Atoms object:
    atoms = Atoms(''.join([f'{el}{n:d}' for el, n in zip(atom_list[:-1], number_list[:-1])]))
    I_ase = compton_scattering(atoms, q_org)
    atoms = {key:value for key, value in zip(atom_list, number_list) if key != 'H2O'}
    I_dict = compton_scattering(atoms, q_org)
    assert np.sum(np.abs(I_ase - I_dict)) / I_ase.sum() < 1e-10


def test_special_cases():
    # Currently only just runs the code for Pt and Tl to check that it doesn't crash.
    qvec = np.arange(0, 1, 0.01)
    atoms = {'Pt': 1}
    I = compton_scattering(atoms, qvec)
    
    atoms = {'Tl': 1}
    I = compton_scattering(atoms, qvec)
    
    atoms = {'H': 1}
    I = compton_scattering(atoms, qvec)
