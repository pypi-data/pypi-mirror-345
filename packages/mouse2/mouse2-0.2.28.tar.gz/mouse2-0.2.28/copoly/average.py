#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 12:16:20 2024

@author: misha
"""

import numpy as np


scalar_classes = [int, float, np.int64, np.float64]
array_classes = [list, np.ndarray]
dict_classes = [dict]


def average_list(data_list):
    """Average a list, that can contain scalars, arrays or dictionaries
       The data structures can be nested."""

    data_types = list(set([type(data) for data in data_list]))
    if len(data_types) > 1:
        raise NameError(f'Heterogeneous data {data_types}')
    data_type = data_types[0]
    #pdb.set_trace()
    if (data_type in scalar_classes) or (data_type in array_classes):
        mean = np.mean(data_list, axis = 0)
        stdev = np.std(data_list, axis = 0)
    elif data_type in dict_classes:
        all_keys = list([list(data.keys()) for data in data_list])
        all_keys_tuples = []
        for keys in all_keys:
            keys.sort()
            all_keys_tuples.append(tuple(keys))
        unique_keys = list(set(all_keys_tuples))
        #pdb.set_trace()
        if len(unique_keys) > 1:
            raise NameError(f'Heterogeneous dict keys {unique_keys}')
        keys = unique_keys[0]
        mean = {}
        stdev = {}
        for key in keys:
            mean[key], stdev[key] = average_list(
                                            [x[key] for x in data_list])
    else:
        raise NameError(f"Unimplemented data type {str(data_type)}")
    return mean, stdev