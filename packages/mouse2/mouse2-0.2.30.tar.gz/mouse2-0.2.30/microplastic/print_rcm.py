#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 17:33:26 2025

@author: misha
"""
import MDAnalysis as mda
import argparse

parser = argparse.ArgumentParser("Print center of mass coordinates at each\
                                 timestep of the dump file")
parser.add_argument("--data", type = str, nargs = 1, help = "LAMMPS data file")
parser.add_argument("--dump", type = str, nargs = 1, help = "LAMMPS dump file")

args = parser.parse_args()

u = mda.Universe(args.data[0], args.dump[0])
for ts in u.trajectory:
        rcm = u.atoms.center_of_mass()
        print(f"{rcm[0]}\t{rcm[1]}\t{rcm[2]}")
