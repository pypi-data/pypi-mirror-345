import logging
from . import core as jiminy
from .core import EffortSensor as EffortSensor, EncoderSensor as EncoderSensor, ForceSensor as ForceSensor, ImuSensor as ImuSensor, SimpleMotor as SimpleMotor
from _typeshed import Incomplete
from types import ModuleType
from typing import Any, Sequence

DEFAULT_UPDATE_RATE: float
DEFAULT_FRICTION_DRY_SLOPE: float
EXTENSION_MODULES: Sequence[ModuleType]
GeometryModelType: Incomplete
GeometryObjectType: Incomplete

class _DuplicateFilter(logging.Filter):
    msgs: set[str]
    def __init__(self) -> None: ...
    def filter(self, record: logging.LogRecord) -> bool: ...

LOGGER: Incomplete

def generate_default_hardware_description_file(urdf_path: str, hardware_path: str | None = None, default_update_rate: float = ..., verbose: bool = True) -> None: ...
def load_hardware_description_file(robot: jiminy.Robot, hardware_path: str, avoid_instable_collisions: bool = True, verbose: bool = True) -> dict[str, Any]: ...

class BaseJiminyRobot(jiminy.Robot):
    extra_info: dict[str, Any]
    hardware_path: str | None
    def __init__(self, name: str = '') -> None: ...
    def initialize(self, urdf_path: str, hardware_path: str | None = None, mesh_dir_path: str | None = None, mesh_package_dirs: Sequence[str] = (), has_freeflyer: bool = True, avoid_instable_collisions: bool = True, load_visual_meshes: bool = False, verbose: bool = True) -> None: ...
    def __del__(self) -> None: ...
