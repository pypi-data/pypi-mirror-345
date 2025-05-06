from ._misc import (
    meshgrid as meshgrid,
    make_samples_absolute as make_samples_absolute,
)
from .._utils import Aarray as Aarray
from ._forward import (
    project as project,
    aproject as aproject,
)
from ..gaussfun import diffuse as diffuse
from ._backward import (
    warp as warp,
    awarp as awarp,
)

def deform_backward(data, deltas, order: int = 1, spline_type: float = 0.0):
    """deform_backward(data, deltas, order=1, spline_type=0.0)

    Interpolate data according to the deformations specified in deltas.
    Deltas should be a tuple of numpy arrays similar to 'samples' in
    the warp() function. They represent the relative sample positions
    expressed in world coordinates.

    """

def deform_forward(data, deltas):
    """deform_forward(data, deltas)

    Like deform_backward(), but applied to project (forward deformation).

    """

def resize(data, new_shape, order: int = 3, spline_type: float = 0.0, prefilter: bool = False, extra: bool = False):
    """resize(data, new_shape, order=3, spline_type=0.0, prefilter=False, extra=False)

    Resize the data to the specified new shape.

    Parameters
    ----------
    data : numpy array
        The data to rezize.
    new_shape : tuple
        The new shape of the data (z-y-x order).
    order : {0,1,3} or {'nearest', 'linear', 'cubic'}
        The interpolation order to use.
    spline_type : float or string
        Only for cubic interpolation. Specifies the type of spline.
        Can be 'Basis', 'Hermite', 'Cardinal', 'Catmull-rom', 'Lagrange',
        'Lanczos', 'quadratic', or a float, specifying the tension parameter
        for the Cardinal spline. See the docs of get_cubic_spline_coefs()
        for more information.
    prefilter : bool
       Whether to apply (discrete Gaussian diffusion) anti-aliasing
       (when downampling). Default False.
    extra : bool
        Whether to extrapolate the data a bit. In this case, each datapoint
        is seen as spanning a space equal to the distance between the data
        points. This is the method used when you resize an image using
        e.g. paint.net or photoshop. If False, the first and last datapoint
        are exactly on top of the original first and last datapoint (like
        scipy.ndimage.zoom). Default False.

    Notes on extrapolating
    ----------------------
    For the sake of simplicity, assume that the new shape is exactly
    twice that of the original.
    When extra if False, the sampling between the pixels is not a factor 2
    of the original. When extra is True, the sampling decreases with a
    factor of 2, but the data now has an offset. Additionally, extrapolation
    is performed, which is less accurate than interpolation

    """

def imresize(data, new_shape, order: int = 3):
    """imzoom(data, factor, order=3)

    Convenience function to resize the image data (1D, 2D or 3D).

    This function uses pirt.resize() with 'prefilter' and 'extra' set to True.
    This makes it more suitble for generic image resizing. Use pirt.resize()
    for more fine-grained control.

    Parameters
    ----------
    data : numpy array
        The data to rezize.
    new_shape : tuple
        The new shape of the data (z-y-x order).
    order : {0,1,3} or {'nearest', 'linear', 'cubic'}
        The interpolation order to use.

    """

def zoom(data, factor, order: int = 3, spline_type: float = 0.0, prefilter: bool = False, extra: bool = False):
    """zoom(data, factor, order=3, spline_type=0.0, prefilter=False, extra=False)

    Resize the data with the specified factor. The default behavior is
    the same as scipy.ndimage.zoom(), but three times faster.

    Parameters
    ----------
    data : numpy array
        The data to rezize.
    factor : scalar or tuple
        The resize factor, optionally for each dimension (z-y-z order).
    order : {0,1,3} or {'nearest', 'linear', 'cubic'}
        The interpolation order to use.
    spline_type : float or string
        Only for cubic interpolation. Specifies the type of spline.
        Can be 'Basis', 'Hermite', 'Cardinal', 'Catmull-rom', 'Lagrange',
        'Lanczos', 'quadratic', or a float, specifying the tension parameter
        for the Cardinal spline. See the docs of get_cubic_spline_coefs()
        for more information.
    prefilter : bool
       Whether to apply (discrete Gaussian diffusion) anti-aliasing
       (when downampling). Default False.
    extra : bool
        Whether to extrapolate the data a bit. In this case, each datapoint
        is seen as spanning a space equal to the distance between the data
        points. This is the method used when you resize an image using
        e.g. paint.net or photoshop. If False, the first and last datapoint
        are exactly on top of the original first and last datapoint (like
        numpy.zoom). Default False.

    Notes on extrapolating
    ----------------------
    For the sake of simplicity, assume a resize factor of 2.
    When extra if False, the sampling between the pixels is not a factor 2
    of the original. When extra is True, the sampling decreases with a
    factor of 2, but the data now has an offset. Additionally, extrapolation
    is performed, which is less accurate than interpolation

    """

def imzoom(data, factor, order: int = 3):
    """imzoom(data, factor, order=3)

    Convenience function to resize the image data (1D, 2D or 3D) with the
    specified factor.

    This function uses pirt.interp.resize() with 'prefilter' and 'extra'
    set to True. This makes it more suitble for generic image resizing.
    Use pirt.resize() for more fine-grained control.

    Parameters
    ----------
    data : numpy array
        The data to rezize.
    factor : scalar or tuple
        The resize factor, optionally for each dimension (z-y-x order).
    order : {0,1,3} or {'nearest', 'linear', 'cubic'}
        The interpolation order to use.

    """
