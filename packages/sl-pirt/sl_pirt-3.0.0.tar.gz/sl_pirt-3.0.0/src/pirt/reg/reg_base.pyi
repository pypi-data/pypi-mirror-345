from _typeshed import Incomplete

from .._utils import (
    Aarray as Aarray,
    Parameters as Parameters,
)
from ..deform import (
    Deformation as Deformation,
    DeformationField as DeformationField,
    DeformationIdentity as DeformationIdentity,
    DeformationGridForward as DeformationGridForward,
    DeformationFieldForward as DeformationFieldForward,
    DeformationGridBackward as DeformationGridBackward,
    DeformationFieldBackward as DeformationFieldBackward,
)
from ..pyramid import ScaleSpacePyramid as ScaleSpacePyramid
from ..splinegrid import SplineGrid as SplineGrid

class classproperty(property):
    def __get__(self, cls, owner): ...

def create_grid_image(shape, sampling: Incomplete | None = None, step: int = 10, bigstep: Incomplete | None = None):
    """create_grid_image(shape, sampling=None, step=10, bigstep=5*step)

    Create an image depicting a grid. The first argument can also be an array.

    """

class Progress:
    """Progress()

    Allows an algorithm to display the progress to the user.

    """

    _progress_last_message: str
    _progress_iter: int
    _progress_max_iters: int
    def __init__(self) -> None: ...
    def start(self, message, max_iters: int = 0) -> None:
        """start(message, max_iters=0)

        Start a progress. The message should indicate what is being done.

        """
    def next(self, extra_info: str = "") -> None:
        """next(extra_info='')

        Update progress to next iteration and show the new progress.
        Optionally a message with extra information can be displayed.

        """
    def show(self, extra_info: str = "") -> None:
        """show(extra_info='')

        Show current progress, and optional extra info.

        """

class Timer:
    """Timer()

    Enables registration objects to time the different components.
    Can be used to optimize the speed of the registration algorithms,
    or to study the effect of a parameter on the speed.

    Multiple things can be timed simultaneously. Timers can also be
    started and stopped multiple times; the total time is measured.

    """

    _timers: Incomplete
    def __init__(self) -> None: ...
    def start(self, id) -> None:
        """start(id)

        Start a timer for the given id, which should best be a string.

        The timer can be started and stopped multiple times.
        In the end the total time spend on 'id' can be displayed
        using show().

        """
    def stop(self, id) -> None:
        """stop(id)

        Stop the timer for 'id'.

        """
    def get(self, id):
        """get(id)

        Get the total time spend in seconds on 'id'.
        Returns -1 if the given id is not valid.

        """
    def show(self, id: Incomplete | None = None) -> None:
        """show(id=None)

        Show (print) the results for the total timings of 'id'.
        If 'id' is not given, will print the result of all timers.

        """

class Visualizer:
    """Visualize

    Tool to visualize the images during registration.

    """

    _f: Incomplete
    def __init__(self) -> None: ...
    def init(self, fig) -> None:
        """init(fig)

        Initialize by giving a figure.

        """
    @property
    def fig(self):
        """Get the figure instance (or None) if init() was not called."""
    def imshow(self, subplot, im, *args, **kwargs):
        """imshow(subplot, im, *args, **kwargs)

        Show the given image in specified subplot. If possible,
        updates the previous texture object.

        """

