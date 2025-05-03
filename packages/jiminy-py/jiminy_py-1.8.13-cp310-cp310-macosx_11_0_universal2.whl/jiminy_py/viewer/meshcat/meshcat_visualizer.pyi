import hppfcl
import meshcat
import meshcat.path
import numpy as np
import pinocchio as pin
from ..geometry import extract_vertices_and_faces_from_geometry as extract_vertices_and_faces_from_geometry
from _typeshed import Incomplete
from meshcat.geometry import Geometry, ReferenceSceneElement, TriangularMeshGeometry
from pinocchio.visualize import BaseVisualizer
from typing import Any

MsgType: Incomplete

class Cone(Geometry):
    radius: Incomplete
    height: Incomplete
    radial_segments: int
    def __init__(self, height: float, radius: float) -> None: ...
    def lower(self, object_data: Any) -> MsgType: ...

class Capsule(TriangularMeshGeometry):
    def __init__(self, height: float, radius: float, num_segments: int = 32) -> None: ...

class DaeMeshGeometryWithTexture(ReferenceSceneElement):
    path: meshcat.path.Path | None
    material: meshcat.geometry.Material | None
    dae_raw: Incomplete
    img_resources: dict[str, str]
    def __init__(self, dae_path: str, cache: set[str] | None = None) -> None: ...
    def lower(self) -> dict[str, Any]: ...

def update_floor(viewer: meshcat.Visualizer, geom: hppfcl.CollisionGeometry | None = None) -> None: ...

class MeshcatVisualizer(BaseVisualizer):
    cache: set[str]
    root_name: str | None
    visual_group: str | None
    collision_group: str | None
    display_visuals: bool
    display_collisions: bool
    viewer: Incomplete
    def initViewer(self, viewer: meshcat.Visualizer = None, loadModel: bool = False, mustOpen: bool = False, **kwargs: Any) -> None: ...
    def getViewerNodeName(self, geometry_object: pin.GeometryObject, geometry_type: pin.GeometryType) -> str: ...
    def loadPrimitive(self, geometry_object: pin.GeometryObject) -> hppfcl.ShapeBase: ...
    def loadMesh(self, geometry_object: pin.GeometryObject) -> ReferenceSceneElement: ...
    def loadViewerGeometryObject(self, geometry_object: pin.GeometryObject, geometry_type: pin.GeometryType, color: np.ndarray | None = None, material_class: type[meshcat.geometry.Material] = ...) -> None: ...
    def loadViewerModel(self, root_node_name: str, color: np.ndarray | None = None) -> None: ...
    def display(self, q: np.ndarray) -> None: ...
    def displayCollisions(self, visibility: bool) -> None: ...
    def displayVisuals(self, visibility: bool) -> None: ...
