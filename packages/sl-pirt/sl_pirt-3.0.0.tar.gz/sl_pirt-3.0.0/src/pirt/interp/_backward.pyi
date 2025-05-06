from ._cubic import (
    spline_type_to_id as spline_type_to_id,
    set_cubic_spline_coefs as set_cubic_spline_coefs,
    cubicsplinecoef_cardinal as cubicsplinecoef_cardinal,
    cubicsplinecoef_quadratic as cubicsplinecoef_quadratic,
)

def floor(i): ...
def warp(data, samples, order: int = 1, spline_type: float = 0.0):
    """warp(data, samples, order=\'linear\', spline_type=0.0)

    Interpolate (sample) data at the positions specified by samples
    (pixel coordinates).

    Parameters
    ----------
    data : array (float32 or float64)
        Data to interpolate, can be 1D, 2D or 3D.
    samples : tuple with numpy arrays
        Each array specifies the sample position for one dimension (in
        x-y-z order). Can also be a stacked array as in skimage\'s warp()
        (in z-y-x order).
    order : integer or string
        Order of interpolation. Can be 0:\'nearest\', 1:\'linear\', 2: \'quadratic\',
        3:\'cubic\'.
    spline_type : float or string
        Only for cubic interpolation. Specifies the type of spline.
        Can be \'Basis\', \'Hermite\', \'Cardinal\', \'Catmull-rom\', \'Lagrange\',
        \'Lanczos\', \'quadratic\', or a float, specifying the tension
        parameter for the Cardinal spline. See the docs of
        get_cubic_spline_coefs() for more information.

    Returns
    -------
    result : array
        The result is of the same type as the data array, and of the
        same shape of the samples arrays, which can be of any shape.
        This flexibility makes this function suitable as a base function
        for higher level "sampling functions".

    Notes
    -----------
    The input data can have up to three dimensions. It can be of any dtype,
    but float32 or float64 is recommended in general.

    An order of interpolation of 2 would naturally correspond to
    quadratic interpolation. However, due to its uneven coefficients
    it reques the same support (and speed) as a cubic interpolant.
    This implementation adds the two quadratic polynomials. Note that
    you can probably better use order=3 with a Catmull-Rom spline, which
    corresponds to the linear interpolation of the two quadratic polynomials.

    It can be shown (see Thevenaz et al. 2000 "Interpolation Revisited")
    that interpolation using a Cardinal spline is equivalent to
    interpolating-B-spline interpolation.
    """

def awarp(data, samples, *args, **kwargs):
    """awarp(data, samples, order='linear', spline_type=0.0)

    Interpolation in anisotropic array. Like warp(), but the
    samples are expressed in world coordimates.

    """

def warp1(data_, result_, samplesx_, order, spline_id) -> None: ...
def warp2(data_, result_, samplesx_, samplesy_, order, spline_id) -> None: ...
def warp3(data_, result_, samplesx_, samplesy_, samplesz_, order, spline_id) -> None: ...
