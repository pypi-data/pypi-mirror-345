#!/usr/bin/env python3

"""

    Calculate the molecular ordering parameters for lamellae
    containing tilted copolymer blocks, as described in the
    paper by M. A. Osipov, M. V. Gorkunov, A. V. Berezkin,
    A. A. Antonov and Y. V. Kudryavtsev "Molecular theory
    of the tilting transition and computer simulations of
    the tilted lamellar phase of rod–coil diblock copolymers"
    https://doi.org/10.1063/5.0005854
    

@author: Anna Glagoleva, Mikhail Glagolev

"""


import numpy as np
import MDAnalysis as mda
from MDAnalysis import transformations
from .utilities import normalize_vectors


def normal_vector(dir_vectors):
    """
    Calculate the normal vector, as the vector corresponding
    to the largest eigenvalue.

    """
    # compute the gyration tensor for the vectors connecting COMs
    tensor = (np.einsum('im,in->mn', dir_vectors, dir_vectors) 
                   / float(len(dir_vectors)))
    # find eigenvalues and eigenvectors 
    eigen_vals, eigen_vecs = np.linalg.eig(tensor)
    # the maximal eigenvalue
    max_col = list(eigen_vals).index(max(eigen_vals))
    # the corresponding eigenvector
    normal_vector = eigen_vecs[:,max_col]
    return normal_vector

def pk_v_theta(vectors, reference_2, reference_3, average_sk):
    """
    Calculate order parameters Pk, V, and the angle theta
    as described in https://doi.org/10.1063/5.0005854

    """
    c = np.cross(reference_2, reference_3)
    # The following operations are performed for arrays:
    sc = np.dot(vectors, reference_2)
    # Determine the angle between the vectors in the range [0,pi]
    gamma = np.arccos( sc / np.linalg.norm(vectors, axis = 1)
                          / np.linalg.norm(reference_2))
    sc_r = np.outer(sc, reference_2)
    rot_ak = vectors - sc_r
    phi = np.arccos( np.dot(rot_ak, c)
                    / np.linalg.norm(rot_ak, axis = 1)
                    / np.linalg.norm(c))
    pk = np.sin(gamma) * np.sin(gamma) * np.cos( 2. * phi)
    v = np.sin(2. * gamma) * np.cos(phi)
    average_pk = np.average(pk)
    average_v = np.average(v)
    tan_2theta = average_v / ( average_sk - 0.5 * average_pk)
    theta = np.arctan (tan_2theta) / 2.0
    return average_pk, average_v, theta


