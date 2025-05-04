#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np
from sklearn.semi_supervised import LabelPropagation, LabelSpreading
import random
import os
import argparse


# Variables

model_parameters = {
    "f" :
            {"min" : 0,
           "max" : 1.,
           "step" : 0.01},
    "nsplit" : 
            { "min" : 2,
              "max" : 64,
              "step" : 1}
    }
    
n_iterations = 100

uc_threshold = 0.01
uc_sampling_mode = "MS"

outfile_name = "out.data"
infile_name = "in.data"
run_template_name = "template.lammps"
n_random = 10

initial_sequence_file = "initial_sequence.data"

r_neigh_aggregation = 1.2

run_options = "--mode 1gpu --nproc 1"

# Function definitions

def parameter_ordered_names(parameters):
    p_names = list(parameters.keys())
    p_names.sort()
    return p_names


def normalize(parameter, value):
    return (value - parameter["min"]) / (parameter["max"] - parameter["min"])


def restore(parameter, value):
    return parameter["min"] + value * (parameter["max"] - parameter["min"])


def nvalues(parameter):
    return int((parameter["max"] - parameter["min"]) / parameter["step"]) + 1


def create_points(parameters, samples_df):
    p_names = parameter_ordered_names(parameters)
    points = np.mgrid[
                       parameters[p_names[0]]["min"]
                      :parameters[p_names[0]]["max"]
                      +parameters[p_names[0]]["step"]
                      :parameters[p_names[0]]["step"],
                       parameters[p_names[1]]["min"]
                      :parameters[p_names[1]]["max"]
                      +parameters[p_names[1]]["step"]
                      :parameters[p_names[1]]["step"]
                     ].reshape(2,-1).T
    labels = []
    for point in points:
        samples = (samples_df[
            (samples_df[p_names[0]] == point[0]) &
            (samples_df[p_names[1]]== point[1])])
        if len(samples) > 0:
            labels.append(samples["state"].iloc[0])
        else:
            labels.append(-1)
    return points, labels


def normalize_points(parameters, points):
    p_names = parameter_ordered_names(parameters)
    normalized_points = []
    for point in points:
        normalized_points.append([normalize(parameters[p_names[0]], point[0]),
                                  normalize(parameters[p_names[1]], point[1])])
    return normalized_points


def restore_points(parameters, points):
    p_names = parameter_ordered_names(parameters)
    restored_points = []
    for point in points:
        restored_points.append([restore(parameters[p_names[0]], point[0]),
                                restore(parameters[p_names[1]], point[1])])
    return restored_points


def uncertainties_eb(label_distributions):
    """ Entropy-based: sum(p*log(p)) """
    uncertainties = []
    for sample in label_distributions:
        if np.max(sample) == 1.:
            uncertainties.append(0.)
        else:
            uncertainties.append(-1. * np.dot(sample, np.log(sample)))
    return uncertainties


def uncertainties_lc(label_distributions):
    """ Least certain: 1 - max(X,p) """
    uncertainties = []
    for sample in label_distributions:
        uncertainties.append(1. - np.max(sample))
    return uncertainties


def uncertainties_ms(label_distributions):
    """ Margin sampling: 1 - [max(X,p) - second_max(X,p)] """
    uncertainties = []
    for sample in label_distributions:
        prob_ix = np.argsort(sample)
        uncertainties.append(1. - sample[prob_ix[-1]] + sample[prob_ix[-2]])
    return uncertainties


def uncertainties(label_distributions, mode = None):
    match mode:
        case "EB":
            return uncertainties_eb(label_distributions)
        case "LC":
            return uncertainties_lc(label_distributions)
        case "MS":
            return uncertainties_ms(label_distributions)


def fit_model(parameters, points, labels, mode = None):

    normalized_points = normalize_points(parameters, points)

    label_prop = LabelSpreading(kernel = 'rbf', gamma = 20,
                                max_iter = 100000)

    label_prop.fit(normalized_points, labels)

    distributions = label_prop.label_distributions_

    uc = uncertainties(distributions, mode = mode)

    uc_features = list(zip(uc, points))

    uc_features.sort(key = lambda k: k[0])
    
    return uc_features, points, distributions


