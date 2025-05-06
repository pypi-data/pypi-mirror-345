from ..interp._cubic import cubicsplinecoef_basis as cubicsplinecoef_basis

def get_field(grid):
    """get_field(grid)
    Sample the grid at all the pixels of the underlying field.
    """

def get_field_sparse(grid, pp):
    """get_field_sparse(grid, pp)

    Sparsely sample the grid at a specified set of points (which are in
    world coordinates).

    Also see get_field_at().

    """

def get_field_at(grid, samples):
    """get_field_at(grid, samples)

    Sample the grid at specified sample locations (in pixels, x-y-z order),
    similar to pirt.interp.interp().

    Also see get_field_sparse().

    """

def _get_field1(result, grid_sampling_in_pixels, knots) -> None: ...
def _get_field2(result, grid_sampling_in_pixels, knots) -> None: ...
def _get_field3(result, grid_sampling_in_pixels, knots) -> None: ...
def _get_field_at1(result, grid_sampling_in_pixels, knots, samplesx_) -> None: ...
def _get_field_at2(result_, grid_sampling_in_pixels, knots, samplesx_, samplesy_) -> None: ...
def _get_field_at3(result_, grid_sampling_in_pixels, knots, samplesx_, samplesy_, samplesz_) -> None: ...
def _set_field_using_num_and_dnum(knots_, num_, dnum_) -> None: ...
def set_field(grid, field, weights) -> None:
    """set_field(grid, pp)
    Set the grid using the specified field (and optional weights).
    """

def set_field_sparse(grid, pp, values) -> None:
    """set_field_sparse(grid, pp, values)

    Set the grid by providing the field values at a set of points (wich
    are in world coordinates).

    """

def _set_field1(grid_sampling_in_pixels, knots, field, weights): ...
def _set_field2(grid_sampling_in_pixels, knots, field, weights): ...
def _set_field3(grid_sampling_in_pixels, knots, field, weights): ...
def _set_field_sparse1(grid_sampling, knots, pp, values): ...
def _set_field_sparse2(grid_sampling, knots, pp, values): ...
def _set_field_sparse3(grid_sampling, knots, pp, values): ...
