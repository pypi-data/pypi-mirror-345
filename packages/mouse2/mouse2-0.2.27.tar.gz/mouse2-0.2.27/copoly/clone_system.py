#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 15:19:55 2024

@author: misha
"""
import MDAnalysis as mda
from MDAnalysis import transformations
import argparse
import numpy as np

spacing_factor = [1.01, 1.01, 1.01]


def pos_boundaries(u, axis):
    pos_min = np.min(u.atoms.positions[:, axis])
    pos_max = np.max(u.atoms.positions[:, axis])
    return pos_min, pos_max

def cell_size(u, axis, spacing_factor):
    pos_min, pos_max = pos_boundaries(u, axis)
    cell_size = (pos_max - pos_min) * spacing_factor[axis]
    return cell_size

def tile_universe(universe, nclone, shift):
    copied = []
    atom_molecule_tags = []
    i_universe = 0
    for x in range(nclone[0]):
        for y in range(nclone[1]):
            for z in range(nclone[2]):
                i_universe += 1
                atom_molecule_tags += [i_universe] * universe.atoms.n_atoms
                u_ = universe.copy()
                move_by = np.multiply(shift, (x, y, z))
                u_.atoms.translate(move_by)
                copied.append(u_.atoms)

    new_universe = mda.Merge(*copied)
    new_box = np.multiply(shift,nclone)
    new_universe.dimensions = list(new_box) + [90]*3
    new_universe.trajectory.ts.data['molecule_tag'] = atom_molecule_tags
    return new_universe

# Read command line options

parser = argparse.ArgumentParser(
    description =
        'Clone the conformations along the axes for specified number of times')

parser.add_argument('input', metavar = 'DATA', type = str, nargs = 1,
    help = 'input data file')

parser.add_argument('output', metavar = 'DATA', type = str, nargs = 1,
    help = 'output data file')

parser.add_argument('--x', metavar = 'Nx', type = int,
          nargs = '?', default = 1, help = 'number of clones along the X axis')

parser.add_argument('--y', metavar = 'Ny', type = int,
          nargs = '?', default = 1, help = 'number of clones along the Y axis')

parser.add_argument('--z', metavar = 'Nz', type = int,
          nargs = '?', default = 1, help = 'number of clones along the Z axis')

args = parser.parse_args()

nclone = [args.x, args.y, args.z]

# Load data
u = mda.Universe(args.input[0])
unwrap = transformations.unwrap(u.atoms)
u.trajectory.add_transformations(unwrap)

# Determine xlo, xhi, ylo, yhi, zlo, zhi
xcell = cell_size(u, 0, spacing_factor)
ycell = cell_size(u, 1, spacing_factor)
zcell = cell_size(u, 2, spacing_factor)

shift = max([xcell, ycell, zcell])
shift_vec = [shift] * 3

u_new = tile_universe(u, nclone, shift_vec)

u_new.atoms.write(args.output[0])