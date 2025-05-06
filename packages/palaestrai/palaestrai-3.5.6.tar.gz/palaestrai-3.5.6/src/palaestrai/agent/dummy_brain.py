from __future__ import annotations

import io
import sys
from typing import TYPE_CHECKING, List, Optional

from .brain import Brain
from .brain_dumper import BrainDumper
from ..core.protocol import MuscleUpdateResponse

if TYPE_CHECKING:
    from .sensor_information import SensorInformation
    from .actuator_information import ActuatorInformation


class DummyBrain(Brain):
    def __init__(self):
        super().__init__()
        self._dummy_value = 42  # Our brain state. Designated by fair dice roll

    def thinking(self, muscle_id, data_from_muscle):
        self._dummy_value = (
            data_from_muscle + 1 if data_from_muscle is not None else 0
        )
        return self._dummy_value  # Assume this is the Muscle's "self.iter"

    def load(self):
        try:
            self._dummy_value = int.from_bytes(
                BrainDumper.load_brain_dump(self._dumpers).read(),
                sys.byteorder,
            )
        except AttributeError:
            # We returned "None"
            pass

    def store(self):
        bio = io.BytesIO(
            self._dummy_value.to_bytes(
                (self._dummy_value.bit_length() + 7) // 8, sys.byteorder
            )
        )
        BrainDumper.store_brain_dump(bio, self._dumpers)
