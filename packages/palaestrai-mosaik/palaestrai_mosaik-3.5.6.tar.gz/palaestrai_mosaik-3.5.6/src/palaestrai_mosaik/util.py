"""This module contains the function :func:`.load_funcs` to load a
mosaik environment.

This comprises to instantiate a world object und retrieve sensor and
actuator descriptions

"""

from __future__ import annotations

import logging
from copy import copy
from datetime import datetime
from importlib import import_module
from socket import socket
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

import numpy as np
from palaestrai.agent.actuator_information import ActuatorInformation
from palaestrai.agent.sensor_information import SensorInformation
from palaestrai.types import Space

from .config import DATE_FORMAT, ENVIRONMENT_LOGGER_NAME

if TYPE_CHECKING:
    from mosaik import AsyncWorld, World

    from .aio.mosaik_environment import (
        MosaikEnvironment as MosaikEnvironmentAsync,
    )
    from .mp.mosaik_environment import MosaikEnvironment

LOG = logging.getLogger(f"{ENVIRONMENT_LOGGER_NAME}.util")


def load_funcs(
    module_name: str, description_func: str, instance_func: str
) -> Tuple[
    Callable[[Dict[str, Any]], World, AsyncWorld],
    Callable[
        [Dict[str, Any]],
        Tuple[
            List[Union[SensorInformation, Dict[str, Any]]],
            List[Union[ActuatorInformation, Dict[str, Any]]],
        ],
    ],
]:
    """Load the description functions.

    Expects a dictionary containing the keys *"module"*,
    *"description_func"*, and "instance_func". *"module"* can
    either be a python module or a python class. The path segments
    for modules are separated by a dot "." and a class is separated
    by a colon ":", e.g., if *descriptor* is a module::

        {
            "module": "midas.adapter.harlequin.descriptor",
            "description_func": "describe",
            "instance_func": "get_world",
        }

    or, if *Descriptor* is a class::

        {
            "module": "midas.adapter.harlequin:Descriptor",
            "description_func": "describe",
            "instance_func": "get_world",
        }


    Parameters
    ----------
    params : dict
        A *dict* containing the keys as described above.

    Returns
    -------
    tuple
        A *tuple* of the description function and the instance
        function.

    """

    if ":" in module_name:
        module, clazz = module_name.split(":")
        module = import_module(module)
        obj = getattr(module, clazz)()
    else:
        obj = import_module(module_name)

    dscr_func = getattr(obj, description_func)
    inst_func = getattr(obj, instance_func)

    return dscr_func, inst_func


def load_functions(env: Union[MosaikEnvironment, MosaikEnvironmentAsync]):
    LOG.debug("%s loading description and instance functions ...", log_(env))
    try:
        description, instance = load_funcs(
            env.module, env.description_func, env.instance_func
        )
    except Exception:
        msg = (
            "%s: Error during loading of loader functions. Module: '%s' "
            "description function: '%s', instance function: '%s'",
            log_(env),
            env.module,
            env.description_func,
            env.instance_func,
        )
        raise ValueError(msg)

    return description, instance


def parse_start_date(start_date: str, rng: np.random.RandomState):
    if start_date is None:
        LOG.info("Start_date is None, time information will not be available")
        return None
    if "random" in start_date:
        if start_date == "random":
            year = 2020
            month = rng.randint(1, 13)
        else:
            fixed, _ = start_date.split("_")

            if "-" in fixed:
                year, month = fixed.split("-")
                year = int(year)
                month = int(month)
            else:
                year = int(fixed)
                month = rng.randint(1, 13)
        start_date = (
            f"{year:04d}-{month:02d}-"
            f"{rng.randint(1, 29):02d} "
            f"{rng.randint(0, 24):02d}:00:00+0100"
        )
    try:
        datetime.strptime(start_date, DATE_FORMAT)
    except ValueError:
        LOG.exception(
            "Unable to parse start_date %s (format string: %s). "
            "Expect errors ahead if this is not by intention.",
            start_date,
            DATE_FORMAT,
        )
    return start_date


def parse_end(end: Union[str, int]) -> int:
    """Read the *end* value from the params dict.

    The *end* value is an integer, but sometimes it is provided
    as float, or as str like '15*60'. In the latter case, the
    str is evaluated (i.e., multiplied). In any case, *end* is
    returned as int.

    """
    if isinstance(end, str):
        smnds = end.split("+")
        end = 0
        for p in smnds:
            parts = p.split("*")
            prod = 1
            for part in parts:
                prod *= float(part)
            end += prod
    return int(end)


def log_(env):
    return f"MosaikEnvironment (id={id(env)}, uid={env.uid})"


