#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 20:22:55 2024

@author: misha
"""

import MDAnalysis as mda
import argparse
import random
from numpy.random import choice
import pandas as pd

import pdb
types = ['1']


def modify_midchain(ag, total_prob = 0.,
                    distrib = None,
                    check_current_type = True,
                    source_types = None):

    atomtypes = ag.atoms.types

    natoms = len(ag.atoms)
    
    target_n_modified = int(round(natoms * total_prob))

    n_modified = 0

    while n_modified < target_n_modified:
        i = random.randrange(natoms)
        bead_type = choice(distrib['type'], 1,
                           p = distrib['chain']/distrib['chain'].sum())[0]
        if atomtypes[i] in source_types or check_current_type == False:
            atomtypes[i] = bead_type
            n_modified += 1


def split_points_uniform(n, nparts):
    """Returns the indices of the atoms before the splits"""
    split_points = [int(round(i*nparts/n)) for i in range(nparts-1)]
    # nparts = n: split_points = 0...n-2
    return list(split_points)


def split_points_random(n, nparts):
    """Returns the indices of the atoms before the splits"""
    split_points = random.choices(range(n), k=nparts-1)
    return split_points


def molecule_tags(n, split_points):
    molecule_tags = []
    molecule_tag = 1
    for i in range(n):
        molecule_tags.append(molecule_tag)
        if i in split_points:
            molecule_tag += 1
    return molecule_tags


def delete_connections(u, n, split_points):
    
def split_and_modify(ag, nparts = 1,
                     distrib = None,
                     check_current_type = False,
                     source_types = None,
                     spacing = 'random'):
    #generate split points
    if spacing == 'random':
        split_points = split_points_random(len(ag.atoms), nparts)
    elif spacing == 'uniform':
        split_points = split_points_uniform(len(ag.atoms), nparts)
    else:
        raise NameError(f"Spacing scheme {spacing} is not implemented")
    
    #generate molecule tags sequence
    
    #remove bonds and angles

    #Remove bonds
    if nsplit is not None:
        atom_molecule_tags = [int(i*nsplit/npoly)+1 for i in range(npoly)]
        prev_tag = atom_molecule_tags[:-1]
        prev_ix = u.atoms.ix[:-1]
        next_tag = atom_molecule_tags[1:]
        next_ix = u.atoms.ix[1:]
        diff_tags = [next_tag != prev_tag for prev_tag, next_tag
                     in zip(prev_tag, next_tag)]
        indices = [i for i, to_cut in enumerate(diff_tags) if to_cut]
        prev_atom_ix = [prev_ix[ix] for ix in indices]
        next_atom_ix = [next_ix[ix] for ix in indices]
        #Remove angles
        bonds_to_delete = list(zip(prev_atom_ix, next_atom_ix))
        u.delete_bonds(bonds_to_delete)
        for bond_atoms in bonds_to_delete:
            for angle in u.angles:
                atom_in_angle_count = 0
                for i in range(3):
                    atom_ix = angle.atoms[i].ix
                    if atom_ix in bond_atoms:
                        atom_in_angle_count += 1
                if atom_in_angle_count >= 2:
                    u.delete_angles([angle])
        u.trajectory.ts.data['molecule_tag'] = atom_molecule_tags

if __name__ == "__main__":

    parser = argparse.ArgumentParser("Modify some atoms' types from 1 to 2")

    parser.add_argument("input", type = str, help = "input filename")

    parser.add_argument("output", type = str, help = "output filename")

    parser.add_argument("--prob", type = float, help = "probability of atom type change")
    
    parser.add_argument("--distributions", type = str, help = "modification probabilities")

    parser.add_argument("--split-equal", metavar = "M", nargs = 1, type = int, 
                        default = None, help = "split into M equal chains")

    args = parser.parse_args()

    prob = args.prob

    distributions = pd.read_excel(args.distributions)

    nsplit = args.split_equal[0]

    # Read configuration

    u = mda.Universe(args.input)

    modify_seq(u, prob = prob, distrib = distributions, nsplit = nsplit)

    u.atoms.write(args.output)