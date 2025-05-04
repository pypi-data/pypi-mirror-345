#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 16 20:21:48 2024

@author: Mikhail Glagolev
"""

import MDAnalysis as mda
import argparse
import sys
import os
import json

home = os.getenv("HOME")
sys.path.append(f'{home}/Documents/Codes/git')

from copoly.block_boundaries import block_boundaries
from mouse2.lib.aggregation import determine_aggregates

def ix_to_resindex(u, ix):
    ag = u.select_atoms(f'index {ix}')
    resid = ag.atoms[0].resindex
    return resindex

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description = 'Find aggregates by type 1 tails')
    parser.add_argument('input', type = str, help = "input file")
    args = parser.parse_args()
    
    u = mda.Universe(args.input)
    
    tail_indices = []
    
    for resindex in set(u.atoms.resindices):
        ag = u.select_atoms(f'resindex {resindex}')
        blocks = block_boundaries(ag.atoms.types)
        block_ix_low = ag.atoms.indices[blocks['2']['max']]
        block_ix_high = ag.atoms.indices[blocks['1']['max']]
        tail = list(range(block_ix_low+1, block_ix_high+1))
        tail_indices += tail
        
    tail_indices_str = ' '.join(map(str, tail_indices))
        
    aggregates = determine_aggregates(u, 1.2,
                                      selection = f'index {tail_indices_str}')
    
    full_aggregates = {}
    full_aggregates["data"] = {}
    
    for key in aggregates["data"]:
        full_aggregates["data"][key] = []
        for i, aggregate in enumerate(aggregates["data"][key]):
            resindices = [ix_to_resindex(u, ix) for ix in aggregate]
            unique_resindices = set(list(resindices))
            unique_resindices_str = ' '.join(map(str, unique_resindices))
            aggregate_ag = u.select_atoms(f'resindex {unique_resindices_str}')
            aggregate_atoms_indices = list(aggregate_ag.atoms.indices)
            ###
            full_aggregates["data"][key].append(list(map(int, aggregate_atoms_indices)))
            aggregates["data"][key][i] = aggregate_atoms_indices
    
    print(json.dumps(full_aggregates))