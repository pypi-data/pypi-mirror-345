#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 19:50:56 2023

@author: Mikhail Glagolev
"""

import unittest
import MDAnalysis as mda
import os
import sys
parent_dir_name = os.path.dirname(os.path.realpath(__file__))
sys.path.append(parent_dir_name + '/../..')
from mouse2.bond_autocorrelations import bond_autocorrelations
from mouse2.local_alignment import local_alignment
from mouse2.lib.lamellar_orientation import lamellar_alignment
from mouse2.backbone_twist import backbone_twist
import numpy as np
import csv
import time

test_dir = absolute_path = os.path.dirname(__file__)

test_file = os.path.join(test_dir, "helical_lamellae.data.gz")

tolerance = 1e-6

bond_autocorr_tgt = {
    "lamellae_flexible" : 
        { "k_max" : 10,
          "selection" : "type 1",
          "different_molecules" : False,
          "test_file" : "helical_lamellae.data.gz",
          "data" : { "ck" : np.asarray([
                  1.0,
                  0.204648203125,
                  0.08333987862723215,
                  0.04822373422475962,
                  0.04239111735026042,
                  0.028410007546164774,
                  0.0326979833984375,
                  0.0241927001953125,
                  0.019064814758300783,
                  0.017419686453683036,
                  0.017799589029947917,
                  ]),
              }
         },
    "lamellae_helical" : 
        { "k_max" : 10,
          "selection" : "type 2",
          "different_molecules" : False,
          "test_file" : "helical_lamellae.data.gz",
          "data" : { "ck" : np.asarray([
                  1.0,
                  -0.016461666666666666,
                  -0.2911587890625,
                  0.8378388221153846,
                  0.3077317708333333,
                  -0.41193316761363635,
                  0.607004609375,
                  0.5848464409722223,
                  -0.376908251953125,
                  0.31830694754464284,
                  0.747251171875
                  ]),
              }
         },
    "disordered_helices" :
        { "k_max" : 18,
          "selection" : None,
          "different_molecules" : False,
          "test_file" : "disordered_helices.pdb",
          "data" : { "ck" : np.asarray([
                  1.0,
                  -0.00041347082455952963,
                  -0.3038591452205882,
                  0.8871704711914062,
                  0.4083623697916667,
                  -0.4639172014508929,
                  0.5886043419471154,
                  0.7663565266927084,
                  -0.3978091264204546,
                  0.1958014892578125,
                  0.9634552951388888,
                  -0.13286221313476562,
                  -0.16088459123883928,
                  0.9480305989583333,
                  0.23268154296875,
                  -0.35744268798828127,
                  0.7705703125,
                  0.5165108642578125,
                  -0.245722412109375
                  ]),
              }
         },
    "disordered_helices_different_mol" :
        { "k_max" : 25,
          "selection" : None,
          "different_molecules" : True,
          "test_file" : "disordered_helices.pdb",
          "data" : { "ck" : np.asarray([
                  1.0,
                  -0.0013696978246822635,
                  -0.2720864159254191,
                  0.7483043635768517,
                  0.3199276627223801,
                  -0.3440386446065531,
                  0.4055456886398926,
                  0.48207786202347586,
                  -0.2358160696602932,
                  0.10598854839717861,
                  0.4571763657224635,
                  -0.0643645341040315,
                  -0.05886949897722338,
                  0.3040254572739416,
                  0.05214486917717573,
                  -0.07994574252936434,
                  0.12923324883774873,
                  0.04798963242086223,
                  -0.023802412829888986,
                  0.007082524961524098,
                  -5.407812847028001e-05,
                  -0.012452094885233501,
                  0.0014287276876650868,
                  0.00400884942526295,
                  -0.009362746053235562,
                  -0.0040081568194204505
                  ]),
              }
         },
    }
    
local_alignment_tgt = {
    "disordered_rods_same_mol_excluded" :
        {
            "test_file" : "disordered_rods.pdb",
            "r_min" : 1e-6,
            "r_max" : 3.,
            "mode" : "average",
            "n_bins" : 0,
            "selection" : None,
            "same_molecule" : False,
            "id_pairs" : None,
            "data" : { 'average_s' : -0.0035014018032770156 }
        },
    "disordered_rods_same_mol_included" :
        {
            "test_file" : "disordered_rods.pdb",
            "r_min" : 1e-6,
            "r_max" : 3.,
            "mode" : "average",
            "n_bins" : 0,
            "selection" : None,
            "same_molecule" : True,
            "id_pairs" : None,
            "data" : {'average_s': 0.4284608779711845 }
        },
    "ordered_rods_same_mol_included" :
        {
            "test_file" : "ordered_rods.pdb",
            "r_min" : 1e-6,
            "r_max" : 3.,
            "mode" : "average",
            "n_bins" : 0,
            "selection" : None,
            "same_molecule" : True,
            "id_pairs" : None,
            "data" : {'average_s': 0.999999244982867,
                      'bin_edges_cos_sq_theta': [
                          0.0,
                          0.06666666666666667,
                          0.13333333333333333,
                          0.2,
                          0.26666666666666666,
                          0.3333333333333333,
                          0.4,
                          0.4666666666666667,
                          0.5333333333333333,
                          0.6,
                          0.6666666666666666,
                          0.7333333333333333,
                          0.8,
                          0.8666666666666667,
                          0.9333333333333333,
                          1.0],
                      'bin_edges_cos_theta': [
                         0.0,
                         0.2581988897471611,
                         0.3651483716701107,
                         0.4472135954999579,
                         0.5163977794943222,
                         0.5773502691896257,
                         0.6324555320336759,
                         0.6831300510639732,
                         0.7302967433402214,
                         0.7745966692414834,
                         0.816496580927726,
                         0.8563488385776752,
                         0.8944271909999159,
                         0.9309493362512627,
                         0.9660917830792959,
                         1.0],
                      'bin_edges_theta': [
                          1.5707963267948966,
                          1.5040801783846713,
                          1.437064737384955,
                          1.369438406004566,
                          1.300863530961493,
                          1.2309594173407747,
                          1.1592794807274085,
                          1.0852782044993055,
                          1.008260082251041,
                          0.9272952180016123,
                          0.8410686705679303,
                          0.7475843496690209,
                          0.6435011087932843,
                          0.5223148218060486,
                          0.3672080205578371,
                          0.0],
                      'cos_sq_area_normalized_histogram': [
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          15.000000000000004],
                      'cos_sq_raw_histogram': [
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          912493.0],
                      'cos_sq_solid_angle_normalized_histogram': [
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          0.0,
                          15.000000000000002]}
        },
    "lamellae_helical_lists":
        {
            "test_file" : "helical_lamellae.data.gz",
            "r_min" : 1e-6,
            "r_max" : 3.,
            "mode" : "average",
            "n_bins" : 0,
            "selection" : None,
            "same_molecule" : True,
            "id_pairs" : list(csv.reader(open(
                            "indices_helical.dat"), delimiter = ' ')),
            "data" : { 'average_s' : 0.9616488085180521 },
        },
        
    "lamellae_flexible_lists":
        {
            "test_file" : "helical_lamellae.data.gz",
            "r_min" : 1e-6,
            "r_max" : 3.,
            "mode" : "average",
            "n_bins" : 0,
            "selection" : None,
            "same_molecule" : True,
            "id_pairs" : list(csv.reader(open(
                            "indices_flexible.dat"), delimiter = ' ')),
            "data" : { 'average_s' : 0.10374670755565163 },
        },
        
    }
    
lamellar_alignment_tgt = {
    "helical_lamellae" : 
        {
            "test_file" : "helical_lamellae.data.gz",
            "block_A" : '1',
            "block_B" : '2',
            "data" : {
                'ave_sk_A': 0.1349393761206555,
                'ave_sk_B': 0.9484335614978827,
                'director_A': [0.6729965806007385, 
                               0.6719508767127991,
                               -0.3091239333152771],
                'director_B': [-0.6683759689331055,
                               -0.6591828465461731,
                               0.34460344910621643],
                'h_A': [-0.018200051739855783,
                        0.017282652905286855,
                        -0.0020557412337298686],
                'h_B': [-0.00963448950701054,
                        0.007984968781438562,
                        -0.003412347762458301],
                'lam_norm': [0.6688220343349828,
                             0.6647282081332,
                             -0.3328866108752948],
                'pk_A': -0.0047359446982262994,
                'pk_B': -0.0013177566213366798,
                'theta_A': 0.025185892617338553,
                'theta_B': -0.012970832512079157,
                'v_A': 0.006922271924339574,
                'v_B': -0.024626562710843236,
                }
            }
        }
    
backbone_twist_tgt = {
    "twisted_dumbbell" : 
        {
            "test_file" : "twisted_dumbbell.pdb",
            "k_list" : [25,],
            "selection" : "type 2",
            "data" : {
                25 : [
                    -0.899456799030304,
                    -0.5086084604263306,
                    -0.3758271634578705,
                    -0.9083577394485474,
                    -0.7195853590965271,
                    -1.2730724811553955,
                    -0.7488309741020203,
                    -1.2726473808288574,
                    -1.2230472564697266,
                    -0.4401940703392029,
                    0.4922315776348114,
                    -1.278120994567871,
                    -1.6777702569961548,
                    -0.24002833664417267,
                    -1.4382553100585938,
                    -2.311469078063965,
                    2.766162157058716,
                    0.49603745341300964,
                    -2.1207194328308105,
                    -3.122112989425659,
                    -2.534367322921753,
                    3.08029842376709,
                    -2.7310874462127686,
                    -2.6355299949645996,
                    -3.1235690116882324
                    ],
                }
            }
        }
    
    
def dict_max_discrepancy(dict1, dict2):
    discrepancy = 0.
    for key1 in dict1:
        values1 = np.asarray(dict1[key1])
        values2 = np.asarray(dict2[key1])
        discrepancy = max(discrepancy, np.max(np.abs(values1 - values2)))
    return discrepancy

class TestWithTime(unittest.TestCase):
    
    def setUp(self):
        self.startTime = time.time()
        
    def tearDown(self):
        t = time.time() - self.startTime
        print('%s: %.3f' % (self.id(), t))

class TestAutocorrelations(TestWithTime):
    
    def check_autocorrelations(self, target):
        test_file = target["test_file"]
        k_max = target["k_max"]
        selection = target["selection"]
        different_molecules = target["different_molecules"]
        target_data = target["data"]
        u = mda.Universe(test_file)
        result = bond_autocorrelations(u, k_max,
                                    different_molecules = different_molecules,
                                    selection = selection)
        data = list(result["data"].values())[0]
        discrepancy = dict_max_discrepancy(data, target_data)
        assert discrepancy <= tolerance
        
    def test_flexible_sk(self):
        self.check_autocorrelations(bond_autocorr_tgt["lamellae_flexible"])
        
    def test_helical_sk(self):
        self.check_autocorrelations(bond_autocorr_tgt["lamellae_helical"])
        
    def test_disordered_helices(self):
        self.check_autocorrelations(bond_autocorr_tgt["disordered_helices"])
        
    def test_disordered_helices_different_mol(self):
        self.check_autocorrelations(
                       bond_autocorr_tgt["disordered_helices_different_mol"])

     
class TestLocalAlignment(TestWithTime):
    
    def check_local_alignment(self, target):
        test_file = target["test_file"]
        r_min = target["r_min"]
        r_max = target["r_max"]
        mode = target["mode"]
        n_bins = target["n_bins"]
        selection = target["selection"]
        same_molecule = target["same_molecule"]
        id_pairs = target["id_pairs"]
        target_data = target["data"]
        u = mda.Universe(test_file)
        result = local_alignment(u, r_min = r_min, r_max = r_max,
                                 mode = mode, n_bins = n_bins,
                                 id_pairs = id_pairs,
                                 selection = selection,
                                 same_molecule = same_molecule)
        data = list(result["data"].values())[0]
        discrepancy = dict_max_discrepancy(data, target_data)
        assert discrepancy <= tolerance
        
    def test_disordered_rods_same_mol_excluded(self):
        self.check_local_alignment(
                     local_alignment_tgt["disordered_rods_same_mol_excluded"])
    
    def test_rods_disordered_same_mol_included(self):
        self.check_local_alignment(
                     local_alignment_tgt["disordered_rods_same_mol_included"])
        
    def test_ordered_rods_same_mol_included(self):
        self.check_local_alignment(
                     local_alignment_tgt["ordered_rods_same_mol_included"])
        
    def test_lamellae_helical_from_list(self):
        self.check_local_alignment(
                                local_alignment_tgt["lamellae_helical_lists"])
        
    def test_lamellae_flexible_from_list(self):
        self.check_local_alignment(
                                local_alignment_tgt["lamellae_flexible_lists"])
        

class TestLamellarAlignment(TestWithTime):
    
    def check_lamellar_alignment(self, target):
        test_file = target["test_file"]
        block_A = target["block_A"]
        block_B = target["block_B"]
        target_data = target["data"]
        u = mda.Universe(test_file)
        result = lamellar_alignment(u, block_A, block_B)
        data = list(result["data"].values())[0]
        discrepancy = dict_max_discrepancy(data, target_data)
        assert discrepancy <= tolerance
    
    def test_helical_lamellae(self):
        self.check_lamellar_alignment(
                            lamellar_alignment_tgt["helical_lamellae"])


class TestBackboneTwist(TestWithTime):
    
    def check_backbone_twist(self, target):
        test_file = target["test_file"]
        k_list = target["k_list"]
        selection = target["selection"]
        target_data = target["data"]
        u = mda.Universe(test_file)
        result = backbone_twist(u, k_list = k_list, selection = selection)
        data = list(result["data"].values())[0]
        discrepancy = dict_max_discrepancy(data, target_data)
        assert discrepancy <= tolerance
        
    def test_twisted_dumbbell(self):
        self.check_backbone_twist(backbone_twist_tgt["twisted_dumbbell"])

        
if __name__ == "__main__":
    unittest.main()
