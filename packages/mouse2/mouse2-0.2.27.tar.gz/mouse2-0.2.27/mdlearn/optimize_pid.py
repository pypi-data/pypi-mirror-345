#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import os
import optuna
import pandas as pd
import argparse
import json
import math


trials = []
trials_file = "trials.csv"


def substitute_values(template_filename, output_filename,
                      substitutions = None):
    template_file = open(template_filename, 'r')
    template = template_file.read()
    template_file.close()
    if type(substitutions) == list:
        for substitution in substitutions:
            template = template.replace(*substitution)
    elif type(substitutions) == dict:
        for key in substitutions:
            template = template.replace(key, substitutions[key])
    run_file = open(output_filename, 'w')
    run_file.write(template)
    run_file.close()


def objective(trial: optuna.Trial, config):
    try:
        args = []
        script_changes = []
        trial_data = { "ntrial" : trial.number }
        for param, details in config["model_parameters"].items():
            log = details.get('log', False)
            if log == "True":
                log = True
            if details['type'] == "int":
                value = trial.suggest_int(param, details['min'], details['max'], log=log)
            elif details['type'] == "float":
                value = trial.suggest_float(param, details['min'], details['max'], log=log)
            elif details['type'] == "categorical":
                if type(details['values']) == list:
                    value = trial.suggest_categorical(param, details['values'])
                elif type(details['values']) == dict:
                    value = trial.suggest_categorical(param, list(details['values'].keys()))
                else:
                    raise NameError("unsupported values data type")
            else:
                raise ValueError(f"Unsupported parameter type: {details['type']}")

            if details['type'] == "categorical" and type(details['values']) == dict:
                output_value = value
                value = details['values'][value]
            else:
                output_value = value

            if details['usage'] == 'script':
                script_changes.append((param, str(value)))
            elif details['usage'] == 'cli':
                args.append(f"--{param} {value}")
                
            trial_data[param] = output_value

        template = config["opt_parameters"]["template_filename"]
        run_filename_template = config["opt_parameters"]["run_filename_template"]
        run_filename = f"{run_filename_template}{trial.number}.lammps"
        substitute_values(template,run_filename,script_changes)
        
        command = f"/mnt/share/glagolev/run_online.py --input {run_filename} {' '.join(args)}"

        exit_code = os.system(command)
        output_exists = os.path.isfile(f'out_{trial.number}.data')
        if output_exists:
            # Read pid_fit log file
            # Calculate discrepancy of the mean and the dispersion
        else:
            error = math.inf

        trial_data["error"] = performance
        trials.append(trial_data)
        trials_df = pd.DataFrame.from_records(trials)
        
        trials_df.to_csv(trials_file)

        return error

    except Exception as e:
        print(e)
        return 0.


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Model Parameters")
    parser.add_argument("config", metavar = "JSON", type = str, nargs = '?',
    			default = "config.json", help = "study configuration file")
    args = parser.parse_args()
    
    config_filename = args.config
    
    with open(config_filename, "r") as f:
        config = json.load(f) 
    sampler_name = config["opt_parameters"]["sampler"]
    if sampler_name == "Random":
        sampler = optuna.samplers.RandomSampler()
    elif sampler_name == "TPE":
        sampler = optuna.samplers.TPESampler()
    else:
        raise NameError("unknown sampler")
    n_trials = config["opt_parameters"]["iterations"]
    study = optuna.create_study(direction="maximize", sampler = sampler)
    study.optimize(lambda trial: objective(trial, config), n_trials=n_trials, gc_after_trial=True)
    if True:
        print("Study statistics: ")
        print("  Number of finished trials: ", len(study.trials))
        print("Best trial:")
        trial = study.best_trial

        for key, value in trial.params.items():
            print("    {}: {}".format(key, value))

        study.trials_dataframe().to_csv('study.csv')