class AbstractRegistration:
    """AbstractRegistration(*images, makeFloat=True)

    Base class for registration of 2 or more images. This class only provides
    a common interface for the user.

    This base class can for example be inherited by registration classes
    that wrap an external registration algorithm, such as Elastix.

    Also see :class:`pirt.BaseRegistration`.

    Implements:

      * progress, timer, and visualizer objects
      * properties to handle the mapping (forward or backward)
      * functionality to get and set parameters
      * basic functionality to get resulting deformations
      * functionality to show the result (2D only)

    Parameters
    ----------
    None
    """

    _ims: Incomplete
    _deforms: Incomplete
    _params: Incomplete
    _progress: Incomplete
    _timer: Incomplete
    _visualizer: Incomplete
    def __init__(self, *ims, makeFloat: bool = True) -> None: ...
    @classmethod
    def register_and_get_object(cls, *ims, **params):
        """register_get_object(*ims, **params)

        Classmethod to register the given images with the given
        parameters, and return the resulting registration object
        (after the registration has been performed).

        """
    @property
    def progress(self):
        """The progress object, can be used by the algorithm to indicate
        its progress.
        """
    @property
    def timer(self):
        """The timer object, can be used by the algorithm to measure the
        processing time of the different steps in the registration algorithm.
        """
    @property
    def visualizer(self):
        """The visualizer object, can be used by the algorithm to display
        the images as they are deformed during registration.
        """
    @property
    def forward_mapping(self):
        """Whether forward (True) or backward (False)
        mapping is to be used internally.
        """
    @property
    def DeformationField(self):
        """Depending on whether forward or backward mapping is used,
        returns the DeformationFieldForward or DeformationFieldBackward
        class.
        """
    @property
    def DeformationGrid(self):
        """Depending on whether forward or backward mapping is used,
        returns the DeformationGridForward or DeformationGridBackward
        class.
        """
    def _defaultParams(self):
        """Overload to create all default params."""
    @classmethod
    def defaultParams(cls):
        """Class property to get the default params for this registration
        class.
        """
    @property
    def params(self):
        """Get params structure (as a Parameters object)."""
    def set_params(self, params: Incomplete | None = None, **kwargs) -> None:
        """set_params(params=None, **kwargs)

        Set any parameters. The parameters are updated with the given
        dict, Parameters object, and then with the parameters given
        via the keyword arguments.

        Note that the parameter structure can also be accessed directly via
        the 'params' propery.

        """
    def get_deform(self, i: int = 0):
        """get_deform(i=0)

        Get the DeformationField instance for image with index i. If groupwise
        registration was used, this deformation field maps image i to the mean
        shape.

        """
    def get_final_deform(self, i: int = 0, j: int = 1, mapping: Incomplete | None = None):
        """get_final_deform(i=0, j=1, mapping=None)

        Get the DeformationField instance that maps image with index i
        to the image with index j. If groupwise registration was used,
        the deform is a composition of deform 'i' with the inverse of
        deform 'j'.

        Parameters
        ----------
        i : int
            The source image
        j : int
            The target image
        mapping : {'forward', 'backward', Deformation instance}
            Whether the result should be a forward or backward deform.
            When specified here, the result can be calculated with less
            errors than for example using result.as_forward(). If a
            Deformation object is given, the mapping of that deform is used.

        """
    def show_result(self, how: Incomplete | None = None, fig: Incomplete | None = None):
        """show_result(self, how=None, fig=None)

        Convenience method to show the registration result. Only
        works for two dimensional data.
        Requires visvis.

        """
    def register(self, verbose: int = 1, fig: Incomplete | None = None) -> None:
        """register(verbose=1, fig=None)

        Perform the registration process.

        Parameters
        ----------
        verbose : int
            Verbosity level. 0 means silent, 1 means print some, 2 means
            print a lot.
        fig : visvis figure or None
            If given, will display the registration progress in the given
            figure.
        """
    def _register(self, verbose, fig) -> None:
        """Inheriting classes should overload this method."""

class NullRegistration(AbstractRegistration):
    """NullRegistration(*images)

    Inherits from :class:`pirt.AbstractRegistration`.

    A registration algorithm that does nothing. This can be usefull to test
    the result if no registration would be applied.

    Parameters
    ----------
    None

    """
    def _defaultParams(self):
        """Overload to create all default params."""
    def _register(self, *args, **kwargs) -> None: ...

