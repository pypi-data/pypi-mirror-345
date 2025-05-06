from _typeshed import Incomplete

from .. import (
    SplineGrid as SplineGrid,
    interp as interp,
)

class SplineByHand:
    """SplineByHand()

    Demo application to influence a 1D spline grid using control points.
    """

    _fig: Incomplete
    _a1: Incomplete
    _pp: Incomplete
    _line1: Incomplete
    _fieldSize: int
    _sampling: int
    _levels: int
    _active: Incomplete
    def __init__(self) -> None: ...
    def on_key_down(self, event) -> None: ...
    def on_doubleclick(self, event) -> None: ...
    def on_doubleclick_line(self, event): ...
    def on_down_line(self, event): ...
    def on_motion(self, event): ...
    def on_up_line(self, event): ...
    def apply(self, event: Incomplete | None = None) -> None: ...
    _grid: Incomplete
    def freeze_edges(self, grid) -> None: ...
