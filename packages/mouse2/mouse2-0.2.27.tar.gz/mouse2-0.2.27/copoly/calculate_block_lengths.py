#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 12:47:19 2024

@author: misha
"""

import pandas as pd
import numpy as np
import argparse
import os
import sys
from matplotlib import pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'mdlearn'))
from sequences_encoding import block_lengths

freq_avg = 1.

block_name = { 1 : 'VCL', 2 : 'VI'}

parser = argparse.ArgumentParser(
    description = 'Calculate block length distributions')

parser.add_argument('filename', metavar = 'FILE', type = str,
    help = 'pickle filename')

parser.add_argument('--max', metavar = 'MAX BLOCK', type = int,
                    nargs = '?', default = 20, help = 'maximum block length')

args = parser.parse_args()

data = pd.read_pickle(args.filename)


all_blocks = {}
for imol in range(len(data.columns)):
    seq = data[imol]
    seq_nonzero = [atype for atype in seq if atype != 0]
    blocks = block_lengths(seq_nonzero)
    for block_type in blocks.keys():
        try:
            for block in blocks[block_type]:
                all_blocks[block_type].append(block)
        except KeyError:
            all_blocks[block_type] = blocks[block_type]

for block_type in all_blocks.keys():
    type_frequencies, bin_edges = np.histogram(
            all_blocks[block_type], bins = int(args.max / freq_avg),
            range = [1, args.max], density = True)
    bin_centers = (bin_edges[1:] + bin_edges[:-1]) / 2.
    plt.plot(bin_centers, type_frequencies,
             label = f'{block_name[block_type]}')
plt.legend()
plt.show()