#!/usr/bin/python3
import argparse
import pandas as pd
import os
import sys

home = os.environ["HOME"]
sys.path.append(f'{home}/Documents/Codes/git/')

from mdlearn.sequences_encoding import block_lengths


def main():
    parser = argparse.ArgumentParser(
        description = 'Determine the number of single units of type 1 in the chains')

    parser.add_argument('filename', metavar = 'FILE', type = str,
                        help = 'pickle filename')

    args = parser.parse_args()


    data = pd.read_pickle(args.filename)
    
    all_n_1_blocks = []

    for imol in data:
        seq = data[imol]
        seq_nonzero = [atype for atype in seq if atype != 0]
        blocks = block_lengths(seq_nonzero)
        n_1_blocks = sum(1 for i in blocks[1] if i == 1)
        all_n_1_blocks.append((imol,n_1_blocks))

    all_n_1_blocks_sorted = sorted(all_n_1_blocks, key = lambda x: x[1])
    for n_1_blocks in all_n_1_blocks_sorted:
        print (f'Chain #{n_1_blocks[0]+1} 1-blocks: {n_1_blocks[1]}\n')


if __name__ == "__main__":
    main()