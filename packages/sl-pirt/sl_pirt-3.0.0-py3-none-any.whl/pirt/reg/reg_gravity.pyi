from _typeshed import Incomplete

from .._utils import Aarray as Aarray
from .reg_base import (
    GDGRegistration as GDGRegistration,
    create_grid_image as create_grid_image,
)
from ..gaussfun import diffuse2 as diffuse2

def near_root3(arr) -> None:
    """near_root3(n)
    Calculates an approximation of the square root using
    (a few) Newton iterations.
    """

def near_exp3(arr) -> None:
    """near_exp3(n)
    Calculates an approximation of the exp.
    """

class GravityRegistration(GDGRegistration):
    """GravityRegistration(*images)

    Inherits from :class:`pirt.GDGRegistration`

    A registration algorithm based on attraction between masses in both
    images, which is robust for large differences between the images.

    The most important parameters to tune the algorithm with are
    scale_sampling, speed_factor and final_grid_sampling.

    The ``speed_factor`` and ``mass_transforms`` parameters are specific to
    this algorithm. Other important parameters are also listed below.

    Parameters
    ----------
    speed_factor : scalar
        The relative force of the transform. This one of the most important
        parameters to tune. Typical values are between 1 and 5. Default 0.1.
    mass_transforms : int or tuple of ints
        How the image is transformed to obtain the mass image. The number
        refers to the order of differentiation; 1 and 2 are gradient magnitude
        and Laplacian respectively. 0 only performs normalization to subtract
        the background. Can be specified for all images or for each image
        individually. Default 1.
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
        two in scale). For the coarse implementation, this is the amount of
        iterations performed before moving to the next scale (which is always
        a factor of two smaller). Values between 10 and 20 are reasonable in
        most situations. Default 20. Higher values yield better results in
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
    def _get_derivative(self, im, d, o: int = 1, edgeMode: str = "constant"):
        """_get_derivative(im, d, o=1)

        Calculate the derivative (of order o) of the given image
        in the given dimension.

        """
    def _create_mass(self, image_id, im, scale):
        """_create_mass(image_id, im, scale)

        Get the unnormalized mass image for the given image (which has
        the given image_id).

        This method can be overloaded to create the mass image in a
        custom way.

        """
    def _normalize_mass(self, mass):
        """_normalize_mass(mass)

        Normalize the mass image. This method can be overloaded to implement
        custom normalization. This normalization should preferably be
        such that repeated calls won't change the result.

        """
    def _get_mass_and_gradient(self, image_id, iterInfo):
        """_get_mass_and_gradient(image_id, scale)

        Get the mass and the gradient for the given image id.
        Returns a tuple (mass, (gradz, grady, gradx))

        """
    def _soft_limit1(self, data, limit) -> None: ...
    def _soft_limit2(self, data, limit) -> None: ...
    def _visualize(self, mass1: Incomplete | None = None, mass2: Incomplete | None = None, gridStep: int = 10) -> None:
        """_visualize(self,  mass1=None, mass2=None)

        Visualize the registration process.

        """
    def _deform_from_image_pair(self, i, j, iterInfo):
        """_deform_from_image_pair(i, j, iterInfo)

        Calculate the deform for image i to image j.

        """
