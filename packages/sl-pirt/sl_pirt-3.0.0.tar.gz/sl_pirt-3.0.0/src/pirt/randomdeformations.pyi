from _typeshed import Incomplete

from . import (
    FD as FD,
    Aarray as Aarray,
    PointSet as PointSet,
    DeformationFieldForward as DeformationFieldForward,
    DeformationFieldBackward as DeformationFieldBackward,
    diffuse as diffuse,
    gaussfun as gaussfun,
)

def create_random_deformation_gaussian(
    im, amplitude: int = 1, min_sigma: int = 10, nblobs: int = 50, seed: Incomplete | None = None
):
    """create_random_deformation(im, amplitude=1, min_sigma=10, nblobs=50, seed=None)

    Create a random deformation using Gaussian blobs or different scales.
    Returns a DeformationField instance.

    See also the class RandomDeformations.

    Parameters
    ----------
    im : numpy array
        The image to create a deformation field for.
    amplitude : scalar
        The relative amplitude of the deformations.
    min_sigma : scalar
        The smallest sigma to create Gaussian blobs for. The largest sigma
        is a quarter of the maximum shape element of the image.
    nblobs : integer
        The amount of Gaussian blobs to compose the deformation with.
    seed : int or None
        Seed for the random numbers to draw. If you want to repeat the
        same deformations, apply the same seed multiple times.

    """

def create_random_deformation(
    im,
    amplitude: int = 20,
    scale: int = 50,
    n: int = 50,
    frozenedge: bool = True,
    mapping: str = "backward",
    seed: Incomplete | None = None,
):
    """create_random_deformation(im, amplitude=20, scale=50, n=50,
                                frozenedge=True, mapping='backward', seed=None)

    Create a random deformation by creating two random sets of
    deformation vectors which are then converted to an injective
    deformation field using Lee and Choi's method.

    See also the class RandomDeformations.

    Parameters
    ----------
    im : numpy array or pirt.FieldDescription
        The image to create a deformation field for, or anything tha can be
        converted to a FieldDesctription instance.
    amplitude : scalar
        The relative amplitude of the deformations. The deformation vectors
        are randomly chosen with a maximum norm of this amplitude.
    scale : scalar
        The smallest resolution of the B-spline grid to regularize the
        deformation. Default 50.
    n : integer
        The amount of vectors to generate. Default 50.
    frozenedge : bool
        Whether the edges remain fixed or not (default True).
    mapping : {'forward', 'backward'}
        Whether the generated deformation uses forward or backward mapping.
        Default backward.
    seed : int or None
        Seed for the random numbers to draw. If you want to repeat the
        same deformations, apply the same seed multiple times.

    """

class RandomDeformations:
    """RandomDeformations(im, amplitude=20, scale=50, n=50,
                                frozenedge=True, mapping='backward', seed=None)

    Represents a collection of random deformations. This can be used
    in experiments to test multiple methods on the same set of random
    deformations.

    It creates (and stores) random deformations on the fly when requested.

    The seed given to create_random_deformation is (seed + 100*index).
    It can be used to produce a random, yet repeatable set of deformations.
    For the sake of science, let's use a seed when doing experiments that
    are going to be published in a scientific medium, so they
    can be reproduced by others. For the sake of simplicity, let's agree to
    use the arbitrary seeds listed here: 1234 for training sets, 5678 for
    test sets.

    See also the function create_random_deformation()

    Example
    -------
    rd = RandomDeformations(im)
    deform1 = rd[0]
    deform2 = rd[1]
    # etc.

    """

    _fd: Incomplete
    _amplitude: Incomplete
    _scale: Incomplete
    _n: Incomplete
    _frozenedge: Incomplete
    _mapping: Incomplete
    _seed: Incomplete
    _deforms: Incomplete
    def __init__(
        self,
        im,
        amplitude: int = 20,
        scale: int = 50,
        n: int = 50,
        frozenedge: bool = True,
        mapping: str = "backward",
        seed: Incomplete | None = None,
    ) -> None: ...
    def __getitem__(self, index):
        """Get the deformation at the specified index. If it does not yet
        exist, will create a new deformation using arguments specified
        during initialization.
        """
    def get(self, index, *args, **kwargs):
        """get(index, *args, **kwargs)

        Get the deformation at the specified index. If it does not yet
        exist, will create a new deformation using the specified arguments.

        Note that this will not take the seed into account.

        """
