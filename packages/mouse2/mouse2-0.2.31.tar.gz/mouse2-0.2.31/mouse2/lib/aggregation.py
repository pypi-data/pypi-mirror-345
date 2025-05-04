#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 20:15:18 2022

@author: Mikhail Glagolev
"""

import MDAnalysis as mda
import numpy as np
import networkx as nx
from .neighbor import calculate_neighborlists_from_distances

def determine_aggregates(u: mda.Universe, r_neigh: float, selection = None,
                         ts_indices = None, bonded_as_neighbors = False):
    """
    This function returns a data structure containing list of aggregates
    for all of the timesteps in the MDAnalysis universe.
    Each aggregate is determined as a complete graph of neighbors.
    The atoms are considered neighbors if the distance between their
    centers does not exceed r_neigh.
    Each aggregate is represented as a list of MDAnalysis atom indices.

    Parameters
    ----------
    universe : mda.Universe
        MDAnalysis universe. Only the bonds required for calculation of the
        ordering parameter shall be present. All other bonds shall be deleted
        from the universe before the analysis.
    r_max : FLOAT, optional
        Maximum distance at which the atoms are considered neighbors.
    selection : STR, optional
        Selection string for MDAnalysis select_atoms command.
        Only the selected atoms will be considered.
        The default is None, and all atoms are taken into account.

    Returns
    -------
    {description: "Lists of aggregates for a given timestep. Cutoff radius
                   r_max = r_max. [Selection: "selection_string" (optional)]
     data: {ts1: [[aggregate1_atom1, aggregate1_atom2, ...],
                  [aggregate2_atom1, ... ]]
            ts2: [[aggregate1_atom1, aggregate1_atom2, ...],
                 [aggregate2_atom1, ... ]],
            ....
           }
    }

    """
    description = ("Lists of aggregates for a given timestep. Cutoff radius"
                   " r_neigh =" + str(r_neigh))
    # Select atoms by type or read selection criteria in MDAnalysis synthax
    if selection is not None:
        atoms = u.select_atoms(selection)
        description += " Selection: " + selection
    else:
        atoms = u.atoms
        
    data = {}
        
    if ts_indices is None:
        ts_indices = range(len(u.trajectory))
    for i in ts_indices:
        ts = u.trajectory[i]
        # Each aggregate will be presented as a list of lists:
        # [[aggregate1_atom1, aggregate1_atom2, aggregate1_atom3, ...],
        #  [aggregate2_atom1, aggregate2_atom2, ...], [aggregate3_atom1, ...]]
        aggregates = []
        # Create numpy array with a list of atom indices
        atom_indices = atoms.indices
        # Create numpy array with the coordinates of the atoms
        rx = atoms.positions[:, 0]
        ry = atoms.positions[:, 1]
        rz = atoms.positions[:, 2]
    
        atom_positions = [rx, ry, rz]
        # Create neighbor lists. Compare my function to the MDAnalysis standard
        # function
        # neighborlists = { atom_index : [neighbor1_index, neighbor2_index, ]}
        neighborlists = calculate_neighborlists_from_distances(atom_indices,
                                                            atom_positions,
                                                            box = u.dimensions,
                                                            r_max = r_neigh)
        #Option 2: use MDAnalysis function to calculate neighbor lists:
    
        #Add bonded atoms to neighborlists, if necessary:
        if bonded_as_neighbors:
            for ix in neighborlists:
                bonded_indices = [a.index for a in u.atoms[ix].bonded_atoms]
                neighborlists[ix].append(bonded_indices)
                neighborlists[ix] = list(set(neighborlists[ix]))

        # Initialize a NetworkX graph
        graph = nx.Graph()
        # For every atom add the neighbors to the graph
        for atom_index in neighborlists:
            for neighbor in neighborlists[atom_index]:
                graph.add_edge(atom_index, neighbor)
        # Convert atom indices to a list
        atom_indices_list = np.ndarray.tolist(atom_indices)
        # While list length > 0:
        while len(atom_indices_list) > 0:
            aggregate = []
            aggregate_atoms = nx.dfs_postorder_nodes(graph,
                                                     atom_indices_list[0])
            for atom in aggregate_atoms:
                aggregate.append(int(atom))
                atom_indices_list.remove(atom)
            aggregates.append(aggregate)
        data[str(ts)] = aggregates
    return { "description" : description, "data" : data }
