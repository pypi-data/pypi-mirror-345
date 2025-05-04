#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 15:28:36 2025

@author: misha
"""

import MDAnalysis as mda
import pandas as pd
import argparse


def degree_of_modification(filename):
    u = mda.Universe(filename)
    n_atoms1 = len(u.select_atoms("type 1"))
    n_atoms2 = len(u.select_atoms("type 2"))
    f_mod = n_atoms1 / (n_atoms1 + n_atoms2)
    return f_mod


if __name__ == "__main__":

    parser = argparse.ArgumentParser("Check the actual degree of modification\
                                     of samples tested with label propagation\
                                     algorithm")
    parser.add_argument("--samples", type = str, nargs = 1,
                        help = "Samples file (xlsx format")
    parser.add_argument("--output", type = str, nargs = 1,
                        help = "Checked samples file (xlsx format")
    args = parser.parse_args()

    samples_df = pd.read_excel(args.samples[0])

    checked_samples = []

    for i in range(len(samples_df)):
        sample_dict = dict(samples_df.iloc[i])
        n_sample = sample_dict['sample']
        n_steps = sample_dict['step']
        for i_step in range(1, n_steps + 1):
            filename = f"in_{n_sample}.{i_step}.data"
            f_mod = degree_of_modification(filename)
            if i_step == 1:
                reference_f_mod = f_mod
                consistent = True
            else:
                if f_mod != reference_f_mod:
                    consistent = False
        sample_dict['checked_fmod'] = reference_f_mod
        sample_dict['consistent'] = consistent
        checked_samples.append(sample_dict)

    checked_df = pd.DataFrame.from_dict(checked_samples)
    checked_df.to_excel(args.output[0])
