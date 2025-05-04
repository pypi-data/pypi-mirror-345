#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 15:25:22 2022

@author: Mikhail Glagolev
"""

import numpy as np
import MDAnalysis as mda
from MDAnalysis import transformations
import json
if __package__ == None:
    from lib.utilities import normalize_vectors
else:
    from .lib.utilities import normalize_vectors

def backbone_twist(u: mda.Universe, k_list: list,
                   selection = None,
                   different_molecules: bool = False):
    """
    Calculate the list of dihedral angles, formed by the following
    vectors: (r_i, r_{i+k}), (r_{i+k}, r_{i+2*k}), (r_{i+2*k}, r_{i+3*k})
    where i is the index of a monomer unit, and k is a free parameter.
    
    For certain values of k, the distributions of the dihedral angles can
    catch the formation of superhelical structures in polymer conformations.
    
    For helical polymers we suppose selecting k as a multiple of the number
    of monomer units per helix turn and several times smaller than the period
    of a superhelical structure. The example of the analysis is provided in the
    Supplementary Information for https://doi.org/10.1016/j.polymer.2022.124974
    
    The data for trajectory timesteps [ts1, ts2, ...] and the values of k
    in the k_list is returned in a dictionary structure:
    
    {description: "Dihedral angles along the polymer backbone",
     data: {ts1: {k_list[0], [values]}, {k_list[1], [values]}, ...},
            ts2: {k_list[0], [values]}, {k_list[1], [values]}, ...},
            ....
           }
    }
     
    
    Parameters
    ----------
    u : mda.Universe
        Input data for analysis as MDAnalysis Universe.
    k_list : list
        The list of the values of k, corresponding to the distance between
        the starting point of each vector and its endpoint along the backbone.
        It is implicitly taken into account that the selection query leaves 
        only the backbone atoms. The algorithm also uses that the atoms in
        the selection are ordered, as stated in MDAnalysis documentation.
    selection : STRING, optional
        The select_atoms query for MDAnalysis Universe.select_atoms method.
        The default is None.
    different_molecules : bool, optional
        Should the atoms of different molecules be taken into account.
        The default is False.

    Returns
    -------
    Dictionary with "description" and "data" values. "data" contains the
    dictionaries for each timestep. For each timestep, the corresponding
    dictionary contains the value of k and a list of angle values calculated
    for that particular k:
        
        {description: "Dihedral angles along the polymer backbone",
         data: {ts1: {k_list[0], [values]}, {k_list[1], [values]}, ...},
                ts2: {k_list[0], [values]}, {k_list[1], [values]}, ...},
                ....
               }
        }

    """
    # Unwrap all the coordinates, so that all the bond lengths are correct.
    unwrap = transformations.unwrap(u.atoms)
    u.trajectory.add_transformations(unwrap)
    
    # Select atoms by type or read selection criteria in MDAnalysis synthax
    if selection is not None:
        atoms = u.select_atoms(selection)
    else:
        atoms = u.atoms
    
    # Initialize the dictionary with the data for all the timesteps
    data = {}
    
    for ts in u.trajectory:
        values = {}
        #Pad the atom coordinates list by k
        atom_resids = atoms.resids
        atom_coords = atoms.positions
        natoms = len(atoms)
        
        #For each k:
        for k in k_list:
            # Here we create 2 sets of arrays, one padded on the right
            # (index 1) and one padded on the left (index 2)
            coords1 = np.pad(atom_coords, ((0, k), (0, 0)),
                             constant_values = 1.)
            coords2 = np.pad(atom_coords, ((k, 0), (0, 0)),
                             constant_values = 1.)
            valid1 = np.concatenate((np.full((natoms,), True),
                                    np.full((k,), False)))
            valid2 = np.concatenate((np.full((k,), False),
                                     np.full((natoms,), True)))
            
            #Calculate interatom vectors    
            vector_coords = coords2 - coords1
            
            # Check if both ends of the vector are not the padded values:
            valid_atoms = np.logical_and(valid1, valid2)
            
            # If the calculations shall be restricted to the atoms with
            # same residue ids, we shall do additional checks
            if not different_molecules:
                resid1 = np.pad(atom_resids, (0, k), constant_values = 0)
                resid2 = np.pad(atom_resids, (k, 0), constant_values = 0)
                same_resid = np.equal(resid1, resid2)
                valid_vector = np.logical_and(valid_atoms, same_resid)
                vector_resids = resid1
            else:
                valid_vector = valid_atoms
            mask = np.logical_not(valid_vector)
            
            # Create numpy array of valid vectors and associated residue
            # ids array, and compress the arrays.
            masked_vectors = np.ma.masked_array(vector_coords,
                                    mask = np.column_stack((mask, mask, mask)))
            vectors = np.ma.compress_rowcols(masked_vectors, axis = 0)
            if not different_molecules:
                masked_resids = np.ma.masked_array(vector_resids, mask)
                resids = np.ma.compressed(masked_resids)
            
            # Determine the length of the array of valid vectors:
            nvectors = len(vectors)
            
            # Create the list of vectors and associated list of residues
            #Pad the interatom vectors by k and 2k
            r1 = np.pad(vectors, ((0, 2*k), (0, 0)), constant_values = 1.)
            r2 = np.pad(vectors, (( k,  k), (0, 0)), constant_values = 1.)
            r3 = np.pad(vectors, ((2*k, 0), (0, 0)), constant_values = 1.)
            
            # Determine the validity as the validity of all three vectors with
            # the same index
            valid1 = np.concatenate((np.full((nvectors,), True),
                                    np.full((2*k,), False)))
            valid2 = np.concatenate((np.full((k,), False),
                                     np.full((nvectors,), True),
                                     np.full((k,), False)))
            valid3 = np.concatenate((np.full((2*k,), False),
                                     np.full((nvectors,), True)))
            valid123 = np.logical_and(np.logical_and(valid1, valid2),
                                                     valid3)
            if not different_molecules:
                resids1 = np.pad(resids, (0, 2*k), constant_values = 0)
                resids2 = np.pad(resids, ( k,  k), constant_values = 0)
                resids3 = np.pad(resids, (2*k, 0), constant_values = 0)
                same_resids12 = np.equal(resids1, resids2)
                same_resids23 = np.equal(resids2, resids3)
                same_resids = np.logical_and(same_resids12, same_resids23)
                valid_vectors = np.logical_and(valid123, same_resids)
            else:
                valid_vectors = valid123
            phi_mask = np.logical_not(valid_vectors)
            
            # Calculate the angles using the values from 3 arrays
            # TODO: add checks for zero-length r1_x_r2 or r2_x_r3
            r1_x_r2_normed = normalize_vectors(np.cross(r1, r2))
            r2_x_r3_normed = normalize_vectors(np.cross(r2, r3))
            r1_x_r2_normed_x_r2_x_r3_normed = np.cross(r1_x_r2_normed,
                                                       r2_x_r3_normed)
            r2_normed = normalize_vectors(r2)
            sin_phi = np.multiply(r1_x_r2_normed_x_r2_x_r3_normed,
                             r2_normed).sum(1)
            cos_phi = np.multiply(r1_x_r2_normed, r2_x_r3_normed).sum(1)
            all_phi = np.arccos(cos_phi) * np.sign(sin_phi)
            masked_phi = np.ma.masked_array(all_phi, mask = phi_mask)
            phi = np.ma.compressed(masked_phi)
            
            # Add the list of values for the current k to the dictionary for
            # the current timestep:
            values[k] = phi.tolist()
        
        # Add the dictionary for all k values for the current timestep to the
        # common data dictionary:
        data[str(ts)] = values
    # Return the resulting structure:
    return { "description" : "Dihedral angles along the polymer backbone",
             "data" : data}

def main():
    
    import argparse

    parser = argparse.ArgumentParser(
        description =  """
         Calculate the list of dihedral angles, formed by the following
         vectors: (r_i, r_{i+k}), (r_{i+k}, r_{i+2*k}), (r_{i+2*k}, r_{i+3*k})
         where i is the index of a monomer unit. The example of the analysis
         is provided in the Supplementary Information for
         https://doi.org/10.1016/j.polymer.2022.124974""")

    parser.add_argument(
        'input', metavar = 'INPUT', action = "store", nargs = '+',
        help = """input file(s), the format will be guessed by MDAnalysis 
        based on file extension""")

    parser.add_argument(
        '--selection', metavar = 'QUERY', type = str, nargs = '?',
        help 
        = "Consider only selected atoms, use MDAnalysis selection language")
    
    parser.add_argument('--k', metavar = 'VECTOR_LENGTHS', type = int,
                       nargs = '+',
                       help = "List of vector lengths along the backbone")
    
    parser.add_argument('--different-molecules', action = "store_true",
                    help = "Consider the angles spanning different molecules")
    
    parser.add_argument('--plot', action = "store_true",
                        help = "Plot the results")
    
    args = parser.parse_args()

    u = mda.Universe(*args.input)
    
    result = backbone_twist(u, args.k, selection = args.selection,
                            different_molecules = args.different_molecules)
    
    print(json.dumps(result, indent = 2))
    
    # Plot the histogram, if requested, with
    # the values summed across the timesteps
    if args.plot:
        import matplotlib.pyplot as plt
        for k in args.k:
            all_values = []
            for ts in result["data"]:
                all_values += result["data"][ts][k]
            histogram = np.histogram(all_values)
            bincenters = (histogram[1][1:] + histogram[1][:-1]) / 2.
            plt.plot(bincenters, histogram[0], label = "k = " + str(k))
        plt.xlim(-np.pi, np.pi)
        plt.ylim(0)
        plt.xticks([-np.pi, 0, np.pi], [r'$-180°$', r'$0$', '180\u00B0'],
                   fontsize = 18)
        plt.yticks([0], fontsize = 18)
        plt.xlabel('\u03A8', fontsize = 18)
        plt.ylabel('P(\u03A8), a.u.', fontsize = 18)
        plt.legend(shadow = False, fontsize = 18)
        plt.show()
        
if __name__ == "__main__":
    main()
