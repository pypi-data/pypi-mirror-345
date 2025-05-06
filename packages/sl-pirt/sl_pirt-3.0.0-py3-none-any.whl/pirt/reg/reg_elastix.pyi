from _typeshed import Incomplete

from .._utils import Parameters as Parameters
from ..deform import DeformationFieldBackward as DeformationFieldBackward
from .reg_base import AbstractRegistration as AbstractRegistration

NEED_ELASTIX: str

class ElastixRegistration(AbstractRegistration):
    """ElastixRegistration(im1, im2)

    Inherits from :class:`pirt.AbstractRegistration`.

    Registration class for registration using the Elastix toolkit.
    [http://elastix.isi.uu.nl/]

    This class performs a bspline transformation by default. See also
    the convenience subclasses.

    The params property this class returns a struct with a few common
    Elastix parameters. the params2 property contains another set of
    more advanced parameters. Note that any parameter known to elastix
    can be added to the parameter structures, which enables tuning the
    registration in great detail. Also note that two parameter structs
    can be combined by adding them.

    Because the parameters directly represent the parameters for the
    Elastix toolkit, their names do not follow the style of most
    other registration objects in this package. Here we lists some of the
    common parameters, for more details we refer to the elastix manual.

    Parameters
    ----------
    FinalGridSpacingInPhysicalUnits : int
        When using the BSplineTransform, the final spacing of the grid.
        This controls the smoothness of the final deformation.
    NumberOfResolutions : int
        Most registration algorithms adopt a multiresolution approach
        to direct the solution towards a global optimum and to speed
        up the process. This parameter specifies the number of scales
        to apply the registration at. (default 4)
    MaximumNumberOfIterations  : int
        Maximum number of iterations in each resolution level.
        200-2000 works usually fine for nonrigid registration.
        The more, the better, but the longer computation time.
        This is an important parameter! (default 500)

    """

    transformation_type: str
    _params2: Incomplete
    def __init__(self, *args) -> None: ...
    def _defaultParams(self):
        """Overload to create all default params."""
    @property
    def params2(self): ...
    _deformed_image: Incomplete
    def _register(self, verbose: int = 1, fig: Incomplete | None = None) -> None: ...
    def get_elastix_deformed_image(self):
        """get_elastix_deformed_image()

        Get the deformed input image found as Elastix created it. This
        should be the same (except for small interpolation errors) to
        the image obtained using reg.get_deformed_image(0).

        """

class ElastixRegistration_affine(ElastixRegistration):
    """

    Registration class for registration using the Elastix toolkit.
    [http://elastix.isi.uu.nl/]

    This class performs an affine transformation by default. See
    :class:`pirt.ElastixRegistration` for more details.

    Parameters
    ----------
    AutomaticScalesEstimation : bool
        When using a rigid or affine transform. Scales the affine matrix
        elements compared to the translations, to make sure they are in
        the same range. In general, it's best to use automatic scales
        estimation.
    AutomaticTransformInitialization : bool
        When using a rigid or affine transform. Automatically guess an
        initial translation by aligning the geometric centers of the
        fixed and moving.
    NumberOfResolutions : int
        Most registration algorithms adopt a multiresolution approach
        to direct the solution towards a global optimum and to speed
        up the process. This parameter specifies the number of scales
        to apply the registration at. (default 4)
    MaximumNumberOfIterations  : int
        Maximum number of iterations in each resolution level.
        200-2000 works usually fine for nonrigid registration.
        The more, the better, but the longer computation time.
        This is an important parameter! (default 500)

    """

    transformation_type: str

class ElastixRegistration_rigid(ElastixRegistration):
    """

    Registration class for registration using the Elastix toolkit.
    [http://elastix.isi.uu.nl/]

    This class performs a rigid transformation by default. See
    :class:`pirt.ElastixRegistration` for more details.

    Parameters
    ----------
    AutomaticScalesEstimation : bool
        When using a rigid or affine transform. Scales the affine matrix
        elements compared to the translations, to make sure they are in
        the same range. In general, it's best to use automatic scales
        estimation.
    AutomaticTransformInitialization : bool
        When using a rigid or affine transform. Automatically guess an
        initial translation by aligning the geometric centers of the
        fixed and moving.
    NumberOfResolutions : int
        Most registration algorithms adopt a multiresolution approach
        to direct the solution towards a global optimum and to speed
        up the process. This parameter specifies the number of scales
        to apply the registration at. (default 4)
    MaximumNumberOfIterations  : int
        Maximum number of iterations in each resolution level.
        200-2000 works usually fine for nonrigid registration.
        The more, the better, but the longer computation time.
        This is an important parameter! (default 500)

    """

    transformation_type: str

class ElastixGroupwiseRegistration(ElastixRegistration):
    """ElastixGroupwiseRegistration(*images)

    Inherits from :class:`pirt.ElastixRegistration`.

    Registration class for registration using the Elastix toolkit.
    [http://elastix.isi.uu.nl/]

    This variant uses the groupwise registration approach as proposed
    by Metz et al. "Nonrigid registration of dynamic medical imaging data
    using nD+t B-splines and a groupwise optimization approach"

    The params property this class returns a struct with a few common
    Elastix parameters. the params2 property contains another set of
    more advanced parameters. Note that any parameter known to elastix
    can be added to the parameter structures, which enables tuning the
    registration in great detail. Also note that two parameter structs
    can be combined by adding them.

    Because the parameters directly represent the parameters for the
    Elastix toolkit, their names do not follow the style of most
    other registration objects in this package.

    Parameters
    ----------
    FinalGridSpacingInPhysicalUnits : int
        When using the BSplineTransform, the final spacing of the grid.
        This controls the smoothness of the final deformation.
    NumberOfResolutions : int
        Most registration algorithms adopt a multiresolution approach
        to direct the solution towards a global optimum and to speed
        up the process. This parameter specifies the number of scales
        to apply the registration at. (default 4)
    MaximumNumberOfIterations  : int
        Maximum number of iterations in each resolution level.
        200-2000 works usually fine for nonrigid registration.
        The more, the better, but the longer computation time.
        This is an important parameter! (default 500)

    """
