import os
import numpy as np
from ase import Atoms
from grsq.debye import Debye 


def compton_scattering(atoms, qvec):
    """
    Calculates the incoherent (Compton) scattering intensity for an ensemble of atoms/molecules.

    Only works for the elements in the Haidu coefficients file, as well as Pt and Tl.
    Incoherent scattering for H2O can also be calculated by inputting 'H2O' as a key 
    in the atoms dict.

    Parameters:
        atoms : ASE Atoms object OR a dict of elements/molecules and their counts.
            for example: {'C': 2, 'H': 8, 'H2O': 200}
        qvec:   np.ndarray (1, )
            your Q vector    
    Returns:
        I_incoh : ndarray
            The total incoherent intensity.
    """

    s = qvec / (4 * np.pi)
    I_incoh = np.zeros_like(qvec)

    if type(atoms) == Atoms:
        atom_list, number_list = np.unique(atoms.get_chemical_symbols(), return_counts=True)
        atom_list = atom_list.tolist()
        number_list = number_list.tolist()
    elif type(atoms) == dict:
        atom_list = list(atoms.keys())
        number_list = list(atoms.values())
    else:
        raise ValueError("atoms must be an ASE Atoms object or a dict of elements and their counts.")

    # Read in Haidu coefficients from file.
    # The file is assumed to have a header and five columns:
    # Atom (string), Z, M, K, L.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'data', 'HaiduCoefficients.txt')
    data = np.genfromtxt(file_path, encoding='utf-8', skip_header=1, dtype=None)
    
    # Build a dict of dicts mapping atom symbol to its coefficients.
    # Example: coeff_dict['C'] -> {'Z': 6.0, 'M': 0.4972, 'K': 1.8438, 'L': 7.8917}
    keys = ['Z', 'M', 'K', 'L']
    coeff_dict = {entry[0].strip(): {k: float(val) for k, val in zip(keys, list(entry)[1:])} for entry in data}

    # Loop over each atom/molecule species and calculate scattering
    deb = Debye(qvec=qvec)
    for i, atom in enumerate(atom_list):
        atom_name = atom.strip()  # Remove extra whitespace
        
        # Calculate coherent scattering amplitude f0
        if atom == 'H2O':
            cm_h2o = {'H2O': {'a': np.array([1.6607, 1.6277, 3.7743, 2.7903]),
                              'b': np.array([0.3042, 5.1864, 12.7450, 30.7880]),
                              'c': 0.1444}}
            deb2 = Debye(qvec=qvec, custom_cm=cm_h2o)
            I_coherent = deb2.atomic_f0('H2O')**2
        else:
            I_coherent = deb.atomic_f0(atom)**2

        # Skip hydrogen atoms as they are not included in the Haidu coefficients.
        if atom == 'H':
            print('Skipping Hs')
            continue

        # Compute the incoherent scattering intensity
        if atom == 'Pt':
            # Special case for Pt using the palinka expression
            Z_val = 78
            a = 1.0354
            b = 0.5168
            c = 1.7275
            I_incoherent = Z_val * (1 - (a / (1 + b * s)**c))
        elif atom == 'Tl':
            # Special case for Tl using the palinka expression
            Z_val = 81
            a = 1.0339
            b = 0.5341
            c = 1.6544
            I_incoherent = Z_val * (1 - (a / (1 + b * s)**c))
        else:
            if atom not in coeff_dict:
                raise ValueError(f"No matching Haidu coefficients found for atom {atom}")                    
            Z_val = coeff_dict[atom]['Z']
            M = coeff_dict[atom]['M']
            K = coeff_dict[atom]['K']
            L = coeff_dict[atom]['L']
            I_incoherent = (Z_val - I_coherent / Z_val) * (1 - M * (np.exp(-K * s) - np.exp(-L * s)))
        
        # Accumulate the weighted incoherent scattering intensity
        I_incoh += I_incoherent * number_list[i]

    return I_incoh