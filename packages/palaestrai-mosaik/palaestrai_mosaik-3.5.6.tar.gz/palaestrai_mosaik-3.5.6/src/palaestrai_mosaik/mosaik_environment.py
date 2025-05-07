"""This module contains the :class:`MosaikEnvironment`, which
allows to run mosaik co-simulations with palaestrAI.

"""

from __future__ import annotations

import asyncio
import logging
import queue
import sys
from typing import Any, Dict, List, Optional, Union

import mosaik
from numpy.random import RandomState
from palaestrai.environment.environment import Environment
from palaestrai.environment.environment_baseline import EnvironmentBaseline
from palaestrai.environment.environment_state import EnvironmentState
from palaestrai.types import SimTime
from palaestrai.util import seeding

from . import util
from .config import ENVIRONMENT_LOGGER_NAME
from .util import log_

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
        silent: bool = False,
        no_extra_step: bool = False,
        simulation_timeout: int = 60,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(uid, seed=seed)
        self.rng: RandomState = seeding.np_random(self.seed)[0]

        self.sensor_queue: Optional[asyncio.Queue] = None
        self.actuator_queue: Optional[asyncio.Queue] = None
        self.sim_terminate: Optional[asyncio.Event] = None
        self.sim_finished: Optional[asyncio.Event] = None
        self.sync_terminate: Optional[asyncio.Event] = None
        self.sync_finished: Optional[asyncio.Event] = None

        self.module = module
        self.description_func = description_func
        self.instance_func = instance_func
        self._simulation_timeout = simulation_timeout
        self.start_date = start_date
        self.infer_start_date = infer_start_date

        self.mosaik_params = {} if params is None else params
        self.mosaik_params["meta_params"] = {
            "seed": self.rng.randint(sys.maxsize),
            "end": util.parse_end(end) + (0 if no_extra_step else 1),
            "arl_sync_freq": arl_sync_freq,
            "silent": silent,
        }
        if arl_sync_freq >= self.mosaik_params["meta_params"]["end"]:
            msg = (
                f"'arl_sync_freq' ({arl_sync_freq}) has to be < then the 'end'"
                f" ({self.mosaik_params['meta_params']['end']}) of the "
                "simulation"
            )
            raise ValueError(msg)

        self._prev_simtime = SimTime(simtime_ticks=0)
        self.simtime_ticks: int = 0
        self.simtime_timestamp = None
        self.world: Optional[mosaik.AsyncWorld] = None

    def _prepare_async_components(self):
        self.sensor_queue = asyncio.Queue(1)
        self.actuator_queue = asyncio.Queue(1)

        self.sim_terminate = asyncio.Event()
        self.sim_finished = asyncio.Event()
        self.sync_terminate = asyncio.Event()
        self.sync_finished = asyncio.Event()

    async def start_environment(self) -> EnvironmentBaseline:
        LOG.info("%s starting Mosaik Co-simulation ...", log_(self))
        self._prepare_async_components()

        description, instance = util.load_functions(self)
        static_world_state = util.load_sensors_and_actuators(self, description)
        simtime = SimTime(simtime_ticks=0)

        start_date = util.load_start_date(self, static_world_state)
        if start_date is not None:
            simtime.simtime_timestamp = start_date

        LOG.debug("Attempting to retrieve world object ...")
        self.world, entities = await instance(self.mosaik_params)

        self.sync_task = asyncio.create_task(
            _start_mosaik(
                self.world,
                entities,
                self.mosaik_params,
                sensors=[s.uid for s in self.sensors],
                actuators=[a.uid for a in self.actuators],
                sensor_queue=self.sensor_queue,
                actuator_queue=self.actuator_queue,
                sim_finished=self.sim_finished,
                sync_finished=self.sync_finished,
                sync_terminate=self.sync_terminate,
                timeout=self._simulation_timeout,
            )
        )

        LOG.info(
            "%s finished setup. Co-simulation is now running. Now waiting for "
            "initial sensor readings ...",
            log_(self),
        )

        try:
            done, data = await asyncio.wait_for(
                self.sensor_queue.get(), timeout=self._simulation_timeout * 2
            )
        except asyncio.TimeoutError:
            self.sync_terminate.set()
            raise

        util.load_sensors_from_queue_data(self, data)

        return EnvironmentBaseline(
            sensors_available=self.sensors,
            actuators_available=self.actuators,
            simtime=simtime,
        )

    async def update(self, actuators):
        LOG.info("%s updating ...", log_(self))
        data = {}
        self.simtime_ticks = 0
        self.simtime_timestamp = None

        LOG.debug("%s sending actuators to simulation ...", log_(self))
        for actuator in actuators:
            data[actuator.uid] = actuator.value
        try:
            await asyncio.wait_for(
                self.actuator_queue.put(data), timeout=self._simulation_timeout
            )
            LOG.debug("%s waiting for sensor readings ...", log_(self))
            done, data = await asyncio.wait_for(
                self.sensor_queue.get(), timeout=self._simulation_timeout
            )
        except asyncio.TimeoutError:
            self.sync_terminate.set()
            raise

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

    async def shutdown(self, reset=False):
        LOG.info(
            "%s starting shutdown of simulation process ...",
            log_(self),
        )

        self.is_terminal = not reset
        if not self.sim_finished.is_set():
            try:
                await asyncio.wait_for(
                    self.world.shutdown(), timeout=self._simulation_timeout
                )
            except asyncio.TimeoutError:
                LOG.exception(
                    "%s: Simulation did not terminate in time", log_(self)
                )
                return

        # Only in Python 3.13+
        # self.actuator_queue.shutdown()
        # self.sensor_queue.shutdown()

        LOG.info("%s: Simulation terminated gracefully", log_(self))


async def _start_mosaik(
    world: mosaik.AsyncWorld,
    entities: List[Any],
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
    LOG.debug("Starting ARLSyncSimulator ...")
    world.sim_config["ARLSyncSimulator"] = {
        "python": "palaestrai_mosaik.simulator:ARLSyncSimulator"
    }
    arlsim = await world.start(
        "ARLSyncSimulator",
        step_size=meta_params["arl_sync_freq"],
        start_date=meta_params.get("start_date", None),
        sensor_queue=sensor_queue,
        actuator_queue=actuator_queue,
        sync_finished=sync_finished,
        sync_terminate=sync_terminate,
        end=end,
        timeout=timeout,
    )
    LOG.debug("Connecting sensor entities ...")
    for uid in sensors:
        sid, eid, attr = uid.split(".")
        full_id = f"{sid}.{eid}"
        sensor_model = await arlsim.ARLSensor(uid=uid)
        LOG.debug("Connecting %s ...", full_id)
        world.connect(entities[full_id], sensor_model, (attr, "reading"))

    LOG.debug("Connecting actuator entities ...")
    for uid in actuators:
        sid, eid, attr = uid.split(".")
        full_id = f"{sid}.{eid}"
        actuator_model = await arlsim.ARLActuator(uid=uid)
        world.connect(
            actuator_model,
            entities[full_id],
            ("setpoint", attr),
            time_shifted=True,
            initial_data={"setpoint": None},
        )

    LOG.info("Starting mosaik run ...")
    await world.run(
        until=meta_params["end"],
        print_progress=not meta_params["silent"],
    )

    LOG.info("Simulation finished. Initiating shutdown ...")
    await world.shutdown()
    LOG.info("Mosaik shut down successfully.")
    sim_finished.set()
