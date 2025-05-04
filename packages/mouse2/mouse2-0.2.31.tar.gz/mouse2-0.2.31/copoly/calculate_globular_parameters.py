#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 20:07:44 2024

@author: Mikhail Glagolev
"""

import MDAnalysis as mda
from MDAnalysis import transformations
import numpy as np
from asa import calculate_asa, read_radii
from block_boundaries import block_boundaries
from mdlearn.sequences_encoding import block_lengths
import os


atom_types = ['1', '2']
block_name = { '1' : 'VCL', '2' : 'VI'}


r_probe = 0.
n_sphere = 480
default_nbins = 100

radii_file = os.path.join(os.path.dirname(__file__) , 'radii.txt')


radii = read_radii(radii_file)


def calculate_atom_distributions(atoms, ref_point, nbins = None,
                                         min = None, max = None):
    """
        Distributions of atomic distances from the reference point
        and maximum distance
    """
    result = {}
    positions = atoms.positions
    distances = np.linalg.norm(positions - ref_point, axis = 1)
    # Maximum distance from COM
    max_dist = np.max(distances)
    result['Max_dist'] = max_dist
    # Distance histograms
    if min is not None and max is not None:
        frequencies, bin_edges = np.histogram(distances, bins = nbins,
                                      range = (min, max))
    else:
        frequencies, bin_edges = np.histogram(distances, bins = nbins)
    bin_volumes_cumul = 4./3.*np.pi*np.power(bin_edges, 3)
    bin_volumes = bin_volumes_cumul[1:] - bin_volumes_cumul[:-1]
    bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])
    densities = frequencies / bin_volumes
    result['Hist'] = {
        'bin_centers' : bin_centers,
        'dens' : densities,
        'dens_norm' : densities / np.sum(densities),
        'dens_sum' : np.sum(densities)
        }
    return result


def calculate_globule_parameters(file, nbins = default_nbins,
                                  min = None, max = None):
    """
    Need to calculate:
        
    V    Rg / N
    V    SASA(VCL)/NVCL
    V    Rg(VI)
    V    Rg(VCL)
    V    Nblock(VI)
    V    Nblock(VCL)_wo_tail
    
    """


    result = {}

    u = mda.Universe(file)

    n_atom = u.atoms.n_atoms

    unwrap = transformations.unwrap(u.atoms)
    u.trajectory.add_transformations(unwrap)

    com = u.atoms.center_of_mass()
    rg = u.atoms.radius_of_gyration()


    result['N'] = n_atom
    result['Rg'] = rg
    #result['Rg/N'] = rg / n_atom
    
    #Distribution parameters for all beads
    distributions = calculate_atom_distributions(u.atoms, com,
                                                 nbins = nbins,
                                                 min = min, max = max)
    #result['Hist all'] = distributions['Hist']
    #Block lengths without tail
    max_block_2 = block_boundaries(list(u.atoms.types))['2']['max']
    blocks = block_lengths(list(u.atoms.types)[:max_block_2])
    
    # Surface area for all types of beads
    asas = calculate_asa(u.atoms, r_probe, n_sphere, u.dimensions, radii)

    for atom_type in atom_types:
        atoms =u.select_atoms(f'type {atom_type}')
        # Gyration radius
        result[f'Rg {block_name[atom_type]}'] = atoms.radius_of_gyration()
        distributions = calculate_atom_distributions(atoms, com,
                                                     nbins = nbins,
                                                     min = min, max = max)
        result[f'Max_dist {atom_type}'] = distributions['Max_dist']
        #result[f'Hist {atom_type}'] = distributions['Hist']
        # ASA per bead
        result[f'ASA {block_name[atom_type]}'] = np.sum(asas[atom_type])
        result[f'ASA/unit {block_name[atom_type]}'] = np.mean(asas[atom_type])
        result[f'Avg_block {block_name[atom_type]}'] = np.mean(blocks[atom_type])
        result[f'Max_block {block_name[atom_type]}'] = np.max(blocks[atom_type])

    result[f"Rg{block_name['2']}/Rg{block_name['1']}"] = \
                          result[f"Rg {block_name['2']}"]\
                        / result[f"Rg {block_name['1']}"]

    return result


def calculate_globules_parameters(files = None, nbins = None,
                                  min = None, max = None):
    results = []
    for file in files:
        result = calculate_globule_parameters(file, nbins = nbins,
                                                  min = min, max = max)
        results.append(result)
    return results


if __name__ == "__main__":
    import argparse
    import json
    import sys
    from numpyencoder.numpyencoder import NumpyEncoder
    parser = argparse.ArgumentParser(
        description = 'Calculate averaged gyration radius')

    parser.add_argument('file', metavar = 'DATA', type = str, nargs = 1,
                        help = 'simulation data file')
    
    args = parser.parse_args()
    
    result = calculate_globule_parameters(args.file[0])
    json.dump(result, sys.stdout, indent=4, sort_keys=True,
              separators=(', ', ': '), ensure_ascii=False,
              cls=NumpyEncoder)