def lamellar_alignment(u: mda.Universe, type_A, type_B,
                       store_A_values = True, store_B_values = True,
                       store_block_values = False):
    """
    Calculate the molecular orientational ordering parameters 
    for lamellae containing tilted copolymer blocks, as described in the
    https://doi.org/10.1063/5.0005854

    Parameters
    ----------
    u : mda.Universe
        Input data for analysis as MDAnalysis Universe.
    type_A : str
        Bead type for block A beads in the Universe.
    type_B : str
        Bead type for block A beads in the Universe.
    store_A_values : bool, optional
        Calculate and store the values for A blocks. The default is True.
    store_B_values : bool, optional
        Calculate and store the values for B blocks. The default is True.
    store_block_values : bool, optional
        Store the lists of values for individual blocks. The default is False.

    Returns
    -------
    {description: "Lamellar ordering parameters Sk, h, Pk, theta",
     data: {ts1: {"lam_norm": lamellae_director,
                  ["director_A": block_A_director(optional)],
                  ["ave_sk_A": Sk_value_for_block_A(optional)],
                  ["h_A": H_value_for_block_A],
                  ["pk_A": Pk_value_for_block_A],
                  ["v_A": V_value_for_block_A],
                  ["values_sk_A": Sk values for block A of each molecule]},
                  [Same set of values for block B (if store_B_values is True)]}
            ts2: { Same set of values for the next timestep },
            ....
           }
    }

    """
    # Unwrap the atom coordinates
    unwrap = transformations.unwrap(u.atoms)
    u.trajectory.add_transformations(unwrap)
    data = {}
    for ts in u.trajectory:
        # Create a structure for data for this timestep
        values = {}
        # Create data structures for the values for individual residues
        # Optimize performance by creating lists and then converting to NumPy
        A_start_list, A_end_list, A_com_list = [], [], []
        B_start_list, B_end_list, B_com_list = [], [], []
        # Create the list of unique residue ids:
        resids = set(u.atoms.resids)
        # For resid in residue id list:
        for resid in resids:
            # select atoms (resid, type1), select atoms (resid, type2)
            atoms_A = u.select_atoms("resid " + str(resid)
                                    + " and type " + str(type_A))
            atoms_B = u.select_atoms("resid " + str(resid)
                                    + " and type " + str(type_B))
            # The AtomGroups in MDAnalysis are ordered, so we can take
            # the 1st and the last atom of the groups:
            A_start_list.append(atoms_A[0].position)
            A_end_list.append(atoms_A[-1].position)
            A_com_list.append(atoms_A.center_of_mass())
            # Same for type B particles:
            B_start_list.append(atoms_B[0].position)
            B_end_list.append(atoms_B[-1].position)
            B_com_list.append(atoms_B.center_of_mass())
        # Convert lists to NumPy arrays:
        A_start = np.asarray(A_start_list)
        A_end = np.asarray(A_end_list)
        A_com = np.asarray(A_com_list)
        # Same for type B particles:
        B_start = np.asarray(B_start_list)
        B_end = np.asarray(B_end_list)
        B_com = np.asarray(B_com_list)
        # Calculate the end-to-end vectors for both blocks and the vectors
        # between the centers of mass of the blocks
        block_A_vectors_normed = normalize_vectors(A_end - A_start)
        block_B_vectors_normed = normalize_vectors(B_end - B_start)
        com_vectors_normed = normalize_vectors(B_com - A_com)
        lam_norm = normal_vector(com_vectors_normed)
        # the normal to the lamella
        values["lam_norm"] = lam_norm.tolist()
        # Calculate the values for block A, if required
        if store_A_values:
            # Calculate the director of block A using the same approach:
            block_A_director = normal_vector(block_A_vectors_normed)
            values["director_A"] = block_A_director.tolist()
            # Calculate the list of Sk values for block A:
            sk_A = 1.5 * np.square(np.dot(block_A_vectors_normed, 
                                          lam_norm)) - 0.5
            values["ave_sk_A"] = np.average(sk_A)
            # Calculate the H value for block A:
            values["h_A"] = np.cross(block_A_director, lam_norm).tolist()
            # If the tilt is non-zero, calculate the additional parameters:
            if np.linalg.norm(values["h_A"]) != 0.:
                values["pk_A"], values["v_A"], values ["theta_A"] = pk_v_theta(
                                             block_A_vectors_normed, lam_norm, 
                                             values["h_A"], values["ave_sk_A"])
            # If requested, store the values for individual A blocks:
            if store_block_values:
                values["values_sk_A"] = sk_A.tolist()
        # Calculate the values for block B, if required
        if store_B_values:
            # Calculate the director of block B using the same approach:
            block_B_director = normal_vector(block_B_vectors_normed)
            values["director_B"] = block_B_director.tolist()
            # Calculate the list of Sk values for block B:
            sk_B = 1.5 * np.square(np.dot(block_B_vectors_normed,
                                          lam_norm)) - 0.5
            values["ave_sk_B"] = np.average(sk_B)
            # Calculate the H value for block B:
            values["h_B"] = np.cross(block_B_director, lam_norm).tolist()
            # If the tilt is non-zero, calculate the additional parameters:
            if np.linalg.norm(values["h_B"]) != 0.:
                values["pk_B"], values["v_B"], values ["theta_B"] = pk_v_theta(
                                              block_B_vectors_normed, lam_norm, 
                                             values["h_B"], values["ave_sk_B"])
            # If requested, store the values for individual B blocks:
            if store_block_values:
                values["values_sk_B"] = sk_B.tolist()
        data[str(ts)] = values
    return { "description" : "Lamellar ordering parameters Sk, h, Pk, theta",
             "data": data }
