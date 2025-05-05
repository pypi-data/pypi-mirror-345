"""This module contains the :class:`MosaikEnvironment`, which
allows to run mosaik co-simulations with palaestrAI.

"""

from __future__ import annotations

import asyncio
import logging
import multiprocessing
import queue
import sys
import threading
from copy import copy
from datetime import datetime
from multiprocessing import Event
from typing import Any, Callable, Dict, List, Optional, Union

import mosaik
import mosaik_api_v3
import numpy as np
from loguru import logger
from numpy.random import RandomState
from palaestrai.agent.actuator_information import ActuatorInformation
from palaestrai.agent.sensor_information import SensorInformation
from palaestrai.environment.environment import Environment
from palaestrai.environment.environment_baseline import EnvironmentBaseline
from palaestrai.environment.environment_state import EnvironmentState
from palaestrai.types import SimTime, Space
from palaestrai.util import seeding

from .. import util
from ..config import DATE_FORMAT, ENVIRONMENT_LOGGER_NAME
from ..util import log_
from .simulator import ARLSyncSimulator

LOG = logging.getLogger(ENVIRONMENT_LOGGER_NAME)


class MosaikEnvironment(Environment):
    """The Mosaik environment for palaestrAI.

    Parameters
    ==========
    arl_sync_host: str, optional
        Host name for the ARLSyncSimulator. Will probably always be
        localhost.
    arl_sync_port: int, optional
        Specify the port on which the ARLSyncSimulator should listen.
        This is required for the communication with mosaik. Default
        value is 0, i.e. it will be tried to get a port automatically.
        Any other positive number will be used as port if possible.
    silent: bool, optional
        Setting silent to True will tell mosaik to be silent regarding
        terminal outputs.
    no_extra_step: bool, optional
        By default, end will be incremented by one. Background is that
        mosaik starts counting by 0 and ends and end-1. Adding 1 will
        force to have the last step at end. Since from the palaestrAI
        perspective, the first step is 'lost', this makes up for it.
        Setting this to True will prevent this behavior
    simulation_timeout: int, optional
        Timeout for the simulation when no actuator data is received.
        Although it can have different reasons, when no actuator data
        is received, it will be assumed that an error occured in either
        one of the agents or the palaestrAI execution itself and the
        simulation will shutdown after that timeout. Default value is
        60 (seconds).

    """

    def __init__(
        self,
        uid: str,
        *,
        seed: int,
        module: str,
        description_func: str,
        instance_func: str,
        arl_sync_freq: int,
        end: Union[int, str],
        start_date: Optional[str] = None,
        infer_start_date: bool = False,
        # arl_sync_host: str = "localhost",
        # arl_sync_port: int = 0,
        silent: bool = False,
        no_extra_step: bool = False,
        simulation_timeout: int = 60,
        # reward: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        broker_uri: str = "",
        **kwargs,
    ):
        super().__init__(uid, broker_uri, seed)
        self.rng: RandomState = seeding.np_random(self.seed)[0]

        self.sensor_queue: Optional[queue.Queue] = None
        self.actuator_queue: Optional[queue.Queue] = None
        self.sim_terminate: Optional[multiprocessing.Event] = None
        self.sim_finished: Optional[multiprocessing.Event] = None
        self.sync_terminate: Optional[multiprocessing.Event] = None
        self.sync_finished: Optional[multiprocessing.Event] = None
        self._mp_ctx = None
        self.module = module
        self.description_func = description_func
        self.instance_func = instance_func
        self._simulation_timeout = simulation_timeout
        self.start_date = start_date
        self.infer_start_date = infer_start_date

        # self._arl_sync_host = arl_sync_host
        # self._arl_sync_port = (
        #     arl_sync_port if arl_sync_port != 0 else util.find_free_port()
        # )
        # LOG.warning(
        #     "%s attempting to use port %s.",
        #     log_(self),
        #     str(self._arl_sync_port),
        # )
        self.mosaik_params = {} if params is None else params
        self.mosaik_params["meta_params"] = {
            "seed": self.rng.randint(sys.maxsize),
            "end": util.parse_end(end) + (0 if no_extra_step else 1),
            "arl_sync_freq": arl_sync_freq,
            "silent": silent,
        }

        self._prev_simtime = SimTime(simtime_ticks=0)
        self.simtime_ticks: int = 0
        self.simtime_timestamp = None

    def _prepare_mp_components(self):
        self._mp_ctx = multiprocessing.get_context("spawn")
        self.sensor_queue = self._mp_ctx.Queue(1)
        self.actuator_queue = self._mp_ctx.Queue(1)
        self.sim_terminate = self._mp_ctx.Event()
        self.sim_finished = self._mp_ctx.Event()
        self.sync_terminate = self._mp_ctx.Event()
        self.sync_finished = self._mp_ctx.Event()

    # def _load_sensors_and_actuators(self, description_fnc):
    #     try:
    #         sensor_description, actuator_description, static_world_state = (
    #             description_fnc(self._mosaik_params)
    #         )
    #     except Exception:
    #         msg = (
    #             "%s: Error during calling the description function. Params %s",
    #             log_(self),
    #             str(self._mosaik_params),
    #         )
    #         LOG.exception(msg)
    #         raise ValueError(msg)

    #     self.sensors, self.sen_map = create_sensors(sensor_description)
    #     self.actuators, self.act_map = create_actuators(actuator_description)
    #     if not self.sensors or not self.actuators:
    #         msg = (
    #             "%s: No sensors and/or actuators defined in the environment!! "
    #             "Sensors=%s, Actuators=%s",
    #             log_(self),
    #             str(self.sensors),
    #             str(self.actuators),
    #         )
    #         raise ValueError(msg)
    #         # return EnvironmentBaseline(sensors_available=None, actuators_available=None)

    #     return static_world_state

    # def _load_start_date(self, world_state):
    #     start_date = util.parse_start_date(self._start_date, self.rng)
    #     if start_date is not None:
    #         self._mosaik_params["meta_params"]["start_date"] = start_date
    #     elif "start_date" in world_state:
    #         # Start_date was not provided via experiment but is mandatory
    #         # in the environment
    #         if self._infer_start_date:
    #             self._mosaik_params["meta_params"]["start_date"] = world_state[
    #                 "start_date"
    #             ]
    #         else:
    #             msg = (
    #                 "start_date was not provided but is mandatory for "
    #                 "this mosaik world."
    #             )
    #             raise ValueError(msg)

    def start_environment(self):
        LOG.info("%s starting Mosaik Co-simulation ...", log_(self))
        self._prepare_mp_components()

        description, instance = util.load_functions(self)
        static_world_state = util.load_sensors_and_actuators(self, description)
        simtime = SimTime(simtime_ticks=0)
        util.load_start_date(self, static_world_state)

        LOG.debug(f"{log_(self)} starting Co-Simulation ...")
        self.sim_proc = self._mp_ctx.Process(
            target=_start_mosaik,
            args=(instance, self.mosaik_params),
            kwargs={
                "sensors": [s.uid for s in self.sensors],
                "actuators": [a.uid for a in self.actuators],
                "sensor_queue": self.sensor_queue,
                "actuator_queue": self.actuator_queue,
                "sim_finished": self.sim_finished,
                "sync_finished": self.sync_finished,
                "sync_terminate": self.sync_terminate,
                "timeout": self._simulation_timeout,
            },
        )
        self.sim_proc.start()

        LOG.info(
            "%s finished setup. Co-simulation is now running. Now waiting for "
            "initial sensor readings ...",
            log_(self),
        )
        done, data = self.sensor_queue.get(
            block=True, timeout=self._simulation_timeout
        )
        util.load_sensors_from_queue_data(self, data)

        return EnvironmentBaseline(
            sensors_available=self.sensors,
            actuators_available=self.actuators,
            simtime=simtime,
        )

    def update(self, actuators):
        data = {}
        self._simtime_ticks = 0
        self._simtime_timestamp = None

        LOG.debug("%s sending actuators to simulation ...", log_(self))
        for actuator in actuators:
            data[actuator.uid] = actuator.value
        self.actuator_queue.put(data, timeout=5)

        LOG.debug("%s waiting for sensor readings ...", log_(self))
        done, data = self.sensor_queue.get(
            block=True, timeout=self._simulation_timeout
        )
        util.load_sensors_from_queue_data(self, data)

        self._prev_simtime = SimTime(
            simtime_ticks=self.simtime_ticks,
            simtime_timestamp=self.simtime_timestamp,
        )

        rewards = self.reward(self.sensors, actuators)

        if not done:
            LOG.info("%s update complete.", log_(self))
        else:
            LOG.info("%s simulation finished! Terminating.", log_(self))

        return EnvironmentState(
            sensor_information=self.sensors,
            rewards=rewards,
            done=done,
            simtime=self._prev_simtime,
        )

    def shutdown(self, reset=False):
        LOG.info(
            "%s starting shutdown of simulation process ...",
            log_(self),
        )
        self.sim_finished.wait(3)
        if not self.sim_finished.is_set():
            LOG.debug(
                "%s simulation is still running. Attempting to shut down ...",
                log_(self),
            )
            self.sync_terminate.set()
            self.sync_finished.wait(3)
            self.sim_finished.wait(3)
            if self.sim_finished.is_set():
                self.sim_proc.join()
                LOG.debug("%s: Simulation process joined!", log_(self))
            else:
                LOG.info(
                    "%s waiting a bit more for the simulation to finish ...",
                    log_(self),
                )
                self.sim_proc.join(self._simulation_timeout)
                self.sim_proc.kill()
                LOG.debug(
                    "%s: Simulation process killed ... better be sure!",
                    log_(self),
                )

        self.actuator_queue.close()
        self.sensor_queue.close()
        self.is_terminal = not reset

        LOG.info("%s: Simulation terminated gracefully", log_(self))


