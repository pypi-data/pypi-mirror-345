#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 13:42:18 2024

@author: Mikhail Glagolev
"""
import optuna
from lammps import lammps
import math
import mouse2.mouse2.tests.create_configuration as create_configuration
import MDAnalysis as mda
from MDAnalysis import transformations
import numpy as np 
import pandas as pd
import argparse


npoly_min = 128
npoly_max = 4096
est_min = 0.01
est_max = 64
n_trials = 100
duration_factor = 4.

filename = 'research_progress.txt'
template_filename = 'template.lammps'
run_filename_template = 'compute_'
out_data_filename_template = 'out_'


if __name__ == "__main__":
    from mpi4py import MPI
    outfile = open(filename, 'w')
    outfile.write('#trial\tnpoly\test\tshape\tfluct\n')
    outfile.close()


def substitute_values(template_filename, output_filename,
                      substitutions = None):
    template_file = open(template_filename, 'r')
    template = template_file.read()
    template_file.close()
    if type(substitutions) == list:
        for substitution in substitutions:
            template = template.replace(*substitution)
    elif type(substitutions) == dict:
        for key in substitutions:
            template = template.replace(key, substitutions[key])
    run_file = open(output_filename, 'w')
    run_file.write(template)
    run_file.close()

def rg_fluct(file):
    df = pd.read_csv(file, delimiter=' ', skiprows=2, header=None)
    rg=df[4]
    rg_end = rg[int(len(rg)/2):]
    return rg_end.std()/rg_end.mean()


def k1k2(file):
    u = mda.Universe(file)
    # coordinates change for each frame
    unwrap = transformations.unwrap(u.atoms)
    u.trajectory.add_transformations(unwrap)
    coordinates = u.atoms.positions
    center_of_mass = u.atoms.center_of_mass()

    # compute the gyration tensor
    vects = coordinates - center_of_mass
    tensor = (np.einsum('im,in->mn', vects, vects) 
                   / float(len(vects)))
    # find eigenvalues and eigenvectors 
    eigen_vals, eigen_vecs = np.linalg.eig(tensor)
    e_v = np.sort(eigen_vals)
    k1 = (e_v[0] + e_v[1])/(e_v[1] + e_v[2])
    k2 = (e_v[0] + e_v[2])/(e_v[1] + e_v[2])

    return k1, k2

def calculate_globular_order(npoly = None, est = None,
                             number = None, comm = None):
    if comm is not None:
        rank = comm.Get_rank()
    else:
        rank = 0
    if rank == 0:
        create_configuration.create_configuration(
                             system_type = 'disordered-helices',
                             npoly = npoly,
                             nmol = 1,
                             box = npoly_max / 2.,
                             output = f'in_{number}.data',
                             add_angles = True,
                             add_dihedrals = True,
                             self_avoid = True,
                             atomtypes = None)

        tau = duration_factor * npoly

        if est > 0.2 and est < 20:
            ts = 0.002
        else:
                ts = 0.004

    run_filename = f'{run_filename_template}{number}.lammps'
    out_data_filename = f'{out_data_filename_template}{number}.data'
    if rank == 0:
        substitute_values(template_filename, run_filename,
                      [['EST', str(est)], ['NTRIAL', str(number)],
                       ['OUTPUT', out_data_filename],
                       ['TAU', str(tau)],
                       ['TS', str(ts)]])
    if comm is not None:
        MPI.Comm.Barrier(comm)
    try:
        lmp = lammps()
        lmp.file(run_filename)
        if comm is not None:
            MPI.Comm.Barrier(comm)
    except:
        return math.inf, math.inf
    if rank == 0:
        #Calculate radius of gyration
        k1, k2 = k1k2(out_data_filename)
        #Calculate order parameter
        shape_parameter = (k1  - 0.5)**2 + (k2 -  0.5)**2
        fluct_parameter = rg_fluct(f'xdata_{number}.1.lammps')
        return shape_parameter, fluct_parameter
    else:
        return None, None

def objective(trial: optuna.Trial):
    if args.parallel:
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
    else:
        comm = None
        rank = 0
    trial.set_user_attr("rank", rank)
    try:
        if rank == 0:
            npoly = trial.suggest_int("npoly", npoly_min, npoly_max,
                                      log = True)
            est = trial.suggest_float("est", est_min, est_max, log = True)
        else:
            npoly = None
            est = None
        shape_parameter, fluct_parameter = calculate_globular_order(
                                                        npoly = npoly,
                                                        est = est,
                                                        number = trial.number,
                                                        comm = comm)
        if comm is not None:
            MPI.Comm.Barrier(comm)
        if rank == 0:
            outfile = open(filename, 'a')
            outfile.write(f'{trial.number}\t{npoly}\t{est:.2f}\
\t{shape_parameter:.3f}\t{fluct_parameter:.3f}\n')
            outfile.close()
            return shape_parameter + fluct_parameter
        else:
            return math.inf
    except Exception as e:
        print(e)
        return math.inf


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description = 'Optimize the system')
    parser.add_argument(
        '--parallel', action = "store_true", help = "Run with MPI")
    args = parser.parse_args()

    if args.parallel:
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
    else:
        comm = None
        rank = 0

    sampler = optuna.samplers.TPESampler()
    study = optuna.create_study(direction="minimize", sampler = sampler)
    study.optimize(objective, n_trials=n_trials, gc_after_trial=True)
    if rank == 0:
        print("Study statistics: ")
        print("  Number of finished trials: ", len(study.trials))
        print("Best trial:")
        trial = study.best_trial

        for key, value in trial.params.items():
            print("    {}: {}".format(key, value))

        study.trials_dataframe().to_csv('study.csv')
