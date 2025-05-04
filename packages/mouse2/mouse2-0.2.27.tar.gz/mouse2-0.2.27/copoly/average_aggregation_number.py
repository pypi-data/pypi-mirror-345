#!/usr/bin/which python3

import json
import sys

#Read lines from stdin
#lines = sys.stdin.readlines()
#print(lines[:10])
#Decode json
data = json.load(sys.stdin)
#print(data)
k=len(list(data["data"].values())[0])
m=list(data["data"].values())[0]
total = 0 
for i in m:   
    total += len(i) 

print(float(total)/k)
#Count the length of aggregates list

#Print the result
