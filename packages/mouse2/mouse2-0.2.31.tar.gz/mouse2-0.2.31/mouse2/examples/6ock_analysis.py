#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is a sample script to demonstrate the usage of the MOUSE2
local_alignment module.

To run the script, the MOUSE2 package shall be installed either using pip:
    pip install mouse2
or by downloading from the GitHub repository:
    https://github.com/mglagolev/mouse2

In the latter case, the following dependencies shall be installed by the user
manually:
    - MDAnalysis
    - numpy
    - networkx
    - matplotlib
    - scipy
and the import command needs to be modified accordingly.

The identifiers for the atoms at the ends of the helical fragments are derived
from the residue numbers at the ends of the helices, as provided in the
HELIX records of the source .pdb file.

The script is run without any arguments, the lower and upper cutoff radii
for the analysis can be modified through the r_mins and r_maxes variables.
"""

from urllib.request import urlretrieve
import MDAnalysis as mda
import numpy as np
import tempfile
import sys
import os
parent_dir_name = os.path.dirname(os.path.realpath(__file__))
sys.path.append(parent_dir_name + '/../..')
from mouse2.local_alignment import local_alignment
from matplotlib import pyplot as plt

atom_nums = [ # Taken from the HELIX records of the source .pdb
    [96,105],
    [5,15],
    [282,292],
    [470,480],
    [65,76],
    [119,130],
    [322,337],
    [15,31],
    [130,146],
    [207,223],
    [249,267],
    [150,169],
    [342,361],
    [419,438],
    [517,536],
    [540,559],
    [227,247],
    [35,56],
    [563,584],
    [441,467],
    [174,207],
    [377,415],
]

# Adjust the numbers to use the positions of the nitrogen atoms of the backbone
atom_ids = [[i[0]-2, i[1]-2] for i in atom_nums]


r_maxes = np.arange(7, 21, dtype = int)
r_mins = np.arange(5, 19, dtype = int)

histo_radii = [8, 14]

d_r = r_maxes[0] - r_mins[0]


# Create a filename for an intermediate .pdb file
_, tmpfilename = tempfile.mkstemp(suffix = '.pdb')

# Retreive the PDB file
url = "https://files.rcsb.org/download/6OCK.pdb"
filename = "6OCK.pdb"
urlretrieve(url, filename)

u = mda.Universe(filename)

# Select the N atoms of the backbone
b = u.select_atoms('backbone and name N')
ow = b.split('segment')

# Bond the atoms, so that the structure can be unwrapped by MDAnalysis
# The bonds are added to the original universe, so to store only the
# bonded N atoms of the backbone, the latter need to be selected once again
bonds = []
bond_types = []
for i in ow:
    for j in range(len(i)-1):
        bonds.append([i[j].ix, i[j+1].ix])
        bond_types.append('1')
u.add_bonds(bonds, types = bond_types)

# Store the intermediate .pdb with the N atoms of the backbone
b = u.select_atoms('backbone and name N')
b.write(tmpfilename)

r_values = []
s_values = []
print("# r\ts")
for i in range(len(r_mins)):
    r_min, r_max = r_mins[i], r_maxes[i]
    r = (r_min + r_max) / 2.
    u = mda.Universe(tmpfilename)
    result = local_alignment(u, r_min = r_min, r_max = r_max,
                             mode = 'average', id_pairs = atom_ids)
    s = list(result['data'].values())[0]['average_s']
    r_values.append(r)
    s_values.append(s)
    print(f"{r:.1f}\t{s:.3f}")

plt.plot(r_values, s_values)
plt.xlabel('r', fontsize = 20)
plt.ylabel('s', fontsize = 20)
plt.show()
plt.cla()

for i, r in enumerate(histo_radii):
    r_min, r_max = r - d_r / 2., r + d_r / 2.
    u = mda.Universe(tmpfilename)
    result = local_alignment(u, r_min = r_min, r_max = r_max, n_bins = 10,
                             mode = 'histogram', id_pairs = atom_ids)
    sa_norm_histo = list(result['data'].values())[0]\
        ["cos_sq_solid_angle_normalized_histogram"]
    bin_edges = np.asarray(list(result['data'].values())[0]\
        ["bin_edges_cos_sq_theta"])
    bin_centers = (bin_edges[1:] + bin_edges[:-1]) / 2.
    p = plt.bar(bin_centers + (i-0.5)*0.04, sa_norm_histo, width = 0.05,
                label = f"r = {r}")

plt.legend(fontsize = 20)
plt.xlabel('cos²(χ)', fontsize = 14)
plt.tick_params(left = False, labelleft = False) 
plt.show()
    

os.remove(tmpfilename)
