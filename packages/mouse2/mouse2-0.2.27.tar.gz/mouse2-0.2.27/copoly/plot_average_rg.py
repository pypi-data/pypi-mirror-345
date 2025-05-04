#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 13:47:28 2024

@author: Mikhail Glagolev
"""
from matplotlib import pyplot as plt
import pandas as pd
import argparse

font = {'size' : 16}

color = { 0.55 : 'red', 0.7 : 'green', 0.85 : 'blue', 1.0 : 'black'}
line_style = {0.55 : '-', 0.7 : '--', 0.85 : ':', 1.0 : '-'}

primary_exp = [0.55, 0.7, 0.85, 1.0]

def plot_label(f_vcl):
    if f_vcl < 1.:
        label = f'$[VCL]_{0}/[VI]_{0} = {round(f_vcl*100)}/{round((1-f_vcl)*100)}$'
    elif f_vcl == 1.:
        label = 'VCL homopolymer'
    return label

parser = argparse.ArgumentParser(
    description = 'Plot averaged gyration radii')

parser.add_argument('file', metavar = 'XLS', type = str, nargs = 1,
    help = 'file with the rg data')

args = parser.parse_args()

plt.rc('font', **font)

df = pd.read_excel(args.file[0])

for f in primary_exp:
    steps = df['step']
    rg = df[f'f_{f}_mean']
    plt.plot((steps - 20) * 0.01, rg, color = color[f], linestyle = line_style[f],
             label = plot_label(f))
    
plt.legend()
plt.xlim([0,1])
plt.ylim([2, 35])
plt.xlabel('$-𝜀_{VCL}$')
plt.ylabel('$r_{g}$')
fig = plt.gcf()
fig.set_size_inches(8., 6.)
plt.savefig('rg_vs_solvent.png', transparent=True)
plt.show()