#     def _get_sensors_from_queue_data(self, data):
#         sensors = []
#         for uid, value in data.items():
#             # Special cases for ticks and timestamp
#             if uid == "simtime_ticks":
#                 self._simtime_ticks = value
#                 continue
#             if uid == "simtime_timestamp":
#                 if value is not None:
#                     try:
#                         self._simtime_timestamp = datetime.strptime(
#                             data["simtime_timestamp"], DATE_FORMAT
#                         )
#                     except ValueError:
#                         LOG.error(
#                             "Unable to parse simtime_timestamp: "
#                             f"{data['simtime_timestamp']}"
#                         )
#                 continue

#             new_sensor = copy(self.sen_map[uid])
#             # new_sensor.value = value
#             new_sensor.value = np.array(value, dtype=new_sensor.space.dtype)
#             sensors.append(new_sensor)
#         return sensors

#     async def _mosaik_entrypoint(self, instance: mosaik.AsyncWorld):
#         loop = asyncio.get_event_loop()
#         if loop.is_running():
#             self.sim_proc = await loop.create_task(
#                 _test(
#                     # instance,
#                     # self._mosaik_params,
#                     # sensors=[s.uid for s in self.sensors],
#                     # actuators=[a.uid for a in self.actuators],
#                     # sensor_queue=self.sensor_queue,
#                     # actuator_queue=self.actuator_queue,
#                     # sim_finished=self.sim_finished,
#                     # sync_finished=self.sync_finished,
#                     # sync_terminate=self.sync_terminate,
#                 ),
#             )
#             # loop.run_until_complete(_test)
#         else:
#             LOG.info("Loop is not running")

