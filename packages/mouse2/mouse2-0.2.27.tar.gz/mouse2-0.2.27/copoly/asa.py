#!/usr/bin/env python3

"""
Routines to calculate the Accessible Surface Area of a set of atoms.
The algorithm is adapted from the Rose lab's chasa.py, which uses
the dot density technique found in:

Shrake, A., and J. A. Rupley. "Environment and Exposure to Solvent
of Protein Atoms. Lysozyme and Insulin." JMB (1973) 79:351-371.
"""


import math
import os
import numpy as np

radii_file = os.path.join(os.path.dirname(__file__) , 'radii.txt')

def read_radii(radii_file):
    # reading the data from the file 
    with open(radii_file) as f: 
        data = f.read()
    radii_dict = eval(data)
    return radii_dict

def pos_distance(p1, p2, cell):
  return math.sqrt(pos_distance_sq(p2, p1, cell))


def pos_distance_sq(p1, p2, cell):

    x = p1[0] - p2[0] - cell[0] * round((p1[0] - p2[0])/cell[0])

    y = p1[1] - p2[1] - cell[1] * round((p1[1] - p2[1])/cell[1])

    z = p1[2] - p2[2] - cell[2] * round((p1[2] - p2[2])/cell[2])

    return x*x + y*y + z*z;


def generate_sphere_points(n):
    """
    Returns list of 3d coordinates of points on a sphere using the
    Golden Section Spiral algorithm.
    """
    points = np.ndarray((n, 3), dtype = float)
    #points = []
    inc = math.pi * (3 - math.sqrt(5))
    offset = 2 / float(n)
    for k in range(int(n)):
        y = k * offset - 1 + (offset / 2)
        r = math.sqrt(1 - y*y)
        phi = k * inc
        points[k] = [math.cos(phi)*r, y, math.sin(phi)*r]
        #points.append([math.cos(phi)*r, y, math.sin(phi)*r])
    return points


def find_neighbor_indices(atoms, probe, k, cell, radii):
    """
    Returns list of indices of atoms within probe distance to atom k. 
    """
    neighbor_indices = []
    atom_k = atoms[k]
    radius = radii[atom_k.type] + probe + probe
    indices = list(range(k))
    indices.extend(range(k+1, len(atoms)))
    for i in indices:
        atom_i = atoms[i]
        dist = pos_distance(atom_k.position, atom_i.position, cell)
        if dist < radius + radii[atom_i.type]:
            neighbor_indices.append(i)
    return neighbor_indices


def calculate_asa(atoms, probe, n_sphere_point, cell, radii):
    """
    Returns list of accessible surface areas of the atoms, using the probe
    and atom radius to define the surface.
    """
    sphere_points = generate_sphere_points(n_sphere_point)

    const = 4.0 * math.pi / len(sphere_points)
    #test_point = np.ndarray((3,))
    areas = {}
    for i, atom_i in enumerate(atoms):
        
        element = atom_i.type

        neighbor_indices = find_neighbor_indices(atoms, probe, i, cell, radii)
        n_neighbor = len(neighbor_indices)
        j_closest_neighbor = 0
        radius = probe + radii[atom_i.type]

        n_accessible_point = 0
        
        test_points = sphere_points * radius + atom_i.position
        for i_point in range(len(test_points)):
            is_accessible = True

            cycled_indices = list(range(j_closest_neighbor, n_neighbor))
            cycled_indices.extend(range(j_closest_neighbor))

            for j in cycled_indices:
                atom_j = atoms[neighbor_indices[j]]
                r = radii[atom_j.type] + probe
                diff_sq = pos_distance_sq(atom_j.position,
                                          test_points[i_point], cell)
                if diff_sq < r*r:
                    j_closest_neighbor = j
                    is_accessible = False
                    break
            if is_accessible:
                n_accessible_point += 1

        area = const*n_accessible_point*radius*radius
        try:
            areas[element].append(area)
        except KeyError:
            areas[element] = [area]
    return areas


def main():
  import sys
  import getopt
  #import molecule
  import MDAnalysis as mda


  usage = \
  """

  Copyright (c) 2007 Bosco Ho
  Modified  (c) 2013 Mikhail Glagolev
  
  Calculates the total Accessible Surface Area (ASA) of atoms in a 
  PDB file. 

  Usage: asa.py -s n_sphere in_pdb [out_pdb]
  
  - out_pdb    PDB file in which the atomic ASA values are written 
               to the b-factor column.
               
  -n n_sphere  number of points used in generating the spherical
               dot-density for the calculation (default=960). The 
               more points, the more accurate (but slower) the 
               calculation.

  -c cell_size cell size

  """

  opts, args = getopt.getopt(sys.argv[1:], "n:p:")
  if len(args) < 1:
    print(usage)
    return
    
  u = mda.Universe(args[0])
  atoms = u.atoms
  radii = read_radii(radii_file)
  cell = u.dimensions

  n_sphere = 960
  for o, a in opts:
    if '-n' in o:
      n_sphere = int(a)
      #print "Points on sphere: ", n_sphere
    if '-p' in o:
      r_probe = float(a)
      #print "Probe radius: ", r_probe
  asas = calculate_asa(atoms, r_probe, n_sphere, cell, radii)
  for element in asas:
      print(f"Type {element} {sum(asas[element]):.1f}") #angstrom squared
  
  
if __name__ == "__main__":
  main()