from _typeshed import Incomplete

from .. import interp as interp
from ._subs import (
    DeformationIdentity as DeformationIdentity,
    DeformationGridForward as DeformationGridForward,
    DeformationGridBackward as DeformationGridBackward,
)
from .._utils import Aarray as Aarray
from ..splinegrid import (
    FD as FD,
    GridInterface as GridInterface,
    calculate_multiscale_sampling as calculate_multiscale_sampling,
)
from ._deformbase import Deformation as Deformation

class DeformationField(Deformation):
    """DeformationField(*fields)

    A deformation field represents a deformation using an array for
    each dimension, thus specifying the deformation at each pixel/voxel.
    The fields should be in z-y-x order. The deformation is represented
    in world units (not pixels, unless pixel units are used).

    Can be initialized with:
      * DeformationField(field_z, field_y, field_x)
      * DeformationField(image) # Null deformation
      * DeformationField(3) # Null deformation specifying only the ndims

    This class has functionality to reshape the fields. This can be usefull
    during registration if using a scale space pyramid.

    """

    _field_shape: Incomplete
    _field_sampling: Incomplete
    _fields: Incomplete
    def __init__(self, *fields) -> None: ...
    def __repr__(self) -> str: ...
    def resize_field(self, new_shape):
        """resize_field(new_shape)

        Create a new DeformationField instance, where the underlying field is
        resized.

        The parameter new_shape can be anything that can be converted
        to a FieldDescription instance.

        If the field is already of the correct size, returns self.

        """
    def _sampling_equal(self, fd1, fd2): ...
    def _resize_field(self, fd):
        """_resize_field(fd)

        Create a new DeformationField instance, where the underlying field is
        reshaped. Requires a FieldDescription instance.

        """
    def __len__(self) -> int: ...
    def __getitem__(self, item): ...
    def __iter__(self): ...
    def _check_fields_same_shape(self, fields):
        """_check_fields_same_shape(shape)

        Check whether the given fields all have the same shape.

        """
    def _check_which_shape_is_larger(self, shape):
        """_check_which_shape_is_larger(self, shape)

        Test if shapes are equal, smaller, or larger:
          *  0: shapes are equal;
          *  1: the shape of this deformation field is larger
          * -1: the given shape is larger

        """
    @classmethod
    def from_field_multiscale(
        cls,
        field,
        sampling,
        weights: Incomplete | None = None,
        injective: bool = True,
        frozenedge: bool = True,
        fd: Incomplete | None = None,
    ):
        """from_field_multiscale(field, sampling, weights=None,
                                  injective=True, frozenedge=True, fd=None)

        Create a DeformationGrid from the given deformation field
        (z-y-x order).

        Uses B-spline grids in a multi-scale approach to regularize the
        sparse known deformation. This produces a smooth field (minimal
        bending energy), similar to thin plate splines.

        The optional weights array can be used to individually weight the
        field elements. Where the weight is zero, the values are not
        evaluated. The speed can therefore be significantly improved if
        there are relatively few nonzero elements.

        Parameters
        ----------
        field : list of numpy arrays
            These arrays describe the deformation field (one per dimension).
        sampling : scalar
            The smallest sampling of the B-spline grid that is used to create
            the field.
        weights : numpy array
            This array can be used to weigh the contributions of the
            individual elements.
        injective : bool or number
            Whether to prevent the grid from folding. An injective B-spline
            grid is diffeomorphic. When a number between 0 and 1 is given,
            the unfold constraint can be tightened to obtain smoother
            deformations.
        frozenedge : bool
            Whether the edges should be frozen. This can help the registration
            process. Also, when used in conjunction with injective, a truly
            diffeomorphic deformation is obtained: every input pixel maps
            to a point within the image boundaries.
        fd : field
            Field description to describe the shape and sampling of the
            underlying field to be deformed.

        Notes
        -----
        The algorithmic is based on:
        Lee S, Wolberg G, Chwa K-yong, Shin SY. "Image Metamorphosis with
        Scattered Feature Constraints". IEEE TRANSACTIONS ON VISUALIZATION
        AND COMPUTER GRAPHICS. 1996;2:337--354.

        The injective constraint desctribed in this paper is not applied
        by this method, but by the DeformationGrid, since it is method
        specifically for deformations.

        """
    @classmethod
    def from_points_multiscale(cls, image, sampling, pp1, pp2, injective: bool = True, frozenedge: bool = True):
        """from_points_multiscale(image, sampling, pp1, pp2,
                                   injective=True, frozenedge=True)

        Obtains the deformation field described by the two given sets
        of corresponding points. The deformation describes moving the
        points pp1 to points pp2. Note that backwards interpolation is
        used, so technically, the image is re-interpolated by sampling
        at the points in pp2 from pixels specified by the points in pp1.

        Uses B-spline grids in a multi-scale approach to regularize the
        sparse known deformation. This produces a smooth field (minimal
        bending energy), similar to thin plate splines.

        Parameters
        ----------
        image : numpy array or shape
            The image (of any dimension) to which the deformation applies.
        sampling : scalar
            The sampling of the smallest grid to describe the deform.
        pp1 : PointSet, 2D ndarray
            The base points.
        pp2 : PointSet, 2D ndarray
            The target points.
        injective : bool or number
            Whether to prevent the grid from folding. An injective B-spline
            grid is diffeomorphic. When a number between 0 and 1 is given,
            the unfold constraint can be tightened to obtain smoother
            deformations.
        frozenedge : bool
            Whether the edges should be frozen. This can help the registration
            process. Also, when used in conjunction with injective, a truly
            diffeomorphic deformation is obtained: every input pixel maps
            to a point within the image boundaries.

        Notes
        -----
        The algorithmic is based on:
        Lee S, Wolberg G, Chwa K-yong, Shin SY. "Image Metamorphosis with
        Scattered Feature Constraints". IEEE TRANSACTIONS ON VISUALIZATION
        AND COMPUTER GRAPHICS. 1996;2:337--354.

        The injective constraint desctribed in this paper is not applied
        by this method, but by the DeformationGrid, since it is method
        specifically for deformations.

        """
    @classmethod
    def _multiscale(cls, setResidu, getResidu, field, sampling):
        """_multiscale(setResidu, getResidu, field, sampling)

        Method for generating a deformation field using a multiscale
        B-spline grid approach. from_field_multiscale()
        and from_points_multiscale() use this classmethod by each supplying
        appropriate setResidu and getResidu functions.

        """
    def test_jacobian(self, show: bool = True):
        """test_jacobian(show=True)

        Test the determinand of the field's Jacobian. It should be all
        positive for the field to be diffeomorphic.

        Returns the number of pixels where the Jacobian <= 0. If show==True,
        will show a figure with these pixels indicated.

        """
