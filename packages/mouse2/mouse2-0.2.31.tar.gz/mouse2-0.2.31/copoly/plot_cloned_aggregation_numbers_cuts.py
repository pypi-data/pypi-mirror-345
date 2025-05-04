#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  2 13:56:50 2024

@author: misha
"""

import pandas as pd
from matplotlib import pyplot as plt
import glob

compositions = [0.55] #[0.55, 0.7, 0.85]
samples = [1,2,3] #[23,31,33,52,55] #[1,2,3]
from_steps = [220]
cuts = ['0.125', '0.25', '0.375', 'full']
filename="n_aggregates.txt"

font = {'size' : 16}
#color = { 0.55 : 'red', 0.7 : 'green', 0.85 : 'blue'}
color = { 'full' : 'red', '0.375' : 'green', '0.25' : 'blue', '0.125' : 'black'}
epsilon = {120: -1., 220: -2.}


plt.rc('font', **font)


for composition in compositions:
    for cut in cuts:
        step = from_steps[0]
        for sample in samples:
            read_files = glob.glob(f'cut_{cut}/f_{composition}_chain_{sample}_*/x8?from{step}/{filename}')
            data = pd.read_csv(read_files[0], delimiter=' ', header=None)
            plt.plot(data[0], data[1], color = color[cut],
                     label = f'[VCL]={composition}, tail={cut}, sample={sample}')
            
plt.legend()
plt.xlabel('$x10^{4}$ time units')
plt.ylabel('Number of aggregates')
plt.show()
