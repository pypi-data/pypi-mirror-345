from _typeshed import Incomplete

from . import _splinegridfuncs as _splinegridfuncs
from .._utils import (
    Aarray as Aarray,
    PointSet as PointSet,
)

class FieldDescription:
    """FieldDescription(*args)

    Describes the dimensions of a field (i.e. Aarray). It stores
    the following properties: shape, sampling, origin

    This class can for example be used to instantiate a new grid
    without requiring the actual field.

    This class can be instantiated with a shape and sampling tuple, or with
    any object that describes a field in a way that we know of
    (e.g. SplineGrid and DeformationField instances).

    Examples
    --------
      * FieldDescription(shape, sampling=None, origin=None)
      * FieldDescription(grid)
      * FieldDescription(Aarray)
      * FieldDescription(np.ndarray) # assumes unit sampling and zero origin

    """

    _defined_samping: bool
    _defined_origin: bool
    _shape: Incomplete
    _sampling: Incomplete
    _origin: Incomplete
    def __init__(self, shape, sampling: Incomplete | None = None, origin: Incomplete | None = None) -> None: ...
    @property
    def ndim(self):
        """The number of dimensions of the field."""
    @property
    def shape(self):
        """The shape of the field."""
    @property
    def sampling(self):
        """The sampling between the pixels of the field."""
    @property
    def origin(self):
        """The origin (spatial offset) of the field."""
    @property
    def defined_sampling(self):
        """Whether the sampling was explicitly defined."""
    @property
    def defined_origin(self):
        """Whether the origin was explicitly defined."""

FD = FieldDescription

def calculate_multiscale_sampling(grid, sampling):
    """calculate_multiscale_sampling(grid, sampling)
    Calculate the minimal and maximal sampling from user input.
    """

class GridInterface:
    """GridInterface(field, sampling=5)

    Abstract class to define the interface of a spline grid.
    Implemented by the Grid and GridContainer classes.

    This class provides some generic methods and properties for grids
    in general. Most importantly, it handles initialization of the
    desctiption of the grid (dimensionality, shape and sampling of the
    underlying field, and the shape and sampling of the grid itself).

    Parameters
    ----------
    field : shape-tuple, numpy-array, Aarray, or FieldDescription
        A description of the field that this grid applies to.
        The field itself is not stored, only the field's shape and
        sampling are of interest.
    sampling : number
        The spacing of the knots in the field. (For anisotropic fields,
        the spacing is expressed in world units.)

    """

    _field_shape: Incomplete
    _field_sampling: Incomplete
    _grid_sampling: Incomplete
    _grid_shape: Incomplete
    def __init__(self, field, sampling) -> None: ...
    @property
    def ndim(self):
        """The number of dimensions of this grid."""
    @property
    def field_shape(self):
        """The shape of the underlying field. (i.e. the size in each dim.)"""
    @property
    def field_sampling(self):
        """For each dim, the sampling of the field, i.e. the distance
        (in world units) between pixels/voxels (all 1's if isotropic).
        """
    @property
    def grid_shape(self):
        """The shape of the grid. (i.e. the size in each dim.)"""
    @property
    def grid_sampling(self):
        """A *scalar* indicating the spacing (in world units) between the knots."""
    @property
    def grid_sampling_in_pixels(self):
        """For each dim, the spacing (in sub-pixels) between the knots.
        A dimension that has a low field sampling will have a high grid
        sampling in pixels (since the pixels are small, more fit between
        two knots).
        """
    def copy(self):
        """copy()

        Return a deep copy of the grid.

        """
    def refine(self):
        """refine()

        Refine the grid, returning a new grid instance (of the same type)
        that represents the same field, but with half the grid_sampling.

        """
    def add(self, other_grid):
        """add(other_grid)

        Create a new grid by adding this grid and the given grid.

        """
    def resize_field(self, new_shape: Incomplete | None = None):
        """resize_field(new_shape)

        Create a new grid, where the underlying field is reshaped. The
        field is still the same; it only has a different shape and sampling.

        The parameter new_shape can be anything that can be converted
        to a FieldDescription instance.

        Note that the knots arrays are shallow copied (which makes
        this function very efficient).

        """
    @classmethod
    def _multiscale(cls, setResidu, getResidu, field, sampling):
        """_multiscale(setResidu, getResidu, field, sampling)

        General method for multiscale grid formation. from_field_multiscale()
        and from_points_multiscale() use this classmethod by each supplying
        appropriate setResidu and getResidu functions.

        """

