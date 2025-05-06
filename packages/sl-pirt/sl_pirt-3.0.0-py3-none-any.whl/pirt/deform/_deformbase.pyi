from _typeshed import Incomplete

from .. import interp as interp
from ._subs import (
    DeformationIdentity as DeformationIdentity,
    DeformationGridForward as DeformationGridForward,
    DeformationFieldForward as DeformationFieldForward,
    DeformationGridBackward as DeformationGridBackward,
    DeformationFieldBackward as DeformationFieldBackward,
)
from .._utils import Aarray as Aarray
from ..splinegrid import FD as FD
from ._deformgrid import DeformationGrid as DeformationGrid
from ._deformfield import DeformationField as DeformationField

class Deformation:
    """Deformation

    This class is an abstract base class for deformation grids and
    deformation fields.

    A deformation maps one image (1D, 2D or 3D) to another. A deformation
    can be represented using a B-spline grid, or using a field (i.e. array).
    A deformation is either forward mapping or backward mapping.

    """

    _forward_mapping: Incomplete
    @property
    def forward_mapping(self):
        """Returns True if this deformation is forward mapping."""
    @property
    def is_identity(self):
        """Returns True if this is an identity deform, or null deform;
        representing no deformation at all.
        """
    @property
    def ndim(self):
        """The number of dimensions of the deformation."""
    @property
    def field_shape(self):
        """The shape of the deformation field."""
    @property
    def field_sampling(self):
        """For each dim, the sampling (distance between pixels/voxels)
        of the field (all 1's if isotropic).
        """
    def __add__(self, other): ...
    def __mul__(self, other): ...
    def copy(self):
        """copy()

        Copy this deformation instance (deep copy).

        """
    def scale(self, factor):
        """scale(factor)

        Scale the deformation (in-place) with the given factor. Note that the result
        is diffeomorphic only if the original is diffeomorphic and the
        factor is between -1 and 1.

        """
    def add(def1, def2):
        """add(other)

        Combine two deformations by addition.

        Returns a DeformationGrid instance if both deforms are grids.
        Otherwise returns deformation field. The mapping (forward/backward)
        is taken from the left deformation.

        Notes
        -----
        Note that the resulting deformation is not necesarily diffeomorphic
        even if the individual deformations are.

        Although diffeomorphisms can in general not be averaged, the
        constraint of Choi used in this framework enables us to do so
        (add the individual deformations and scale with 1/n).

        This function can also be invoked using the plus operator.

        """
    def compose(def1, def2):
        """compose(other):

        Combine two deformations by composition. The left is the "static"
        deformation, and the right is the "delta" deformation.

        Always returns a DeformationField instance. The mapping
        (forward/backward) of the result is taken from the left deformation.

        Notes
        -----
        Let "h = f.compose(g)" and "o" the mathematical composition operator.
        Then mathematically "h(x) = g(f(x))" or "h = g o f".

        Practically, new deformation vectors are created by sampling in one
        deformation, at the locations specified by the vectors of the other.

        For forward mapping we sample in g at the locations of f. For backward
        mapping we sample in f at the locations of g.

        Since we cannot impose the field values for a B-spline grid without
        resorting to some multi-scale approach (which would use composition
        and is therefore infinitely recursive), the result is always a
        deformation field.

        If the deformation to sample in (f for forward mapping, g for backward)
        is a B-spline grid, the composition does not introduce any errors;
        sampling in a field introduces interpolation errors. Since the static
        deformation f is often a DeformationField, forward mapping is preferred
        with regard to the accuracy of composition.

        """
    def _compose_forward(def1, def2): ...
    def _compose_backward(def1, def2): ...
    def get_deformation_locations(self):
        """get_deformation_locations()

        Get a tuple of arrays (x,y,z order) that represent sample locations
        to apply the deformation. The locations are absolute and expressed
        in pixel coordinates. As such, they can be fed directly to interp()
        or project().

        """
    def get_field(self, d):
        """get_field(d)

        Get the field corresponding to the given dimension.

        """
    def get_field_in_points(self, pp, d, interpolation: int = 1):
        """get_field_in_points(pp, d, interpolation=1)

        Obtain the field for dimension d in the specied points.
        The interpolation value is used only if this is a deformation
        field.

        The points pp should be a point set (x-y-z order).

        """
    def apply_deformation(self, data, interpolation: int = 3):
        """apply_deformation(data, interpolation=3)

        Apply the deformation to the given data. Returns the deformed data.

        Parameters
        ----------
        data : numpy array
            The data to deform
        interpolation : {0,1,3}
            The interpolation order (if backward mapping is used).

        """
    def show(self, axes: Incomplete | None = None, axesAdjust: bool = True):
        """show(axes=None, axesAdjust=True)

        Illustrates 2D deformations.

        It does so by creating an image of a grid and deforming it.
        The image is displayed in the given (or current) axes.
        Returns the texture object of the grid image.

        Requires visvis.

        """
    def inverse(self):
        """inverse()

        Get the inverse deformation. This is only valid if the
        current deformation is diffeomorphic. The result is always
        a DeformationField instance.

        """
    def as_deformation_field(self):
        """as_deformation_field()

        Obtain a deformation fields instance that represents the same
        deformation. If this is already a deformation field, returns self.

        """
    def as_other(self, other):
        """as_other(other)

        Returns the deformation as a forward or backward mapping,
        so it matches the other deformations.

        """
    def as_forward(self):
        """as_forward()

        Returns the same deformation as a forward mapping. Returns
        the original if already in forward mapping.

        """
    def as_forward_inverse(self):
        """as_forward_inverse()

        Returns the inverse deformation as a forward mapping. Returns
        the inverse of the original if already in forward mapping. If
        in backward mapping, the data is the same, but wrapped in a
        Deformation{Field/Grid}Backward instance.

        Note: backward and forward mappings with the same data are
        each-others reverse.

        """
    def as_backward(self):
        """as_backward()

        Returns the same deformation as a backward mapping. Returns
        the original if already in backward mapping.

        """
    def as_backward_inverse(self):
        """as_forward_inverse()

        Returns the inverse deformation as a forward mapping. Returns
        the inverse of the original if already in forward mapping. If
        in backward mapping, the data is the same, but wrapped in a
        DeformationFieldBackward instance.

        Note: backward and forward mappings with the same data are
        each-others reverse.

        """
