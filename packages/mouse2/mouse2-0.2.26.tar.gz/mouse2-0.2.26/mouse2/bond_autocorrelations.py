#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 19:59:20 2022

@author: Mikhail Glagolev
"""
import MDAnalysis as mda
from MDAnalysis import transformations
import numpy as np
import json

# Fitting parameters for the autocorrelation function
A_GUESS = 1.
P_GUESS = 3.
BETA_GUESS = 0.
B_GUESS = 0.

FIT_PLOT_DENSITY = 10 # Must be integer

def bond_autocorrelations(u: mda.Universe, k_max,
                                    selection = None,
                                    different_molecules: bool = False):
    """
    
    Calculate the autocorrelation function of the polymer bonds.
    The formula is presented in https://doi.org/10.1134/S0965545X10070102
    Application to all-atom simulations: https://doi.org/10.3390/polym11122056

    Parameters
    ----------
    u : mda.Universe
        Input data for analysis as MDAnalysis Universe.
    k_max : integer
        The maximum value of the distance between the bonds along the backbone
    different_molecules : bool
        Take into account the bonds where the particles have different
        residue ids. The default value is False.

    Returns
    -------
    {description: "Bond vectors autocorrelation function, for k in 
                   [0,...,k_max] the vectors belonging to different
                   molecules are (not) taken into account",
     data: {ts1: [c(0), c(1), c(2), ..., c(k_max)],
            ts2: [c(0), c(1), c(2), ..., c(k_max)],
            ....
           }
    }

    """
    # Prepare the description of the output:
    description = "Bond vectors autocorrelation function, for k in [0,...,"
    description += str(k_max)
    if different_molecules:
        description += ("], the vectors belonging to different molecules"
                    + "are taken into account")
    else:
        description += ("], the vectors belonging to different molecules"
                    + "are not taken into account")
    # Unwrap all the coordinates, so that all the bond lengths are correct.
    unwrap = transformations.unwrap(u.atoms)
    u.trajectory.add_transformations(unwrap)
    
    # Select atoms by type or read selection criteria in MDAnalysis synthax
    if selection is not None:
        atoms = u.select_atoms(selection)
    else:
        atoms = u.atoms
    
    # Create the dictionary structure for the data for all timesteps
    data = {}
    
    for ts in u.trajectory:
        # List of c[k] = c(k), k = 0, 1, 2, ...
        ck = []
        # Total number of bonds
        nbonds = len(atoms.bonds)
        # Molecule ids
        bond_resids = atoms.bonds.atom1.resids
        #Determine the vectors for all the bonds with NumPy
        b = atoms.bonds.atom2.positions - atoms.bonds.atom1.positions   
        # Consider each value of the shift between the bonds k
        for k in range(0, k_max + 1):
            # Create two array shifted by k, by padding the arrays with
            # the values of "1." (so that vector length is not zero)
            b1 = np.pad(b, ((0, k), (0, 0)), constant_values = 1.)
            b2 = np.pad(b, ((k, 0), (0, 0)), constant_values = 1.)
            # Consider the calculation result valid if neither value is padded
            valid1 = np.concatenate((np.full((nbonds,), True),
                                    np.full((k,), False)))
            valid2 = np.concatenate((np.full((k,), False),
                                    np.full((nbonds,), True)))
            valid = np.logical_and(valid1, valid2)
            # If cross-molecule correlations should not be accounted for,
            # then also check for the equality of the resids
            if not different_molecules:
                # Pad the residue id arrays
                resid1 = np.pad(bond_resids, (0, k), constant_values = 0)
                resid2 = np.pad(bond_resids, (k, 0), constant_values = 0)
                # Take into account only molecules with same residue id
                valid = np.logical_and(valid, np.equal(resid1, resid2))
            # Mask is True for the values that are not valid    
            mask = np.logical_not(valid)
            # Calculate the correlation values for all the bonds
            c = ( np.sum( np.multiply(b1, b2), axis = 1)
                 / np.linalg.norm(b1, axis = 1)
                 / np.linalg.norm(b2, axis = 1))
            c_masked = np.ma.masked_array(c, mask = mask)
            c_average = np.ma.average(c_masked)
            ck.append(c_average)
        data[str(ts)] = { "ck" : ck }
    return { "description" : description, "data" : data }

def main():
    
    import argparse

    parser = argparse.ArgumentParser(
        description = """Calculate the autocorrelation function of the 
        polymer bonds. The formula is presented in 
        https://doi.org/10.1134/S0965545X10070102 Application to
        all-atom simulations: https://doi.org/10.3390/polym11122056""")

    parser.add_argument(
        'input', metavar = 'INPUT', action = "store", nargs = '+',
        help = """input file(s), the format will be guessed by MDAnalysis 
        based on file extension""")

    parser.add_argument(
        '--k_max', metavar = 'k_max', type = int, nargs = '?',
        default = 0,
        help = "maximum distance between the bonds along the backbone")
    
    parser.add_argument(
        '--selection', metavar = 'QUERY', type = str, nargs = '?',
        help 
        = "Consider only selected atoms, use MDAnalysis selection language")
    
    parser.add_argument(
        "--different-molecules", action = "store_true",
        help = "Calculate correlations based on particle index number,\
            even if the bonds belong to different molecules")
            
    parser.add_argument('--plot', action = "store_true",
                            help = "Plot the averaged results")
    
    parser.add_argument('--fit', action = "store_true",
        help = 
        "Fit the averaged results with a modulated exponential function")
    
    parser.add_argument(
        '--p_guess', metavar = 'NUMBER', type = float, nargs = '?',
        default = 3.5,
        help = "Initial guess for the number of monomer units per turn")
    

    args = parser.parse_args()

    u = mda.Universe(*args.input)
    
    result = bond_autocorrelations(u, k_max = args.k_max,
                                   selection = args.selection,
                                   different_molecules = 
                                   args.different_molecules)

    
    if args.plot or args.fit:
        #Average the data across the timesteps
        summed_data = np.ndarray((args.k_max + 1,))
        for ts in result["data"]:
            summed_data += np.asarray(result["data"][ts]["ck"])
        averaged_data = summed_data / len(result["data"])
        
    if args.fit:
        # Fit the averaged results with a fitting function
        from scipy.optimize import curve_fit
        def fitting_function(x, a, p, beta, b):
            return a * (np.cos(2. * np.pi * x / p) + b) * np.exp(x * beta)
        initial_guess = [ A_GUESS, args.p_guess, BETA_GUESS, B_GUESS ]
        # Fit the averaged data, starting with k=1
        params, covariance = curve_fit(fitting_function,
                                       list(range(1, args.k_max + 1 )), 
                                       averaged_data[1:], p0=initial_guess)
            
    # Plot the values, if requested, with
    # the values averaged across the timesteps
    if args.plot:
        import matplotlib.pyplot as plt
        plt.plot(range(args.k_max + 1), averaged_data)
        if args.fit:
            # Create points for the fitting function. 
            fitting_x = np.asarray(list(range(args.k_max 
                                              * FIT_PLOT_DENSITY + 1)))
            fitting_x = fitting_x / float(FIT_PLOT_DENSITY)
            vectorized_fitting_function = np.vectorize(fitting_function,
                                                       excluded = [1, 2, 3, 4])
            fitting_y = vectorized_fitting_function(fitting_x, params[0],
                                            params[1], params[2], params[3])
            plt.plot(fitting_x, fitting_y,
                     label = "p=%.2f" % params[1] 
                     + "\nbeta=%.2f" % params[2]
                     + "\nb=%.2f" % params[3])
        plt.xlabel('k', fontsize = 18)
        plt.ylabel('C(k)', fontsize = 18)
        plt.legend(shadow = False, fontsize = 18)
        plt.show()
        
    print(json.dumps(result, indent = 2))

if __name__ == "__main__":
    main()
