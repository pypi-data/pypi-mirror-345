#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 18:19:25 2025

@author: misha
"""

import os
from tempfile import NamedTemporaryFile
from mouse2.tests.create_configuration import create_configuration
import pandas as pd
import numpy as np

#Transfer e_pair reader to microplastics library
def e_pair_reader(file = None):
    # Read epair from file
    df = pd.read_csv(file, delimiter = ' ', skiprows = 2, header = None)
    data_length = df.shape[0]
    e_pair_data = df[1][int(data_length/2):]
    return e_pair_data.mean()

# Create configuration with target cell size and density
def run_mc(simulation):
    config = simulation["config"]
    i_iter = simulation["iteration"]
    box = config["run_parameters"]["cell_size"]
    nmol = config["run_parameters"]["nmol"]
    npoly = config["run_parameters"]["npoly"]
    run_command = config["run_parameters"]["run_command"]
    in_filename = f"{config['run_parameters']['in_filename_template']}{i_iter}.data"
    run_filename = f"{config['run_parameters']['run_filename_template']}{i_iter}.lammps"
    mc_trials = config["run_parameters"]["mc_trials"]
    e_pairs = []
    for n_trial in range(mc_trials):
        #in_filename = NamedTemporaryFile(suffix = ".data")
        create_configuration(system_type = "random", npoly = npoly, nmol = nmol,
                             box = box, output = in_filename, add_angles = True,
                             add_dihedrals = False, self_avoid = 1.0,
                             atomtypes = None)
        command = f"{run_command} --input {run_filename}"
        exit_code = os.system(command)
        e_pair = e_pair_reader(file = "e_pair.dat")
        e_pairs.append(e_pair)
    mean_e_pair = np.mean(e_pairs)
    simulation["feedbacks"]["e_pair"] = mean_e_pair