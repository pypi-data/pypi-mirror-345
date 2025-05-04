#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Common utilities for the mouse2 toolkit

Created on Mon Dec 12 01:24:29 2022

@author: Mikhail Glagolev
"""

import numpy as np

def normalize_vectors(vectors):
    """
    Normalize an array of vectors

    """
    shape = vectors.shape
    norms = np.linalg.norm(vectors, axis = 1).reshape((shape[0], 1))
    return vectors / norms

def names_from_types(u):
    """
    Create name attribute for a universe and write type values to it

    """
    u.add_TopologyAttr('name', ['']*u.atoms.n_atoms)

    atomtypes = list(set([atom.type for atom in u.atoms]))

    for atomtype in atomtypes:
        selection = u.select_atoms("type " + str(atomtype))
        selection.atoms.names = [str(atomtype)] * selection.atoms.n_atoms