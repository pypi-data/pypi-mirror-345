#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mikhail Glagolev
"""
from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "mouse2" / "README.md").read_text()

setup(
    name='mouse2',
    version='0.2.27',
    description="""A toolkit for processing molecular dynamics simulation data
    with a focus on chiral ordering""",
    url='https://github.com/mglagolev',
    author='Mikhail Glagolev, Anna Glagoleva',
    author_email='mikhail.glagolev@gmail.com',
    license='GNU GPL v3',
    packages=['mouse2','mdlearn','copoly','microplastic'],
    install_requires=['numpy',
                      'MDAnalysis',
                      'networkx',
                      'matplotlib',
                      'scipy',
                      'scikit-learn',
                      'pandas',
                      'optuna',
                      'openpyxl',
                      
                      ],
    entry_points = {'console_scripts': ['aggregates = mouse2.aggregates:main',
    'bond_autocorrelations = mouse2.bond_autocorrelations:main',
    'backbone_twist = mouse2.backbone_twist:main',
    'local_alignment = mouse2.local_alignment:main',
    'lamellar_alignment = mouse2.lamellar_alignment:main',
    'data2pdb = mouse2.data2pdb:main',
    'create_configuration = mouse2.create_configuration.main',
    ]},
    long_description = long_description,
    long_description_content_type='text/markdown',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
    ],
)
