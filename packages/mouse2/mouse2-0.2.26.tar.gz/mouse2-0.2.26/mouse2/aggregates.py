#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 23:34:30 2022

@author: Mikhail Glagolev


"""

import MDAnalysis as mda
import json
if __package__ == None:
    from lib.aggregation import determine_aggregates
else:
    from .lib.aggregation import determine_aggregates


def main():
    
    import argparse

    parser = argparse.ArgumentParser(
        description =
        """This utility returns a data structure containing list of aggregates
        for all of the timesteps in the MDAnalysis universe.
        Each aggregate is determined as a complete graph of neighbors.
        The atoms are considered neighbors if the distance between their
        centers does not exceed r_neigh.
        Each aggregate is represented as a list of MDAnalysis atom indices.""")

    parser.add_argument(
        'input', metavar = 'INPUT', action = "store", nargs = '+',
        help = """input file(s), the format will be guessed by MDAnalysis 
        based on file extension""")

    parser.add_argument(
        '--r_neigh', metavar = 'R_neigh', type = float, nargs = '?',
        default = 1.2, help = "neighbor cutoff")

    parser.add_argument(
        '--selection', metavar = 'QUERY', type = str, nargs = '?',
        help 
        = "Consider only selected atoms, use MDAnalysis selection language")

    args = parser.parse_args()

    u = mda.Universe(*args.input)

    result = determine_aggregates(u, args.r_neigh, args.selection)
    
    print(json.dumps(result, indent = 2))
    
if __name__ == "__main__":
    main()
