#!/usr/bin/which python3

import json
import sys
import argparse
import MDAnalysis as mda
from mouse2.mouse2.lib.aggregation import determine_aggregates

#data = json.load(sys.stdin)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description = 'Split system into separate data files, one for each aggregate')
    parser.add_argument('input', type = str, help = "input file")
    args = parser.parse_args()

    u = mda.Universe(args.input)
    
    data = determine_aggregates(u, r_neigh = 1.2)
    
    aggregates_atom_indices = list(data["data"].values())[0]

    for aggregate_number, aggregate_indices in enumerate(aggregates_atom_indices):
        indices_string = ' '.join(map(str, aggregate_indices))
        aggregate_ag = u.select_atoms(f'index {indices_string}')
        name_parts = args.input.split('.')
        extension = name_parts[-1]
        name_parts = name_parts[:-1]
        name_parts += [f'aggregate_{aggregate_number+1}', extension]
        output = '.'.join(name_parts)
        aggregate_ag.write(output)
