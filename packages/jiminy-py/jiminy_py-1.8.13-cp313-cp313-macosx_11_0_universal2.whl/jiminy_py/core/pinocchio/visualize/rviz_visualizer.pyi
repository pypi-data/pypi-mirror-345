from . import BaseVisualizer
from _typeshed import Incomplete

__all__ = ['RVizVisualizer']

class RVizVisualizer(BaseVisualizer):
    class Viewer:
        app: Incomplete
        viz: Incomplete
        viz_manager: Incomplete
    viewer: Incomplete
    def initViewer(self, viewer: Incomplete | None = None, windowName: str = 'python-pinocchio', loadModel: bool = False, initRosNode: bool = True): ...
    visuals_publisher: Incomplete
    visual_Display: Incomplete
    visual_ids: Incomplete
    collisions_publisher: Incomplete
    collision_Display: Incomplete
    collision_ids: Incomplete
    group_Display: Incomplete
    seq: int
    def loadViewerModel(self, rootNodeName: str = 'pinocchio') -> None: ...
    def clean(self) -> None: ...
    def display(self, q: Incomplete | None = None) -> None: ...
    def displayCollisions(self, visibility) -> None: ...
    def displayVisuals(self, visibility) -> None: ...
    def sleep(self, dt) -> None: ...
