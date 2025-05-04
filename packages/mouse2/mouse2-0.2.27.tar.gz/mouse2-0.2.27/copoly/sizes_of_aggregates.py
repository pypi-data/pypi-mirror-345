#!/usr/bin/which python3

import json
import sys

#Read lines from stdin
#lines = sys.stdin.readlines()
#print(lines[:10])
#Decode json
data = json.load(sys.stdin)
#print(data)
#n_aggr=len(list(data["data"].values())[0])
sizes = [ len(x) for x in list(data["data"].values())[0]]

print(sizes)
#Count the length of aggregates list

#Print the result
