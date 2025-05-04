#!/usr/bin/which python3
import MDAnalysis as mda
import numpy as np
from modify_seq import remove_connectivity

npoly = 16
atomtypes = ['1','2']

sequences = {
    '0.0' : [1],
    '12.5' : [1, 2, 9],
    '18.75' : [1, 2, 7, 11],
    '25.0' : [1, 2, 6, 9, 13],
    '31.25' : [1, 2, 5, 8, 11, 14],
    '37.5' : [1, 2, 4, 6, 9, 11, 13],
    '43.75' : [1, 2, 4, 6, 8, 10, 12, 14],
    '50.0' : [1, 2, 4, 6, 8, 10, 11, 13, 14],
    '56.25' : [1, 2, 4, 5, 7, 8, 10, 11, 13, 14]
}

for fmod in sequences:
    u = mda.Universe('initial_sequence.data')
    natoms = u.atoms.n_atoms
    if natoms % npoly == 0:
        nmol = int(natoms / npoly)
    else:
        raise NameError(f"{natoms} atoms are not divisible into {npoly}-mers")
    new_atomtypes = np.full(natoms, atomtypes[0])
    atom_molecule_tags = []
    for imol in range(nmol):
        for iatom in sequences[fmod]:
            new_atomtypes[iatom - 1 + imol * npoly] = atomtypes[1]
        atom_molecule_tags += [imol + 1] * npoly
    u.atoms.types = new_atomtypes
    u.trajectory.ts.data['molecule_tag'] = atom_molecule_tags
    remove_connectivity(u)
    u.atoms.write(f"initial_{fmod}.data")
