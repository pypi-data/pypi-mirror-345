from _typeshed import Incomplete

from .new_pointset import PointSet as PointSet

_precalculated_A1: Incomplete
_precalculated_Ai1: Incomplete
tmp: str
_precalculated_A2: Incomplete
_precalculated_Ai2: Incomplete

def fit_lq1(pp):
    """fit_lq1(points) -> t_max, [a,b,c]

    Fit quadratic polynom to three points in 1D. If more than three
    points are given, the result is the least squares solution.

    points can be a 2D ndarray object, resulting in a general
    solution. If only 3 values are given (as list of numpy array),
    the point locations are assumed at t=(-1,0,1).

    """

def fit_lq2(patch, sample: bool = False):
    """fit_lq2(patch) --> x_max, y_max

    Quadratic (least squares) 2d fitting and subsequent finding of real max.

    Patch is a matrix of the 9 pixels around the extreme.
    Uses the centre and its 4 direct neighours, as specified
    in patch. fit_lq2(patch, True) will also return a
    300x300 image illustrating the surface in the 3x3 area.

    """