class GridContainer(GridInterface):
    """GridContainer(field, sampling=5)

    Abstract base class that represents multiple SplineGrid instances.
    Since each SplineGrid instance describes a field of scalar values,
    the GridContainer can be used to describe vectors/tensors. Examples
    are color and 2D/3D deformations.

    The implementing class should:
      * instantiate SplineGrid instances and append them to '_grids'
      * implement methods to set the grid accordingly, probably using
        classmethods such as from_points, from_field, etc.

    """

    _grids: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def __len__(self) -> int: ...
    def __getitem__(self, item): ...
    def __iter__(self): ...
    @property
    def grids(self):
        """A tuple of subgrids."""
    def _map(self, method, source, *args, **kwargs) -> None:
        """_map(self, method, source, *args, **kwargs)

        Set the knots of the sub-grids by mapping a method on the
        subgrids of a source grid, optionally with additional grid
        arguments.

        Examples
        --------
        newGrid._map('copy', sourceGrid)
        newGrid._map('add', sourceGrid1, sourceGrid2)

        """

class SplineGrid(GridInterface):
    """SplineGrid(field, sampling=5)

    A SplineGrid is a representation of a scalar field in N
    dimensions. This field is represented in a sparse way using
    knots, which are distributed in a uniform grid.

    The manner in which these knots describe the field depends
    on the underlying spline being used, which is a Cubic
    B-spline. This spline adopts a shape corresponding to minimum
    bending energy, which makes them the preferred choice for many
    interpolation tasks. (Earlier versions of Pirt allowed setting the
    spline types, but to make things easier, and because the B-spline is
    the only sensible choice, this option was removed.)

    Parameters
    ----------
    field : shape-tuple, numpy-array, Aarray, FieldDescription
        A description of the field that this grid applies to.
        The field itself is not stored, only the field's shape and
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

    _knots: Incomplete
    _thisDim: int
    def __init__(self, *args, **kwargs) -> None: ...
    def show(self, axes: Incomplete | None = None, axesAdjust: bool = True, showGrid: bool = True):
        """show(axes=None, axesAdjust=True, showGrid=True)

        For 2D grids, shows the field and the knots of the grid.
        The image is displayed in the given (or current) axes. By default
        the positions of the underlying knots are also shown using markers.
        Returns the texture object of the field image.

        Requires visvis.

        """
    @property
    def knots(self):
        """A numpy array that represent the values of the knots."""
    def get_field(self):
        """get_field()

        Obtain the full field that this grid represents.

        """
    def get_field_in_points(self, pp):
        """get_field_in_points(pp)

        Obtain the field in the specied points (in world coordinates).

        """
    def get_field_in_samples(self, samples):
        """get_field_in_samples(pp)

        Obtain the field in the specied samples (a tuple with pixel
        coordinates, in x-y-z order).

        """
    @classmethod
    def from_field(cls, field, sampling, weights: Incomplete | None = None):
        """from_field(field, sampling, weights=None)

        Create a SplineGrid from a given field. Note that the smoothness
        of the grid and the extent to which the grid follows the given values.
        Also see from_field_multiscale()

        The optional weights array can be used to individually weight the
        field elements. Where the weight is zero, the values are not
        evaluated. The speed can therefore be significantly improved if
        there are relatively few nonzero elements.

        Parameters
        ----------
        field : numpy array or shape
            The field to represent with this grid.
        sampling : scalar
            The sampling of the returned grid.
        weights : (optional) numpy array
            This array can be used to weigh the contributions of the
            individual elements.

        """
    @classmethod
    def from_field_multiscale(cls, field, sampling, weights: Incomplete | None = None):
        """from_field_multiscale(field, sampling, weights=None)

        Create a SplineGrid from the given field. By performing a
        multi-scale approach the grid adopts a minimal bending to
        conform to the given field.

        The optional weights array can be used to individually weight the
        field elements. Where the weight is zero, the values are not
        evaluated. The speed can therefore be significantly improved if
        there are relatively few nonzero elements.

        Parameters
        ----------
        field : numpy array or shape
            The field to represent with this grid.
        sampling : scalar
            The sampling of the returned grid.
        weights : (optional) numpy array
            This array can be used to weigh the contributions of the
            individual elements.

        Notes
        -----
        The algorithmic is based on:
        Lee, Seungyong, George Wolberg, and Sung Yong Shin. 1997.
        "Scattered Data Interpolation with Multilevel B-splines".
        IEEE TRANSACTIONS ON VISUALIZATION AND COMPUTER GRAPHICS 3 (3): 228-244.

        """
    @classmethod
    def from_points(cls, field, sampling, pp, values):
        """from_points(field, sampling, pp, values)

        Create a SplineGrid from the values specified at a set of
        points. Note that the smoothness of the grid and the extent to
        which the grid follows the given values. Also see
        from_points_multiscale()

        Parameters
        ----------
        field : numpy array or shape
            The image (of any dimension) to which the grid applies.
        sampling : scalar
            The sampling of the returned grid.
        pp : PointSet, 2D ndarray
            The positions (in world coordinates) at which the values are given.
        values : list or numpy array
            The values specified at the given positions.

        """
    @classmethod
    def from_points_multiscale(cls, field, sampling, pp, values):
        """from_points_multiscale(field, sampling, pp, values)

        Create a SplineGrid from the values specified at a set of
        points. By performing a multi-scale approach the grid adopts a
        minimal bending to conform to the given values.

        Parameters
        ----------
        field : numpy array or shape
            The image (of any dimension) to which the grid applies.
        sampling : scalar
            The sampling of the returned grid.
        pp : PointSet, 2D ndarray
            The positions (in world coordinates) at which the values are given.
        values : list or numpy array
            The values specified at the given positions.

        Notes
        -----
        The algorithmic is based on:
        Lee, Seungyong, George Wolberg, and Sung Yong Shin. 1997.
        "Scattered Data Interpolation with Multilevel B-splines".
        IEEE TRANSACTIONS ON VISUALIZATION AND COMPUTER GRAPHICS 3 (3): 228-244.

        """
    def _select_points_inside_field(self, pp, values: Incomplete | None = None):
        """_select_points_inside_field(self, pp, values=None)

        Selects the points which lay inside the field, discarting the
        outliers.

        When values is given, returns a tuple (pp, values) with the
        new pointset and values array. If values is not given, sets
        the outlier points in pp to the origin.

        """
    def _set_using_field(self, field, weights: Incomplete | None = None) -> None:
        """_set_using_field(field, weights=None)

        Set the grid using an existing field, optionally with weighting.

        """
    def _set_using_points(self, pp, values) -> None:
        """_set_using_points(pp, values)

        Set the grid using sparse data, defined at the points in pp.

        """
    def _refine(self, knots):
        """_refine(knots)

        Workhorse method to refine the knots array.

        Designed for B-splines. For other splines, this method introduces
        errors; the resulting grid does not exactly represent the original.

        Refines the grid to a new grid (newGrid). Let grid have
        (n+3)*(m+3) knots, then newGrid has (2n+3)*(2m+3) knots (sometimes
        the grid needs one row less, this is checked in the Refine() method).
        In both grids, the second knot lays exactly on the first pixel of the
        image. Below is an illustration of a few knots:

        ( )   ( )   ( )
            x  x  x  x                      ( ): knots of grid
        ( ) x (x) x (x) ------------         x : knots of newGrid
            x  x  x  x
              |            image
              |

        Lee tells on page 7 of "Lee et al. 1997 - Scattered Data Interpolation
        With Multilevel B-splines" that there are several publications on how
        to create a lattice from another lattice in such a way that they
        describe the same deformation. Our case is relatively simple because we
        have about the same lattice, but with a twice as high accuracy. What we
        do here is based on what Lee says on page 7 of his article. Note that
        he handles the indices a bit different as I do.

        For each knot in the grid we update four knots in new grid. The indexes
        of the knots to update in newGrid are calculated using a simple formula
        that can be derived from the illustration shown below: For each knot in
        grid ( ) we determine the 4 x\'s (in newGrid) from the 0\'s.
          0      0       0

          0     (x)  x   0
                 x   x
          0      0       0

        We can note a few things.
          * the loose x\'s are calculated using 2 neighbours in each dimension.
          * the x\'s insided ( ) are calculated using 3 neighbours in each dim.
          * (Knots can also be loose in one dim and not loose in another.)
          * the newGrid ALWAYS has its first knot between grid\'s first and
            second knot.
          * newGrid can have a smaller amount of rows and/or cols than you
            would think. According to Lee the newGrid has 2*(lat.rows-3)+3
            rows, but in our case this is not necessarily true. The image does
            not exactly fit an integer amount of knots, we thus need one knot
            extra. But when we go from a course lattice to a finer one, we
            might need one row/col of knots less.

        """
