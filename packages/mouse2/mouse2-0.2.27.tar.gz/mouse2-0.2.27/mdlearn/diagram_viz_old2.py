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
import pdb
import scipy


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
    g.set_yticklabels(yticks)
    plt.pcolor(heatmap, hatch='//', alpha=0.)
    plt.xlabel('$n_{cut}$')
    plt.ylabel('$f_{mod}$, %')
    plt.show()
    
    
def plot_distributions(parameters, points, distributions, samples_file = None):
    prob1_values = [i[0] for i in distributions]
    param1_values = [i[0] for i in points]
    param2_values = [i[1] for i in points]
    rel_prob_values = [i[0]/(i[0]+i[1]) for i in distributions]

    p_names = parameter_ordered_names(parameters)
    
    p_0_min, p_0_max = parameters[p_names[0]]["min"], parameters[p_names[0]]["max"]
    p_1_min, p_1_max = parameters[p_names[1]]["min"], parameters[p_names[1]]["max"]

    try:
        nvalues0 = nvalues(parameters[p_names[0]])
        nvalues1 = nvalues(parameters[p_names[1]])
    except KeyError:
        nvalues0 = NVALUES0_DEFAULT
        nvalues1 = NVALUES1_DEFAULT

    heatmap, param1_edges, param2_edges = np.histogram2d(param1_values, param2_values, 
                                   bins = (nvalues0, nvalues1),
                                   range = [[parameters[p_names[0]]["min"],
                                             parameters[p_names[0]]["max"]],
                                            [parameters[p_names[1]]["min"],
                                             parameters[p_names[1]]["max"]]],
                                   weights = prob1_values)
    
    param1_centers = (param1_edges[:-1] + param1_edges[1:])/2
    param2_centers = (param2_edges[:-1] + param2_edges[1:])/2
    smoothed_heatmap = scipy.ndimage.filters.gaussian_filter(heatmap,[16.,1.28])
    #pdb.set_trace()
    #g = sns.heatmap(heatmap, cmap = sns.color_palette("vlag", as_cmap=True))
    plt.contour(param2_centers, param1_centers, smoothed_heatmap, [0.45, 0.5, 0.55], alpha = 1, linewidth = 2, colors = "green")
    xticks = [2] + list(np.arange(10, parameters[p_names[0]]["max"], 10))
    #g.set_xticks(xticks)
    #g.set_xticks([value_to_nbin(parameters[p_names[0]], nvalues0, val) for val in xtick_labels])
    yticks = list(np.arange(parameters[p_names[0]]["min"],
                            parameters[p_names[0]]["max"],
                            0.1))
    #g.set_yticks([value_to_nbin(parameters[p_names[1]], nvalues1, val) for val in ytick_labels])
    #g.set_yticks(yticks)
    #g.set_xticklabels(xticks)
    #g.set_yticklabels(yticks)
    plt.xlabel('$n_{cut}$')
    plt.ylabel('$f_{mod}$, %')
    plt.rcParams["figure.figsize"] = (8,6)
    #boundary_start = [2, boundary_y(2, samples_file)]
    #boundary_end = [16, boundary_y(16, samples_file)]
    #print(boundary_start)
    #print(boundary_end)
    #plt.plot(boundary_start, boundary_end, linewidth = 2)
    plt.show()
    #plt.savefig('probabilities.png', transparent = True)


def linear_boundary_coeffs(samples_file):
    df = pd.read_excel('samples_out.xlsx')
    params = df[["nsplit", "fmod"]]
    state = df["state"]
    clf = svm.SVC(kernel = 'linear',  gamma=0.7, C=1)
    clf.fit(params, state)
    w = clf.coef_[0]
    a = -w[0] / w[1]
    b = -1 * clf.intercept_[0] / w[1]
    return a, b

def boundary_y(x, samples_file):
    a, b = linear_boundary_coeffs(samples_file)
    return a * x + b

if __name__ == "__main__":
    from matplotlib import pyplot as plt
    from matplotlib.colors import ListedColormap
    import seaborn as sns
    import pandas as pd
    import numpy as np
    import argparse
    import json
    from label_prop import create_points, fit_model
    
    parser = argparse.ArgumentParser(
        description = 'Build a phase diagram')

    parser.add_argument('--samples', metavar = 'XLS', type = str, nargs = 1,
        help = 'file with datapoints')

    parser.add_argument('--config', metavar = 'JSON', type = str, nargs = 1,
        help = 'configuration file')

    args = parser.parse_args()

    samples_filename = args.samples[0]

    config_filename = args.config[0]

    samples_df = pd.read_excel(samples_filename)

    with open(config_filename, "r") as f:
         config = json.load(f)
         
    model_parameters = config["model_parameters"]

    points, labels = create_points(model_parameters, samples_df)
    uc_features, points, distributions = fit_model(model_parameters,
                                                       points, labels,
                                                       mode = "grid")
    #plot_uncertainties(model_parameters, uc_features)
    plot_distributions(model_parameters, points, distributions)