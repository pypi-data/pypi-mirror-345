import unittest
from unittest.mock import MagicMock, Mock, patch

import numpy as np
from palaestrai.agent import ActuatorInformation, SensorInformation
from palaestrai.types import Box

from palaestrai_mosaik.mp.mosaik_environment import (
    MosaikEnvironment,
    _start_mosaik,
)


class TestMosaikEnvironment(unittest.TestCase):
    def setUp(self):
        self.test_sensors1 = [
            {
                "uid": "test_uid1",
                "space": "Box(low=0, high=1, shape=(), dtype=np.int32)",
            },
            SensorInformation(
                value=None,
                space=Box(0, 1, (), dtype=np.int32),
                uid="test_uid2",
            ),
        ]
        self.test_sensors2 = [
            SensorInformation(
                value=None,
                space=Box(0, 1, (), dtype=np.int32),
                uid="test_uid1",
            ),
            SensorInformation(
                value=None,
                space=Box(0, 1, (), dtype=np.int32),
                uid="test_uid2",
            ),
        ]
        self.test_actuators1 = [
            {
                "uid": "test_uid3",
                "space": "Box(low=0, high=1, shape=(), dtype=np.int32)",
            },
            ActuatorInformation(
                value=None, space=Box(0, 1, (), np.int32), uid="test_uid4"
            ),
        ]
        self.test_actuators2 = [
            ActuatorInformation(
                value=None, space=Box(0, 1, (), np.int32), uid="test_uid3"
            ),
            ActuatorInformation(
                value=None, space=Box(0, 1, (), np.int32), uid="test_uid4"
            ),
        ]
        self.test_actuators2[0].value = np.array(0, dtype=np.int32)
        self.test_actuators2[1].value = np.array(1, dtype=np.int32)

    def test_start_environment(self):
        rng = MagicMock()
        rng.randint = Mock(return_value=0)
        np_random = MagicMock(return_value=[rng])
        with patch(
            "palaestrai.util.seeding.np_random",
            new_callable=MagicMock(return_value=np_random),
        ):
            menv = MosaikEnvironment(
                "test_uid",
                broker_uri="test_uri",
                seed=0,
                module="test.module",
                description_func="describe",
                instance_func="get_world",
                arl_sync_freq=900,
                end=9000,
            )
        with self.assertRaises(
            ValueError, msg="Error during loading of loader functions"
        ):
            baseline = menv.start_environment()
            self.assertIsNone(baseline.sensors_available)
            self.assertIsNone(baseline.actuators_available)

        desc_fnc = MagicMock(return_value=([], [], {}))
        loader = MagicMock(
            return_value=MagicMock(return_value=(desc_fnc, MagicMock()))
        )
        with (
            patch(
                "palaestrai_mosaik.util.load_functions", new_callable=loader
            ),
            self.assertRaises(
                ValueError, msg="Error during calling the description function"
            ),
        ):
            baseline = menv.start_environment()
            self.assertIsNone(baseline.sensors_available)
            self.assertIsNone(baseline.actuators_available)
        desc_fnc.assert_called_with(
            {
                "meta_params": {
                    "seed": 0,
                    "end": 9001,
                    "arl_sync_freq": 900,
                    "silent": False,
                }
            }
        )

        loader_fncs = MagicMock(
            return_value=MagicMock(
                return_value=(
                    MagicMock(return_value=([], [], {})),
                    MagicMock(),
                )
            )
        )
        with (
            patch(
                "palaestrai_mosaik.util.load_functions",
                new_callable=loader_fncs,
            ) as mocked_load,
            patch("multiprocessing.Process.start", new_callable=MagicMock()),
            patch.multiple(
                "queue.Queue",
                put=MagicMock(),
                get=MagicMock(return_value=(True, {})),
            ),
            self.assertRaises(ValueError, msg="No sensors and"),
        ):
            baseline = menv.start_environment()
            self.assertIsNone(baseline.sensors_available)
            self.assertIsNone(baseline.actuators_available)

        mocked_load.assert_called()

        loader_fncs = MagicMock(
            return_value=MagicMock(
                return_value=(
                    MagicMock(
                        return_value=(
                            self.test_sensors1,
                            self.test_actuators1,
                            {},
                        )
                    ),
                    MagicMock(),
                )
            )
        )
        qo = MagicMock(name="queue_obj")
        qo.get = MagicMock(
            name="get", return_value=(False, {"test_uid1": 0, "test_uid2": 1})
        )
        q = MagicMock(name="Context")
        q.Queue = MagicMock(name="Queue", return_value=qo)
        mp_ctx = MagicMock(name="get_context", return_value=q)

        with (
            patch(
                "palaestrai_mosaik.util.load_funcs", new_callable=loader_fncs
            ),
            patch(
                "multiprocessing.get_context",
                new_callable=MagicMock(name="Root", return_value=mp_ctx),
            ),
        ):
            baseline = menv.start_environment()

        self.assertEqual(2, len(baseline.sensors_available))
        self.assertEqual(2, len(baseline.actuators_available))
        self.assertEqual("test_uid1", baseline.sensors_available[0].uid)
        self.assertEqual("test_uid2", baseline.sensors_available[1].uid)
        self.assertEqual(0, baseline.sensors_available[0].value)
        self.assertEqual(1, baseline.sensors_available[1].value)
        self.assertEqual("test_uid3", baseline.actuators_available[0].uid)
        self.assertEqual("test_uid4", baseline.actuators_available[1].uid)

    def test_update(self):
        menv = MosaikEnvironment(
            "test_uid",
            broker_uri="test_uri",
            seed=0,
            module="test.module",
            description_func="describe",
            instance_func="get_world",
            arl_sync_freq=900,
            end=9000,
        )
        menv.sen_map = {
            "test_uid1": self.test_sensors2[0],
            "test_uid2": self.test_sensors2[1],
        }
        menv.actuator_queue = MagicMock()
        menv.actuator_queue.put = MagicMock()
        menv.sensor_queue = MagicMock()
        menv.sensor_queue.get = MagicMock(
            return_value=(False, {"test_uid1": 0, "test_uid2": 1})
        )
        menv.reward = MagicMock(return_value=[])
        state = menv.update(self.test_actuators2)

        self.assertEqual(2, len(state.sensor_information))
        self.assertEqual(0, state.sensor_information[0].value)
        self.assertEqual(1, state.sensor_information[1].value)
        self.assertEqual(0, len(state.rewards))
        self.assertFalse(state.done)

    def test_start_world(self):
        arlsim = MagicMock()

        world = MagicMock()
        world.start = MagicMock(return_value=arlsim)
        world.connect = MagicMock()
        world.run = MagicMock()
        get_world = MagicMock(return_value=(world, {}))
        params = {
            "meta_params": {"arl_sync_freq": 900, "end": 9000, "silent": True}
        }
        sensors = [
            "test_uid1.test_eid.test_attr",
            "test_uid2.test_eid.test_attr",
        ]
        actuators = [
            "test_uid3.test_eid.test_attr",
            "test_uid4.test_eid.test_attr",
        ]

        with self.assertRaises(KeyError):
            _start_mosaik(
                get_world,
                params,
                sensors=sensors,
                actuators=actuators,
                sensor_queue=MagicMock(),
                actuator_queue=MagicMock(),
                sim_finished=MagicMock(),
                sync_finished=MagicMock(),
                sync_terminate=MagicMock(),
                timeout=60,
            )

        arlsim.ARLSensor = MagicMock(side_effect=["Sensor-1", "Sensor-2"])
        arlsim.ARLActuator = MagicMock(
            side_effect=["Actuator-1", "Actuator-2"]
        )
        get_world = MagicMock(
            return_value=(
                world,
                {
                    "test_uid1.test_eid": "Model-1",
                    "test_uid2.test_eid": "Model-2",
                    "test_uid3.test_eid": "Model-3",
                    "test_uid4.test_eid": "Model-4",
                },
            )
        )

        _start_mosaik(
            get_world,
            params,
            sensors=sensors,
            actuators=actuators,
            sensor_queue=MagicMock(),
            actuator_queue=MagicMock(),
            sim_finished=MagicMock(),
            sync_finished=MagicMock(),
            sync_terminate=MagicMock(),
            timeout=60,
        )

        world.connect.assert_any_call(
            "Model-1", "Sensor-1", ("test_attr", "reading")
        )
        world.connect.assert_any_call(
            "Model-2", "Sensor-2", ("test_attr", "reading")
        )
        world.connect.assert_any_call(
            "Actuator-1",
            "Model-3",
            ("setpoint", "test_attr"),
            time_shifted=True,
            initial_data={"setpoint": None},
        )
        world.connect.assert_any_call(
            "Actuator-2",
            "Model-4",
            ("setpoint", "test_attr"),
            time_shifted=True,
            initial_data={"setpoint": None},
        )

        world.run.assert_called_with(until=9000, print_progress=False)


if __name__ == "__main__":
    unittest.main()
