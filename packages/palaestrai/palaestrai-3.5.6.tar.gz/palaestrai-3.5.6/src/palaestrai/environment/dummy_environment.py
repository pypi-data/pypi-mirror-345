"""
This module contains the class :class:`DummyEnvironment`. It could be
used in an experiment for reference purposes.
"""

import numpy as np
import random
from typing import List, Callable

from palaestrai.agent import SensorInformation, ActuatorInformation
from palaestrai.types import Discrete, Box
from .environment import Environment
from ..agent.reward_information import RewardInformation


class DummyEnvironment(Environment):
    """
    This class provides a dummy environment with a fixed number of sensors. The
    environment terminates after a fixed number of updates.

    Parameters
    ----------
    connection : broker_connection
        the URI which is used to connect to the simulation broker. It is used
        to communicate with the simulation controller.
    uid : uuid4
        a universal id for the environment
    seed : int
        Seed for recreation
    discrete : bool, optional
        If set to True, the environment will only use discrete spaces.
        Otherwise, the spaces are continuous. Default is `True`.
    """

    def __init__(
        self,
        uid: str,
        broker_uri: str,
        seed: int,
        discrete: bool = True,
        max_iter: int = 10,
    ):
        super().__init__(uid, broker_uri, seed)
        self.iter: int = 0
        self.max_iter: int = max_iter
        self.discrete: bool = discrete

    def start_environment(self):
        """
        This method is called when an `EnvironmentStartRequest` message is
        received. This dummy environment is represented by 10 sensors and
        10 actuators. The sensors are of the type `SensorInformation` and have
        a random value of either 0 or 1, an `observation_space` between 0 and 1
        and an integer number as id.
        The actuators are of the type `ActuatorInformation` and contain a
        value of Discrete(1), a `space` of None and an integer
        number as id.

        Returns
        -------
        tuple :
            A list containing the `SensorInformation` for each of the 10
            sensors and a list containing the `ActuatorInformation` for each
            of the 10 actuators.
        """
        self.iter = 0
        return (
            [self._create_sensor(i) for i in range(10)],
            [self._create_actuator(i) for i in range(10)],
        )

    def update(self, actuators):
        """
        This method is called when an `EnvironmentUpdateRequest` message is
        received. While values of the actuators manipulate an actual
        environment, in here those values have no impact on the behavior of
        the dummy environment.
        The state of this dummy environment is represented via random values of
        the `SensorInformation` from the 10 sensors.
        In this dummy environment the reward for the state is a random value of
        either 0 or 1.
        The method returns a list of `SensorInformation`, the random reward and
        the boolean `is_terminal`. After 10 updates the `is_terminal` value is
        set to True which triggers the respective shutdown messages.

        Parameters
        ----------
        actuators : list[`ActuatorInformation`]
            A list of `ActuatorInformation` to interact with the environment.

        Returns
        -------
        tuple :
            A list of `SensorInformation` representing the 10 sensors, the
            reward and boolean for `is_terminal`.

        """

        self.iter += 1
        return (
            [self._create_sensor(i) for i in range(10)],
            self.create_reward(),
            (self.iter >= self.max_iter),
        )

    def _create_actuator(self, actuator_id):
        if self.discrete:
            return ActuatorInformation(
                space=Discrete(100),
                value=0,
                uid=f"{actuator_id}",
            )
        else:
            return ActuatorInformation(
                space=Box(0, 10, shape=()),
                value=0,
                uid=f"{actuator_id}",
            )

    def create_reward(self):
        return [
            RewardInformation(
                self.iter % self.max_iter,
                Discrete(self.max_iter + 1),
                "Dummy Reward",
            )
        ]

    def _create_sensor(self, sensor_id):
        if self.discrete:
            return SensorInformation(
                value=self.iter % self.max_iter,
                space=Discrete(self.max_iter + 1),
                uid=f"{sensor_id}",
            )
        else:
            return SensorInformation(
                value=random.randint(0, 1),
                space=Box(0, 2, shape=()),
                uid=f"{sensor_id}",
            )
