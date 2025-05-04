#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 13:26:21 2024

@author: misha
"""
import argparse
import numpy as np
import json
from matplotlib import pyplot as plt
from matplotlib.ticker import FormatStrFormatter, StrMethodFormatter
from average import average_list
from calculate_globular_parameters import calculate_globules_parameters


block_name = { '1' : 'VCL', '2' : 'VI', 'a' : 'Total'}
line_style = {'1' : '-', '2' : '--', 'a' : ':'}
line_color = { 'Hist 1' : 'red', 'Hist 2' : 'blue', 'Hist all' : 'black'}

font = {'size' : 20}


parser = argparse.ArgumentParser(
    description = 'Calculate globule parameters')

parser.add_argument('files', metavar = 'DATA', type = str, nargs = '+',
    help = 'simulation data')

parser.add_argument('--nbins', metavar = 'NBINS', type = int,
                        nargs = '?', default = 15, help = 'histogram bins')

parser.add_argument('--min', metavar = 'MIN', type = int,
                        nargs = '?', default = 0, help = 'histogram minimum')

parser.add_argument('--max', metavar = 'MAX', type = int,
                        nargs = '?', default = 12, help = 'histogram maximum')

parser.add_argument('--plot', action = 'store_true',
                        help = 'plot histograms')
    
args = parser.parse_args()

arguments = vars(args)

make_plot = arguments.pop('plot')

if make_plot:
    plt.rc('font', **font)
    plt.gca().yaxis.set_major_formatter(StrMethodFormatter('{x:,.2f}')) # 2 decimal places

results = calculate_globules_parameters(**arguments)

results_mean, results_stdev = average_list(results)

print('#parameter\tvalue\tstdev')
for key in results_mean.keys():
    if key[:4] != 'Hist':
        print(f'{key}\t{results_mean[key]:.3g}\t{results_stdev[key]:.3g}')
    else:
        if make_plot:
            atom_type = key[5:6]
            plt.plot(results_mean[key]['bin_centers'],
                results_mean[key]['dens']/results_mean['Hist all']['dens_sum'],
                linestyle = line_style[atom_type],
                color = line_color[key],
                label = f'{block_name[atom_type]}')

if make_plot:
    plt.xlim([args.min, args.max])
    plt.yticks([])
    plt.xlabel("$r-r_{c.m.}$", fontsize=28)
    plt.ylabel("Avg. density, normalized")
    plt.legend()
    plt.tight_layout()
    plt.show()
