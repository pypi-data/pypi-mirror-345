#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 18:20:21 2024

@author: misha
"""

import numpy as np
import MDAnalysis as mda
from mouse2.mouse2.lib.aggregation import determine_aggregates
from matplotlib import pyplot as plt

r_neigh_aggregation = 1.2

dis_steps = []
first_dis_steps = []

for isample in range(1, 79):
    naggr = 1
    for istep in range(1,11):
        u = mda.Universe(f"{isample}.{istep}.data")
        aggregates_dict = determine_aggregates(u, r_neigh = r_neigh_aggregation)
        aggregates_list = aggregates_dict["data"][list(aggregates_dict["data"].keys())[0]]
        naggr_new = len(aggregates_list)
        if naggr_new > naggr:
            if naggr == 1:
                first_dis_steps.append(istep)
                if istep == 10:
                    print(f"{isample} disintegrated on step 10")
            dis_steps.append(istep)
            naggr = naggr_new
            
dis_hist, dis_bin_edges = np.histogram(dis_steps,
                                       bins = 10, range = (0.5, 10.5))

first_dis_hist, first_dis_bin_edges = np.histogram(first_dis_steps,
                                       bins = 10, range = (0.5, 10.5))

dis_bin_centers = (dis_bin_edges[:-1] + dis_bin_edges[1:]) / 2.
first_dis_bin_centers = (first_dis_bin_edges[:-1] + first_dis_bin_edges[1:]) / 2.

print("All events")
print(dis_hist)

print("First event")
print(first_dis_hist)

plt.plot(dis_bin_centers, dis_hist, label = "All disintegration events")
plt.plot(first_dis_bin_centers, first_dis_hist, label = "First disintegration event")
plt.xlabel("$x2x10^{5} t$")
plt.ylabel("Disintegration events frequency")
plt.ylim(0., None)
plt.legend()
plt.show()