Welcome to ProteinPlot's documentation!
============================================

Welcome to the documentation for **ProteinPlot**, a University package for analysing PDB entries in python

Introduction
------------

ProteinPlot helps in the analysis of PDB entries. The given files from the databank of rcsb.org is loaded into pandas dataframes and in this way manipulations have become easier

Features
--------

- PDB entry reading into pandas df
- Structure alignment
- Structure comparison
- Ramachadran plots
- 2D and 3D figures

Installation
------------

Install via pip: pip install ProteinPlot

Quick Start
-----------

Here's a basic example:

  The package automatically installs an IDE, that can be opened with the following bash command:
  
  jupyter-lab
  
  Load in the package and your first **PDB** file
   
   from ProteinPlot import protplot
   example = protplot.read_pdb('6vxx')
   
You are ready to go. For further examples please visit the documentation!