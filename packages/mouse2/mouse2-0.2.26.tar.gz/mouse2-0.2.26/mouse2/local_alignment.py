#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 17:20:41 2022

@author: Mikhail Glagolev
"""

import MDAnalysis as mda
from MDAnalysis import transformations
import numpy as np
if __package__ == None:
    from lib.vector_orientational_ordering \
        import calculate_cos_sq_for_reference
else:
    from .lib.vector_orientational_ordering \
        import calculate_cos_sq_for_reference
import json

def averaged_frequencies_bin_centers(result, frequencies_key, bin_edges_key):
    """
    Return averaged histogram data across the time steps.
    Bin edges are assumed to be the same for all the timesteps.

    """
    bin_edges = np.asarray(list(result["data"].values())[0][bin_edges_key])
    bincenters = (bin_edges[1:] + bin_edges[:-1]) / 2.
    n_bins = len(bincenters)
    frequencies = np.zeros((n_bins))
    for ts in result["data"]:
        frequencies += np.asarray(
                    result["data"][ts][frequencies_key])
    frequencies /= len(result["data"])
    return frequencies, bincenters
    

def local_alignment(
        u: mda.Universe, r_min = 0., r_max = -1., 
        id_pairs = None, selection = None,
        n_bins = 150, mode = 'average', same_molecule = True):
    """
    
    This function calculates the angles between the bonds, if their
    midpoints are located within the range of [rmin, rmax].
    The local ordering parameter is then calculated as
    S = 3/2 ( <(cos(gamma))^2>) - 1/2)
    where "gamma" is the angle between the bond vectors.
    The distributions are stored if the "histogram" mode is selected.

    Parameters
    ----------
    universe : mda.Universe
        MDAnalysis universe. Only the bonds required for calculation of the
        ordering parameter shall be present. All other bonds shall be deleted
        from the universe before the analysis.
    r_min : FLOAT, optional
        Minimum distance between the bond vector centers to consider.
        The default is 0.. To exclude the bond itself, consider setting
        r_min to a small value, e. g. 1e-6
    r_max : FLOAT, optional
        Maximum distance between the bond vector centers to consider.
        The default is 0., which means choosing the cutoff based on the
        size of the simulation cell.
        Setting the value to -1, means considering all the bonds.
    mode : STRING, optional
        Whether an average value or a histogram shall be returned.
        The default is 'average'.
    same_molecule : BOOL, optional
        Whether the bonds from the same molecule (resid) shall be accounted
        for. The default is True.

    Returns
    -------
    Dictionary with "description" and "data" values. "data" contains the
    dictionaries for each timestep. For each timestep, the corresponding
    dictionary contains the key:value pairs of the parameters. The average
    value of the parameter s is calculated in the "average" mode, and
    the histograms normed by the total area in terms of cos^2(theta) and
    normed by the solid angle values are calculated in the "histogram" mode.
        
        {description: "Description containing the calculation parameters",
         data: {ts1: {"average_s": s, ...},
                ts2: {"average_s": s, ...},
                ....
               }
        }

    """
    if r_max == 0.:
        r_max = min(u.dimensions) / 2.
    
    # Prepare the description of the output:
    description = "Local orientational ordering parameter s"
    if mode == "histogram":
        description += (" and the distribution of " 
                     + "mutual orientation angle theta")
    description += (" r_min=" + str(r_min) + ", r_max=" + str(r_max))
    if same_molecule:
        description += ", same molecules taken into account"
    else:
        description += ", same molecules not taken into account"
    # Unwrap all the coordinates, so that all the bond lengths are
    # real. The closest images of the bonds will be found in the nested
    # function.
    unwrap = transformations.unwrap(u.atoms)
    try:
        u.trajectory.add_transformations(unwrap)
    except ValueError:
        pass
    
    # Select atoms by type or read selection criteria in MDAnalysis synthax
    if selection is not None:
        selected_atoms = u.select_atoms(selection)
    else:
        selected_atoms = u.atoms
    
    #Select the atoms
    if id_pairs is not None:
        # To generate sorted selections, we have to add the atoms one by one:
        atoms1 = mda.AtomGroup([],u)
        atoms2 = mda.AtomGroup([],u)
        for i in range(len(id_pairs)):
            atoms1 += selected_atoms.select_atoms("id " + str(id_pairs[i][0]))
            atoms2 += selected_atoms.select_atoms("id " + str(id_pairs[i][1]))
    else:
        atoms1 = selected_atoms.bonds.atom1
        atoms2 = selected_atoms.bonds.atom2
    
    data = {}
    
    for ts in u.trajectory:
        # Create data structure for the current timestep:
        values = {}
        #if mode == "average":
        cos_sq_sum = 0.
        i_s = 0
        if mode == "histogram":
            cos_sq_raw_hist = np.zeros(n_bins)
            _, bin_edges = np.histogram(cos_sq_raw_hist, bins = n_bins,
                                                       range = (0.,1.))
            # Calculate the values of cos_theta from cos_sq_theta:
            bin_edges_cosine = np.sqrt(bin_edges)
            # Calculate the values of theta corresponding to bin edges:
            solid_angle_normalization = np.diff(bin_edges_cosine)
            # Calculate the values of angle corresponding to bin edges:
            bin_edges_theta = np.arccos(bin_edges)
        
        # Calculate vector components
        # 1D arrays, one for each of the coordinates, provide more efficient
        # numpy calculations. Converting the data here, outside of the main
        # loop provided additional 15% speedup in the test runs.
        bx = (atoms2.positions[:, 0] - atoms1.positions[:, 0])
        by = (atoms2.positions[:, 1] - atoms1.positions[:, 1])
        bz = (atoms2.positions[:, 2] - atoms1.positions[:, 2])
    
        bond_components = [bx, by, bz]
    
        # Creating 1D arrays with bond midpoints
        rx = (atoms1.positions[:, 0] 
              + atoms2.positions[:, 0]) / 2.
        ry = (atoms1.positions[:, 1]
              + atoms2.positions[:, 1]) / 2.
        rz = (atoms1.positions[:, 2]
              + atoms2.positions[:, 2]) / 2.
    
        bond_midpoints = [rx, ry, rz]
    
        if not same_molecule:
            bond_resids = atoms1.resids
        else:
            bond_resids = None
    
        for ivector in range(len(atoms1)):
            # Determine the reference vector components and midpoint
            # from the atom coordinates
            ref_components = atoms2[ivector].position - atoms1[ivector].position
            ref_midpoint = (atoms1[ivector].position 
                            + atoms2[ivector].position) / 2.
            # If needed, exclude bonds from the same molecule
            if not same_molecule:
                excluded_resids = list(set([atoms1[ivector].resid,
                                       atoms2[ivector].resid]))
            else:
                excluded_resids = None
            # Calculate ordering parameter value for the reference bond
            cos_sq_values = calculate_cos_sq_for_reference(
                bond_components, bond_midpoints, ref_components, ref_midpoint,
                u.dimensions, r_min = r_min, r_max = r_max,
                vector_attributes = bond_resids,
                excluded_attributes = excluded_resids)
            
            #if mode == "average":
            if np.shape(cos_sq_values)[0] > 0:
                cos_sq_sum += np.average(cos_sq_values)
                i_s += 1
            else:
                pass
                
            if mode == "histogram":
                cos_sq_hist_increment, _ = np.histogram(cos_sq_values,
                                           bins = n_bins, range = (0.,1.))
                cos_sq_raw_hist += cos_sq_hist_increment

        #if mode == "average":
        if i_s > 0:
            # Normalize the values. Normalization procedure ensures that
            # double consideration of each of the bonds doesn't affect
            # the result
            values["average_s"] = 1.5 * cos_sq_sum / i_s - 0.5
        if mode == "histogram":
            values["cos_sq_raw_histogram"] = cos_sq_raw_hist.tolist()
            norm = np.sum(cos_sq_raw_hist * np.diff(bin_edges))
            values["cos_sq_area_normalized_histogram"] = ( cos_sq_raw_hist
                                                            / norm).tolist()
            solid_angle_norm = np.sum(cos_sq_raw_hist * np.diff(bin_edges)
                                      / solid_angle_normalization )
            values["cos_sq_solid_angle_normalized_histogram"] = (
                cos_sq_raw_hist / solid_angle_normalization
                / solid_angle_norm ).tolist()
            values["bin_edges_cos_sq_theta"] = bin_edges.tolist()
            values["bin_edges_cos_theta"] = bin_edges_cosine.tolist()
            values["bin_edges_theta"] = bin_edges_theta.tolist()
        data[str(ts)] = values
    return { "description" : description, "data" : data }

def main():
    
    import argparse

    parser = argparse.ArgumentParser(
        description = """This utility calculates the angles between the bonds,
        if their midpoints are located within the range of [rmin, rmax].
        The local ordering parameter is then calculated as
        S = 3/2 ( <(cos(gamma))^2>) - 1/2)
        where "gamma" is the angle between the bond vectors.
        The distributions are stored if the --histogram flag is provided.
        The example applications are
        https://doi.org/10.1016/j.polymer.2020.122232
        and https://doi.org/10.1016/j.polymer.2022.124974""")

    parser.add_argument(
        'input', metavar = 'INPUT', action = "store", nargs = '+',
        help = """input file(s), the format will be guessed by MDAnalysis 
        based on file extension""")

    parser.add_argument(
        '--r_max', metavar = 'R_max', type = float, nargs = '?',
        default = 0., help = "outer cutoff radius")

    parser.add_argument(
        '--r_min', metavar = 'R_min', type = float, nargs = '?',
        default = 0., help = "inner cutoff radius")
        
    parser.add_argument(
        '--selection', metavar = 'QUERY', type = str, nargs = '?',
        help 
        = "Consider only selected atoms, use MDAnalysis selection language")
    
    parser.add_argument(
        "--same-molecule", action = "store_true",
        help = "Take into account bonds from the same molecule")

    parser.add_argument(
        '--histogram', action = "store_true",
        help = "Store and optionally plot the distribution of the angles")

    parser.add_argument(
        '--n_bins', metavar = 'N_bins', type = int, nargs = '?',
        default = 150, help = "Number of bins of the distribution histogram")
    
    parser.add_argument('--plot', metavar = 'IMAGE_FILE', nargs = '?',
                        default = False, const = '-',
                        help = "Plot the distribution histogram. The image "
                        + "can be stored as a file, if a name is provided")
    
    parser.add_argument('--saplot', metavar = 'IMAGE_FILE', nargs = '?',
                        default = False, const = '-',
                        help = "Plot the distribution histogram, normalized "
                        + "by the solid angle value. The image "
                        + "can be stored as a file, if a name is provided")

    parser.add_argument('--pairs-file', type = str, nargs = '?',
                        default = "",
                        help = "CSV file with pairs of indices,"
                        + " corresponding to vector ends")

    args = parser.parse_args()

    u = mda.Universe(*args.input)
    
    mode = "average"
    if args.histogram:
        mode = "histogram"
        
    if len(args.pairs_file) > 0:
        import csv
        pairs = []
        with open(args.pairs_file, newline = '') as pairs_file:
            pairs_data = csv.reader(pairs_file, delimiter = ' ')
            for pair in pairs_data:
                pairs.append(pair)
    else:
        pairs = None
    
    result = local_alignment(u, r_min = args.r_min, r_max = args.r_max,
                             mode = mode, n_bins = args.n_bins,
                             id_pairs = pairs, selection = args.selection,
                             same_molecule = args.same_molecule,
                             )

    print(json.dumps(result, indent = 2))

    # Plot the histogram, if requested, with
    # the values summed across the timesteps
    if args.plot and mode == "histogram":
        import matplotlib.pyplot as plt
        frequencies, bincenters = averaged_frequencies_bin_centers(result,
           "cos_sq_area_normalized_histogram", "bin_edges_cos_sq_theta")
        plt.plot(bincenters, frequencies)
        plt.xlim(0, 1)
        plt.ylim(0)
        plt.yticks([0], fontsize = 18)
        plt.xlabel('cos_sq_\u03B8', fontsize = 18)
        plt.ylabel('P(\u03B8), a.u.', fontsize = 18)
        plt.legend(shadow = False, fontsize = 18)
        if args.plot != '-':
            plt.savefig(args.plot)
        else:
            plt.show()

    # Plot the histogram, if requested, with
    # the values summed across the timesteps
    if args.saplot and mode == "histogram":
        import matplotlib.pyplot as plt
        frequencies, bincenters = averaged_frequencies_bin_centers(result,
           "cos_sq_solid_angle_normalized_histogram", "bin_edges_cos_sq_theta")
        plt.plot(bincenters, frequencies, label = "Solid angle normalized")
        plt.xlim(0, 1)
        plt.ylim(0)
        plt.yticks([0], fontsize = 18)
        plt.xlabel('cos_sq_\u03B8', fontsize = 18)
        plt.ylabel('P(\u03B8), a.u.', fontsize = 18)
        plt.legend(shadow = False, fontsize = 18)
        if args.plot != '-':
            plt.savefig(args.plot)
        else:
            plt.show()

if __name__ == "__main__":
    main()
