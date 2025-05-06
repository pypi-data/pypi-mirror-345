def meshgrid(*args):
    """Meshgrid implementation for 1D, 2D, 3D and beyond.

    meshgrid(nx, ny) will create meshgrids with the specified shapes.

    meshgrid(ndarray) will create meshgrids corresponding to the shape
    of the given array (which must have 2 or 3 dimension).

    meshgrid([2,3,4], [1,2,3], [4,1,2]) uses the supplied values to
    create the grids. These lists can also be numpy arrays.

    Returns a tuple with the grids in x-y-z order, with arrays of type float32.
    """

def uglyRoot(n):
    """uglyRoot(n)
    Calculates an approximation of the square root using
    (a few) Newton iterations.
    """

def make_samples_absolute(samples):
    """make_samples_absolute(samples)

    Note: this function is intended for sampes that represent a
    deformation; the number of dimensions of each array should
    match the number of arrays.

    Given a tuple of arrays that represent a relative deformation
    expressed in world coordinates (x,y,z order), returns a tuple
    of sample arrays that represents the absolute sample locations in pixel
    coordinates. It is assumed that the sampling of the data is the same
    as for the sample arrays. The origin property is not used.

    This process can also be done with relative ease by adding a meshgrid
    and then using awarp() or aproject(). But by combining it in
    one step, this process becomes faster and saves memory. Note that
    the deform_*() functions use this function.

    """

def make_samples_absolute1(samples_, result_, sampling, dim: int = 0) -> None: ...
def make_samples_absolute2(samples_, result_, sampling, dim: int = 0) -> None: ...
def make_samples_absolute3(samples_, result_, sampling, dim: int = 0) -> None: ...
