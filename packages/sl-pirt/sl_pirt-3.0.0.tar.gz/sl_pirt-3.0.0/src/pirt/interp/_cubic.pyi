from _typeshed import Incomplete

LUTS: Incomplete

def get_cubic_spline_coefs(t, spline_type: float = 0.0):
    """get_cubic_spline_coefs(t, spline_type=\'Catmull-Rom\')

    Calculates the coefficients for a cubic spline and returns them as
    a tuple. t is the ratio between "left" point and "right" point on the
    lattice.  If performance matters, consider using get_lut() instead.

    spline_type can be (case insensitive):

        <number between -1 and 1>: Gives a Cardinal spline with the
        specified number as its tension parameter. A Cardinal spline
        is a type of Hermite spline, where the tangents are calculated
        using points p0 and p3; the coefficients can be directly applied
        to p0 p1 p2 p3.

        \'Catmull-Rom\' or \'Cardinal0\': is a cardinal spline a tension of 0.
        An interesting note: if we would create two quadractic splines, that
        would fit a polynomial "f(t) = a*t*t + b*t + c" to the first three
        and last three knots respectively, and if we would then combine
        the two using linear interpolation, we would obtain a catmull-rom
        spline. I don\'t know whether this is how the spline was designed,
        or if this is a "side-effect".

        \'B-pline\': Basis spline. Not an interpolating spline, but an
        approximating spline. Here too, the coeffs can be applied to p0-p3.

        \'Hermite\': Gives the Hermite coefficients to be applied to p1 m1 p2
        m2 (in this order), where p1 p2 are the closest knots and m1 m2 the
        tangents.

        \'Lagrange\': The Lagrange spline or Lagrange polynomial is an
        interpolating spline. It is the same as Newton polynomials, but
        implemented in a different manner (wiki). The Newton implementation
        should be more efficient, but this implementation is much simpler,
        and is very similar to the B-spline implementation (only the
        coefficients are different!). Also, when for example interpolating
        an image, coefficients are reused often and can be precalculated
        to enhance speed.

        \'Lanczos\': Lanczos interpolation (windowed sync funcion). Note that
        this is not really a spline, and that sum of the coefficients is
        not exactly 1. Often used in audio processing. The Lanczos spline is
        very similar to the Cardinal spline with a tension of -0.25.

        \'quadratic\': Quadratic interpolation with a support of 4, essentially
        the addition of the two quadratic polynoms.

        \'linear\': Linear interpolation. Effective support is 2. Added
        for completeness and testing.

        \'nearest\': Nearest neighbour interpolation. Added for completeness
        and testing.

    """

def set_cubic_spline_coefs(t, spline_id, out) -> None:
    """set_cubic_spline_coefs(t, spline_id, out)

    Calculate cubuc spline coefficients for the given spline_id, and
    store them in the given array. See get_cubic_spline_coefs() and
    spline_type_to_id() for details.
    """

def get_lut(spline_type, n: int = 32768):
    """get_lut(spline_type, n=32768)

    Calculate the look-up table for the specified spline type
    with n entries. Returns a float64 1D array that has a size of (n + 2 * 4)
    that can be used in get_coef().

    The spline_type can be 'cardinal' or a float between -1 and 1 for
    a Cardinal spline, or 'hermite', 'lagrange', 'lanczos', 'quadratic',
    'linear', 'nearest'. Note that the last three are available for
    completeness; its inefficient to do nearest, linear or quadratic
    interpolation with a cubic kernel.
    """

def _calculate_lut(lut, spline_id) -> None: ...
def spline_type_to_id(spline_type):
    """spline_type_to_id(spline_type)

    Method to map a spline name to an integer ID. This is used so that
    set_cubic_spline_coefs() can be efficient.

    The spline_type can also be a number between -1 and 1, representing
    the tension for a Cardinal spline.
    """

def get_coef(lut, t):
    """get_coef(lut, t)

    Get the coefficients for given value of t. This simply obtains
    the nearest coefficients in the table. For a more accurate result,
    use the AccurateCoef class.
    """

def cubicsplinecoef_catmullRom(t, out) -> None: ...
def cubicsplinecoef_cardinal(t, out, tension) -> None: ...
def cubicsplinecoef_basis(t, out) -> None: ...
def cubicsplinecoef_hermite(t, out) -> None: ...
def cubicsplinecoef_lagrange(t, out) -> None: ...
def cubicsplinecoef_lanczos(t, out) -> None: ...
def cubicsplinecoef_nearest(t, out) -> None: ...
def cubicsplinecoef_linear(t, out) -> None: ...
def cubicsplinecoef_quadratic(t, out) -> None: ...
