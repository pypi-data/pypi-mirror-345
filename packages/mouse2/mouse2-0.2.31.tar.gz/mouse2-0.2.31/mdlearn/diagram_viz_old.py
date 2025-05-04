#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 15:23:31 2025

@author: misha
"""

import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn import svm
import pandas as pd


NVALUES0_DEFAULT = 15
NVALUES1_DEFAULT = 98


def value_to_nbin(parameter, nbins, value):
    nbin = ((value - parameter["min"])
            / (parameter["max"] - parameter["min"])
            * nbins)
    return nbin

def parameter_ordered_names(parameters):
    if type(parameters) == dict:
        p_names = list(parameters.keys())
    elif type(parameters) == list:
        p_names = parameters
    else:
        raise NameError(f"Unsupported parameters type {type(parameters)}")
    p_names.sort()
    return p_names

def nvalues(parameter):
    return int((parameter["max"] - parameter["min"]) / parameter["step"]) + 1


def plot_uncertainties(parameters, uc_features):
    uc_values = [i[0] for i in uc_features]
    param1_values = [i[1][0] for i in uc_features]
    param2_values = [i[1][1] for i in uc_features]

    p_names = parameter_ordered_names(parameters)
    
    try:
        nvalues0 = nvalues(parameters[p_names[0]])
        nvalues1 = nvalues(parameters[p_names[1]])
    except KeyError:
        nvalues0 = NVALUES0_DEFAULT
        nvalues1 = NVALUES1_DEFAULT

    heatmap, _, _ = np.histogram2d(param1_values, param2_values, 
                                   bins = (nvalues0, nvalues1),
                                   range = [[parameters[p_names[0]]["min"],
                                             parameters[p_names[0]]["max"]],
                                            [parameters[p_names[1]]["min"],
                                             parameters[p_names[1]]["max"]]],
                                   weights = uc_values)
    g = sns.heatmap(heatmap)
    xticks = [2] + list(np.arange(10, parameters[p_names[0]]["max"], 10))
    g.set_xticks(xticks)
    #g.set_xticks([value_to_nbin(parameters[p_names[0]], nvalues0, val) for val in xtick_labels])
    yticks = list(np.arange(parameters[p_names[0]]["min"], 
                            parameters[p_names[0]]["max"],
                            0.1))
    #g.set_yticks([value_to_nbin(parameters[p_names[1]], nvalues1, val) for val in ytick_labels])
    g.set_yticks(yticks)
    g.set_xticklabels(xticks)
    #g.set_yticklabels(yticks)
    plt.xlabel('$n_{cut}$')
    plt.ylabel('$f_{mod}$, %')
    plt.show()
    
    
def plot_distributions(parameters, points, distributions):
    prob1_values = [i[0] for i in distributions]
    param1_values = [i[0] for i in points]
    param2_values = [i[1] for i in points]

    p_names = parameter_ordered_names(parameters)

    heatmap, _, _ = np.histogram2d(param1_values, param2_values, 
                                   bins = (nvalues(parameters[p_names[0]]),
                                           nvalues(parameters[p_names[1]])),
                                   weights = prob1_values)
    g = sns.heatmap(heatmap, cmap = sns.color_palette("vlag", as_cmap=True))
    g.set_xticks([10, 20, 30, 40, 50, 60])
    g.set_yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    g.set_xticklabels([10, 20, 30, 40, 50, 60])
    g.set_yticklabels([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    plt.xlabel('$n_{cut}$')
    plt.ylabel('$f_{mod}$, %')
    plt.show()


def linear_boundary_coeffs(samples_file):
    df = pd.read_excel('samples_out.xlsx')
    params = df[["nsplit", "fmod"]]
    state = df["state"]
    clf = svm.SVC(kernel = 'linear',  gamma=0.7, C=1)
    clf.fit(params, state)
    w = clf.coef_[0]
    a = -w[0] / w[1]
    b = -1 * clf.intercept_[0] / w[1]
    print(a, b)
