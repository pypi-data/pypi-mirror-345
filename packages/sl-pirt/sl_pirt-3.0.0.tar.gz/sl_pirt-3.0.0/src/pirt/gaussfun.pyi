from _typeshed import Incomplete

from ._utils import Aarray as Aarray

def _gaussiankernel(sigma, order, t):
    """_gaussiankernel(sigma, order, t)
    Calculate a Gaussian kernel of the given sigma and with the given
    order, using the given t-values.
    """

def gaussiankernel(sigma, order: int = 0, N: Incomplete | None = None, returnt: bool = False, warn: bool = True):
    """gaussiankernel(sigma, order=0, N=None, returnt=False, warn=True)

    Creates a 1D gaussian derivative kernel with the given sigma
    and the given order. (An order of 0 is a "regular" Gaussian.)

    The returned kernel is a column vector, thus working in the first
    dimension (in images, this often is y).

    The returned kernel is odd by default. Using N one can specify the
    full kernel size (if not int, the ceil operator is applied). By
    specifying a negative value for N, the tail length (number of elements
    on both sides of the center element) can be specified.
    The total kernel size than becomes ceil(-N)*2+1. Though the method
    to supply it may be a bit obscure, this measure can be handy, since
    the tail length if often related to the sigma. If not given, the
    optimal N is determined automatically, depending on sigma and order.

    If the given scale is a small for the given order, a warning is
    produced (unless warn==True).

    ----- Used Literature:

    Koenderink, J. J.
    The structure of images.
    Biological Cybernetics 50, 5 (1984), 363-370.

    Lindeberg, T.
    Scale-space for discrete signals.
    IEEE Transactions on Pattern Analysis and Machine Intelligence 12, 3 (1990), 234-254.

    Ter Haar Romeny, B. M., Niessen, W. J., Wilting, J., and Florack, L. M. J.
    Differential structure of images: Accuracy of representation.
    In First IEEE International Conference on Image Processing, (Austin, TX) (1994).
    """

def gaussiankernel2(sigma, ox, oy, N: Incomplete | None = None):
    """gaussiankernel2(sigma, ox, oy, N=-3*sigma)
    Create a 2D Gaussian kernel.
    """

def diffusionkernel(sigma, N: int = 4, returnt: bool = False):
    """diffusionkernel(sigma, N=4, returnt=False)

    A discrete analog to the continuous Gaussian kernel,
    as proposed by Toni Lindeberg.

    N is the tail length factor (relative to sigma).

    """

def gfilter(L, sigma, order: int = 0, mode: str = "constant", warn: bool = True):
    """gfilter(L, sigma, order=0, mode='constant', warn=True)

    Gaussian filterering and Gaussian derivative filters.

    Parameters
    ----------
    L : np.ndarray
        The input data to filter
    sigma : scalar or list-of-scalars
        The smoothing parameter, can be given for each dimension
    order : int or list-of-ints
        The order of the derivative, can be given for each dimension
    mode : {'reflect','constant','nearest','mirror', 'wrap'}
        Determines how edge effects are handled. (see scipy.ndimage.convolve1d)
    warn : boolean
        Whether to show a warning message if the sigma is too small to
        represent the required derivative.

    Notes
    =====
    Makes use of the seperability property of the Gaussian by convolving
    1D kernels in each dimension.


    Example
    =======
    # Calculate the second order derivative with respect to x (Lx) (if the
    # first dimension of the image is Y).
    result1 = gfilter( im, 2, [0,2] )
    # Calculate the first order derivative with respect to y and z (Lyz).
    result2 = gfilter( volume, 3, [0,1,1] )

    """

def diffuse(L, sigma, mode: str = "nearest"):
    """diffuse(L, sigma)

    Diffusion using a discrete variant of the diffusion operator.

    Parameters
    ----------
    L : np.ndarray
        The input data to filter
    sigma : scalar or list-of-scalars
        The smoothing parameter, can be given for each dimension

    Details
    -------
    In the continous domain, the Gaussian is the only true diffusion
    operator. However, by using a sampled Gaussian kernel in the
    discrete domain, errors are introduced, particularly if for
    small sigma.

    This implementation uses a a discrete variant of the diffusion
    operator, which is based on modified Bessel functions. This results
    in a better approximation of the diffusion process, particularly
    when applying the diffusion recursively. There are also advantages
    for calculating derivatives, see below.

    Based on:
    Lindeberg, T. "Discrete derivative approximations with scale-space
    properties: A basis for low-level feature extraction",
    J. of Mathematical Imaging and Vision, 3(4), pp. 349--376, 1993.

    Calculating derivatives
    -----------------------
    Because this imeplementation applies diffusion using a discrete
    representation of the diffusion kernel, one can calculate true
    derivatives using small-support derivative operators. For 1D:
      * Lx = 0.5 * ( L[x+1] - L[x-1] )
      * Lxx = L[x+1] - 2*L[x] + L(x-1)

    """

def gfilter2(L, scale, order: int = 0, mode: str = "reflect", warn: bool = True):
    """gfilter2(L, scale, order=0, mode='reflect', warn=True)

    Apply Gaussian filtering by specifying a scale in world coordinates
    rather than a sigma. This function determines the sigmas to apply,
    based on the sampling of the elements.

    See gfilter for more information.

    (If L is not an Aarray, this function yields the same result as gfilter.)

    """

def diffuse2(L, scale, mode: str = "nearest"):
    """diffuse2(L, scale, mode='nearest')

    Apply diffusion by specifying a scale in world coordinates
    rather than a sigma. This function determines the sigmas to apply,
    based on the sampling of the elements.

    See diffuse for more information.

    (If L is not an Aarray, this function yields the same result as diffuse.)

    """
