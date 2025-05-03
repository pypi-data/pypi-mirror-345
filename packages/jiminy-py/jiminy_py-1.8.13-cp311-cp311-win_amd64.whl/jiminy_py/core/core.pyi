from __future__ import annotations
import jiminy_py.core
import typing
import Boost.Python
import ctypes
import hppfcl.hppfcl
import inspect
import jiminy_py.core.GJKInitialGuess
import jiminy_py.core.HeightmapType
import jiminy_py.core.JointModelType
import jiminy_py.core.pinocchio.pinocchio_pywrap
import jiminy_py.core.pinocchio.pinocchio_pywrap.serialization
import logging
import numpy
import os
import pinocchio.pinocchio_pywrap
import re
import sys
_Shape = typing.Tuple[int, ...]

__all__ = [
    "AbstractConstraint",
    "AbstractController",
    "AbstractMotor",
    "AbstractSensor",
    "BadControlFlow",
    "BaseConstraint",
    "BaseController",
    "BaseFunctionalController",
    "ConstraintTree",
    "ContactSensor",
    "CouplingForce",
    "CouplingForceVector",
    "DistanceConstraint",
    "EffortSensor",
    "EncoderSensor",
    "Engine",
    "ForceSensor",
    "FrameConstraint",
    "FunctionalController",
    "GJKInitialGuess",
    "HeightmapFunction",
    "HeightmapType",
    "ImpulseForce",
    "ImpulseForceVector",
    "ImuSensor",
    "JointConstraint",
    "JointModelType",
    "LogicError",
    "LookupError",
    "Model",
    "NotImplementedError",
    "OSError",
    "PCG32",
    "PeriodicFourierProcess",
    "PeriodicGaussianProcess",
    "PeriodicPerlinProcess1D",
    "PeriodicPerlinProcess2D",
    "PeriodicPerlinProcess3D",
    "PeriodicTabularProcess",
    "ProfileForce",
    "ProfileForceVector",
    "RandomPerlinProcess1D",
    "RandomPerlinProcess2D",
    "RandomPerlinProcess3D",
    "Robot",
    "RobotState",
    "SensorMeasurementTree",
    "SimpleMotor",
    "SphereConstraint",
    "StepperState",
    "TimeStateBoolFunctor",
    "TimeStateForceFunctor",
    "WheelConstraint",
    "__raw_version__",
    "__version__",
    "aba",
    "array_copyto",
    "boost_type_index",
    "build_geom_from_urdf",
    "build_models_from_urdf",
    "computeJMinvJt",
    "computeKineticEnergy",
    "crba",
    "discretize_heightmap",
    "get_cmake_module_path",
    "get_frame_indices",
    "get_include",
    "get_joint_indices",
    "get_joint_position_first_index",
    "get_joint_type",
    "get_libraries",
    "interpolate_positions",
    "is_position_valid",
    "load_heightmap_from_binary",
    "load_robot_from_binary",
    "merge_heightmaps",
    "multi_array_copyto",
    "normal",
    "periodic_perlin_ground",
    "periodic_stairs_ground",
    "query_heightmap",
    "random_perlin_ground",
    "random_tile_ground",
    "rnea",
    "save_robot_to_binary",
    "seed",
    "sharedMemory",
    "solveJMinvJtv",
    "std_type_index",
    "sum_heightmaps",
    "unidirectional_periodic_perlin_ground",
    "unidirectional_random_perlin_ground",
    "uniform"
]


