from _typeshed import Incomplete

from ._utils import Aarray as Aarray
from .interp import zoom as zoom
from .gaussfun import diffuse2 as diffuse2

class BasePyramid: ...
class HaarPyramid: ...

class ScaleSpacePyramid:
    """ScaleSpacePyramid(data, min_scale=None, scale_offset=0,
                                            use_buffer=False, level_factor=2)

    The scale space pyramid class provides a way to manage a scale
    space pyramid. Given an input image (of arbitrary dimension),
    it provides two simple methods to obtain the image at the a specified
    scale or level.

    Parameters
    ----------
    data : numpy array
        An array of any dimension. Should preferably be of float type.
    min_scale : scalar, optional
        The minimum scale to sample from the pyramid. If not given,
        scale_offset is used. If larger than zero, the image is smoothed
        to this scale before creating the zeroth level. If the smoothness
        is sufficient, the data is also downsampled. This makes a registration
        algorithm much faster, because the image data for the final scales
        does not have a unnecessary high resolution.
    scale_offset : scalar
        The scale of the given data. Use this if the data is already smooth.
        Be careful not to set this value too high, as aliasing artifacts
        may be introduced. Default zero.
    use_buffer : bool
        Whether a result obtained with get_scale() is buffered for later use.
        Only one image is buffered. Default False.
    level_factor : scalar
        The scale distance between two levels. A larger number means saving
        a bit of memory in trade of speed. You're probably fine with 2.0.

    Notes
    -----
    Note that this scale space representation handles anisotropic arrays
    and that scale is expressed in world units.

    Note that images at higher levels do not always have a factor 2 sampling
    difference with the original! This is because the first and last pixel
    are kept the same, and the number of pixels is decreased with factors
    of two (or almost a factor of two if the number is uneven).

    The images always have the same offset though.

    We adopt the following concepts:
      * level: the level in the pyramid. Each level is a factor two smaller
        in size (in each dimension) than the previous.
      * scale: the scale in world coordinates

    """

    _level_factor: Incomplete
    _use_buffer: Incomplete
    _buffer: Incomplete
    def __init__(
        self,
        data,
        min_scale: Incomplete | None = None,
        scale_offset: int = 0,
        use_buffer: bool = False,
        level_factor: int = 2,
    ) -> None: ...
    _levels: Incomplete
    def _initialize_level0(self, data, min_scale, scale_offset) -> None:
        """_initialize_level0(data, min_scale, scale_offset)

        Smooth the input image if necessary so it is at min_scale.
        The data is resampled at lower resolution if the scale is
        high enough.

        """
    def calculate(self, levels: Incomplete | None = None, min_shape: Incomplete | None = None):
        """calculate(levels=None, min_shape=None)

        Create the image pyramid now. Specify either the amount of levels,
        or the minimum shape component of the highest level.
        If neither levels nor min_shape is given, uses min_shape=8.

        Returns (max_level, max_sigma) of the current pyramid.

        """
    def get_scale(self, scale: Incomplete | None = None):
        """get_scale(scale)

        Get the image at the specified scale (expressed in world units).
        For higher scales, the image has a smaller shape than the original
        image. If min_scale and scale_offset are not used, a scale of 0
        represents the original image.

        To calculate the result, the image at the level corresponding to
        the nearest lower scale is obtained, and diffused an extra bit
        to obtain the requested scale.

        The result is buffered (if the pyramid was instantiated with
        use_buffer=True), such that calling this function multiple
        times with the same scale is much faster. Only buffers the last
        used scale.

        The returned image has two added properties: _pyramid_scale and
        _pyramid_level, wich specify the image scale and level in the
        pyramid.

        """
    def get_level(self, level):
        """get_level(level):

        Get the image at the specified (integer) level, zero being the
        lowest level (the original image).

        Each level is approximately a factor two smaller in size that the
        previous level. All levels are buffered.

        The returned image has two added properties: _pyramid_scale and
        _pyramid_level, wich specify the image scale and level in the
        pyramid.

        """
    def _add_Level(self) -> None:
        """_add_Level()

        Add a level to the scale space pyramid.

        """
