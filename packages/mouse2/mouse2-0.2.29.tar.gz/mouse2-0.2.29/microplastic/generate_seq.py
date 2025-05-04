#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 31 13:59:28 2024

@author: misha
"""
import random
import argparse

choices = [ "1", "2" ]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description = 'Generate a random sequence of 1s with an f fraction of 2s')
    parser.add_argument('--length', type = int, help = "sequence length")
    parser.add_argument('--fraction', type = float, help = "fraction of 2s")
    args = parser.parse_args()

    for i in range(args.length):
        r = random.random()
        if r > args.fraction:
            print(choices[0])
        else:
            print(choices[1])
