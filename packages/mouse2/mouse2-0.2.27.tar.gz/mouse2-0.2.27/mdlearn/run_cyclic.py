#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import argparse
import json


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
        description = 'Run a simulation iteratively, until the target' 
                      + ' state is reached')

    parser.add_argument('--config', metavar = 'JSON', type = str, nargs = 1,
        help = 'configuration file')

    parser.add_argument('--run', nargs = '?', default = "none",
                        const = "module",
                        help = 'run the simulation,' 
                        + ' set the executable type (module|standalone)')

    args = parser.parse_args()

    config_filename = args.config[0]

    with open(config_filename, "r") as f:
         config = json.load(f)
         

    run_parameters = config["run_parameters"]

    run_template_name = run_parameters["run_template"]
    initial_sequence_file = run_parameters["initial_data"]
    n_steps = run_parameters["n_steps"]
    actions = eval(run_parameters["actions"])
    run_options = run_parameters["run_options"]
    r_neigh_aggregation = run_parameters["r_neigh_aggregation"]
    status_filename = run_parameters["status_file"]


    if args.run != "none":
        import MDAnalysis as mda
        try:
            from mouse2.mouse2.lib.aggregation import determine_aggregates
        except ModuleNotFoundError:
            from mouse2.lib.aggregation import determine_aggregates
        from parzen_search import substitute_values
        # Main loop
        for i_iter in range(1):
            # Run the simulation
            for i_step in range(1, n_steps + 1):
                run_filename = f"run_{i_step}.lammps"
                infile_name = f"in_{i_step}.data"
                prev_outfile_name = f"out_{i_step-1}.data"
                outfile_name = f"out_{i_step}.data"
                logfile_name = f"{i_step}.log"
                xdata_name = f"xdata.{i_step}.lammps"
                dump_name = f"atoms.{i_step}.lammpsdump"
                substitute_values(run_template_name, run_filename,
                                  [["INPUT", infile_name],
                                   ["OUTPUT", outfile_name],
                                   ["LOG", logfile_name],
                                   ["XDATA", xdata_name],
                                   ["DUMP", dump_name]
                                   ])
                if i_step == 1:
                    os.system(f"cp -a {initial_sequence_file} {infile_name}")
                else:
                    os.system(f"cp -a {prev_outfile_name} {infile_name}")
                if args.run == "module":
                    from lammps import lammps
                    lmp = lammps()
                    lmp.file(run_filename)
                elif args.run == "standalone":
                    command = "/mnt/share/glagolev/run_online.py " \
                            + f"--input {run_filename} {run_options}"
                    exit_code = os.system(command)
            # Process the simulation data: determine the aggregation number
                output_exists = os.path.isfile(outfile_name)
                if output_exists:
                    u = mda.Universe(outfile_name)
                    state = label(u)
                else:
                    state = 0
                status_file = open(status_filename, "w")
                status_file.write(str(state))
                status_file.close()
                if actions[state] == "break":
                    break