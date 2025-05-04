#!/usr/bin/env python3
# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
# MOUSE
# Copyright (c) 2022 Mikhail Glagolev
#
# Released under the GNU Public Licence, v2 or any higher version

import argparse
import MDAnalysis as mda
from MDAnalysis import transformations
if __package__ == None:
    from lib.utilities import names_from_types
else:
    from .lib.utilities import names_from_types

def main():
    """
    This utility reads LAMMPS data file, and writes out the configuration
    in the PDB format

    Possible options are:
    --no-pbc-bonds
    hide the bonds which are not between the nearest images
    of the particles, used for visualisation
    """

    parser = argparse.ArgumentParser(
        description = 'Convert LAMMPS data file into PDB')

    parser.add_argument(
        'input', metavar = 'LAMMPS_DATA', nargs = '+', help = "input file")

    parser.add_argument(
        'output', metavar = 'PDB', nargs = 1, help = "output file")

    parser.add_argument(
        "--show-pbc-bonds", action = "store_true",
        help = "Show the bonds transversing the periodic boundary conditions")

    parser.add_argument(
        "--unwrap", action = "store_true",
        help = "Unwrap the molecules")

    args = parser.parse_args()
    
    if len(args.input) == 1:
        input_fmt = 'DATA'
    if len(args.input) > 1:
        input_fmt = 'LAMMPSDUMP'

    u = mda.Universe(*args.input, format = input_fmt)
    
    if args.unwrap:
        unwrap = transformations.unwrap(u.atoms)
        try:
            u.trajectory.add_transformations(unwrap)
        except ValueError:
            pass

    if not args.show_pbc_bonds:
        minbox = min(u.dimensions) / 2.
        bonds_to_delete = [
            bond for bond in u.bonds if bond.length(pbc = False) > minbox]
        u.delete_bonds(bonds_to_delete)

    names_from_types(u)

    with mda.Writer(args.output[0], multiframe = True) as W:
        for ts in u.trajectory:
            W.write(u.atoms)

if __name__ == "__main__":
    main()
