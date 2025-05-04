#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 14:25:38 2023

@author: Mikhail Glagolev

This script can create different simple initial configurations
for molecular dynamics simulations, which are used to check the
assessment of the ordering parameters by the mouse2 routines.

Currently, it can create a cubic cell with a choice of the following:
    - randomly distributed random walk polymer chains
    - randomly distributed polymer rods (all bonds of the macromolecule
      are parallel to each other)
    - randomly distributed polymer rods, each rod oriented randomly
    - randomly distributed helical fragments
    
In case of rods and helices, they can be oriented either along one common
director, generated randomly for all the system, or, if the --type is used
with the "disorder-" prefix, each be oriented along its own random director.
     
"""

import MDAnalysis as mda
import numpy as np
import random
import math
import argparse
from scipy.spatial.transform import Rotation
try:
    from mouse2.mouse2.lib.neighbor import calculate_squared_distances
except ModuleNotFoundError:
    from mouse2.lib.neighbor import calculate_squared_distances

RANDOM_SEED = 42
# System parameters
LBOND = 1.
#RBEAD = 1.25 * LBOND / 2. #1.122 * LBOND / 2.
# Helical structure parameters
RTUBE = 0.53
PITCH = 1.66
PER_TURN = 3.3

def create_empty_universe(ntotal, cell):
    u = mda.Universe.empty(ntotal, trajectory = True,
                           atom_resindex = [0,] * ntotal)

    u.add_TopologyAttr('type')
    u.add_TopologyAttr('mass') #, values = [1.,] * NMOL * NPOLY)
    u.add_TopologyAttr('resids')
    u.add_TopologyAttr('resnums')
    u.add_TopologyAttr('angles', values = [])
    u.add_TopologyAttr('dihedrals', values = [])
    u.add_TopologyAttr('impropers', values = [])

    #Set the simulation cell size
    u.dimensions = cell

    return u


def overlap4d(probe4d, coords4d, box, r = LBOND / 2.):
    """
    Check if the sphere of radius r placed at the probe coordinates
    overlaps with one of the spheres of radius r placed at coords coordinates.

    """
    # Add periodic boundary conditions
    x_coords4d = coords4d[:, 1]
    y_coords4d = coords4d[:, 2]
    z_coords4d = coords4d[:, 3]
    real_coords4d = [x_coords4d, y_coords4d, z_coords4d]
    real_probe4d = probe4d[1:]
    real_dr_sq = calculate_squared_distances(real_coords4d, real_probe4d, box)
    virtual_dr_sq = np.square(coords4d[:,0] - probe4d[0])
    total_dr_sq = real_dr_sq + virtual_dr_sq
    overlap = np.sum(np.less_equal(total_dr_sq, 4. * r**2))
    if overlap > 0:
        return True
    else:
        return False


def read_atomtypes(atomtypes_filename):
    """
    Read the atom types sequences.
    One sequence per string
    """
    all_atomtypes = []
    atomtypes_file = open(atomtypes_filename, 'r')
    for line in atomtypes_file.readlines():
        all_atomtypes.append(line.split())
    return all_atomtypes


def create_configuration(system_type = None, npoly = None, nmol = None,
                         box = None, output = None, add_angles = False,
                         add_dihedrals = False, self_avoid = None,
                         atomtypes = None):
    
    if ((nmol is not None) or (npoly is not None)) and atomtypes is not None:
        raise NameError("Atomtype sequences can not be used together with\
                        nmol or npoly")

    cell = [box] * 3 + [90, 90, 90]
    if atomtypes is None:
        npolys = [npoly] * nmol
    else:
        all_atomtypes = read_atomtypes(atomtypes)
        nmol = len(all_atomtypes)
        npolys = [len(seq) for seq in all_atomtypes]
    ntotal = sum(npolys)

    #random.seed(RANDOM_SEED)

    u = create_empty_universe(ntotal, cell)

    ix = 0
    bonds = []
    bond_types = []
    if add_angles:
        angles = []
        angle_types = []
    if add_dihedrals:
        dihedrals = []
        dihedral_types = []
    molecule_tags = []

    if self_avoid is not None:
        RBEAD = float(self_avoid) * LBOND / 2.
        raw_coords = np.full((ntotal, 4), [2 * RBEAD, 0., 0., 0.])

    all_molecules = mda.AtomGroup([],u)

    # If the system is not "disordered", all of the molecules will have
    # the same (random) orientation
    if system_type[:10] != "disordered":
        molecule_rotation = Rotation.random()


    for imol in range(nmol):
        npoly = npolys[imol]
        #Generate molecule:
        current_residue = u.add_Residue(resid = imol + 1, resnum = imol + 1)
        molecule_atoms = []
        this_molecule_tags = [imol + 1] * npoly
        if atomtypes is not None:
            molecule_atomtypes = read_atomtypes(atomtypes)[imol]
            if len(molecule_atomtypes) != npoly:
                raise NameError("Atomtype string length != N")
        else:
            molecule_atomtypes = ['1'] * npoly
        molecule_atom_masses = []
        x, y, z = 0., 0., 0.
        for iatom in range(npoly):
            #Calculating coordinates for the next atom:
            #Random walk
            if system_type[:6] == "random":
                bond_vector = [0., 0., LBOND]
                while True:
                    rotation = Rotation.random()
                    rotated_bond = Rotation.apply(rotation, bond_vector)
                    xnew = x + rotated_bond[0]
                    ynew = y + rotated_bond[1]
                    znew = z + rotated_bond[2]
                    # Check overlapping and return doesnt_overlap
                    if self_avoid is not None:
                        if iatom == 0:
                            overlaps = overlap4d([0., xnew, ynew, znew],
                                                 raw_coords, cell[:3],
                                                 r = RBEAD)
                        else:
                            overlaps = overlap4d([0., xnew, ynew, znew],
                                                 np.delete(raw_coords, ix-1,
                                                 axis = 0), cell[:3],
                                                 r = RBEAD)
                        if not overlaps:
                            break
                    else:
                            break
                x = xnew
                y = ynew
                z = znew
                raw_coords[ix] = [0., x, y, z]
            #Rod
            if system_type[-4:] == "rods":
                bond_vector = [0., 0., LBOND]
                x += bond_vector[0]
                y += bond_vector[1]
                z += bond_vector[2]
            #Helix
            if system_type[-7:] == "helices":
                x = RTUBE * math.cos((iatom + 1) * 2. * math.pi / PER_TURN)
                y = RTUBE * math.sin((iatom + 1) * 2. * math.pi / PER_TURN)
                z = PITCH * (iatom + 1) / PER_TURN
            #Creating an atom with the current coordinates:
            atom = mda.core.groups.Atom(u = u, ix = ix)
            atom.position = np.array([x, y, z])
            atom.residue = current_residue
            molecule_atoms.append(atom)
            if iatom > 0:
                bonds.append([ix - 1, ix])
                bond_types.append('1')
            if add_angles and iatom > 1:
                angles.append([ix - 2, ix - 1, ix])
                angle_types.append('1')
            if add_dihedrals and iatom > 2:
                dihedrals.append([ix - 3, ix - 2, ix - 1, ix])
                dihedral_types.append('1')
            #molecule_atomtypes.append('1')
            molecule_atom_masses.append(1.)
            ix += 1
        molecule_group = mda.AtomGroup(molecule_atoms)
        molecule_tags += this_molecule_tags
        # Place the first monomer unit randomly in the simulation cell
        while True:
            translation_vector = np.array(cell[:3]) * \
                np.array([random.random(), random.random(), random.random()])
            if system_type[:10] == "disordered":
                molecule_rotation = Rotation.random()
            new_positions = Rotation.apply(molecule_rotation,
                                        molecule_group.atoms.positions)
            new_positions += translation_vector
            has_overlap = False
            if self_avoid is not None:
                for i_atom, atom_pos in enumerate(new_positions):
                    #checked_atom_ix = ix - len(new_positions) + i_atom
                    atom_pos_4d = [0, atom_pos[0], atom_pos[1], atom_pos[2]]
                    #raw_coords_excl = np.delete(raw_coords, checked_atom_ix, axis = 0)
                    if overlap4d(atom_pos_4d, raw_coords, cell[:3], r=RBEAD):
                        has_overlap = True
                        break
            if not has_overlap:
                for i_atom, atom_pos in enumerate(new_positions):
                    current_atom_ix = ix - len(new_positions) + i_atom
                    raw_coords[current_atom_ix] = [0, atom_pos[0],
                                                   atom_pos[1], atom_pos[2]]
                molecule_group.atoms.positions = new_positions
                break
        molecule_group.atoms.types = molecule_atomtypes
        molecule_group.atoms.masses = molecule_atom_masses
        all_molecules += molecule_group
    u.add_bonds(bonds, types = bond_types)
    if add_angles:
        u.add_angles(angles, types = angle_types)
    if add_dihedrals:
        u.add_dihedrals(dihedrals, types = dihedral_types)
    u.trajectory.ts.data['molecule_tag'] = molecule_tags
    all_molecules.write(output)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description = 'Create test systems for mouse2 library')

    parser.add_argument(
        '--type', metavar = 'TYPE', nargs = 1, type = str,
        help = "system type: [disordered-]rods, [disordered-]helices," +
        " random")

    parser.add_argument(
        '--npoly', metavar = 'N', nargs = '?', type = int, const = None,
        help = "degree of polymerization")

    parser.add_argument(
        '--nmol', metavar = 'n', nargs = '?', type = int, const = None,
        help = "number of macromolecules")

    parser.add_argument(
        '--box', metavar = 'SIZE', nargs = 1, type = float,
        help = "rectangular simulation cell size")

    parser.add_argument(
        'output', metavar = 'FILE', action = "store",
        help = "output file, the format is determined by MDAnalysis based" +
        " on the file extension")
    
    parser.add_argument(
        '--angles', action = "store_true", help = "Add bond angles")

    parser.add_argument(
        '--dihedrals', action = "store_true", help = "Add dihedral angles")

    parser.add_argument(
        '--self-avoid', nargs = "?", const = 1.122, default = None,
        help = "Avoid overlapping of the spheres with diameter=bond length")

    parser.add_argument(
        '--atomtypes', metavar = 'ATOM_TYPES_SEQUENCE', nargs = '?', 
        type = str, default = None, help = "file with atomtypes sequences")

    args = parser.parse_args()

    create_configuration(system_type = args.type[0],
                         npoly = args.npoly,
                         nmol = args.nmol,
                         box = args.box[0],
                         output = args.output,
                         add_angles = args.angles,
                         add_dihedrals = args.dihedrals,
                         self_avoid = args.self_avoid,
                         atomtypes = args.atomtypes)
