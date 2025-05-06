from _typeshed import Incomplete

from .. import interp as interp
from .._utils import (
    Aarray as Aarray,
    PointSet as PointSet,
)
from ..splinegrid import (
    SplineGrid as SplineGrid,
    GridContainer as GridContainer,
    GridInterface as GridInterface,
    calculate_multiscale_sampling as calculate_multiscale_sampling,
)
from ._deformbase import Deformation as Deformation
from ._deformfield import DeformationField as DeformationField

class DeformationGrid(Deformation, GridContainer):
    """DeformationGrid(image, sampling=5)

    A deformation grid represents a deformation using a spline grid.

    The 'grids' property returns a tuple of SplineGrid instances (one for
    each dimension). These sub-grids can also obtained by indexing and
    are in z,y,x order.

    Parameters
    ----------
    image : shape-tuple, numpy-array, Aarray, or FieldDescription
        A description of the field that this grid applies to.
        The image itself is not stored, only the field's shape and
        sampling are of interest.
    sampling : number
        The spacing of the knots in the field. (For anisotropic fields,
        the spacing is expressed in world units.)

    Usage
    -----
    After normal instantiation, the grid describes a field with all zeros.
    Use the From* classmethods to obtain a grid which represents the given
    values.

    Limitations
    -----------
    The grid can in principle be of arbitrary dimension, but this
    implementation currently only supports 1D, 2D and 3D.

    """
    def __init__(self, *args, **kwargs) -> None: ...
    def show(self, axes: Incomplete | None = None, axesAdjust: bool = True, showGrid: bool = True):
        """show(axes=None, axesAdjust=True, showGrid=True)

        For 2D grids, illustrates the deformation and the knots of the grid.
        A grid image is made that is deformed and displayed in the given
        (or current) axes. By default the positions of the underlying knots
        are also shown using markers.
        Returns the texture object of the grid image.

        Requires visvis.

        """
    @classmethod
    def from_field(
        cls,
        field,
        sampling,
        weights: Incomplete | None = None,
        injective: bool = True,
        frozenedge: bool = True,
        fd: Incomplete | None = None,
    ):
        """from_field(field, sampling, weights=None, injective=True,
                       frozenedge=True, fd=None)

        Create a DeformationGrid from the given deformation field
        (z-y-x order). Also see from_field_multiscale()

        The optional weights array can be used to individually weight the
        field elements. Where the weight is zero, the values are not
        evaluated. The speed can therefore be significantly improved if
        there are relatively few nonzero elements.

        Parameters
        ----------
        field : list of numpy arrays
            These arrays describe the deformation field (one per dimension).
        sampling : scalar
            The sampling of the returned grid
        weights : numpy array
            This array can be used to weigh the contributions of the
            individual elements.
        injective : bool
            Whether to prevent the grid from folding. This also penetalizes
            large relative deformations. An injective B-spline grid is
            diffeomorphic.
        frozenedge : bool
            Whether the edges should be frozen. This can help the registration
            process. Also, when used in conjunction with injective, a truly
            diffeomorphic deformation is obtained: every input pixel maps
            to a point within the image boundaries.
        fd : field
            Field description to describe the shape and sampling of the
            underlying field to be deformed.
        """
    @classmethod
    def from_field_multiscale(cls, field, sampling, weights: Incomplete | None = None, fd: Incomplete | None = None):
        """from_field_multiscale(field, sampling, weights=None, fd=None)

        Create a DeformationGrid from the given deformation field
        (z-y-x order). Applies from_field_multiscale() for each
        of its subgrids.

        Important notice
        ----------------
        Note that this is not the best way to make a deformation, as it does
        not take aspects specific to deformations into account, such as
        injectivity, and uses addition to combine the sub-deformations instead
        of composition.

        See DeformationField.from_points_multiscale() for a sound alternative.

        Parameters
        ----------
        field : list of numpy arrays
            These arrays describe the deformation field (one per dimension).
        sampling : scalar
            The sampling of the returned grid
        weights : numpy array
            This array can be used to weigh the contributions of the
            individual elements.
        fd : field
            Field description to describe the shape and sampling of the
            underlying field to be deformed.
        """
    @classmethod
    def from_points(cls, image, sampling, pp1, pp2, injective: bool = True, frozenedge: bool = True):
        """from_points(image, sampling, pp1, pp2,
                        injective=True, frozenedge=True)

        Obtains the deformation field described by the two given sets
        of corresponding points. The deformation describes moving the
        points pp1 to points pp2. Note that backwards interpolation is
        used, so technically, the image is re-interpolated by sampling
        at the points in pp2 from pixels specified by the points in pp1.

        Parameters
        ----------
        image : numpy array or shape
            The image (of any dimension) to which the deformation applies.
        sampling : scalar
            The sampling of the returned grid.
        pp1 : PointSet, 2D ndarray
            The base points.
        pp2 : PointSet, 2D ndarray
            The target points.
        injective : bool
            Whether to prevent the grid from folding. This also penetalizes
            large relative deformations. An injective B-spline grid is
            diffeomorphic.
        frozenedge : bool
            Whether the edges should be frozen. This can help the registration
            process. Also, when used in conjunction with injective, a truly
            diffeomorphic deformation is obtained: every input pixel maps
            to a point within the image boundaries.

        """
    @classmethod
    def from_points_multiscale(cls, image, sampling, pp1, pp2):
        """from_points_multiscale(image, sampling, pp1, pp2)

        Obtains the deformation field described by the two given sets
        of corresponding points. The deformation describes moving the
        points pp1 to points pp2. Applies from_points_multiscale() for each
        of its subgrids.

        See DeformationField.from_points_multiscale() for a sound alternative.

        Important notice
        ----------------
        Note that this is not the best way to make a deformation, as it does
        not take aspects specific to deformations into account, such as
        injectivity, and uses addition to combine the sub-deformations instead
        of composition.

        Parameters
        ----------
        image : numpy array or shape
            The image (of any dimension) to which the deformation applies.
        sampling : scalar
            The sampling of the returned grid.
        pp1 : PointSet, 2D ndarray
            The base points.
        pp2 : PointSet, 2D ndarray
            The target points.

        """
    def _set_using_field(
        self, deforms, weights: Incomplete | None = None, injective: bool = True, frozenedge: bool = True
    ) -> None:
        """_set_using_field(deforms, weights=None, injective=True, frozenedge=True)

        Sets the deformation by specifying deformation fields for
        each dimension (z-y-x order). Optionally, an array with
        weights can be given to weight each deformation unit.

        """
    def _set_using_points(self, pp, dd, injective: bool = True, frozenedge: bool = True) -> None:
        """_set_using_points(pp, dd, injective=True, frozenedge=True)

        Deform the lattices according to points pp with the deformations
        defined in dd.

        pp is the position to apply the deformation, dd is the relative
        position to sample the pixels from.

        By default performs folding and shearing prevention to obtain
        a grid that is injective (i.e. can be inverted).

        """
    def _unfold(self, factor) -> None:
        """_unfold(factor)

        Prevent folds in the grid, by putting a limit to the values
        that the knots may have.

        The factor determines how smooth the deformation should be. Zero
        is no deformation, 1 is *just* no folding. Better use a value of
        0.9 at the highest, to account for numerical errors.

        Based on:
        Choi, Yongchoel, and Seungyong Lee. 2000. "Injectivity conditions of
        2d and 3d uniform cubic b-spline functions". GRAPHICAL MODELS 62: 2000.

        But we apply a smooth mapping rather than simply truncating the values.
        Give a negative factor to use the truncated method

        """
    def _freeze_edges(self):
        """_freeze_edges()

        Freeze the outer knots of the grid such that the deformation is
        zero at the edges of the image.

        This sets three rows of knots to zero at the top/left of the
        grid, and four rows at the bottom/right. This is because at the
        left there is one knot extending beyond the image, while at the
        right there are two.

        """
