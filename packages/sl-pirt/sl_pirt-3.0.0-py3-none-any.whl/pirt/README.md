# pirt

This package features mostly unchanged [pirt](https://github.com/almarklein/pirt) source code, which has been repackaged
using Sun lab tools and includes important fixes to make it compatible with the latest versions of numpy and numba. 
This updated package is an important dependency for the multiday suite2p-based cell tracking algorithm adapted from the 
[osm manuscript](https://www.nature.com/articles/s41586-024-08548-w) and integrated into the lab-maintained 
suite2p [fork](https://github.com/Sun-Lab-NBB/suite2p).

This is the root of the package PIRT.

- pirt.apps: small apps related to deformations. Serve as nice examples,
  and can also be used for user interaction.
- pirt.interp: the code related to interpolation, agnostic about deformations.
- pirt.splinegrid: implements B-spline grids.
- pirt.deform: classes to work with deformations.
- pirt.reg: the registration algorithms.
