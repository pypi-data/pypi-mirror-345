#!/usr/bin/python3

"""
This is a sample script to demonstrate the usage of the MOUSE2
backbone_correlations module.
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
and the script_command parameter needs to be be adjusted.
The script is run without any arguments, the correlation length can varied
by altering the k_max parameter in the script.
"""

from urllib.request import urlretrieve
import MDAnalysis as mda
import os

#Script command
#In case of manual installation, this needs to be adjusted
script_command = "bond_autocorrelations"

#Set the maximum correlation length
k_max = 10

#Retreive the PDB file
url = "https://files.rcsb.org/download/3H5G.pdb"
filename = "3H5G.pdb"
urlretrieve(url, filename)

#Import the data
u = mda.Universe(filename)

#Select the nitrogen atoms of the backbone
b = u.select_atoms('backbone and name N')

#Split the atoms by segment IDs
ow = b.split('segment')


#Find the atom numbers for the pseudobonds
#between the nitrogen atoms of the backbone
bonds = []
bond_types = []
for i in ow:
    for j in range(len(i)-1):
        bonds.append([i[j].ix, i[j+1].ix])
        bond_types.append('1')

#Add the bonds to the universe
u.add_bonds(bonds, types = bond_types)

#Select the required atoms from the universe with the pseudobonds
c = u.select_atoms('backbone and name N')
c.atoms.residues.resids = [ord(segid) - 64 for segid in c.atoms.segids]
c.write('3h5g_for_analysis.pdb')
#Run the analysis command
os.system(f"{script_command} 3h5g_for_analysis.pdb \
          --k_max {k_max} --plot --fit")
