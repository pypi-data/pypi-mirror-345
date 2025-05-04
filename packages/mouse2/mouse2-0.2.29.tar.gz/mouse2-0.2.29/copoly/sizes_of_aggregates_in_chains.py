#!/usr/bin/which python3

import json
import sys
import argparse
import MDAnalysis as mda
from mouse2.mouse2.lib.aggregation import determine_aggregates

parser = argparse.ArgumentParser(
        description = 'Aggregate sizes in chains')

parser.add_argument('--npoly', metavar = 'N', type = int, nargs = 1,
                        help = 'chain length')
                        
parser.add_argument('--first', metavar = 'FIRST_STEP', type = int, nargs = 1,
                        help = 'first step')
                        
parser.add_argument('--last', metavar = 'LAST_STEP', type = int, nargs = 1,
                        help = 'last step')
                        
                        
    
args = parser.parse_args()

#Read lines from stdin
#lines = sys.stdin.readlines()
#print(lines[:10])
#Decode json

first = args.first[0]
last = args.last[0]

aggregates_hist = {}

for i in range(first, last):
	sys.stderr.write(f"\r{i}")
	u = mda.Universe(f"{i}.data")
	data = determine_aggregates(u, r_neigh = 1.2)
	sizes = [ int(len(x)/args.npoly[0]) for x in list(data["data"].values())[0]]
	for size in sizes:
		try:
			aggregates_hist[size] += 1
		except KeyError:
			aggregates_hist[size] = 1
	#print(sizes)
print(aggregates_hist)
#data = json.load(sys.stdin)

#print(data)
#n_aggr=len(list(data["data"].values())[0])


#print(sizes)
#Count the length of aggregates list

#Print the result
