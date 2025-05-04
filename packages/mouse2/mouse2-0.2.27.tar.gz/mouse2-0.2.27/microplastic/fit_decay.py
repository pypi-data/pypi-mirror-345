#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 13:33:32 2025

@author: misha
"""
import pandas as pd
import numpy as np
import argparse
import math
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt
from matplotlib.ticker import StrMethodFormatter

def fitting_function(x, a, gamma):
    return a * np.exp(-gamma * x)

vectorized_fitting_function = np.vectorize(fitting_function,
                                               excluded = [1,2])

def guess_max_nbins(times):
    for i in range(1,len(times)):
        times_hist, time_bins = np.histogram(np.array(times), bins = i+1)
        declining = True
        for j in range(i):
            if times_hist[j+1] > times_hist[j]:
                declining = False
        if declining == False:
            max_bins = i
            break
        max_bins = i+1
        return max_bins

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser("Fit disintegration times with \
                                     exponential decay function")
    parser.add_argument("data", type = str, nargs = 1, metavar = "XLSX",
                        help = "Dataset in Excel format")
    parser.add_argument("--nbins", type = int, nargs = "?", metavar = "NBINS",
                        help = "Number of histogram bins",
                        default = None)
    parser.add_argument("--npoints-plot", type = int, nargs = "?", metavar = "NPOINTS",
                        help = "Number of points on the plot",
                        default = 1000)
    args = parser.parse_args()

    data_filename = args.data[0]
    nbins = args.nbins

    df = pd.read_excel(data_filename)

    times = df["longevity"]
    
    nbins = args.nbins
    if nbins == None:
        nbins = guess_max_nbins(times)
    

    times_hist, time_bins = np.histogram(np.array(times), bins = nbins)
    time_bin_centers = (time_bins[1:] + time_bins[:-1]) / 2
    time_max = time_bins[-1]
    bin_width = time_bins[1] - time_bins[0]

    initial_guess = [1., 2./time_max]
    
    params, covariance = curve_fit(fitting_function, time_bin_centers,
                                   times_hist, p0 = initial_guess)
    
    fitting_x = np.arange(args.npoints_plot, dtype = float)
    fitting_x /= args.npoints_plot
    fitting_x *= time_max
    
    fitting_y = vectorized_fitting_function(fitting_x, *params)
    
    plt.rcParams.update({'font.size': 18})
    plt.rcParams.update({'figure.figsize': (8,7)})
    #plt.gca().xaxis.set_major_formatter(StrMethodFormatter('{x:,.0e}'))
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(2))

    plt.bar(time_bin_centers, times_hist, width = bin_width * 0.95, color = 'red')
    
    plt.plot(fitting_x, fitting_y, lw = 5, 
             label = f"{params[0]:,.1f} * exp(-t/{1./params[1]:,.1f})")
    plt.xlabel("Time to the first chain desorption, reduced LJ units")
    plt.ylabel("Nr. of NP particles with corresponding desorption time")
    plt.legend()
    plt.show()
    
    print(params)
    print(covariance)