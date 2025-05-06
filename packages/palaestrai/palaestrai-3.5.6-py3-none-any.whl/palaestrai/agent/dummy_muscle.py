import numpy as np

from palaestrai.types import Discrete
from palaestrai.util.exception import OutOfActionSpaceError

from .muscle import Muscle


class DummyMuscle(Muscle):
    """Implements the simples possible Muscle.

    This Muscle implementation simply samples the action spaces of all
    actuators connected to it.
    If the additional mode ``count_upwards`` is set, then all :class:`Discrete`
    action spaces receive upwards counting values (modulo the space dimension).
    The latter mode exists as convience for testing purposes.

    Parameters
    ----------
    count_upwards : bool, default: False
        Enables upward counting modulo action space for :class:`Discrete`
        actuators.
    """

    def __init__(self, count_upwards: bool = False):
        super().__init__()
        self.iter = -1
        self.count_upwards = count_upwards

    def propose_actions(self, sensors, actuators_available):
        for actuator in actuators_available:
            if isinstance(actuator.space, Discrete) and self.count_upwards:
                value = int(self.iter % actuator.space.n)
            else:
                value = actuator.space.sample()
            try:
                actuator(value)
            except OutOfActionSpaceError:
                actuator(np.array(value, dtype=actuator.space.dtype))

        return actuators_available, self.iter

    def update(self, data):
        self.iter = data
