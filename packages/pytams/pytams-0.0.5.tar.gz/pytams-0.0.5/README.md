# pyTAMS

[![github license badge](https://img.shields.io/github/license/nlesc-eTAOC/pyTAMS)](https://github.com/nlesc-eTAOC/pyTAMS)
[![RSD](https://img.shields.io/badge/rsd-pyTAMS-00a3e3.svg)](https://research-software-directory.org/software/pytams)
[![DOI](https://zenodo.org/badge/707169096.svg)](https://zenodo.org/doi/10.5281/zenodo.10057843)
[![build](https://github.com/nlesc-eTAOC/pyTAMS/actions/workflows/build.yml/badge.svg)](https://github.com/nlesc-eTAOC/pyTAMS/actions/workflows/build.yml)
[![sonarcloud](https://github.com/nlesc-eTAOC/pyTAMS/actions/workflows/sonarcloud.yml/badge.svg)](https://github.com/nlesc-eTAOC/pyTAMS/actions/workflows/sonarcloud.yml)
[![workflow scc badge](https://sonarcloud.io/api/project_badges/measure?project=nlesc-eTAOC_pyTAMS&metric=coverage)](https://sonarcloud.io/dashboard?id=nlesc-eTAOC_pyTAMS)


## Overview

*pyTAMS* is a modular implementation of the trajectory-adaptive multilevel splitting (TAMS) method
introduced by [Lestang et al.](https://doi.org/10.1088/1742-5468/aab856). This method aims at predicting
rare events probabilities in dynamical systems by biasing an system trajectories ensemble.

The main objective of *pyTAMS* is to provide a general framework for applying TAMS to high-dimensional
systems such as the ones encountered in geophysical or engineering applications.


## Installation

To install *pyTAMS* from GitHub repository, do:

```console
git clone git@github.com:nlesc-eTAOC/pyTAMS.git
cd pyTAMS
python -m pip install .
```

## Quick start

To get started with *pyTAMS*, let's have a look at the classical double-well potential case.
Although it is not a high-dimensional system, it provides a good overview of *pyTAMS* capabilities.
A 3D version of the double-well is available in the [examples](examples) folder. To run the case,
simply do:

```console
cd examples
python doubleWell3D.py -i input_dw3D.toml
```

This minimal example runs TAMS 10 times in order to get an estimate of the transition probability
as well as the corresponding standard error. For a more in-depth explanation about this case, setting up the
model and running the simulations, have a look at the tutorial [here](https://nlesc-eTAOC.github.io/pyTAMS/Tutorials.html).

## Documentation

[![doc](https://github.com/nlesc-eTAOC/pyTAMS/actions/workflows/documentation.yml/badge.svg)](https://github.com/nlesc-eTAOC/pyTAMS/actions/workflows/documentation.yml)

*pyTAMS* documentation is hosted on GitHub [here](https://nlesc-etaoc.github.io/pyTAMS/)

## Contributing

If you want to contribute to the development of *pyTAMS*,
have a look at the [contribution guidelines](CONTRIBUTING.md).

## Acknowledgements

The development of *pyTAMS* was supported by the Netherlands eScience Center
in collaboration with the Institute for Marine and Atmospheric research Utrecht [IMAU](https://www.uu.nl/onderzoek/imau).

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [NLeSC/python-template](https://github.com/NLeSC/python-template).