#         # self.sim_proc = asyncio.run_coroutine_threadsafe(coro, loop)
#         # await self.sim_proc


# def create_sensors(sensor_defs) -> List[SensorInformation]:
#     """Create sensors from the sensor description.

#     The description is provided during initialization.

#     Returns
#     -------
#     list
#         The *list* containing the created sensor objects.

#     """
#     sensors = []
#     sensor_map = {}
#     for sensor in sensor_defs:
#         if isinstance(sensor, SensorInformation):
#             sensors.append(sensor)
#             uid = sensor.uid
#         else:
#             uid = str(sensor.get("uid", sensor.get("sensor_id", "Unnamed Sensor")))
#             try:
#                 space = Space.from_string(
#                     sensor.get("space", sensor.get("observation_space", None))
#                 )
#                 value = sensor.get("value", None)
#                 sensors.append(
#                     SensorInformation(
#                         uid=uid,
#                         space=space,
#                         value=value,
#                     )
#                 )
#             except RuntimeError:
#                 LOG.exception(sensor)
#                 raise
#         sensor_map[uid] = copy(sensors[-1])

#     return sensors, sensor_map


# def create_actuators(actuator_defs) -> List[ActuatorInformation]:
#     """Create actuators from the actuator description.

#     The description is provided during initialization.

#     Returns
#     -------
#     list
#         The *list* containing the created actuator objects.

#     """
#     actuators = []
#     actuator_map = {}
#     for actuator in actuator_defs:
#         if isinstance(actuator, ActuatorInformation):
#             actuators.append(actuator)
#             uid = actuator.uid
#         else:
#             uid = str(
#                 actuator.get("uid", actuator.get("actuator_id", "Unnamed Actuator"))
#             )

#             try:
#                 space = Space.from_string(
#                     actuator.get("space", actuator.get("action_space", None))
#                 )
#                 value = actuator.get(
#                     "value",
#                     actuator.get("setpoint", None),
#                 )
#                 actuators.append(
#                     ActuatorInformation(
#                         value=value,
#                         uid=uid,
#                         space=space,
#                     )
#                 )
#             except RuntimeError:
#                 LOG.exception(actuator)
#                 raise
#         actuator_map[uid] = copy(actuators[-1])
#     return actuators, actuator_map


# def _start_simulator(host, port, q1, q2, end, timeout, terminate, finished):
#     argv_backup = sys.argv
#     sys.argv = [
#         argv_backup[0],
#         "--remote",
#         f"{host}:{port}",
#         "--log-level",
#         "error",
#     ]

#     mosaik_api_v3.start_simulation(
#         ARLSyncSimulator(q1, q2, terminate, finished, end, timeout)
#     )
#     sys.argv = argv_backup


