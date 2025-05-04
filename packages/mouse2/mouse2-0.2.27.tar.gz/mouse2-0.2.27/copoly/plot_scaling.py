#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 15:50:37 2025

@author: misha
"""
import pandas as pd
import argparse
from matplotlib import pyplot as plt
import pdb

chain_lengths = [250, 500, 1000]


def plot_series(df, variable, fixed_parameters, chain_lengths):
    """Plot parameter dependencies on chain length"""
    #For every chain length:
    lengths = []
    values = []
    for chain_length in chain_lengths:
        query_array = []
        for parameter in fixed_parameters:
            if type(fixed_parameters[parameter]) != str:
                query_array.append(f"{parameter} == {fixed_parameters[parameter]}")
            else:
                query_array.append(f"{parameter} == '{fixed_parameters[parameter]}'")
        label = " ".join(query_array)
        query_array.append(f"`typical N` == {chain_length}")
        query = " & ".join(query_array)
        samples = df.query(query)
        if len(samples) > 0:
            value = samples[variable].mean()
            lengths.append(chain_length)
            values.append(value)
    #pdb.set_trace()
    plt.plot(lengths, values, label = label)
    plt.xlabel("Degree of polymerization N")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                            description = "Plot chain length dependencies")

    parser.add_argument('datafile', metavar = "TABLE", nargs = 1,
                        help = "table with simulation data")

    args = parser.parse_args()

    df = pd.read_excel(args.datafile[0])

    plot_series(df, "ASA VI per unit", 
                {'cut' : 'full', 'f' : 0.85, 'n' : 1}, chain_lengths)
    plot_series(df, "ASA VI per unit", 
                {'cut' : 0, 'f' : 0.85, 'n' : 1}, chain_lengths)
    plt.legend()
    plt.show()
    plt.savefig("plot.png")