from __future__ import annotations

from typing import Any

from .brain import Brain


class NoneBrain(Brain):
    """A Brain implementation that never does anything.

    For a kind of agent that consists only of a :class:`Muscle`,
    e.g., simple scripted agents, there exists no learning component.
    For these cases, this NoneBrain exists.
    It simply never returns an update to the corresponding :class:`Muscle`.
    """

    def thinking(self, *args, **kwargs) -> Any:
        return None

    def load(self):
        pass

    def store(self):
        pass