# async def _test(*args, **kwargs):
#     print("Hello from coroutine!")


# async def _start_mosaik(
#     get_world: mosaik.AsyncWorld,
#     params: Dict[str, Any],
#     *,
#     sensors: list[str],
#     actuators: list[str],
#     sensor_queue: queue.Queue,
#     actuator_queue: queue.Queue,
#     sim_finished: asyncio.Event,
#     sync_terminate: asyncio.Event,
#     sync_finished: asyncio.Event,
#     timeout: int,
# ):
#     print("Starting mosaik")
#     meta_params = params["meta_params"]
#     end = meta_params["end"]
#     LOG.debug("Attempting to retrieve world object ...")
#     world, entities = await get_world(params)
#     LOG.debug("Starting ARLSyncSimulator ...")
#     world.sim_config["ARLSyncSimulator"] = {
#         "python": "palaestrai_mosaik.simulator:ARLSyncSimulator"
#     }
#     arlsim = await world.start(
#         "ARLSyncSimulator",
#         step_size=meta_params["arl_sync_freq"],
#         start_date=meta_params.get("start_date", None),
#         sensor_queue=sensor_queue,
#         actuator_queue=actuator_queue,
#         sync_finished=sync_finished,
#         sync_terminate=sync_terminate,
#         end=end,
#         timeout=timeout,
#     )
#     LOG.debug("Connecting sensor entities ...")
#     for uid in sensors:
#         sid, eid, attr = uid.split(".")
#         full_id = f"{sid}.{eid}"
#         sensor_model = await arlsim.ARLSensor(uid=uid)
#         LOG.debug("Connecting %s ...", full_id)
#         world.connect(entities[full_id], sensor_model, (attr, "reading"))

#     LOG.debug("Connecting actuator entities ...")
#     for uid in actuators:
#         sid, eid, attr = uid.split(".")
#         full_id = f"{sid}.{eid}"
#         actuator_model = await arlsim.ARLActuator(uid=uid)
#         world.connect(
#             actuator_model,
#             entities[full_id],
#             ("setpoint", attr),
#             time_shifted=True,
#             initial_data={"setpoint": None},
#         )

#     LOG.info("Starting mosaik run ...")
#     await world.run(
#         until=meta_params["end"],
#         print_progress=not meta_params["silent"],
#     )

#     LOG.info("Simulation finished.")
#     sim_finished.set()


def _start_mosaik(
    get_world: Callable,
    params: Dict[str, Any],
    *,
    sensors: list[str],
    actuators: list[str],
    sensor_queue: queue.Queue,
    actuator_queue: queue.Queue,
    sim_finished: asyncio.Event,
    sync_terminate: asyncio.Event,
    sync_finished: asyncio.Event,
    timeout: int,
):
    """Start the mosaik simulation process

    TODO: Error handling for the case that
    - get_world does not work
    - uid does not match the scheme
    - full_id is not present in entities
    - Mosaik connection errors

    """
    meta_params = params["meta_params"]
    end = meta_params["end"]
    LOG.debug("Attempting to retrieve world object ...")
    world, entities = get_world(params)

    LOG.debug("Starting ARLSyncSimulator ...")
    world.sim_config["ARLSyncSimulator"] = {
        "python": "palaestrai_mosaik.mp.simulator:ARLSyncSimulator"
    }
    arlsim = world.start(
        "ARLSyncSimulator",
        step_size=meta_params["arl_sync_freq"],
        start_date=meta_params.get("start_date", None),
        end=end,
        sensor_queue=sensor_queue,
        actuator_queue=actuator_queue,
        sync_finished=sync_finished,
        sync_terminate=sync_terminate,
        timeout=timeout,
    )

    LOG.debug("Connecting sensor entities ...")
    for uid in sensors:
        sid, eid, attr = uid.split(".")
        full_id = f"{sid}.{eid}"
        sensor_model = arlsim.ARLSensor(uid=uid)
        world.connect(entities[full_id], sensor_model, (attr, "reading"))

    LOG.debug("Connecting actuator entities ...")
    for uid in actuators:
        sid, eid, attr = uid.split(".")
        full_id = f"{sid}.{eid}"
        actuator_model = arlsim.ARLActuator(uid=uid)
        world.connect(
            actuator_model,
            entities[full_id],
            ("setpoint", attr),
            time_shifted=True,
            initial_data={"setpoint": None},
        )

    logger.disable("mosaik")

    LOG.info("Starting mosaik run ...")
    try:
        world.run(until=end, print_progress=not meta_params["silent"])
    except Exception as exc:
        sim_finished.set()
        msg = "Error during the simulation."
        # LOG.exception("Error during the simulation:")
        raise ValueError(msg) from exc

    sim_finished.set()
