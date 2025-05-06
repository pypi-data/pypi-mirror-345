def floor(i): ...
def ceil(i): ...
def project(data, samples):
    """project(data, samples)

    Interpolate data to the positions specified by samples (pixel coordinates).

    In contrast to warp(), the project() function applies forward
    deformations, moving the pixels/voxels to the given locations,
    rather than getting the pixel values from the given locations.
    Although this may feel closer to how one would like to think about
    deformations, this function is slower and has no options to determine
    the interpolation, because there is no interpolation, but splatting.

    Parameters
    ----------
    data : array (float32 or float64)
        Data to interpolate, can be 1D, 2D or 3D.
    samples : tuple with numpy arrays
        Each array specifies the sample position for one dimension (in
        x-y-z order).  In contrast to warp(), each array must have the same
        shape as data. Can also be a stacked array as in skimage's warp()
        (in z-y-x order).

    Returns
    -------
    result : array
        The result is of the same type and shape as the data array.
    """

def aproject(data, samples):
    """aproject(data, samples)

    Interpolation in anisotropic array. Like project(), but the
    samples are expressed in world coordimates.

    """

def project1(data_, result_, deformx_) -> None: ...
def project2(data_, result_, deformx_, deformy_) -> None: ...
def project3(data_, result_, deformx_, deformy_, deformz_) -> None: ...