def find_free_port():
    port = 0
    with socket() as s:
        s.bind(("", 0))
        port = s.getsockname()[1]
        s.close()
    return port


def load_sensors_and_actuators(
    env: Union[MosaikEnvironment, MosaikEnvironmentAsync], description_fnc
):
    try:
        sensors, actuators, world_state = description_fnc(env.mosaik_params)
    except Exception:
        msg = (
            "%s: Error during calling the description function. Params %s",
            log_(env),
            str(env.mosaik_params),
        )
        LOG.exception(msg)
        raise ValueError(msg)

    env.sensors, env.sen_map = create_sensors(sensors)
    env.actuators, env.act_map = create_actuators(actuators)

    if not env.sensors or not env.actuators:
        msg = (
            "%s: No sensors and/or actuators defined in the environment!! "
            "Sensors=%s, Actuators=%s",
            log_(env),
            str(env.sensors),
            str(env.actuators),
        )
        raise ValueError(msg)

    return world_state


def load_start_date(
    env: Union[MosaikEnvironment, MosaikEnvironmentAsync], world_state
) -> Optional[datetime]:
    start_date = parse_start_date(env.start_date, env.rng)
    if start_date is not None:
        env.mosaik_params["meta_params"]["start_date"] = start_date
    elif "start_date" in world_state:
        # Start_date was not provided via experiment but is mandatory
        # in the environment
        if env._infer_start_date:
            env.mosaik_params["meta_params"]["start_date"] = world_state[
                "start_date"
            ]
        else:
            msg = "start_date was not provided but is mandatory for this mosaik world."
            raise ValueError(msg)
    else:
        return None
    return datetime.strptime(
        env.mosaik_params["meta_params"]["start_date"], DATE_FORMAT
    )


def create_sensors(sensor_defs) -> List[SensorInformation]:
    """Create sensors from the sensor description.

    The description is provided during initialization.

    Returns
    -------
    list
        The *list* containing the created sensor objects.

    """
    sensors = []
    sensor_map = {}
    for sensor in sensor_defs:
        if isinstance(sensor, SensorInformation):
            sensors.append(sensor)
            uid = sensor.uid
        else:
            uid = str(
                sensor.get("uid", sensor.get("sensor_id", "Unnamed Sensor"))
            )
            try:
                space = Space.from_string(
                    sensor.get("space", sensor.get("observation_space", None))
                )
                value = sensor.get("value", None)
                sensors.append(
                    SensorInformation(
                        uid=uid,
                        space=space,
                        value=value,
                    )
                )
            except RuntimeError:
                LOG.exception(sensor)
                raise
        sensor_map[uid] = copy(sensors[-1])

    return sensors, sensor_map


def create_actuators(actuator_defs) -> List[ActuatorInformation]:
    """Create actuators from the actuator description.

    The description is provided during initialization.

    Returns
    -------
    list
        The *list* containing the created actuator objects.

    """
    actuators = []
    actuator_map = {}
    for actuator in actuator_defs:
        if isinstance(actuator, ActuatorInformation):
            actuators.append(actuator)
            uid = actuator.uid
        else:
            uid = str(
                actuator.get(
                    "uid", actuator.get("actuator_id", "Unnamed Actuator")
                )
            )

            try:
                space = Space.from_string(
                    actuator.get("space", actuator.get("action_space", None))
                )
                value = actuator.get(
                    "value",
                    actuator.get("setpoint", None),
                )
                actuators.append(
                    ActuatorInformation(
                        value=value,
                        uid=uid,
                        space=space,
                    )
                )
            except RuntimeError:
                LOG.exception(actuator)
                raise
        actuator_map[uid] = copy(actuators[-1])
    return actuators, actuator_map


def load_sensors_from_queue_data(
    env: Union[MosaikEnvironment, MosaikEnvironmentAsync], data
):
    sensors = []
    for uid, value in data.items():
        # Special cases for ticks and timestamp
        if uid == "simtime_ticks":
            env.simtime_ticks = value
            continue
        if uid == "simtime_timestamp":
            if value is not None:
                try:
                    env.simtime_timestamp = datetime.strptime(
                        data["simtime_timestamp"], DATE_FORMAT
                    )
                except ValueError:
                    LOG.error(
                        "Unable to parse simtime_timestamp: "
                        f"{data['simtime_timestamp']}"
                    )
            continue

        new_sensor = copy(env.sen_map[uid])
        # new_sensor.value = value
        new_sensor.value = np.array(value, dtype=new_sensor.space.dtype)
        sensors.append(new_sensor)
    env.sensors = sensors
