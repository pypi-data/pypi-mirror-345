#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 20:22:55 2024

@author: misha
"""

import MDAnalysis as mda
import argparse
import random
import math


types = ['1', '2']

def modify_seq(u, prob = 0., nsplit = None, distribution = "random"):
    if nsplit is not None and nsplit > 1:
        split_sequence_uniform(u, nsplit)
    if prob > 0.:
        if distribution == "random":
            modify_atoms_random(u, prob)
        elif distribution == "uniform":
            modify_atoms_uniform(u, prob)
        else:
            raise NameError(f"{distribution} atomtype modification\
 is not implemented")


def modify_atoms_random(u, prob):
    atomtypes = u.atoms.types

    npoly = len(u.atoms)

    target_n_modified = int(round(npoly * prob))

    n_modified = 0

    while n_modified < target_n_modified:
        i = random.randrange(npoly)
        if atomtypes[i] == types[0]:
            atomtypes[i] = types[1]
            n_modified += 1

    u.atoms.types = atomtypes


def modify_atoms_uniform(u, prob):
    atomtypes = []
    npoly = len(u.atoms)
    for iatom in range(npoly):
        if math.floor((iatom + 1) * prob) > math.floor(iatom * prob):
            atomtypes.append(types[1])
        else:
            atomtypes.append(types[0])

    u.atoms.types = atomtypes


def split_sequence_uniform(u, nsplit):
    npoly = len(u.atoms)
    #Remove bonds
    atom_molecule_tags = [int(i*nsplit/npoly)+1 for i in range(npoly)]
    u.trajectory.ts.data['molecule_tag'] = atom_molecule_tags
    remove_connectivity(u)


def remove_connectivity(u):
    atom_molecule_tags = u.trajectory.ts.data['molecule_tag']
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


def prepare_sample(simulation):
    """Fetch the required inital sequence and modify it"""

    config = simulation['config']
    run_parameters = config['run_parameters']
    model_parameters = config['model_parameters']
    trial_parameters = simulation['trial_parameters']

    initial_sequence_file = run_parameters['initial_data']

    for model_parameter in model_parameters:
        initial_sequence_file = initial_sequence_file.replace(
                             model_parameter, str(
                        trial_parameters[model_parameter]))

    u = mda.Universe(initial_sequence_file)

    prob = trial_parameters.get('fmod', 0.)
    nsplit = trial_parameters.get('nsplit', 1)
    try:
        distribution = model_parameters['fmod']['details']['distribution']
    except KeyError:
        distribution = "random"
    modify_seq(u, prob = prob, nsplit = nsplit, distribution = distribution)

    return u


if __name__ == "__main__":

    parser = argparse.ArgumentParser("Modify some atoms' types from 1 to 2")

    parser.add_argument("input", type = str, help = "input filename")

    parser.add_argument("output", type = str, help = "output filename")

    parser.add_argument("--prob", type = float, help = "probability of atom type change")

    parser.add_argument("--split-equal", metavar = "M", nargs = 1, type = int, 
                        default = None, help = "split into M equal chains")

    args = parser.parse_args()

    prob = args.prob

    nsplit = args.split_equal[0]

    # Read configuration

    u = mda.Universe(args.input)

    modify_seq(u, prob = prob, nsplit = nsplit)

    u.atoms.write(args.output)