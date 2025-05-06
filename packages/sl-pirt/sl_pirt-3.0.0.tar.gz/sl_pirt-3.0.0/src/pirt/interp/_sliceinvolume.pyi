from _typeshed import Incomplete

from .._utils import Aarray as Aarray
from ._backward import warp as warp
from ..new_pointset import PointSet as PointSet

def get_span_vectors(normal, c, d):
    """get_span_vectors(normal, prevA, prevB) -> (a,b)

    Given a normal, return two orthogonal vectors which are both
    orthogonal to the normal. The vectors are calculated so they match
    as much as possible the previous vectors.
    """

class SliceInVolume:
    """SliceInVolume(self, pos, normal=None, previous=None)
    Defines a slice in a volume.

    The two span vectors are in v and u respectively. In other words,
    vec1 is up, vec2 is right.
    """

    _pos: Incomplete
    _normal: Incomplete
    _vec1: Incomplete
    _vec2: Incomplete
    def __init__(self, pos, normal: Incomplete | None = None, previous: Incomplete | None = None) -> None: ...
    def get_slice(self, volume, N: int = 128, spacing: float = 1.0): ...
    def convert_local_to_global(self, p2d, p3d):
        """convert_local_to_global(p2d, p3d)
        Convert local 2D points to global 3D points.
        UNTESTED
        """

def slice_from_volume(data, pos, vec1, vec2, Npatch, order: int = 3):
    """slice_from_volume(data, pos, vec1, vec2, Npatch, order=3)
    Samples a square 2D slice from a 3D volume, using a center position
    and two vectors that span the patch. The length of the vectors
    specify the sample distance for the patch.
    """

def _slice_samples_from_volume(data, sampling, origin, pos, vec1, vec2, Npatch, order: int = 3): ...
