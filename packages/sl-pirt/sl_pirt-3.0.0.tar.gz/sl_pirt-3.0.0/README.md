# SL-PIRT - Sun lab Python Image Registration Toolkit.

A modified [pirt](https://github.com/almarklein/pirt) library distribution used in the Sun lab’s
[sl-suite2p](https://github.com/Sun-Lab-NBB/suite2p) library multi-day registration pipeline.

![PyPI - Version](https://img.shields.io/pypi/v/sl-pirt)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sl-pirt)
[![uv](https://tinyurl.com/uvbadge)](https://github.com/astral-sh/uv)
[![Ruff](https://tinyurl.com/ruffbadge)](https://github.com/astral-sh/ruff)
![type-checked: mypy](https://img.shields.io/badge/type--checked-mypy-blue?style=flat-square&logo=python)
![PyPI - License](https://img.shields.io/pypi/l/sl-pirt)
![PyPI - Status](https://img.shields.io/pypi/status/sl-pirt)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/sl-pirt)
___

## Detailed Description

This library is used as part of the suite2p multi-day registration pipeline maintained by the Sun lab. It has been 
minorly refactored from the original and now unmaintained version (2.0.0) to work with modern Python versions (3.11+)
and dependency libraries. See the [change log](#change-log) section for the list of specific source code changes as 
part of our refactoring effort.

***Note!*** The refactoring and repackaging efforts were specifically aimed at getting the package to work with the 
suite2p multi-day pipeline. They might have broken some components of the library, and they were not aimed at fixing 
existing bugs or restoring other functions of this library or its dependencies. Overall, it is highly advised NOT to 
use this library in any other project.

***Warning!*** This library is a temporary implementation used until the Sun lab finalizes implementing a registration
algorithm for the maintained sl-suite2p package. Once that work is complete, we will no longer maintain this package.
---

## Change Log
The following changes have been made to this library version (3.0.0) relative to the base pirt version it was made 
against (2.1.1):

1. The source code has been reformatted with Ruff to match the standard Sun lab code style.
2. The source code has been modified where necessary to make it compatible with NumPy 2.0.0+ and SciPy 1.9.0+, making it
   compatible with the dependency versions used by sl-suite2p library.
3. Default parameters for some types of registration have been adjusted to prevent failing available test cases and 
   produce expected results in suite2p pipeline testing.
4. The library has been repackaged using Sun lab automation and packaging tools, which also matches the modern Python 
   packaging standards.
5. All library dependencies have been appropriately pinned to the necessary major and, where appropriate, minor 
   versions. The Python versions have been limited to 3.11+, consistent with other Sun-lab-managed libraries.

***Note!*** The library retains existing documentation, overall structure, and license.

---

## Introduction

Pirt is the "Python image registration toolkit." It is a library for (elastic, i.e., non-rigid) image registration of 
2D and 3D images with support for groupwise registration. It has support to constrain the deformations to be 
"diffeomorphic," i.e., without folding or shearing, and thus invertible.

Pirt is written in pure Python and uses Numba for speed. It depends on Numpy, Scipy, Numba. It has an optional 
dependency on Visvis for visualization, and on pyelastix for the Elastix registration algorithm.

Pirt implements its own interpolation functions, which, incidentally, are faster than the corresponding functions in 
scipy and scikit-image (after Numba’s JIT warmup).

Pirt is hosted on [Github](https://github.com/almarklein/pirt) and has [docs on rtd](http://pirt.readthedocs.io/).

---

## Overview

Image registration itself requires several image processing techniques and data types, which are also included in this 
package:

1. [gaussfun](/src/pirt/gaussfun.py) module, which contains the function for Gaussian smoothing and derivatives and 
   image pyramid class.
2. [interp](/src/pirt/interp) package, which contains the tools for interpolating 1D, 2D, and 3D data (nearest, linear,
   and various spline interpolants).
3. [splinegrid](/src/pirt/splinegrid) package, which defines a B-spline grid class (for data up to three dimensions) and
   a class to describe a deformation grid (consisting of a B-spline grid for each dimension).
4. [deform](/src/pirt/deform) package, which defines classes to represent and compose deformations.
5. [reg](/src/pirt/reg) package, which stores the actual registration algorithms.

---

## Dependencies

For users, all library dependencies are installed automatically for all supported installation methods 
(see [Installation](#installation) section). For developers, this library additionally requires PySide6 and Imageio.
___

## Installation

### Source

1. Download this repository to your local machine using your preferred method, such as git-cloning. Optionally, use one
   of the stable releases that include precompiled binary wheels in addition to source code.
2. ```cd``` to the root directory of the project using your command line interface of choice.
3. Run ```python -m pip install .``` to install the project. Alternatively, if using a distribution with precompiled 
   binaries, use ```python -m pip install WHEEL_PATH```, replacing 'WHEEL_PATH' with the path to the wheel file.

### PIP

Use the following command to install the library using PIP: ```pip install sl-pirt```\

---

## Status and licensing

Pirt package is currently unmaintained by the original author. The Sun lab package is only maintained for the extent of
working with the sl-suite2p package.

Pirt is BSD licensed, see [LICENSE](LICENSE) for more information.