class AbstractConstraint():
    def compute_jacobian_and_drift(self, q: numpy.ndarray, v: numpy.ndarray) -> None: 
        """
        Compute the jacobian and drift of the constraint.


        .. note::
            To avoid redundant computations, it assumes that `computeJointJacobians` and
            `framesForwardKinematics` has already been called on `model->pinocchioModel_`.

        :param q:
            Current joint position.
        :param v:
            Current joint velocity.
        """
    def reset(self, q: numpy.ndarray, v: numpy.ndarray) -> None: 
        """
        .. note::
            This method does not have to be called manually before running a simulation.
            The Engine is taking care of it.
        """
    @property
    def baumgarte_freq(self) -> float:
        """
        :type: float
        """
    @baumgarte_freq.setter
    def baumgarte_freq(self: jiminy_py.core.core.AbstractConstraint) -> None:
        pass
    @property
    def drift(self) -> numpy.ndarray:
        """
        Drift of the constraint.

        :type: numpy.ndarray
        """
    @property
    def is_enabled(self) -> bool:
        """
        :type: bool
        """
    @is_enabled.setter
    def is_enabled(self: jiminy_py.core.core.AbstractConstraint) -> None:
        pass
    @property
    def jacobian(self) -> numpy.ndarray:
        """
        Jacobian of the constraint.

        :type: numpy.ndarray
        """
    @property
    def kd(self) -> float:
        """
        :type: float
        """
    @kd.setter
    def kd(self: jiminy_py.core.core.AbstractConstraint) -> None:
        pass
    @property
    def kp(self) -> float:
        """
        :type: float
        """
    @kp.setter
    def kp(self: jiminy_py.core.core.AbstractConstraint) -> None:
        pass
    @property
    def lambda_c(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def size(self) -> int:
        """
        Dimension of the constraint.

        :type: int
        """
    @property
    def type(self) -> str:
        """
        :type: str
        """
    pass
class AbstractController():
    def compute_command(self, t: float, q: numpy.ndarray, v: numpy.ndarray, command: numpy.ndarray) -> None: 
        """
        Compute the command.

        It assumes that the robot internal state (including sensors) is consistent
        with other input arguments. It fetches the sensor data automatically.

        :param t:
            Current time.
        :param q:
            Current configuration vector.
        :param v:
            Current velocity vector.
        :param command:
            Output effort vector.
        """
    def get_options(self) -> dict: 
        """
        Dictionary with the parameters of the controller.
        """
    def initialize(self, robot: jiminy_py.core.Robot) -> None: 
        """
        Initialize the internal state of the controller for a given robot.

        This method can be called multiple times with different robots. The internal
        state of the controller will be systematically overwritten.

        :param robot:
            Robot
        """
    def internal_dynamics(self, t: float, q: numpy.ndarray, v: numpy.ndarray, u_custom: numpy.ndarray) -> None: 
        """
        Emulate custom phenomenon that are part of the internal dynamics of the system
        but not included in the physics engine.

        :param t:
            Current time.
        :param q:
            Current configuration vector.
        :param v:
            Current velocity vector.
        :param uCustom:
            Output effort vector.
        """
    def register_constant(self, name: str, value: typing.Any) -> None: 
        """
        Register a constant (so-called invariant) to the telemetry.

        The user is responsible to convert it as a byte array (eg `std::string`),
        either using `toString` for arithmetic types or `saveToBinary` complex types.

        :param name:
            Name of the constant.
        :param value:
            Constant to add to the telemetry.
        """
    def register_variable(self, name: str, value: typing.Any) -> None: 
        """
        Dynamically registered a scalar variable to the telemetry. It is the main entry
        point for a user to log custom variables.

        Internally, all it does is to store a reference to the variable, then it logs
        its value periodically. There is no update mechanism what so ever nor safety
        check. The user has to take care of the life span of the variable, and to
        update it manually whenever it is necessary to do so.

        :param name:
            Name of the variable. It will appear in the header of the log.
        :param values:
            Variable to add to the telemetry.
        """
    def register_variables(self, fieldnames: list, values: typing.Any) -> None: ...
    def remove_entries(self) -> None: 
        """
        Remove all variables dynamically registered to the telemetry.

        Note that one must reset Jiminy Engine for this to take effect.
        """
    def reset(self, reset_dynamic_telemetry: bool = False) -> None: 
        """
        Reset the internal state of the controller.

        Note that it resets the configuration of the telemetry.


        .. note::
            s This method is not intended to be called manually. The Engine is taking care
            of it when its own `reset` method is called.

        :param resetDynamicTelemetry:
            Whether variables dynamically registered to the
            telemetry must be removed. Optional: False by default.
        """
    def set_options(self, options: dict) -> None: 
        """
        Set the configuration options of the controller.

        Note that one must reset Jiminy Engine for this to take effect.

        :param controllerOptions:
            Dictionary with the parameters of the controller.
        """
    @property
    def is_initialized(self) -> bool:
        """
        Whether the controller has been initialized.


        .. note::
            Note that a controller can be considered initialized even if its telemetry is
            not properly configured. If not, it must be done before being ready to use.

        :type: bool
        """
    @property
    def robot(self) -> jiminy_py.core.core.Robot:
        """
        :type: jiminy_py.core.core.Robot
        """
    @property
    def sensor_measurements(self) -> jiminy_py.core.core.SensorMeasurementTree:
        """
        :type: jiminy_py.core.core.SensorMeasurementTree
        """
    pass
class AbstractMotor():
    def get_options(self) -> dict: 
        """
        Configuration options of the sensor.
        """
    def set_options(self, arg2: dict) -> None: 
        """
        Set the configuration options of the motor.

        :param motorOptions:
            Dictionary with the parameters of the motor.
        """
    @property
    def armature(self) -> float:
        """
        Rotor inertia of the motor on joint side.

        :type: float
        """
    @property
    def backlash(self) -> float:
        """
        Backlash of the transmission on joint side.

        :type: float
        """
    @property
    def effort_limit(self) -> float:
        """
        Maximum effort of the motor.

        :type: float
        """
    @property
    def index(self) -> int:
        """
        Index of the sensor of the global shared buffer.

        :type: int
        """
    @property
    def is_attached(self) -> bool:
        """
        Whether the sensor has been attached to a robot.

        :type: bool
        """
    @property
    def is_initialized(self) -> bool:
        """
        Whether the sensor has been initialized.


        .. note::
            Note that a sensor can be considered initialized even if its telemetry is not
            properly configured. If not, it must be done before being ready to use.

        :type: bool
        """
    @property
    def joint_index(self) -> int:
        """
        Index of the joint associated with the motor in the kinematic tree.

        :type: int
        """
    @property
    def joint_name(self) -> str:
        """
        Name of the joint associated with the motor.

        :type: str
        """
    @property
    def name(self) -> str:
        """
        Name of the sensor.

        :type: str
        """
    @property
    def position_limit_lower(self) -> float:
        """
        Maximum position of the actuated joint translated on motor side.

        :type: float
        """
    @property
    def position_limit_upper(self) -> float:
        """
        Minimum position of the actuated joint translated on motor side.

        :type: float
        """
    @property
    def velocity_limit(self) -> float:
        """
        Maximum velocity of the motor.

        :type: float
        """
    pass
class AbstractSensor():
    def __repr__(self) -> str: ...
    def get_options(self) -> dict: 
        """
        Configuration options of the sensor.
        """
    def set_options(self, arg2: dict) -> None: 
        """
        Set the configuration options of the sensor.

        :param sensorOptions:
            Dictionary with the parameters of the sensor.
        """
    @property
    def data(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @data.setter
    def data(self: jiminy_py.core.core.AbstractSensor) -> None:
        pass
    @property
    def fieldnames(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString:
        """
        Name of each element of the data measured by the sensor.

        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString
        """
    @property
    def index(self) -> int:
        """
        Index of the sensor of the global shared buffer.

        :type: int
        """
    @property
    def is_attached(self) -> bool:
        """
        Whether the sensor has been attached to a robot.

        :type: bool
        """
    @property
    def is_initialized(self) -> bool:
        """
        Whether the sensor has been initialized.


        .. note::
            Note that a sensor can be considered initialized even if its telemetry is not
            properly configured. If not, it must be done before being ready to use.

        :type: bool
        """
    @property
    def name(self) -> str:
        """
        Name of the sensor.

        :type: str
        """
    @property
    def type(self) -> str:
        """
        Type of the sensor.

        :type: str
        """
    pass
class LogicError(Exception, BaseException):
    pass
class BaseConstraint(AbstractConstraint):
    def __init__(self) -> None: ...
    def compute_jacobian_and_drift(self, arg2: numpy.ndarray, arg3: numpy.ndarray) -> None: 
        """
        Compute the jacobian and drift of the constraint.


        .. note::
            To avoid redundant computations, it assumes that `computeJointJacobians` and
            `framesForwardKinematics` has already been called on `model->pinocchioModel_`.

        :param q:
            Current joint position.
        :param v:
            Current joint velocity.
        """
    def reset(self, arg2: numpy.ndarray, arg3: numpy.ndarray) -> None: 
        """
        .. note::
            This method does not have to be called manually before running a simulation.
            The Engine is taking care of it.
        """
    __instance_size__ = 40
    type = 'UserConstraint'
    pass
class BaseController(AbstractController):
    def __init__(self) -> None: ...
    def compute_command(self, t: float, q: numpy.ndarray, v: numpy.ndarray, command: numpy.ndarray) -> None: 
        """
        Compute the command.

        It assumes that the robot internal state (including sensors) is consistent
        with other input arguments. It fetches the sensor data automatically.

        :param t:
            Current time.
        :param q:
            Current configuration vector.
        :param v:
            Current velocity vector.
        :param command:
            Output effort vector.
        """
    def internal_dynamics(self, t: float, q: numpy.ndarray, v: numpy.ndarray, u_custom: numpy.ndarray) -> None: 
        """
        Emulate custom phenomenon that are part of the internal dynamics of the system
        but not included in the physics engine.

        :param t:
            Current time.
        :param q:
            Current configuration vector.
        :param v:
            Current velocity vector.
        :param uCustom:
            Output effort vector.
        """
    def reset(self, reset_dynamic_telemetry: bool = False) -> None: ...
    __instance_size__ = 40
    pass
class BaseFunctionalController(AbstractController):
    pass
class ConstraintTree():
    @property
    def bounds_joints(self) -> dict:
        """
        :type: dict
        """
    @property
    def collision_bodies(self) -> list:
        """
        :type: list
        """
    @property
    def contact_frames(self) -> dict:
        """
        :type: dict
        """
    @property
    def user(self) -> dict:
        """
        :type: dict
        """
    pass
class ContactSensor(AbstractSensor):
    def __init__(self, name: str) -> None: ...
    def initialize(self, frame_name: str) -> None: ...
    @property
    def frame_index(self) -> int:
        """
        :type: int
        """
    @property
    def frame_name(self) -> str:
        """
        :type: str
        """
    __instance_size__ = 40
    fieldnames = ['FX', 'FY', 'FZ']
    type = 'ContactSensor'
    pass
class CouplingForce():
    @property
    def func(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def robot_index_1(self) -> int:
        """
        :type: int
        """
    @property
    def robot_index_2(self) -> int:
        """
        :type: int
        """
    @property
    def robot_name_1(self) -> str:
        """
        :type: str
        """
    @property
    def robot_name_2(self) -> str:
        """
        :type: str
        """
    pass
class CouplingForceVector():
    def __contains__(self, arg2: typing.Any) -> bool: ...
    def __delitem__(self, arg2: typing.Any) -> None: ...
    def __getitem__(self, arg2: typing.Any) -> typing.Any: ...
    def __iter__(self) -> typing.Any: ...
    def __len__(self) -> int: ...
    def __setitem__(self, arg2: typing.Any, arg3: typing.Any) -> None: ...
    def append(self, arg2: typing.Any) -> None: ...
    def extend(self, arg2: typing.Any) -> None: ...
    pass
class DistanceConstraint(AbstractConstraint):
    def __init__(self, first_frame_name: str, second_frame_name: str) -> None: ...
    @property
    def frame_indices(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def frame_names(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def reference_distance(self) -> float:
        """
        :type: float
        """
    @reference_distance.setter
    def reference_distance(self: jiminy_py.core.core.DistanceConstraint) -> None:
        pass
    __instance_size__ = 40
    type = 'DistanceConstraint'
    pass
class EffortSensor(AbstractSensor):
    def __init__(self, name: str) -> None: ...
    def initialize(self, motor_name: str) -> None: ...
    @property
    def motor_index(self) -> int:
        """
        :type: int
        """
    @property
    def motor_name(self) -> str:
        """
        :type: str
        """
    __instance_size__ = 40
    fieldnames = ['U']
    type = 'EffortSensor'
    pass
class EncoderSensor(AbstractSensor):
    def __init__(self, name: str) -> None: ...
    def initialize(self, motor_name: typing.Any = None, joint_name: typing.Any = None) -> None: ...
    @property
    def joint_index(self) -> int:
        """
        :type: int
        """
    @property
    def joint_name(self) -> str:
        """
        :type: str
        """
    @property
    def motor_index(self) -> int:
        """
        :type: int
        """
    @property
    def motor_name(self) -> str:
        """
        :type: str
        """
    __instance_size__ = 40
    fieldnames = ['Q', 'V']
    type = 'EncoderSensor'
    pass
class Engine():
    def __init__(self) -> None: ...
    def add_robot(self, robot: jiminy_py.core.Robot) -> None: ...
    @staticmethod
    def compute_forward_kinematics(robot: jiminy_py.core.Robot, q: numpy.ndarray, v: numpy.ndarray, a: numpy.ndarray) -> None: ...
    def compute_robots_dynamics(self, t_end: float, q_list: typing.Any, v_list: typing.Any) -> list: ...
    def get_options(self) -> dict: ...
    def get_robot(self, robot_name: str) -> jiminy_py.core.Robot: ...
    def get_robot_index(self, robot_name: str) -> int: ...
    def get_robot_state(self, robot_name: str) -> jiminy_py.core.RobotState: ...
    def get_simulation_options(self) -> dict: 
        """
        Get the options of the engine and all the robots.

        The key 'engine' maps to the engine options, whereas `robot.name` maps to the
        individual options of each robot for multi-robot simulations, 'robot' for
        single-robot simulations.
        """
    @staticmethod
    def read_log(fullpath: str, format: typing.Any = None) -> dict: 
        """
        Read a logfile from jiminy.

        .. note::
            This function supports both binary and hdf5 log.

        :param fullpath: Name of the file to load.
        :param format: Name of the file to load.

        :returns: Dictionary containing the logged constants and variables.
        """
    def register_coupling_force(self, robot_name_1: str, robot_name_2: str, frame_name_1: str, frame_name_2: str, force_func: typing.Any) -> None: 
        """
        Add a force linking both robots together.

        This function registers a callback function that links both robots by a given
        force. This function must return the force that the second robots applies to
        the first robot, in the global frame of the first frame, i.e. expressed at
        the origin of the first frame, in word coordinates.

        :param robotName1:
            Name of the robot receiving the force.
        :param robotName2:
            Name of the robot applying the force.
        :param frameName1:
            Frame on the first robot where the force is applied.
        :param frameName2:
            Frame on the second robot where the opposite force is applied.
        :param forceFunc:
            Callback function returning the force that robotName2 applies on
            robotName1, in the global frame of frameName1.
        """
    def register_impulse_force(self, robot_name: str, frame_name: str, t: float, dt: float, force: numpy.ndarray) -> None: 
        """
        Apply an impulse force on a frame for a given duration at the desired time.


        .. warning::
            The force must be given in the world frame.
        """
    def register_profile_force(self, robot_name: str, frame_name: str, force_func: typing.Any, update_period: float = 0.0) -> None: ...
    @typing.overload
    def register_viscoelastic_coupling_force(self, robot_name_1: str, robot_name_2: str, frame_name_1: str, frame_name_2: str, stiffness: numpy.ndarray, damping: numpy.ndarray, alpha: float = 0.5) -> None: ...
    @typing.overload
    def register_viscoelastic_coupling_force(self, robot_name: str, frame_name_1: str, frame_name_2: str, stiffness: numpy.ndarray, damping: numpy.ndarray, alpha: float = 0.5) -> None: ...
    @typing.overload
    def register_viscoelastic_directional_coupling_force(self, robot_name_1: str, robot_name_2: str, frame_name_1: str, frame_name_2: str, stiffness: float, damping: float, rest_length: float = 0.0) -> None: ...
    @typing.overload
    def register_viscoelastic_directional_coupling_force(self, robot_name: str, frame_name_1: str, frame_name_2: str, stiffness: float, damping: float, rest_length: float = 0.0) -> None: ...
    def remove_all_forces(self) -> None: ...
    @typing.overload
    def remove_coupling_forces(self, robot_name_1: str, robot_name_2: str) -> None: ...
    @typing.overload
    def remove_coupling_forces(self, robot_name: str) -> None: ...
    def remove_impulse_forces(self, robot_name: str) -> None: ...
    def remove_profile_forces(self, robot_name: str) -> None: ...
    def remove_robot(self, robot_name: str) -> None: ...
    def reset(self, reset_random_generator: bool = False, remove_all_forces: bool = False) -> None: ...
    def set_options(self, arg2: dict) -> None: ...
    def set_simulation_options(self, arg2: dict) -> None: 
        """
        Set the options of the engine and all the robots.

        :param simulationOptions:
            Dictionary gathering all the options. See
            `getSimulationOptions` for details about the hierarchy.
        """
    @typing.overload
    def simulate(self, t_end: float, q_init_dict: dict, v_init_dict: dict, a_init_dict: typing.Any = None, callback: typing.Any = None) -> None: 
        """
        Run a simulation of duration tEnd, starting at xInit.

        :param tEnd:
            Duration of the simulation.
        :param qInit:
            Initial configuration of every robots, i.e. at t=0.0.
        :param vInit:
            Initial velocity of every robots, i.e. at t=0.0.
        :param aInit:
            Initial acceleration of every robots, i.e. at t=0.0.
            Optional: Zero by default.
        :param callback:
            Callable that can be specified to abort simulation. It will be
            evaluated after every simulation step. Abort if false is returned.
        """
    @typing.overload
    def simulate(self, t_end: float, q_init: numpy.ndarray, v_init: numpy.ndarray, a_init: typing.Any = None, is_state_theoretical: bool = False, callback: typing.Any = None) -> None: ...
    @typing.overload
    def start(self, q_init_dict: dict, v_init_dict: dict, a_init_dict: typing.Any = None) -> None: 
        """
        Start the simulation


        .. warning::
            This function calls `reset` internally only if necessary, namely if it was not
            done manually at some point after stopping the previous simulation if any.

        :param qInit:
            Initial configuration of every robots.
        :param vInit:
            Initial velocity of every robots.
        :param aInit:
            Initial acceleration of every robots.
            Optional: Zero by default.
        """
    @typing.overload
    def start(self, q_init: numpy.ndarray, v_init: numpy.ndarray, a_init: typing.Any = None, is_state_theoretical: bool = False) -> None: ...
    def step(self, step_dt: float = -1) -> None: 
        """
        Advance the ongoing simulation forward by a given amount of time.

        Internally, the integrator must perform multiple steps, which may involve
        calling the controller to compute command or internal dynamics.

        :param stepSize:
            Duration of integration. For convenience, a sensible default will
            be selected automatically a negative value is specified. This
            default either corresponds the discrete-time controller update
            period, the discrete-time sensor update period, or stepper option
            'dtMax', depending on which one of this criteria is applicable, in
            this priority order.
            Optional: -1 by default.
        """
    def stop(self) -> None: 
        """
        Stop the simulation completely.

        It releases the lock on the robot and the telemetry, so that it is possible
        again to update the robot (for example to update the options, add or remove
        sensors...) and to register new variables or forces. Resuming a simulation is
        not supported.
        """
    def write_log(self, fullpath: str, format: str) -> None: ...
    @property
    def coupling_forces(self) -> jiminy_py.core.core.CouplingForceVector:
        """
        :type: jiminy_py.core.core.CouplingForceVector
        """
    @property
    def impulse_forces(self) -> dict:
        """
        :type: dict
        """
    @property
    def is_simulation_running(self) -> bool:
        """
        :type: bool
        """
    @property
    def log_data(self) -> dict:
        """
        :type: dict
        """
    @property
    def profile_forces(self) -> dict:
        """
        :type: dict
        """
    @property
    def robot_states(self) -> list:
        """
        :type: list
        """
    @property
    def robots(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def stepper_state(self) -> jiminy_py.core.core.StepperState:
        """
        :type: jiminy_py.core.core.StepperState
        """
    __instance_size__ = 40
    simulation_duration_max = 922337203.6854776
    telemetry_time_unit = 1e-10
    pass
class ForceSensor(AbstractSensor):
    def __init__(self, name: str) -> None: ...
    def initialize(self, frame_name: str) -> None: ...
    @property
    def frame_index(self) -> int:
        """
        :type: int
        """
    @property
    def frame_name(self) -> str:
        """
        :type: str
        """
    @property
    def joint_index(self) -> int:
        """
        :type: int
        """
    __instance_size__ = 40
    fieldnames = ['FX', 'FY', 'FZ', 'MX', 'MY', 'MZ']
    type = 'ForceSensor'
    pass
class FrameConstraint(AbstractConstraint):
    def __init__(self, frame_name: str, mask_fixed: typing.Any = None) -> None: ...
    def set_normal(self, arg2: numpy.ndarray) -> None: ...
    @property
    def dofs_fixed(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def frame_index(self) -> int:
        """
        :type: int
        """
    @property
    def frame_name(self) -> str:
        """
        :type: str
        """
    @property
    def local_rotation(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def reference_transform(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.SE3:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.SE3
        """
    @reference_transform.setter
    def reference_transform(self: jiminy_py.core.core.FrameConstraint) -> None:
        pass
    type = 'FrameConstraint'
    pass
class FunctionalController(BaseFunctionalController, AbstractController):
    def __init__(self, compute_command: typing.Any = None, internal_dynamics: typing.Any = None) -> None: ...
    def reset(self, reset_dynamic_telemetry: bool = False) -> None: ...
    pass
class GJKInitialGuess(Boost.Python.enum, int):
    BoundingVolumeGuess = jiminy_py.core.GJKInitialGuess.BoundingVolumeGuess
    CachedGuess = jiminy_py.core.GJKInitialGuess.CachedGuess
    DefaultGuess = jiminy_py.core.GJKInitialGuess.DefaultGuess
    __slots__ = ()
    names = {'DefaultGuess': jiminy_py.core.GJKInitialGuess.DefaultGuess, 'CachedGuess': jiminy_py.core.GJKInitialGuess.CachedGuess, 'BoundingVolumeGuess': jiminy_py.core.GJKInitialGuess.BoundingVolumeGuess}
    values = {0: jiminy_py.core.GJKInitialGuess.DefaultGuess, 1: jiminy_py.core.GJKInitialGuess.CachedGuess, 2: jiminy_py.core.GJKInitialGuess.BoundingVolumeGuess}
    pass
class HeightmapFunction():
    def __call__(self, position: numpy.ndarray) -> tuple: ...
    def __init__(self, heightmap_function: typing.Any, heightmap_type: jiminy_py.core.HeightmapType = jiminy_py.core.HeightmapType.GENERIC) -> None: ...
    @property
    def py_function(self) -> typing.Any:
        """
        :type: typing.Any
        """
    pass
class HeightmapType(Boost.Python.enum, int):
    CONSTANT = jiminy_py.core.HeightmapType.CONSTANT
    GENERIC = jiminy_py.core.HeightmapType.GENERIC
    STAIRS = jiminy_py.core.HeightmapType.STAIRS
    __slots__ = ()
    names = {'CONSTANT': jiminy_py.core.HeightmapType.CONSTANT, 'STAIRS': jiminy_py.core.HeightmapType.STAIRS, 'GENERIC': jiminy_py.core.HeightmapType.GENERIC}
    values = {1: jiminy_py.core.HeightmapType.CONSTANT, 2: jiminy_py.core.HeightmapType.STAIRS, 3: jiminy_py.core.HeightmapType.GENERIC}
    pass
class ImpulseForce():
    @property
    def dt(self) -> float:
        """
        :type: float
        """
    @property
    def force(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.Force:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.Force
        """
    @property
    def frame_index(self) -> int:
        """
        :type: int
        """
    @property
    def frame_name(self) -> str:
        """
        :type: str
        """
    @property
    def t(self) -> float:
        """
        :type: float
        """
    pass
class ImpulseForceVector():
    def __contains__(self, arg2: typing.Any) -> bool: ...
    def __delitem__(self, arg2: typing.Any) -> None: ...
    def __getitem__(self, arg2: typing.Any) -> typing.Any: ...
    def __iter__(self) -> typing.Any: ...
    def __len__(self) -> int: ...
    def __setitem__(self, arg2: typing.Any, arg3: typing.Any) -> None: ...
    def append(self, arg2: typing.Any) -> None: ...
    def extend(self, arg2: typing.Any) -> None: ...
    pass
class ImuSensor(AbstractSensor):
    def __init__(self, name: str) -> None: ...
    def initialize(self, frame_name: str) -> None: ...
    @property
    def frame_index(self) -> int:
        """
        :type: int
        """
    @property
    def frame_name(self) -> str:
        """
        :type: str
        """
    __instance_size__ = 40
    fieldnames = ['GyroX', 'GyroY', 'GyroZ', 'AccelX', 'AccelY', 'AccelZ']
    type = 'ImuSensor'
    pass
class JointConstraint(AbstractConstraint):
    def __init__(self, joint_name: str) -> None: ...
    @property
    def joint_index(self) -> int:
        """
        :type: int
        """
    @property
    def joint_name(self) -> str:
        """
        :type: str
        """
    @property
    def reference_configuration(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @reference_configuration.setter
    def reference_configuration(self: jiminy_py.core.core.JointConstraint) -> None:
        pass
    @property
    def rotation_dir(self) -> bool:
        """
        :type: bool
        """
    @rotation_dir.setter
    def rotation_dir(self: jiminy_py.core.core.JointConstraint) -> None:
        pass
    __instance_size__ = 40
    type = 'JointConstraint'
    pass
class JointModelType(Boost.Python.enum, int):
    FREE = jiminy_py.core.JointModelType.FREE
    LINEAR = jiminy_py.core.JointModelType.LINEAR
    NONE = jiminy_py.core.JointModelType.NONE
    PLANAR = jiminy_py.core.JointModelType.PLANAR
    ROTARY = jiminy_py.core.JointModelType.ROTARY
    ROTARY_UNBOUNDED = jiminy_py.core.JointModelType.ROTARY_UNBOUNDED
    SPHERICAL = jiminy_py.core.JointModelType.SPHERICAL
    __slots__ = ()
    names = {'NONE': jiminy_py.core.JointModelType.NONE, 'LINEAR': jiminy_py.core.JointModelType.LINEAR, 'ROTARY': jiminy_py.core.JointModelType.ROTARY, 'ROTARY_UNBOUNDED': jiminy_py.core.JointModelType.ROTARY_UNBOUNDED, 'PLANAR': jiminy_py.core.JointModelType.PLANAR, 'SPHERICAL': jiminy_py.core.JointModelType.SPHERICAL, 'FREE': jiminy_py.core.JointModelType.FREE}
    values = {0: jiminy_py.core.JointModelType.NONE, 1: jiminy_py.core.JointModelType.LINEAR, 2: jiminy_py.core.JointModelType.ROTARY, 3: jiminy_py.core.JointModelType.ROTARY_UNBOUNDED, 4: jiminy_py.core.JointModelType.PLANAR, 6: jiminy_py.core.JointModelType.SPHERICAL, 7: jiminy_py.core.JointModelType.FREE}
    pass
class BadControlFlow(LogicError, Exception, BaseException):
    pass
class LookupError(Exception, BaseException):
    pass
class Model():
    def __init__(self) -> None: ...
    def add_collision_bodies(self, body_names: typing.Any = [], ignore_meshes: bool = False) -> None: ...
    def add_constraint(self, name: str, constraint: jiminy_py.core.AbstractConstraint) -> None: ...
    def add_contact_points(self, frame_names: typing.Any = []) -> None: ...
    def add_frame(self, frame_name: str, parent_body_name: str, frame_placement: jiminy_py.core.pinocchio.pinocchio_pywrap.SE3) -> None: ...
    def compute_constraints(self, q: numpy.ndarray, v: numpy.ndarray) -> None: 
        """
        Compute jacobian and drift associated to all the constraints.

        The results are accessible using getConstraintsJacobian and
        getConstraintsDrift.

        .. note::
            It is assumed frames forward kinematics has already been called.

        :param q:
            Joint position.
        :param v:
            Joint velocity.
        """
    def copy(self) -> Model: ...
    def get_constraints_jacobian_and_drift(self) -> tuple: ...
    def get_extended_position_from_theoretical(self, mechanical_position: numpy.ndarray) -> numpy.ndarray: ...
    def get_extended_velocity_from_theoretical(self, mechanical_velocity: numpy.ndarray) -> numpy.ndarray: ...
    def get_options(self) -> dict: ...
    def get_theoretical_position_from_extended(self, flexibility_position: numpy.ndarray) -> numpy.ndarray: ...
    def get_theoretical_velocity_from_extended(self, flexibility_velocity: numpy.ndarray) -> numpy.ndarray: ...
    @typing.overload
    def initialize(self, urdf_path: str, has_freeflyer: bool = False, mesh_package_dirs: typing.Any = [], load_visual_meshes: bool = False) -> None: ...
    @typing.overload
    def initialize(self, pinocchio_model: jiminy_py.core.pinocchio.pinocchio_pywrap.Model, collision_model: typing.Any = None, visual_model: typing.Any = None) -> None: ...
    def remove_collision_bodies(self, body_names: typing.Any) -> None: ...
    def remove_constraint(self, name: str) -> None: ...
    def remove_contact_points(self, frame_names: typing.Any) -> None: ...
    def remove_frames(self, frame_names: typing.Any) -> None: ...
    def reset(self, generator: typing.Any) -> None: 
        """
        .. note::
            This method does not have to be called manually before running a simulation.
            The Engine is taking care of it.
        """
    def set_options(self, options: dict) -> None: ...
    @property
    def backlash_joint_indices(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_Index:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_Index
        """
    @property
    def backlash_joint_names(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString
        """
    @property
    def collision_body_indices(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_Index:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_Index
        """
    @property
    def collision_body_names(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString
        """
    @property
    def collision_data(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.GeometryData:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.GeometryData
        """
    @property
    def collision_model(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.GeometryModel:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.GeometryModel
        """
    @property
    def collision_model_th(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.GeometryModel:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.GeometryModel
        """
    @property
    def collision_pair_indices(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_IndexVector:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_IndexVector
        """
    @property
    def constraints(self) -> jiminy_py.core.core.ConstraintTree:
        """
        :type: jiminy_py.core.core.ConstraintTree
        """
    @property
    def contact_forces(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_Force:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_Force
        """
    @property
    def contact_frame_indices(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_Index:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_Index
        """
    @property
    def contact_frame_names(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString
        """
    @property
    def flexibility_joint_indices(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_Index:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_Index
        """
    @property
    def flexibility_joint_names(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString
        """
    @property
    def has_constraints(self) -> bool:
        """
        Returns true if at least one constraint is active on the robot.

        :type: bool
        """
    @property
    def has_freeflyer(self) -> bool:
        """
        :type: bool
        """
    @property
    def is_flexibility_enabled(self) -> bool:
        """
        :type: bool
        """
    @property
    def is_initialized(self) -> bool:
        """
        :type: bool
        """
    @property
    def log_acceleration_fieldnames(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString
        """
    @property
    def log_constraint_fieldnames(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString
        """
    @property
    def log_effort_fieldnames(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString
        """
    @property
    def log_f_external_fieldnames(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString
        """
    @property
    def log_position_fieldnames(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString
        """
    @property
    def log_velocity_fieldnames(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString
        """
    @property
    def mechanical_joint_indices(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_Index:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_Index
        """
    @property
    def mechanical_joint_names(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString
        """
    @property
    def mechanical_joint_position_indices(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def mechanical_joint_velocity_indices(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def mesh_package_dirs(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString
        """
    @property
    def nq(self) -> int:
        """
        :type: int
        """
    @property
    def nv(self) -> int:
        """
        :type: int
        """
    @property
    def nx(self) -> int:
        """
        :type: int
        """
    @property
    def pinocchio_data(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.Data:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.Data
        """
    @property
    def pinocchio_data_th(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.Data:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.Data
        """
    @property
    def pinocchio_model(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.Model:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.Model
        """
    @property
    def pinocchio_model_th(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.Model:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.Model
        """
    @property
    def urdf_path(self) -> str:
        """
        :type: str
        """
    @property
    def visual_data(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.GeometryData:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.GeometryData
        """
    @property
    def visual_model(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.GeometryModel:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.GeometryModel
        """
    @property
    def visual_model_th(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.GeometryModel:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.GeometryModel
        """
    __instance_size__ = 40
    pass
class NotImplementedError(LogicError, Exception, BaseException):
    pass
class OSError(Exception, BaseException):
    pass
class PCG32():
    def __call__(self) -> int: ...
    @typing.overload
    def __init__(self, state: int) -> None: ...
    @typing.overload
    def __init__(self, seed_seq: list) -> None: ...
    def seed(self, seed_seq: list) -> None: ...
    __instance_size__ = 40
    max = 4294967295
    min = 0
    pass
class PeriodicTabularProcess():
    def __call__(self, time: float) -> float: ...
    def grad(self, time: float) -> float: ...
    def reset(self, generator: typing.Any) -> None: ...
    @property
    def period(self) -> float:
        """
        :type: float
        """
    @property
    def wavelength(self) -> float:
        """
        :type: float
        """
    pass
class PeriodicGaussianProcess(PeriodicTabularProcess):
    def __init__(self, wavelength: float, period: float) -> None: ...
    __instance_size__ = 40
    pass
class PeriodicPerlinProcess1D():
    @typing.overload
    def __call__(self, arg2: float) -> float: ...
    @typing.overload
    def __call__(self, vec: numpy.ndarray) -> float: ...
    def __init__(self, wavelength: float, period: float, num_octaves: int = 6) -> None: ...
    @typing.overload
    def grad(self, arg2: float) -> numpy.ndarray: ...
    @typing.overload
    def grad(self, vec: numpy.ndarray) -> numpy.ndarray: ...
    def reset(self, generator: typing.Any) -> None: ...
    @property
    def num_octaves(self) -> int:
        """
        :type: int
        """
    @property
    def period(self) -> float:
        """
        :type: float
        """
    @property
    def wavelength(self) -> float:
        """
        :type: float
        """
    __instance_size__ = 40
    pass
class PeriodicPerlinProcess2D():
    @typing.overload
    def __call__(self, arg2: float, arg3: float) -> float: ...
    @typing.overload
    def __call__(self, vec: numpy.ndarray) -> float: ...
    def __init__(self, wavelength: float, period: float, num_octaves: int = 6) -> None: ...
    @typing.overload
    def grad(self, arg2: float, arg3: float) -> numpy.ndarray: ...
    @typing.overload
    def grad(self, vec: numpy.ndarray) -> numpy.ndarray: ...
    def reset(self, generator: typing.Any) -> None: ...
    @property
    def num_octaves(self) -> int:
        """
        :type: int
        """
    @property
    def period(self) -> float:
        """
        :type: float
        """
    @property
    def wavelength(self) -> float:
        """
        :type: float
        """
    __instance_size__ = 40
    pass
class PeriodicPerlinProcess3D():
    @typing.overload
    def __call__(self, arg2: float, arg3: float, arg4: float) -> float: ...
    @typing.overload
    def __call__(self, vec: numpy.ndarray) -> float: ...
    def __init__(self, wavelength: float, period: float, num_octaves: int = 6) -> None: ...
    @typing.overload
    def grad(self, arg2: float, arg3: float, arg4: float) -> numpy.ndarray: ...
    @typing.overload
    def grad(self, vec: numpy.ndarray) -> numpy.ndarray: ...
    def reset(self, generator: typing.Any) -> None: ...
    @property
    def num_octaves(self) -> int:
        """
        :type: int
        """
    @property
    def period(self) -> float:
        """
        :type: float
        """
    @property
    def wavelength(self) -> float:
        """
        :type: float
        """
    __instance_size__ = 40
    pass
class PeriodicFourierProcess(PeriodicTabularProcess):
    def __init__(self, wavelength: float, period: float) -> None: ...
    __instance_size__ = 40
    pass
class ProfileForce():
    @property
    def force(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.Force:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.Force
        """
    @property
    def frame_index(self) -> int:
        """
        :type: int
        """
    @property
    def frame_name(self) -> str:
        """
        :type: str
        """
    @property
    def func(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def update_period(self) -> float:
        """
        :type: float
        """
    pass
class ProfileForceVector():
    def __contains__(self, arg2: typing.Any) -> bool: ...
    def __delitem__(self, arg2: typing.Any) -> None: ...
    def __getitem__(self, arg2: typing.Any) -> typing.Any: ...
    def __iter__(self) -> typing.Any: ...
    def __len__(self) -> int: ...
    def __setitem__(self, arg2: typing.Any, arg3: typing.Any) -> None: ...
    def append(self, arg2: typing.Any) -> None: ...
    def extend(self, arg2: typing.Any) -> None: ...
    pass
class RandomPerlinProcess1D():
    @typing.overload
    def __call__(self, arg2: float) -> float: ...
    @typing.overload
    def __call__(self, vec: numpy.ndarray) -> float: ...
    def __init__(self, wavelength: float, num_octaves: int = 6) -> None: ...
    @typing.overload
    def grad(self, arg2: float) -> numpy.ndarray: ...
    @typing.overload
    def grad(self, vec: numpy.ndarray) -> numpy.ndarray: ...
    def reset(self, generator: typing.Any) -> None: ...
    @property
    def num_octaves(self) -> int:
        """
        :type: int
        """
    @property
    def wavelength(self) -> float:
        """
        :type: float
        """
    __instance_size__ = 40
    pass
class RandomPerlinProcess2D():
    @typing.overload
    def __call__(self, arg2: float, arg3: float) -> float: ...
    @typing.overload
    def __call__(self, vec: numpy.ndarray) -> float: ...
    def __init__(self, wavelength: float, num_octaves: int = 6) -> None: ...
    @typing.overload
    def grad(self, arg2: float, arg3: float) -> numpy.ndarray: ...
    @typing.overload
    def grad(self, vec: numpy.ndarray) -> numpy.ndarray: ...
    def reset(self, generator: typing.Any) -> None: ...
    @property
    def num_octaves(self) -> int:
        """
        :type: int
        """
    @property
    def wavelength(self) -> float:
        """
        :type: float
        """
    __instance_size__ = 40
    pass
class RandomPerlinProcess3D():
    @typing.overload
    def __call__(self, arg2: float, arg3: float, arg4: float) -> float: ...
    @typing.overload
    def __call__(self, vec: numpy.ndarray) -> float: ...
    def __init__(self, wavelength: float, num_octaves: int = 6) -> None: ...
    @typing.overload
    def grad(self, arg2: float, arg3: float, arg4: float) -> numpy.ndarray: ...
    @typing.overload
    def grad(self, vec: numpy.ndarray) -> numpy.ndarray: ...
    def reset(self, generator: typing.Any) -> None: ...
    @property
    def num_octaves(self) -> int:
        """
        :type: int
        """
    @property
    def wavelength(self) -> float:
        """
        :type: float
        """
    __instance_size__ = 40
    pass
class Robot(Model):
    def __init__(self, name: str = '') -> None: ...
    def attach_motor(self, motor: jiminy_py.core.AbstractMotor) -> None: ...
    def attach_sensor(self, sensor: jiminy_py.core.AbstractSensor) -> None: ...
    def compute_sensor_measurements(self, t: float, q: numpy.ndarray, v: numpy.ndarray, a: numpy.ndarray, u_motor: numpy.ndarray, f_external: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_Force) -> None: 
        """
        .. warning::
            It assumes that kinematic quantities have been updated previously and are
            consistent with the following input arguments. If not, one must call
            `pinocchio::forwardKinematics` and `pinocchio::updateFramePlacements`
            beforehand.
        """
    def copy(self) -> Robot: ...
    def detach_motor(self, joint_name: str) -> None: ...
    def detach_motors(self, joints_names: typing.Any = []) -> None: ...
    def detach_sensor(self, sensor_type: str, sensor_name: str) -> None: ...
    def detach_sensors(self, sensor_type: str = '') -> None: ...
    def get_model_options(self) -> dict: ...
    def get_motor(self, motor_name: str) -> jiminy_py.core.AbstractMotor: ...
    def get_options(self) -> dict: ...
    def get_sensor(self, sensor_type: str, sensor_name: str) -> jiminy_py.core.AbstractSensor: ...
    @typing.overload
    def initialize(self, urdf_path: str, has_freeflyer: bool = False, mesh_package_dirs: typing.Any = [], load_visual_meshes: bool = False) -> None: ...
    @typing.overload
    def initialize(self, pinocchio_model: jiminy_py.core.pinocchio.pinocchio_pywrap.Model, collision_model: typing.Any = None, visual_model: typing.Any = None) -> None: ...
    def set_model_options(self, model_options: dict) -> None: ...
    def set_options(self, robot_options: dict) -> None: ...
    @property
    def controller(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @controller.setter
    def controller(self: jiminy_py.core.core.Robot) -> None:
        pass
    @property
    def is_locked(self) -> bool:
        """
        :type: bool
        """
    @property
    def log_command_fieldnames(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_StdString
        """
    @property
    def motors(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def nmotors(self) -> int:
        """
        :type: int
        """
    @property
    def sensor_measurements(self) -> jiminy_py.core.core.SensorMeasurementTree:
        """
        :type: jiminy_py.core.core.SensorMeasurementTree
        """
    @property
    def sensors(self) -> typing.Any:
        """
        :type: typing.Any
        """
    __instance_size__ = 40
    pass
class RobotState():
    def __repr__(self) -> str: ...
    @property
    def a(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def command(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def f_external(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_Force:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.StdVec_Force
        """
    @property
    def q(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def u(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def u_custom(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def u_internal(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def u_motor(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def u_transmission(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def v(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    pass
class SensorMeasurementTree():
    def __contains__(self, key: tuple) -> bool: ...
    @typing.overload
    def __getitem__(self, sensor_info: tuple) -> numpy.ndarray: ...
    @typing.overload
    def __getitem__(self, sensor_type: str, sensor_name: str) -> numpy.ndarray: ...
    @typing.overload
    def __getitem__(self, sensor_type: str) -> numpy.ndarray: ...
    def __init__(self, sensor_measurements: dict) -> None: ...
    def __iter__(self) -> typing.Any: ...
    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...
    def items(self) -> list: ...
    @typing.overload
    def keys(self) -> list: ...
    @typing.overload
    def keys(self, sensor_type: str) -> list: ...
    def values(self) -> list: ...
    pass
class SimpleMotor(AbstractMotor):
    def __init__(self, motor_name: str) -> None: ...
    def initialize(self, arg2: str) -> None: ...
    __instance_size__ = 40
    pass
class SphereConstraint(AbstractConstraint):
    def __init__(self, frame_name: str, radius: float) -> None: ...
    @property
    def frame_index(self) -> int:
        """
        :type: int
        """
    @property
    def frame_name(self) -> str:
        """
        :type: str
        """
    @property
    def normal(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def radius(self) -> float:
        """
        :type: float
        """
    @property
    def reference_transform(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.SE3:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.SE3
        """
    @reference_transform.setter
    def reference_transform(self: jiminy_py.core.core.SphereConstraint) -> None:
        pass
    __instance_size__ = 40
    type = 'SphereConstraint'
    pass
class StepperState():
    def __repr__(self) -> str: ...
    @property
    def a(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def dt(self) -> float:
        """
        :type: float
        """
    @property
    def iter(self) -> int:
        """
        :type: int
        """
    @property
    def iter_failed(self) -> int:
        """
        :type: int
        """
    @property
    def q(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def t(self) -> float:
        """
        :type: float
        """
    @property
    def v(self) -> typing.Any:
        """
        :type: typing.Any
        """
    pass
class TimeStateBoolFunctor():
    def __call__(self, t: float, q: numpy.ndarray, v: numpy.ndarray) -> bool: ...
    pass
class TimeStateForceFunctor():
    def __call__(self, t: float, q: numpy.ndarray, v: numpy.ndarray) -> jiminy_py.core.pinocchio.pinocchio_pywrap.Force: ...
    pass
class WheelConstraint(AbstractConstraint):
    def __init__(self, frame_name: str, radius: float, ground_normal: numpy.ndarray, wheel_axis: numpy.ndarray) -> None: ...
    @property
    def axis(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def frame_index(self) -> int:
        """
        :type: int
        """
    @property
    def frame_name(self) -> str:
        """
        :type: str
        """
    @property
    def normal(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def radius(self) -> float:
        """
        :type: float
        """
    @property
    def reference_transform(self) -> jiminy_py.core.pinocchio.pinocchio_pywrap.SE3:
        """
        :type: jiminy_py.core.pinocchio.pinocchio_pywrap.SE3
        """
    @reference_transform.setter
    def reference_transform(self: jiminy_py.core.core.WheelConstraint) -> None:
        pass
    __instance_size__ = 40
    type = 'WheelConstraint'
    pass
class boost_type_index():
    """
    The class type_index holds implementation-specific information about a type, including the name of the type and means to compare two types for equality or collating order.
    """
    def __eq__(self, arg2: boost_type_index) -> typing.Any: 
        """
        C++ signature :
            struct _object * __ptr64 __eq__(class boost::typeindex::stl_type_index {lvalue},class boost::typeindex::stl_type_index)
        """
    def __ge__(self, arg2: boost_type_index) -> typing.Any: 
        """
        C++ signature :
            struct _object * __ptr64 __ge__(class boost::typeindex::stl_type_index {lvalue},class boost::typeindex::stl_type_index)
        """
    def __gt__(self, arg2: boost_type_index) -> typing.Any: 
        """
        C++ signature :
            struct _object * __ptr64 __gt__(class boost::typeindex::stl_type_index {lvalue},class boost::typeindex::stl_type_index)
        """
    def __le__(self, arg2: boost_type_index) -> typing.Any: 
        """
        C++ signature :
            struct _object * __ptr64 __le__(class boost::typeindex::stl_type_index {lvalue},class boost::typeindex::stl_type_index)
        """
    def __lt__(self, arg2: boost_type_index) -> typing.Any: 
        """
        C++ signature :
            struct _object * __ptr64 __lt__(class boost::typeindex::stl_type_index {lvalue},class boost::typeindex::stl_type_index)
        """
    def hash_code(self) -> int: 
        """
        Returns an unspecified value (here denoted by hash code) such that for all std::type_info objects referring to the same type, their hash code is the same.

        C++ signature :
            unsigned __int64 hash_code(class boost::typeindex::stl_type_index {lvalue})
        """
    def name(self) -> str: 
        """
        Returns an implementation defined null-terminated character string containing the name of the type. No guarantees are given; in particular, the returned string can be identical for several types and change between invocations of the same program.

        C++ signature :
            char const * __ptr64 name(class boost::typeindex::stl_type_index {lvalue})
        """
    def pretty_name(self) -> str: 
        """
        Human readible name.

        C++ signature :
            class std::basic_string<char,struct std::char_traits<char>,class std::allocator<char> > pretty_name(class boost::typeindex::stl_type_index {lvalue})
        """
    pass
class std_type_index():
    """
    The class type_index holds implementation-specific information about a type, including the name of the type and means to compare two types for equality or collating order.
    """
    def __eq__(self, arg2: std_type_index) -> typing.Any: 
        """
        C++ signature :
            struct _object * __ptr64 __eq__(class std::type_index {lvalue},class std::type_index)
        """
    def __ge__(self, arg2: std_type_index) -> typing.Any: 
        """
        C++ signature :
            struct _object * __ptr64 __ge__(class std::type_index {lvalue},class std::type_index)
        """
    def __gt__(self, arg2: std_type_index) -> typing.Any: 
        """
        C++ signature :
            struct _object * __ptr64 __gt__(class std::type_index {lvalue},class std::type_index)
        """
    def __le__(self, arg2: std_type_index) -> typing.Any: 
        """
        C++ signature :
            struct _object * __ptr64 __le__(class std::type_index {lvalue},class std::type_index)
        """
    def __lt__(self, arg2: std_type_index) -> typing.Any: 
        """
        C++ signature :
            struct _object * __ptr64 __lt__(class std::type_index {lvalue},class std::type_index)
        """
    def hash_code(self) -> int: 
        """
        Returns an unspecified value (here denoted by hash code) such that for all std::type_info objects referring to the same type, their hash code is the same.

        C++ signature :
            unsigned __int64 hash_code(class std::type_index {lvalue})
        """
    def name(self) -> str: 
        """
        Returns an implementation defined null-terminated character string containing the name of the type. No guarantees are given; in particular, the returned string can be identical for several types and change between invocations of the same program.

        C++ signature :
            char const * __ptr64 name(class std::type_index {lvalue})
        """
    def pretty_name(self) -> str: 
        """
        Human readible name.

        C++ signature :
            class std::basic_string<char,struct std::char_traits<char>,class std::allocator<char> > pretty_name(class std::type_index)
        """
    pass
def aba(pinocchio_model: pinocchio.pinocchio_pywrap.Model, pinocchio_data: pinocchio.pinocchio_pywrap.Data, q: numpy.ndarray, v: numpy.ndarray, u: numpy.ndarray, fext: pinocchio.pinocchio_pywrap.StdVec_Force) -> numpy.ndarray:
    """
    Compute ABA with external forces, store the result in Data::ddq and return it.
    """
def array_copyto(dst: typing.Any, src: typing.Any) -> None:
    pass
def build_geom_from_urdf(pinocchio_model: pinocchio.pinocchio_pywrap.Model, urdf_filename: str, geom_type: int, mesh_package_dirs: typing.Any = [], load_meshes: bool = True, make_meshes_convex: bool = False) -> pinocchio.pinocchio_pywrap.GeometryModel:
    pass
def build_models_from_urdf(urdf_path: str, has_freeflyer: bool, mesh_package_dirs: typing.Any = [], build_visual_model: bool = False, load_visual_meshes: bool = False) -> tuple:
    pass
def computeJMinvJt(pinocchio_model: pinocchio.pinocchio_pywrap.Model, pinocchio_data: pinocchio.pinocchio_pywrap.Data, J: numpy.ndarray, update_decomposition: bool = True) -> numpy.ndarray:
    pass
def computeKineticEnergy(pinocchio_model: pinocchio.pinocchio_pywrap.Model, pinocchio_data: pinocchio.pinocchio_pywrap.Data, q: numpy.ndarray, v: numpy.ndarray, update_kinematics: bool = True) -> float:
    """
    Computes the forward kinematics and the kinematic energy of the model for the given joint configuration and velocity given as input. The result is accessible through data.kinetic_energy.
    """
def crba(pinocchio_model: pinocchio.pinocchio_pywrap.Model, pinocchio_data: pinocchio.pinocchio_pywrap.Data, q: numpy.ndarray, fastmath: bool = False) -> numpy.ndarray:
    """
    Computes CRBA, store the result in Data and return it.
    """
def discretize_heightmap(heightmap: HeightmapFunction, x_min: float, x_max: float, x_unit: float, y_min: float, y_max: float, y_unit: float, must_simplify: bool = False) -> hppfcl.hppfcl.CollisionGeometry:
    pass
def get_frame_indices(pinocchio_model: pinocchio.pinocchio_pywrap.Model, frame_names: pinocchio.pinocchio_pywrap.StdVec_StdString) -> list:
    pass
@typing.overload
def get_joint_indices(pinocchio_model: pinocchio.pinocchio_pywrap.Model, joint_names: pinocchio.pinocchio_pywrap.StdVec_StdString) -> pinocchio.pinocchio_pywrap.StdVec_Index:
    pass
@typing.overload
def get_joint_indices(pinocchio_model: pinocchio.pinocchio_pywrap.Model, joint_names: pinocchio.pinocchio_pywrap.StdVec_StdString) -> list:
    pass
def get_joint_position_first_index(pinocchio_model: pinocchio.pinocchio_pywrap.Model, joint_name: str) -> int:
    pass
@typing.overload
def get_joint_type(joint_model: pinocchio.pinocchio_pywrap.JointModel) -> JointModelType:
    pass
@typing.overload
def get_joint_type(pinocchio_model: pinocchio.pinocchio_pywrap.Model, joint_index: int) -> JointModelType:
    pass
def interpolate_positions(pinocchio_model: pinocchio.pinocchio_pywrap.Model, times_in: numpy.ndarray, positions_in: numpy.ndarray, times_out: numpy.ndarray) -> numpy.ndarray:
    pass
def is_position_valid(pinocchio_model: pinocchio.pinocchio_pywrap.Model, position: numpy.ndarray, tol_abs: float = 1.1920928955078125e-07) -> bool:
    pass
def load_heightmap_from_binary(data: str) -> hppfcl.hppfcl.CollisionGeometry:
    pass
def load_robot_from_binary(data: str, mesh_dir_path: typing.Any = None, mesh_package_dirs: typing.Any = []) -> Robot:
    pass
def merge_heightmaps(heightmaps: typing.Any) -> HeightmapFunction:
    pass
def multi_array_copyto(dst: typing.Any, src: typing.Any) -> None:
    pass
@typing.overload
def normal(generator: typing.Any, mean: numpy.ndarray, stddev: numpy.ndarray) -> numpy.ndarray:
    pass
@typing.overload
def normal(generator: typing.Any, mean: float = 0.0, stddev: float = 1.0, size: typing.Any = None) -> typing.Any:
    pass
def periodic_perlin_ground(wavelength: float, period: float, num_octaves: int, seed: int) -> HeightmapFunction:
    pass
def periodic_stairs_ground(step_width: float, step_height: float, step_number: int, orientation: float) -> HeightmapFunction:
    pass
@typing.overload
def query_heightmap(heightmap: HeightmapFunction, positions: numpy.ndarray, heights: numpy.ndarray) -> None:
    pass
@typing.overload
def query_heightmap(heightmap: HeightmapFunction, positions: numpy.ndarray, heights: numpy.ndarray, normals: numpy.ndarray) -> None:
    pass
def random_perlin_ground(wavelength: float, num_octaves: int, seed: int) -> HeightmapFunction:
    pass
def random_tile_ground(size: numpy.ndarray, height_max: float, interp_delta: numpy.ndarray, sparsity: int, orientation: float, seed: int) -> HeightmapFunction:
    pass
@typing.overload
def rnea(pinocchio_model: pinocchio.pinocchio_pywrap.Model, pinocchio_data: pinocchio.pinocchio_pywrap.Data, q: numpy.ndarray, v: numpy.ndarray, a: numpy.ndarray) -> numpy.ndarray:
    """
    Compute the RNEA without external forces, store the result in Data and return it.

    Compute the RNEA with external forces, store the result in Data and return it.
    """
@typing.overload
def rnea(pinocchio_model: pinocchio.pinocchio_pywrap.Model, pinocchio_data: pinocchio.pinocchio_pywrap.Data, q: numpy.ndarray, v: numpy.ndarray, a: numpy.ndarray, fext: pinocchio.pinocchio_pywrap.StdVec_Force) -> numpy.ndarray:
    pass
def save_robot_to_binary(robot: Robot) -> typing.Any:
    pass
def seed(seed_value: int) -> None:
    """
    Initialize the pseudo-random number generator with the argument seed_value.

    C++ signature :
        void seed(unsigned int)
    """
@typing.overload
def sharedMemory(value: bool) -> None:
    """
    Share the memory when converting from Eigen to Numpy.

    C++ signature :
        void sharedMemory(bool)

    Status of the shared memory when converting from Eigen to Numpy.
    If True, the memory is shared when converting an Eigen::Matrix to a numpy.array.
    Otherwise, a deep copy of the Eigen::Matrix is performed.

    C++ signature :
        bool sharedMemory()
    """
@typing.overload
def sharedMemory() -> bool:
    pass
def solveJMinvJtv(pinocchio_data: pinocchio.pinocchio_pywrap.Data, v: numpy.ndarray, update_decomposition: bool = True) -> numpy.ndarray:
    pass
def sum_heightmaps(heightmaps: typing.Any) -> HeightmapFunction:
    pass
def unidirectional_periodic_perlin_ground(wavelength: float, period: float, num_octaves: int, orientation: float, seed: int) -> HeightmapFunction:
    pass
def unidirectional_random_perlin_ground(wavelength: float, num_octaves: int, orientation: float, seed: int) -> HeightmapFunction:
    pass
@typing.overload
def uniform(generator: typing.Any, lo: numpy.ndarray, hi: numpy.ndarray) -> numpy.ndarray:
    pass
@typing.overload
def uniform(generator: typing.Any, lo: float = 0.0, hi: float = 1.0, size: typing.Any = None) -> typing.Any:
    pass
@typing.overload
def uniform(generator: typing.Any) -> float:
    pass
_JIMINY_REQUIRED_MODULES = ('eigenpy', 'hppfcl', 'pinocchio')
__all__ = ['AbstractConstraint', 'AbstractController', 'AbstractMotor', 'AbstractSensor', 'BadControlFlow', 'BaseConstraint', 'BaseController', 'BaseFunctionalController', 'ConstraintTree', 'ContactSensor', 'CouplingForce', 'CouplingForceVector', 'DistanceConstraint', 'EffortSensor', 'EncoderSensor', 'Engine', 'ForceSensor', 'FrameConstraint', 'FunctionalController', 'GJKInitialGuess', 'HeightmapFunction', 'HeightmapType', 'ImpulseForce', 'ImpulseForceVector', 'ImuSensor', 'JointConstraint', 'JointModelType', 'LogicError', 'LookupError', 'Model', 'NotImplementedError', 'OSError', 'PCG32', 'PeriodicFourierProcess', 'PeriodicGaussianProcess', 'PeriodicPerlinProcess1D', 'PeriodicPerlinProcess2D', 'PeriodicPerlinProcess3D', 'PeriodicTabularProcess', 'ProfileForce', 'ProfileForceVector', 'RandomPerlinProcess1D', 'RandomPerlinProcess2D', 'RandomPerlinProcess3D', 'Robot', 'RobotState', 'SensorMeasurementTree', 'SimpleMotor', 'SphereConstraint', 'StepperState', 'TimeStateBoolFunctor', 'TimeStateForceFunctor', 'WheelConstraint', 'aba', 'array_copyto', 'boost_type_index', 'build_geom_from_urdf', 'build_models_from_urdf', 'computeJMinvJt', 'computeKineticEnergy', 'crba', 'discretize_heightmap', 'get_frame_indices', 'get_joint_indices', 'get_joint_position_first_index', 'get_joint_type', 'interpolate_positions', 'is_position_valid', 'load_heightmap_from_binary', 'load_robot_from_binary', 'merge_heightmaps', 'multi_array_copyto', 'normal', 'periodic_perlin_ground', 'periodic_stairs_ground', 'query_heightmap', 'random_perlin_ground', 'random_tile_ground', 'rnea', 'save_robot_to_binary', 'seed', 'sharedMemory', 'solveJMinvJtv', 'std_type_index', 'sum_heightmaps', 'unidirectional_periodic_perlin_ground', 'unidirectional_random_perlin_ground', 'uniform', 'get_cmake_module_path', 'get_include', 'get_libraries', '__version__', '__raw_version__']
__raw_version__ = '1.8.13'
__version__ = '1.8.13'
_are_all_dependencies_available = False
_is_boost_shared = False
_module_name = 'serialization'
_module_real_path = 'pinocchio.pinocchio_pywrap.serialization'
_module_sym_path = 'pinocchio.serialization'
_submodules: list # value = [('cholesky', <module 'jiminy_py.core.pinocchio.pinocchio_pywrap.cholesky'>), ('liegroups', <module 'jiminy_py.core.pinocchio.pinocchio_pywrap.liegroups'>), ('rpy', <module 'jiminy_py.core.pinocchio.pinocchio_pywrap.rpy'>), ('serialization', <module 'jiminy_py.core.pinocchio.pinocchio_pywrap.serialization'>)]
name = 'uniform'
path = 'D:/a/jiminy/jiminy/workspace/install/lib'
_find_spec = importlib.util.find_spec
_get_config_var = sysconfig.get_config_var
_import_module = importlib.import_module