def choose_parameters(parameters, samples_df, mode = "MS", uc_threshold = 0.01):
    
    points, labels = create_points(parameters, samples_df)
    
    if samples_df.shape[0] > n_random:
    
        uc_features, _, _ = fit_model(parameters, points, labels, mode = mode)

        uc_delta = uc_features[-1][0] - uc_features[0][0]

        if uc_delta > uc_threshold:
            return uc_features[-1][1]
        else:
            return uc_features[random.randrange(0,len(uc_features))][1]
    else:
        return random.choice(points)


def plot_uncertainties(parameters, uc_features):
    uc_values = [i[0] for i in uc_features]
    param1_values = [i[1][0] for i in uc_features]
    param2_values = [i[1][1] for i in uc_features]

    p_names = parameter_ordered_names(parameters)

    heatmap, _, _ = np.histogram2d(param1_values, param2_values, 
                                   bins = (nvalues(parameters[p_names[0]]),
                                           nvalues(parameters[p_names[1]])),
                                   weights = uc_values)
    g = sns.heatmap(heatmap)
    g.set_xticks([10, 20, 30, 40, 50, 60])
    g.set_yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    g.set_xticklabels([10, 20, 30, 40, 50, 60])
    g.set_yticklabels([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
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
    
    

def label(u):
    aggregates_dict = determine_aggregates(u, r_neigh = r_neigh_aggregation)
    aggregates_list = aggregates_dict["data"][list(aggregates_dict["data"].keys())[0]]
    if len(aggregates_list) == 1:
        return 1
    elif len(aggregates_list) > 1:
        return 2
    else:
        raise NameError(f"Aggregates list length is {len(aggregates_list)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = 'Build a phase diagram')

    parser.add_argument('file', metavar = 'XLS', type = str, nargs = 1,
        help = 'file with datapoints')
    
    parser.add_argument('--run', nargs = '?', default = "none",
                        const = "module",
                        help = 'run the simulation,' 
                        + ' set the executable type (module|standalone)')
    
    parser.add_argument('--plot', action = "store_true",
        help = 'plot the uncertainties based on the datafile')


    args = parser.parse_args()

    samples_filename = args.file[0]

    samples_df = pd.read_excel(samples_filename)

    p_names = parameter_ordered_names(model_parameters)

    if args.plot:
        from matplotlib import pyplot as plt
        from matplotlib.colors import ListedColormap
        import seaborn as sns
        uc_features, points, distributions = fit_model(model_parameters, samples_df,
                                               mode = uc_sampling_mode)
        plot_uncertainties(model_parameters, uc_features)
        plot_distributions(model_parameters, points, distributions)

    if args.run != "none":
        import MDAnalysis as mda
        from mouse2.mouse2.lib.aggregation import determine_aggregates
        from microplastic.modify_seq import modify_seq
        from parzen_search import substitute_values
        # Main loop
        for i_iter in range(1, n_iterations + 1):
            # Fit the model and choose simulation parameters
            run_parameters = choose_parameters(model_parameters, samples_df)
            # Dump the model data

            # Create the simulation dict object with all the attributes stored
            simulation = {}
            simulation[p_names[0]] = run_parameters[0]
            simulation[p_names[1]] = run_parameters[1]
            run_filename = f"{i_iter}.lammps"
            infile_name = f"in_{i_iter}.data"
            outfile_name = f"out_{i_iter}.data"
            logfile_name = f"{i_iter}.log"
            # Prepare the simulation
            u = mda.Universe(initial_sequence_file)
            modify_seq(u, prob = simulation["f"], nsplit = simulation["nsplit"])
            u.atoms.write(infile_name)
            # Modify the filenames in the script
            substitute_values(run_template_name, run_filename,
                              [["INPUT", infile_name],
                               ["OUTPUT", outfile_name],
                               ["LOG", logfile_name],
                               ["ITER", str(i_iter)],
                               ])
            # Run the simulation
            if args.run == "module":
                from lammps import lammps
                lmp = lammps()
                lmp.file(run_filename)
            elif args.run == "standalone":
                command = "/mnt/share/glagolev/run_online.py " \
                        + f"--input {run_filename} {run_options}"
                exit_code = os.system(command)
            # Process the simulation data: determine the aggregation number
            u = mda.Universe(outfile_name)
            simulation["state"] = label(u)
            # Update the dataframe
            new_df = pd.DataFrame(simulation, index = [0])
            updated_df = pd.concat([samples_df, new_df], ignore_index = True)
            updated_df.reset_index()
            updated_df.to_excel("samples_out.xlsx")
            samples_df = updated_df