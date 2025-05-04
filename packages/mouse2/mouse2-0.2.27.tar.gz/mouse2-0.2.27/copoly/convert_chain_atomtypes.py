#!/usr/bin/python3
import argparse
import pandas as pd
import sys

parser = argparse.ArgumentParser(
    description = 'Convert pandas in pickle chain sequences to strings')

parser.add_argument('filename', metavar = 'FILE', type = str,
    help = 'pickle filename')

parser.add_argument('--nmol', metavar = 'n', type = int, nargs = '?',
                    const = 1, help = "number of molecules to read")

parser.add_argument('--nmol-offset', metavar = 'offset', type = int,
                    nargs = '?', const = 0,
                    help = "skip this number of sequences")

parser.add_argument('--truncate', metavar = 'N values', type = int,
                    nargs = '*', default = None,
                help = "truncate the chain lengths to the specified values")

args = parser.parse_args()

if (args.truncate is not None) and (len(args.truncate) != args.nmol):
    raise NameError("Truncation list must be equal\
                    to the number of molecules read")

data = pd.read_pickle(args.filename)

for imol in range(args.nmol_offset,args.nmol_offset + args.nmol):
    seq = data[imol]
    seq_nonzero = [atype for atype in seq if atype != 0]
    if args.truncate is not None:
        truncate = args.truncate[imol - args.nmol_offset]
    else:
        truncate = len(seq_nonzero)
    for atype in seq_nonzero[:truncate]:
        print(str(atype) + " ", end = '')
    print('')
    sys.stderr.write(str(len(seq_nonzero[:truncate])) + "\n")
