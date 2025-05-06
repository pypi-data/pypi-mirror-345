from .._utils import Aarray as Aarray
from .reg_base import (
    GDGRegistration as GDGRegistration,
    BaseRegistration as BaseRegistration,
    create_grid_image as create_grid_image,
)
from ..gaussfun import diffuse2 as diffuse2

class BaseDemonsRegistration:
    """BaseDemonsRegistration

    Abstract class that implements the base functionality of the
    Demons algorithm.

    """
    def _get_derivative(self, im, d, o: int = 1, edgeMode: str = "constant"):
        """_get_derivative(im, d, o=1)

        Calculate the derivative (of order o) of the given image
        in the given dimension.

        """
    def _get_image_and_gradient(self, image_id, iterInfo):
        """_get_image_and_gradient(image_id, iterInfo)

        Get the image and the gradient for the given image id.
        Returns a tuple (mass, (gradz, grady, gradx))

        """
    def _visualize(self, gridStep: int = 10) -> None:
        """_visualize(self)

        Visualize the registration process.

        """
    def _deform_from_image_pair(self, i, j, iterInfo):
        """_deform_from_image_pair(i, j, iterInfo)

        Calculate the deform for image i to image j.

        """

class OriginalDemonsRegistration(BaseRegistration, BaseDemonsRegistration):
    """OriginalDemonsRegistration(*images)

    Inherits from :class:`pirt.BaseRegistration`.

    The original version of the Demons algorithm. Uses Gaussian diffusion
    to regularize the deformation field. This is the implementation as
    proposed by He Wang et al. in 2005 "Validation of an accelerated \'demons\'
    algorithm for deformable image registration in radiation therapy"

    See also :class:`pirt.DiffeomorphicDemonsRegistration`.

    The ``speed_factor`` and ``noise_factor`` parameters are specific to this
    algorithm. Other important parameters are also listed below.

    Parameters
    ----------
    speed_factor : scalar
        The relative force of the transform. This one of the most important
        parameters to tune. Default 3.0.
    noise_factor : scalar
        The noise factor. Default 2.5.
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
        two in scale). Values between 20 and 30 are reasonable in
        most situations. Default 30. Higher values yield better results in
        general. The speed of the algorithm scales linearly with this value.

    """
    def _defaultParams(self):
        """Overload to create all default params."""
    def _deform_for_image(self, i, iterInfo): ...

class DiffeomorphicDemonsRegistration(GDGRegistration, BaseDemonsRegistration):
    """DiffeomorphicDemonsRegistration(*images)

    Inherits from :class:`pirt.GDGRegistration`.

    A variant of the Demons algorithm that is diffeomorphic. Based on the
    generice diffeomorphic groupwise registration (GDGRegistration) method .

    See also :class:`pirt.OriginalDemonsRegistration`.

    The ``speed_factor`` parameter is specific to this algorithm. The
    ``noise_factor`` works best set at 1.0, effectively disabling
    its use; it is made redundant by the B-spline based regularization.
    Other important parameters are also listed below.

    Parameters
    ----------
    speed_factor : scalar
        The relative force of the transform. This one of the most important
        parameters to tune. Default 3.0.
    mapping : {'forward', 'backward'}
        Whether forward or backward mapping is used. Default forward.
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
        two in scale). Values between 20 and 30 are reasonable in
        most situations. Default 25. Higher values yield better results in
        general. The speed of the algorithm scales linearly with this value.
    final_grid_sampling : scalar
        The grid sampling of the grid at the final level. During the
        registration process, the B-spine grid sampling scales along
        with the scale. This parameter is usually best coupled to final_scale.
        (When increasing final scale, this value should often be increased
        accordingly.)
    grid_sampling_factor : scalar between 0 and 1
        To what extent the grid sampling scales with the scale. By making
        this value lower than 1, the grid is relatively fine at the the
        higher scales, allowing for more deformations. The default is 0.5.
        Note that setting this value to 1 when using 'frozenedge' can cause
        the image to be 'stuck' at higher scales.

    """
    def _defaultParams(self):
        """Overload to create all default params."""
