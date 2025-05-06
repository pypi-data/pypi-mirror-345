import visvis as vv
from _typeshed import Incomplete

SH_MV_DEFORM: Incomplete
SH_3F_DEFORM: Incomplete

class DeformTexture(vv.textures.TextureObjectToVisualize):
    """DeformTexture(deforms)

    Texture to manage a deformation that can be applied to a
    texture or mesh.

    """

    _interpolate: bool
    def __init__(self, deform) -> None: ...
    _deform_shape: Incomplete
    _deform_origin: Incomplete
    _deform_sampling: Incomplete
    def SetData(self, data) -> None: ...
    def _ScaleBias_get(self):
        """Given clim, get scale and bias to apply in shader.
        In this case, we want to map [0 1] to the full range,
        expressed in world coordinates. In the shader, we use
        the extent (in world units) to convert to texture coords.

        Data to OpenGL: texData = data*scale + bias
        In shader: data_val = (texData-bias) / scale
        """

class DeformableMixin(vv.MotionMixin):
    """DeformableMixin

    Base class to mix with a Wobject class to make it deformable.

    """

    _deforms: Incomplete
    _deformTexture: Incomplete
    _motionAmplitude: float
    def __init__(self) -> None: ...
    def _GetMotionCount(self): ...
    def _SetMotionIndex(self, index, ii, ww) -> None: ...
    def SetDeforms(self, *deforms) -> None:
        """SetDeforms(*deforms)

        Set deformation arrays for this wobject. Each given argument
        represents one deformation. Each deformation consists either
        of a tuple of arrays (one array for each dimension) or a
        single array where the last dimension is ndim elements.

        Call without arguments to remove all deformations.

        If this wobject is a texture, it is assumed that the deformations
        exactly match with it, in a way that the outer pixels of the
        texture match with the outer pixels of the deformatio. The
        resolution does not have to be the same; it can often be lower
        because deformations are in general quite smooth. Smaller
        deformation arrows result in higher FPS.

        If this wobject is not a texture, the given deformations represent
        a deformation somewhere in 3D space. One should use the vv.Aarray
        or pirt.Aarray class to store the arrays. The exact location
        is then specified by the origin and sampling properties.

        """
    def _UpdateDeformShaderAfterSetDeforms(self, origin, sampling, shape) -> None: ...
    motionIndex: Incomplete
    def motionAmplitude():
        """Get/set the relative amplitude of the deformation (default 1).
        Note that values higher than 1 can cause foldings in the deformation.
        Also note that because the deformation is backward mapping, changing
        the amplitude introduces errors in the deformation.
        """

class DeformableTexture3D(vv.Texture3D, DeformableMixin):
    """DeformableTexture3D(parent, data)

    This class represents a 3D texture that can be deformed using a
    3D deformation field, i.e. a vector field that specifies the
    displacement of the texture. This deformation field can (and probably
    should) be of lower resolution than the texture.

    By supplying multiple deformation fields (via SetDeforms()),
    the texture becomes a moving texture subject to the given deformations.
    Note that the motion is interpolated.

    The deformations should be backward mapping. Note that this means
    that interpolation between the deformations and increasing the amplitude
    will yield not the exact expected deformations.

    """

    _ndim: int
    def __init__(self, *args, **kwargs) -> None: ...
    def _UpdateDeformShaderAfterSetDeforms(self, origin, sampling, shape) -> None: ...

class DeformableMesh(vv.Mesh, DeformableMixin):
    """DeformableMesh(parent, vertices, faces=None, normals=None, values=None, verticesPerFace=3)

    This class represents a mesh that can be deformed using a
    3D deformation field, i.e. a vector field that specifies the
    displacement of a region of the 3D space.

    By supplying multiple deformation fields (via SetDeforms()),
    the mesh becomes a moving mesh subject to the given deformations.
    Note that the motion is interpolated.

    The deformations should be forward mapping; interpolation and changing
    the amplitude can be done safely. However, the normals are always the
    same, so for extreme deformations the lighting might become incorrect.

    """

    _ndim: int
    def __init__(self, *args, **kwargs) -> None: ...
    def _UpdateDeformShaderAfterSetDeforms(self, origin, sampling, shape) -> None: ...
