import numpy as np
from _typeshed import Incomplete

class PointSet(np.ndarray):
    """The PointSet class can be used to represent sets of points or
    vectors, as well as singleton points. The dimensionality of the
    vectors in the pointset can be anything, and the dtype can be any
    of those supported by numpy.

    This class inherits from np.ndarray, which makes it very flexible;
    you can threat it as a regular array, and also pass it to functions
    that require a numpy array. The shape of the array is NxD, with N
    the number of points, and D the dimensionality of each point.

    This class has a __repr__ that displays a pointset-aware description.
    To see the underlying array, use print, or use pointset[...] to
    convert to a pure numpy array.

    Parameters
    ----------
    input : various
        If input is in integer, it specifies the dimensionality of the array,
        and an empty pointset is created. If input is a list, it specifies
        a point, with which the pointset is initialized. If input is a numpy
        array, the pointset is a view on that array (ndim must be 2).
    dtype : dtype descrsiption
        The data type of the numpy array. If not given, the result will
        be float32.

    """
    def __new__(cls, input, dtype=...): ...
    def __str__(self) -> str:
        """print() shows elements as normal."""
    def __repr__(self) -> str:
        """ " Return short(one line) string representation of the pointset."""
    @property
    def can_resize(self):
        """Whether points can be appended to/removed from this pointset.
        This can be False if the array does not own its own data or when
        it is not contiguous. In that case, one should make a copy first.
        """
    def __array_wrap__(self, out, context: Incomplete | None = None, return_scalar: bool = False):
        """So that we return a native numpy array (or scalar) when a
        reducting ufunc is applied (such as sum(), std(), etc.)
        """
    def ravel(self, *args, **kwargs): ...
    def __getitem__(self, index):
        """Get a point or part of the pointset."""
    def append(self, *p) -> None:
        """Append a point to this pointset. One can give the elements
        of the points as separate arguments. Alternatively, a tuple or
        numpy array can be given.
        """
    def extend(self, data) -> None:
        """Extend the point set with more points. The shape[1] of the
        given data must match with that of this array.
        """
    def insert(self, index, *p) -> None:
        """Insert a point at the given index."""
    def contains(self, *p):
        """Check whether the given point is already in this set."""
    def remove(self, *p, **kwargs) -> None:
        """Remove the given point from the point set. Produces an error
        if such a point is not present. If the keyword argument `all`
        is given and True, all occurances of that point are removed.
        Otherwise only the first occurance is removed.
        """
    def __delitem__(self, index) -> None:
        """Remove one or multiple points from the pointset."""
    def pop(self, index: int = -1):
        """Remove and returns a point from the pointset. Removes the last
        by default (which is more efficient than popping from anywhere else).
        """
    def _as_point(self, *p):
        """Return as something that can be applied to a row in the array.
        Check whether the point-dimensions match with this point set.
        """
    def norm(self):
        """Calculate the norm (length) of the vector. This is the
        same as the distance to the origin, but implemented a bit
        faster.
        """
    def normalize(self):
        """Return normalized vector (to unit length)."""
    def normal(self):
        """Calculate the normalized normal of a vector. Use
        (p1-p2).normal() to calculate the normal of the line p1-p2.
        Only works on 2D points. For 3D points use cross().
        """
    def _check_and_sort(self, p1, p2, what: str = "something"):
        """_check_and_sort(p1,p2, what='something')
        Check if the two things (self and a second point/pointset)
        can be used to calculate stuff.
        Returns (p1,p2), if one is a point, p1 is it.
        """
    def distance(self, *p):
        """Calculate the Euclidian distance between two points or
        pointsets. Use norm() to calculate the length of a vector.
        """
    def angle(self, *p):
        """Calculate the angle (in radians) between two vectors. For
        2D uses the arctan2 method so the angle has a sign. For 3D the
        angle is the smallest angles between the two vectors.

        If no point is given, the angle is calculated relative to the
        positive x-axis.
        """
    def angle2(self, *p):
        """Calculate the angle (in radians) of the vector between
        two points.

        Say we have p1=(3,4) and p2=(2,1). ``p1.angle(p2)`` returns the
        difference of the angles of the two vectors: ``0.142 = 0.927 - 0.785``

        ``p1.angle2(p2)`` returns the angle of the difference vector ``(1,3)``:
        ``p1.angle2(p2) == (p1-p2).angle()``

        """
    def dot(self, *p):
        """Calculate the dot product of two pointsets. The dot product
        is the standard inner product of the orthonormal Euclidean
        space. The sizes of the point sets should match, or one point
        set should be singular.
        """
    def cross(self, *p):
        """Calculate the cross product of two 3D vectors. Given two
        vectors, returns the vector that is orthogonal to both vectors.
        The right hand rule is applied; this vector is the middle
        finger, the argument the index finger, the returned vector
        points in the direction of the thumb.
        """
