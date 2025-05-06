from .reg_base import (
    GDGRegistration as GDGRegistration,
    BaseRegistration as BaseRegistration,
    NullRegistration as NullRegistration,
    AbstractRegistration as AbstractRegistration,
)
from .reg_demons import (
    OriginalDemonsRegistration as OriginalDemonsRegistration,
    DiffeomorphicDemonsRegistration as DiffeomorphicDemonsRegistration,
)
from .reg_elastix import (
    ElastixRegistration as ElastixRegistration,
    ElastixRegistration_rigid as ElastixRegistration_rigid,
    ElastixRegistration_affine as ElastixRegistration_affine,
    ElastixGroupwiseRegistration as ElastixGroupwiseRegistration,
)
from .reg_gravity import GravityRegistration as GravityRegistration
