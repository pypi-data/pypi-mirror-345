#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 19:47:01 2024

@author: misha
"""
import MDAnalysis as mda
from MDAnalysis import transformations
import numpy as np
import argparse


def c_ratio(u):
    """"Calculate characteristic ratio of a polymer chain"""
    unwrap = transformations.unwrap(u.atoms)
    u.trajectory.add_transformations(unwrap)
    iend = u.atoms[0]
    jend = u.atoms[-1]
    rij1 = []
    rij2 = []
    rij_all = []
    traj_len = len(u.trajectory)

    for ts in u.trajectory:
        rij_all.append(np.linalg.norm(jend.position - iend.position))

    rij1 = rij_all[int(traj_len*0.2):int(traj_len*0.6)]
    rij2 = rij_all[int(traj_len*0.6):]

    rij1_sq = np.power(rij1, 2)
    rij2_sq = np.power(rij2, 2)

    ave_rij_sq = 0.5 * (np.mean(rij1_sq) + np.mean(rij2_sq))

    npoly = len(u.atoms)

    c_ratio = ave_rij_sq / npoly

    err = abs(np.mean(rij1_sq)-np.mean(rij2_sq))/ave_rij_sq

    return c_ratio, err

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description = 'Calculate end to end distance of a polymer')

    parser.add_argument(
            'data', metavar = 'LAMMPS_DATA', nargs = '?',
            default = '0.data', help = "data file")

    parser.add_argument(
            'dump', metavar = 'LAMMPS_DUMP', nargs = '?',
            default = 'atoms.lammpsdump', help = "dump file")

    args = parser.parse_args()

    u = mda.Universe(args.data, args.dump)
    c_ratio, err = c_ratio(u)
    print(f"C = {c_ratio}")
    print(f"Discrepancy {err}")