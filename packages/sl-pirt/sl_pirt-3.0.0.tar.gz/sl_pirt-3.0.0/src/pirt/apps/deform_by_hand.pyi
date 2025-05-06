from _typeshed import Incomplete

from .. import (
    FieldDescription as FieldDescription,
    DeformationGridForward as DeformationGridForward,
    DeformationFieldForward as DeformationFieldForward,
    DeformationGridBackward as DeformationGridBackward,
    DeformationFieldBackward as DeformationFieldBackward,
)

class DeformByHand:
    """DeformByHand(im, grid_sampling=40)

    Demo application to deform a 2D image by hand using a spline grid.

    Use the grid property to obtain the deformation grid.
    Use the run() method to wait for the user to close the figure.

    """

    _im: Incomplete
    _fig: Incomplete
    _a1: Incomplete
    _a2: Incomplete
    _a3: Incomplete
    _a4: Incomplete
    _a5: Incomplete
    _a6: Incomplete
    _text1: Incomplete
    _text2: Incomplete
    _t1: Incomplete
    _t2: Incomplete
    _t3: Incomplete
    _t4: Incomplete
    _t5: Incomplete
    _t6: Incomplete
    _pp1: Incomplete
    _pp2: Incomplete
    _active: Incomplete
    _lines: Incomplete
    _line1: Incomplete
    _line2: Incomplete
    _sampling: Incomplete
    _levels: int
    _multiscale: bool
    _injective: float
    _frozenedge: int
    _forward: bool
    DeformationField: Incomplete
    _field1: Incomplete
    _field2: Incomplete
    def __init__(self, im, grid_sampling: int = 40) -> None: ...
    def on_key_down(self, event) -> None: ...
    def on_down(self, event): ...
    def on_motion(self, event) -> None: ...
    def on_up(self, event): ...
    def apply_deform(self) -> None: ...
    def apply(self) -> None: ...
    @property
    def field(self): ...
    _closed: bool
    def run(self) -> None: ...