class BaseRegistration(AbstractRegistration):
    """BaseRegistration(*images)

    Inherits from :class:`pirt.AbstractRegistration`.

    An abstract registration class that provides common functionality
    shared by almost all registration algorithms.

    This class maintains an image pyramid for each image, implements methods
    to set the delta deform, and get the deformed image at a specified scale.
    Further, this class implements the high level aspect of the registration
    algorithm that iterates through scale space.

    Parameters
    ----------
    mapping : {'forward', 'backward'}
        Whether forward or backward mapping is used. Default forward.
    combine_deforms : {'compose', 'add'}
        How deformations are combined. Default compose. While add is used
        in some (older) registration algorithms, it is a coarse approximation.
    final_scale : scalar
        The minimum scale used during the registration process. This is the
        scale at which the registration ends. Default 1.0. Because calculating
        differentials suffer from more errors as the scale decreases, the
        minimum value is limited at 0.5.
    scale_levels : integer
        The amount of scale levels to use during the registration. Each level
        represents a factor of two in scale. The default (4) works for
        most images, but for large images or large deformations a larger
        value can be used.
    scale_sampling : scalar
        The amount of iterations for each level (i.e. between each factor
        two in scale). What values are reasonable depends on the specific
        algorithm.
    smooth_scale : bool
        Whether a smooth scale space should be used (default) or the scale
        is reduced with a factor of two each scale_sampling iterations.

    """

    _pyramids: Incomplete
    _buffer: Incomplete
    _current_interp_order: int
    def __init__(self, *ims) -> None: ...
    def _defaultParams(self):
        """Overload to create all default params."""
    def _set_delta_deform(self, i, deform) -> None:
        """_set_delta_deform(i, deform)

        Append the given delta deform for image i. It is combined with the
        current deformation for that image.

        """
    def get_deformed_image(self, i, s: int = 0):
        """get_deformed_image(i, s=0)

        Get the image i at scale s, deformed with its current deform.
        Mainly intended for the registration algorithms, but can be of interest
        during development/debugging.

        """
    def _set_buffered_data(self, key1, key2, data) -> None:
        """_set_buffered_data(key1, key2, data)

        Buffer the given data. key1 is where the data is stored under.
        key2 is a check. The most likely use case is using the image
        number as key1 and the scale as key2.

        Intended for the registration algorithm subclasses.

        """
    def _get_buffered_data(self, key1, key2):
        """_get_buffered_data(key1, key2)

        Retrieve buffered data.

        """
    _max_scale: Incomplete
    def _register(self, verbose: int = 1, fig: Incomplete | None = None) -> None: ...
    def _register_iteration(self, iterInfo) -> None:
        """_register_iteration(iterInfo)

        Apply one iteration of the registration algorithm at
        the specified scale (iterInfo[2]).

        """
    def _deform_for_image(self, i, iterInfo) -> None:
        """_deform_for_image(i, iterInfo)

        Calculate the deform for the given image index.

        """

class GDGRegistration(BaseRegistration):
    """GDGRegistration(*images)

    Inherits from :class:`pirt.BaseRegistration`.

    Generic Groupwise Diffeomorphic Registration. Abstract class that
    provides a generic way to perform diffeomorphic groupwise registration.

    Parameters
    ----------
    deform_wise : {\'groupwise\', \'pairwise\'}
        Whether all images are deformed simultaneously, or only the
        first image is deformed. When registering more than 2 images,
        \'groupwise\' registration should be used. Default \'groupwise\'.
    injective : bool
        Whether the injectivity constraint should be used. This value should
        only be set to False in specific (testing?) situation; the resulting
        deformations are only guaranteed to be diffeomorphic if injective=True.
    frozenEdge : bool
        Whether the deformation is set to zero at the edges. If True (default)
        the resulting deformation fields are *fully* diffeomorphic; no pixels
        are mapped from the inside to the outside nor vice versa.

    final_grid_sampling : scalar
        The grid sampling of the grid at the final level. During the
        registration process, the B-spine grid sampling scales along
        with the scale.
    grid_sampling_factor : scalar between 0 and 1
        To what extent the grid sampling scales with the scale. By making
        this value lower than 1, the grid is relatively fine at the the
        higher scales, allowing for more deformations. The default is 0.5.
        Note that setting this value to 1 when using \'frozenedge\' can cause
        the image to be \'stuck\' at higher scales.
    deform_limit : scalar
        If injective is True, the deformations at each iteration are
        constraint by a "magic" limit. By making this limit tighter
        (relative to the scale), the deformations stay in reasonable bounds.
        This feature helps a lot for convergence. Default value is 1.
    """
    def _defaultParams(self):
        """Overload to create all default params."""
    def _get_grid_sampling_old(self, scale): ...
    def _get_grid_sampling(self, scale): ...
    def _get_grid_sampling_full(self, scale): ...
    def _regularize_diffeomorphic(self, scale, deform, weight: Incomplete | None = None):
        """_regularize_diffeomorphic(scale, deform, weight=None)

        Regularize the given DeformationField in a way that makes it
        diffeomorphic. Returns the result as a DeformationGrid.

        """
    def _deform_for_image(self, i, iterInfo):
        """_deform_for_image(i, iterInfo)

        Calculate the deform for the given image index.

        """
    def _deform_for_image_groupwise(self, i, iterInfo):
        """_deform_for_image_groupwise(i, iterInfo)

        Calculate the deform for the given image index. For each image,
        the deform between that image and all other images is
        calculated. The total deform is the average of these deforms.

        """
    def _deform_for_image_pairwise1(self, i, iterInfo):
        """_deform_for_image_pairwise1(i, iterInfo)

        Get the deform for the image only if i is 0; the source image.
        This is what's classic registration does.

        """
    def _deform_for_image_pairwise2(self, i, iterInfo):
        """_deform_for_image_pairwise2(i, iterInfo)

        Get the deform for the image only if i is 1.

        """
