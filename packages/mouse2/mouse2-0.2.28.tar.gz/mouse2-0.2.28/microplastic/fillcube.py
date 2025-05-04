#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 17:10:37 2024

@author: misha
"""

def fillcube(dimensions, start, shift):

    nx = dimensions[0]
    ny = dimensions[1]
    nz = dimensions[2]

    ntotal = nx * ny * nz

    step = {'x' : shift[0], 'y' : shift[1], 'z' : shift[2]}

    x = start[0]
    y = start[1]
    z = start[2]
    
    coords = []

    x_counter = 0
    xy_counter = 0
    xyz_counter = 0

    coords.append([x,y,z])
    xyz_counter += 1

    while xyz_counter < ntotal:
        x += step['x']
        coords.append([x,y,z])
        x_counter += 1
        xy_counter += 1
        xyz_counter += 1
        if xy_counter == nx * ny - 1 and xyz_counter < ntotal:
            step['x'] *= -1
            step['y'] *= -1
            z += step['z']
            coords.append([x,y,z])
            x_counter = 0
            xy_counter = 0
            xyz_counter += 1
        elif x_counter == nx - 1 and xyz_counter < ntotal:
            step['x'] *= -1
            y += step['y']
            coords.append([x,y,z])
            x_counter = 0
            xy_counter += 1
            xyz_counter += 1

    return coords


if __name__ == "__main__":
    import MDAnalysis as mda
    import numpy as np
    from mouse2.mouse2.tests.create_configuration import create_empty_universe

    dimensions = [40, 40, 40]

    lbond = 1.

    shift = [lbond, lbond, lbond]

    cell = [1000, 1000, 1000, 90, 90, 90]
    
    add_angles = True
    add_dihedrals = False
    
    output = "test.data"

    ntotal = dimensions[0] * dimensions[1] * dimensions[2]

    start = [cell[0] - lbond * dimensions[0] / 2,\
             cell[1] - lbond * dimensions[1] / 2,\
             cell[2] - lbond * dimensions[2] / 2 ]
    
    u = create_empty_universe(ntotal, cell)
    
    coords = fillcube(dimensions, start, shift)
    
    residue = u.add_Residue(resid = 1, resnum = 1)
    
    molecule_atoms = []
    molecule_atomtypes = ['1'] * ntotal
    molecule_atom_masses = [1] * ntotal
    bonds = []
    bond_types = []
    angles = []
    angle_types = []
    dihedrals = []
    dihedral_types = []
    
    molecules = mda.AtomGroup([],u)
    
    for ix in range(ntotal):

        atom = mda.core.groups.Atom(u = u, ix = ix)
        atom.position = np.array(coords[ix])
        atom.residue = residue
        molecule_atoms.append(atom)
        if ix > 0:
            bonds.append([ix - 1, ix])
            bond_types.append('1')
        if add_angles and ix > 1:
            angles.append([ix - 2, ix - 1, ix])
            angle_types.append('1')
        if add_dihedrals and ix > 2:
            dihedrals.append([ix - 3, ix - 2, ix - 1, ix])
            dihedral_types.append('1')

    molecule_group = mda.AtomGroup(molecule_atoms)
    molecule_group.atoms.types = molecule_atomtypes
    molecule_group.atoms.masses = molecule_atom_masses
    molecules += molecule_group
    u.add_bonds(bonds, types = bond_types)
    if add_angles:
        u.add_angles(angles, types = angle_types)
    if add_dihedrals:
        u.add_dihedrals(dihedrals, types = dihedral_types)
    molecule_group.write(output)