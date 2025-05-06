from collections import OrderedDict as _dict

import numpy as np
from _typeshed import Incomplete

from .new_pointset import PointSet as PointSet

_dict = dict

def isidentifier(s): ...

class Parameters(_dict):
    """A dict in which the items can be get/set as attributes."""

    __reserved_names__: Incomplete
    __pure_names__: Incomplete
    __slots__: Incomplete
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def __getattribute__(self, key): ...
    def __setattr__(self, key, val): ...
    def __dir__(self): ...

class Aarray(np.ndarray):
    """Aarray(shape_or_array, sampling=None, origin=None, fill=None,
                dtype=\'float32\', **kwargs)

    Anisotropic array; inherits from numpy.ndarray and adds a sampling
    and origin property which gives the sample distance and offset for
    each dimension.

    Parameters
    ----------
    shape_or_array : shape-tuple or numpy.ndarray
        Specifies the shape of the produced array. If an array instance is
        given, the returned Aarray is a view of the same data (i.e. no data
        is copied).
    sampling : tuple of ndim elements
        Specifies the sample distance (i.e. spacing between elements) for
        each dimension. Default is all ones.
    origin : tuple of ndim elements
        Specifies the world coordinate at the first element for each dimension.
        Default is all zeros.
    fill : scalar (optional)
        If given, and the first argument is not an existing array,
        fills the array with this given value.
    dtype : any valid numpy data type
        The type of the data

    All extra arguments are fed to the constructor of numpy.ndarray.

    Implemented properties and methods
    -----------------------------------
      * sampling - The distance between samples as a tuple
      * origin - The origin of the data as a tuple
      * get_start() - Get the origin of the data as a Point instance
      * get_end() - Get the end of the data as a Point instance
      * get_size() - Get the size of the data as a Point instance
      * sample() - Sample the value at the given point
      * point_to_index() - Given a poin, returns the index in the array
      * index_to_point() - Given an index, returns the world coordinate

    Slicing
    -------
    This class is aware of slicing. This means that when obtaining a part
    of the data (for exampled \'data[10:20,::2]\'), the origin and sampling
    of the resulting array are set appropriately.

    When applying mathematical opertaions to the data, or applying
    functions that do not change the shape of the data, the sampling
    and origin are copied to the new array. If a function does change
    the shape of the data, the sampling are set to all zeros and ones
    for the origin and sampling, respectively.

    World coordinates vs tuples
    ---------------------------
    World coordinates are expressed as Point instances (except for the
    "origin" property). Indices as well as the "sampling" and "origin"
    attributes are expressed as tuples in z,y,x order.

    """

    _is_Aarray: bool
    def __new__(
        cls,
        shapeOrArray,
        sampling: Incomplete | None = None,
        origin: Incomplete | None = None,
        fill: Incomplete | None = None,
        dtype: str = "float32",
        **kwargs,
    ): ...
    _sampling: Incomplete
    _origin: Incomplete
    def __array_finalize__(self, ob) -> None:
        """So the sampling and origin is maintained when doing
        calculations with the array."""
    def __getslice__(self, i, j): ...
    def __getitem__(self, index): ...
    def __array_wrap__(self, out, context: Incomplete | None = None, return_scalar: bool = False):
        """So that we return a native numpy array (or scalar) when a
        reducting ufunc is applied (such as sum(), std(), etc.)
        """
    def _correct_sampling(self, index):
        """_correct_sampling(index)

        Get the new sampling and origin when slicing.

        """
    def _set_sampling(self, sampling) -> None: ...
    def _get_sampling(self): ...
    sampling: Incomplete
    def _set_origin(self, origin) -> None: ...
    def _get_origin(self): ...
    origin: Incomplete
    def point_to_index(self, point, non_on_index_error: bool = False):
        """point_to_index(point, non_on_index_error=False)

        Given a point returns the sample index (z,y,x,..) closest
        to the given point. Returns a tuple with as many elements
        as there are dimensions.

        If the point is outside the array an IndexError is raised by default,
        and None is returned when non_on_index_error == True.

        """
    def sample(self, point, default: Incomplete | None = None):
        """sample(point, default=None)

        Take a sample of the array, given the given point
        in world-coordinates, i.e. transformed using sampling.
        By default raises an IndexError if the point is not inside
        the array, and returns the value of "default" if it is given.

        """
    def index_to_point(self, *index):
        """index_to_point(*index)

        Given a multidimensional index, get the corresponding point in world
        coordinates.

        """
    def get_size(self):
        """get_size()

        Get the size (as a vector) of the array expressed in world coordinates.

        """
    def get_start(self):
        """get_start()

        Get the origin of the array expressed in world coordinates.
        Differs from the property 'origin' in that this method returns
        a point rather than indices z,y,x.

        """
    def get_end(self):
        """get_end()

        Get the end of the array expressed in world coordinates.

        """
