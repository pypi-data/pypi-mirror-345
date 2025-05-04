#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 12:48:23 2024

@author: Mikhail Glagolev
"""

import MDAnalysis as mda
from MDAnalysis import transformations
import argparse
import numpy as np

parser = argparse.ArgumentParser(
    description = 'Calculate averaged gyration radius')

parser.add_argument('directories', metavar = 'DIRS', type = str, nargs = '+',
    help = 'directories with simulation data')

parser.add_argument('--first', metavar = 'MIN', type = int,
                        nargs = '?', default = 20, help = 'first step to process')

parser.add_argument('--last', metavar = 'MAX', type = int,
                        nargs = '?', default = 120, help = 'last step to process')

args = parser.parse_args()

print('#step\trg_mean\trg_std')
for step in range(args.first,args.last+1):
    rgs = []
    print(f'{step}\t', end = '')
    for directory in args.directories:
        u = mda.Universe(f'{directory}/{step}.data')
        unwrap = transformations.unwrap(u.atoms)
        u.trajectory.add_transformations(unwrap)
        rg = u.atoms.radius_of_gyration()
        #print(f'{rg}\t', end='')
        rgs.append(rg)
    rg_avg = np.mean(rgs)
    rg_std = np.std(rgs)
    print(f'{rg_avg}\t{rg_std}')