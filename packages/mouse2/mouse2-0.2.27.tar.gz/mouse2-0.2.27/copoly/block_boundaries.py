#!/usr/bin/python3
import argparse
import pandas as pd


def block_boundaries(sequence):
    """Determine minimum and maximum index for each of the element types
       present in the sequence"""

    indexed_sequence = list(zip(range(len(sequence)), sequence))
    element_types = list(set(sequence))
    element_types.sort()
    result = {}
    for element_type in element_types:
        minimum = [i[0] for i in indexed_sequence if i[1] == element_type][0]
        maximum = [i[0] for i in indexed_sequence if i[1] == element_type][-1]
        result[element_type] = {'min' : minimum, 'max' : maximum}
    return result


def main():
    parser = argparse.ArgumentParser(
        description = 'Convert pandas in pickle chain sequences to strings')

    parser.add_argument('filename', metavar = 'FILE', type = str,
                        help = 'pickle filename')

    parser.add_argument('--nmol', metavar = 'n', type = int, nargs = '?',
                        const = 1, help = "number of molecules to read")
                    
    parser.add_argument('--nmol-offset', metavar = 'offset', type = int,
                        nargs = '?', const = 0,
                        help = "skip this number of sequences")

    args = parser.parse_args()


    data = pd.read_pickle(args.filename)

    for imol in range(args.nmol_offset,args.nmol + args.nmol_offset):
        print(f'Seq nr. {imol}:')
        seq = data[imol]
        seq_nonzero = [atype for atype in seq if atype != 0]
        boundaries = block_boundaries(seq_nonzero)
        print(f'Length {len(seq_nonzero)}')
        for atype in boundaries:
            print(f"Type {atype} max {boundaries[atype]['max']}")


if __name__ == "__main__":
    main()